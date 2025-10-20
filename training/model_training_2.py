#pip install torch transformers

import pandas as pd
import numpy as np
import random
import torch
import ast
import os
import re
import csv
import json

from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments

from sklearn.model_selection import train_test_split
from seqeval.metrics import precision_score, recall_score, f1_score

# Констант
RANDOM_STATE=654321

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed(RANDOM_STATE)

df = pd.read_csv('train.csv', sep=';')

# Function to convert annotation string to tuples
def parse_annotations(annotation_str):
    # Use ast.literal_eval to safely convert string to list of tuples
    return ast.literal_eval(annotation_str)

# Apply the parsing function to the annotations column
df['annotations'] = df['annotation'].apply(parse_annotations)

df.loc[4002, 'annotation'] = "[(0, 7, 'B-TYPE'), (8, 9, 'O'), (10, 17, 'O')]"


# Tokenizer initialization
tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')

# Function to convert data to BERT format
def convert_to_bert_format(data, tokenizer):
    input_ids = []
    attention_masks = []
    labels = []
    label_map = {}

    for idx, row in data.iterrows():
        text = row['sample']
        annotations = row['annotations']

        # Tokenize the text
        encodings = tokenizer(text, truncation=True, padding='max_length', max_length=32, is_split_into_words=False)
        input_ids.append(encodings['input_ids'])
        attention_masks.append(encodings['attention_mask'])

        # Create a new label array
        new_label_array = [-100] * len(encodings['input_ids'])  # Initialize with -100 (ignore padding)
        word_ids = encodings.word_ids(batch_index=0)

        for start, end, label in annotations:
            start_token = encodings.char_to_token(start)
            end_token = encodings.char_to_token(end - 1)
            if start_token is None or end_token is None:
                continue

            # Add label to the label_map
            if label not in label_map:
                label_map[label] = len(label_map)

            # Assign the label to the first token of the word
            for i in range(start_token, end_token + 1):
                if word_ids[i] == word_ids[start_token]:  # Same word
                    if i == start_token:  # First subword
                        new_label_array[i] = label_map[label]
                    else:  # Subsequent subwords
                        new_label_array[i] = -100  # Ignore
        labels.append(new_label_array)

    return input_ids, attention_masks, labels, label_map

# Custom Dataset Class
class TokenClassificationDataset(Dataset):
    def __init__(self, input_ids, attention_masks, labels):
        self.input_ids = input_ids
        self.attention_masks = attention_masks
        self.labels = labels

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            'input_ids': torch.tensor(self.input_ids[idx], dtype=torch.long),
            'attention_mask': torch.tensor(self.attention_masks[idx], dtype=torch.long),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

# Define training and evaluation
def train(df):
    # Prepare dataset
    input_ids, attention_masks, labels, label_map = convert_to_bert_format(df, tokenizer)
    dataset = TokenClassificationDataset(input_ids, attention_masks, labels)

    # Create id2label mapping
    id2label = {v: k for k, v in label_map.items()}

    # Save the label_map for later evaluation
    os.makedirs('./saved_model', exist_ok=True)
    with open('./saved_model/label_map.json', 'w') as f:
        json.dump(label_map, f)

    # Split the dataset into train and validation sets
    train_dataset, val_dataset = train_test_split(dataset, test_size=0.1)

    # Prepare data loaders
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)

    # Set up device (GPU if available)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # Load the pre-trained model
    model = AutoModelForTokenClassification.from_pretrained(
        'bert-base-multilingual-cased',
        num_labels=len(label_map),  # Set this dynamically based on label_map
    )

    # Move model to the correct device (GPU or CPU)
    model.to(device)

    # Training arguments
    training_args = TrainingArguments(
        output_dir='./results',  # where to save model
        num_train_epochs=10,  # number of training epochs
        per_device_train_batch_size=16,  # batch size for training
        per_device_eval_batch_size=16,  # batch size for evaluation
        eval_strategy="epoch",  # evaluate every epoch
        save_strategy="epoch",  # save the model every epoch
        logging_dir='./logs',  # where to save logs
        logging_steps=10,  # log every 10 steps
        load_best_model_at_end=True,  # load the best model at the end of training
        metric_for_best_model="f1",  # use F1 score to determine best model
        greater_is_better=True,
    )

    # Compute metrics
    def compute_metrics(pred):
        pred_labels = pred.predictions.argmax(axis=-1)
        true_labels = pred.label_ids

        # Initialize lists to hold the true and predicted labels after filtering padding tokens
        true_labels_filtered = []
        pred_labels_filtered = []

        for true_seq, pred_seq in zip(true_labels, pred_labels):
            true_seq_filtered = []
            pred_seq_filtered = []
            for true_label, pred_label in zip(true_seq, pred_seq):
                if true_label != -100:
                    true_seq_filtered.append(true_label)
                    pred_seq_filtered.append(pred_label)

            true_labels_filtered.append(true_seq_filtered)
            pred_labels_filtered.append(pred_seq_filtered)

        true_labels_converted = [[id2label[label] for label in seq] for seq in true_labels_filtered]
        pred_labels_converted = [[id2label[label] for label in seq] for seq in pred_labels_filtered]

        precision = precision_score(true_labels_converted, pred_labels_converted, average='macro')
        recall = recall_score(true_labels_converted, pred_labels_converted, average='macro')
        f1 = f1_score(true_labels_converted, pred_labels_converted, average='macro')

        return {'precision': precision, 'recall': recall, 'f1': f1}

    # Instantiate the CustomTrainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # Train the model
    trainer.train()

    # Save the model after training
    os.makedirs('./saved_model', exist_ok=True)
    model.save_pretrained('./saved_model')
    tokenizer.save_pretrained('./saved_model')

    # Evaluate the model on the validation set
    results = trainer.evaluate()
    print(results)

# Example of how to call the train and evaluate function
train(df)

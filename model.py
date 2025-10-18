import json
from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch
import re

from app import LOCAL_MODEL_DIR, HF_MODEL_PATH
from pydantic_models import SpanOut


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f'chosen_device:{device}')


def load_model_and_tokenizer_from_local(model_dir: str):
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    with open(f'{model_dir}/label_map.json', 'r') as f:
        label_map = json.load(f)
    id2label = {v: k for k, v in label_map.items()}
    model = model.to(device)
    return model, tokenizer, id2label


def load_model_and_tokenizer(repo_id: str):
    model = AutoModelForTokenClassification.from_pretrained(
        repo_id,
        subfolder="best_model"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        repo_id,
        subfolder="best_model"
    )
    id2label = model.config.id2label
    model = model.to(device)
    return model, tokenizer, id2label


try:
    model, tokenizer, id2label = load_model_and_tokenizer_from_local(
        LOCAL_MODEL_DIR
    )
    print(f'Loaded model from local directory: {LOCAL_MODEL_DIR}')
except Exception as e:
    print(f'Failed to load model from local path: {e}')
    model, tokenizer, id2label = load_model_and_tokenizer(HF_MODEL_PATH)
    print(f'Loaded model from Hugging Face Model Hub: {HF_MODEL_PATH}')


def process_text(text: str):
    tokens = tokenizer(
        text, return_tensors="pt", truncation=True,
        padding=True, is_split_into_words=False
    )
    input_ids = tokens['input_ids'].to(device)
    word_ids = tokens.word_ids(batch_index=0)
    with torch.no_grad():
        outputs = model(input_ids=input_ids)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1).squeeze().tolist()
    input_ids_cpu = input_ids[0].cpu()
    sliced_predictions = predictions[1:-1]
    mask = [
        1 if '##' not in tokenizer.convert_ids_to_tokens(i)
        else 0 for i in input_ids_cpu[1:-1].tolist()
    ]
    masked_predictions = [
        pred for pred, m in zip(sliced_predictions, mask) if m == 1
    ]
    l_final = []
    i = 0
    for match in re.finditer(r'\S+', text):
        word = match.group()
        start_index = match.start()
        end_index = match.end()
        label_index = masked_predictions[i]
        l_final.append(SpanOut(
            start_index=start_index,
            end_index=end_index,
            entity=id2label[label_index]
        ))
        i += 1
    return l_final

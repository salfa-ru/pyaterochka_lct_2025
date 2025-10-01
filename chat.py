
chat_pipeline = None

def get_chat_model():
    global chat_pipeline
    if chat_pipeline is None:
        #from transformers import pipeline
        #chat_pipeline = pipeline()
        pass
    return chat_pipeline

def get_chat_response(user_message: str, history: list[str] = None) -> str:
    if history is None:
        history = []
    model = get_chat_model()
    input_text = "\n".join(history + [f"User: {user_message}"])
    #response = chat_pipeline(input_text)
    #return response
    return "Это заглушка ответа от чат-бота."
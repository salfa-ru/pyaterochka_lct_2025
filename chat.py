from model import process_text
from database import simplest_example_database


def get_chat_response(user_message: str, history: list[str] = None) -> str:
    if history is None:
        history = []
    input_text = "\n".join(history + [f"{user_message}"])

    response = process_text(input_text)
    response_lines = []
    result_responce = {}
    for span in response:
        category = span.entity.split('-')[-1].lower()
        category_ru = {
            "type": "категория",
            "brand": "бренд",
            "volume": "объем",
            "percent": "процент"
        }.get(category, category)
        value = input_text[span.start_index:span.end_index]
        if category == 'type':
            result_responce['image'] = simplest_example_database.get(value.lower())
            result_responce['category'] = value.lower()
        response_lines.append(f"{category_ru} - {value}")
    result_responce['decrypted_data'] = response_lines
    return result_responce

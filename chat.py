from model import process_text


def get_chat_response(user_message: str, history: list[str] = None) -> str:
    if history is None:
        history = []
    input_text = "\n".join(history + [f"{user_message}"])

    response = process_text(input_text)
    response_lines = []

    for span in response:
        category = span.entity.split('-')[-1].lower()
        category_ru = {
            "type": "категория",
            "brand": "бренд",
            "volume": "объем",
            "percent": "процент"
        }.get(category, category)

        value = input_text[span.start_index:span.end_index]
        response_lines.append(f"{category_ru} - {value}")
    return response_lines

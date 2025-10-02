# Pyaterochka NER (NER Hackathon Stub)

Лёгкий сервис распознавания сущностей (NER) на базе Hugging Face Transformers + FastAPI. Проект включает модель в каталоге `best_saved_model_0.9`, API для предсказаний и простой чат-обёртку.
Код автоматически определяет наличие CUDA‑совместимого GPU и использует его при наличии; иначе выполняется на CPU.


### Быстрый запуск локально

```sh
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows
pip install -r [requirements.txt](http://_vscodecontentref_/0)
uvicorn app:app --host 0.0.0.0 --port 8000
```
### Запуск в Docker
Достаточно скопировать на VPS или локальную машину на linux docker-compose.yml и все необходимые данные подтянутся из DockerHub

```sh
docker-compose -f docker-compose.yml up
# или
docker build -t ner-x5 .
docker run -p 8000:8000 ner-x5
```

## API

- GET /health — проверка статуса
- POST /api/predict — payload: { "input": "текст" }, возвращает список объектов SpanOut с полями start_index, end_index, entity
- POST /chat — payload: { "message": "...", "history": ["..."] }, возвращает {"response": [...]}

Модель загружается из best_saved_model в load_model_and_tokenizer.
Файлы модели хранятся в папке best_saved_model, структура необходимых файлов:
- config.json
- label_map.json
- model.safetensors
- special_tokens_map.json
- tokenizer_config.json
- tokenizer.json

## Внешние источники данных и предобученные модели
### Использованные предобученные модели
**BERT-base Multilingual Cased**
- Тип: Предобученная языковая модель трансформеров
- Источник: Hugging Face Model Hub
- Разработчик: Google Research
- Назначение в проекте:
    - Использовалась в качестве базовой модели для тонкой настройки (fine-tuning)
    - Применялась для задачи распознавания именованных сущностей (NER)
    - Токенизатор модели использовался для предобработки текстовых данных


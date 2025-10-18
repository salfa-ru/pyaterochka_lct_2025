# Pyaterochka NER (NER Hackathon Stub)

Лёгкий сервис распознавания сущностей (NER) на базе Hugging Face Transformers + FastAPI. Проект автоматически поднимает модель из локальной папки best_saved_model или из репозитория Hugging Face Model Hub.
Код автоматически определяет наличие CUDA‑совместимого GPU и использует его при наличии; иначе выполняется на CPU.


### Быстрый запуск локально

Скрипт в первую очередь пытается загрузить модель из локальной папки best_saved_model. Если папка отсутствует или модель не может быть загружена, скрипт попытается загрузить модель из репозитория Hugging Face Model Hub по указанному пути.
Ссылка на модель в Hugging Face Model Hub: https://huggingface.co/Reg789/Bert_NER_Piaterochka_2025

```sh
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
### Запуск в Docker
Достаточно скопировать на VPS или локальную машину на linux docker-compose.yml и все необходимые данные подтянутся из DockerHub
Контейнер teosvain/ner-x5 хранится по ссылку (https://hub.docker.com/repository/docker/teosvain/ner-x5/general)

```sh
docker-compose -f docker-compose.yml up
```

## API

- GET /health — проверка статуса
- POST /api/predict — payload: { "input": "текст" }, возвращает список объектов SpanOut с полями start_index, end_index, entity
- POST /chat — payload: { "message": "...", "history": ["..."] }, возвращает {"response": [...]}

Модель загружается из best_saved_model в функции load_model_and_tokenizer.
Файлы модели хранятся в папке best_saved_model, структура необходимых файлов:
- config.json
- label_map.json
- model.safetensors
- special_tokens_map.json
- tokenizer_config.json
- tokenizer.json

## Пути к моделям
Пути к моделям задаются в файле app.py. При необходимости их можно изменить:
```bash
LOCAL_MODEL_DIR = './best_saved_model'
HF_MODEL_PATH = 'Reg789/Bert_NER_Piaterochka_2025'
```

## Настройки FastAPI приложения:
- Название приложения: "NER Hackathon Stub (Async, rule-based)"
- Разрешённые источники (CORS): origins
При необходимости можно изменить название приложения и список разрешённых источников в app.py

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


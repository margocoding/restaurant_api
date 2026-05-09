# Restaurant API

FastAPI + PostgreSQL приложение для управления рестораном.

## Требования

- Python 3.9+
- PostgreSQL 12+

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env с вашими настройками PostgreSQL
```

3. Инициализируйте базу данных:
```bash
python -m app.db.init_db
```

4. Запустите сервер:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Menu
- `GET /api/menu` - Получить список всех блюд меню

### Orders
- `POST /api/orders` - Создать новый заказ
- `GET /api/orders` - Получить список всех заказов
- `PATCH /api/orders/{id}/status` - Обновить статус заказа

## Примеры запросов

### GET /api/menu
Ответ:
```json
[
  {
    "id": 1,
    "name": "Пицца Маргарита",
    "description": "Сыр, томаты, базилик",
    "price": 450,
    "category": "Пицца",
    "image": "https://example.com/margarita.jpg"
  }
]
```

### POST /api/orders
Запрос:
```json
{
  "items": [
    {"menu_item_id": 1, "quantity": 2},
    {"menu_item_id": 3, "quantity": 1}
  ]
}
```

### PATCH /api/orders/{id}/status
Запрос:
```json
{
  "status": "confirmed"
}
```

Возможные статусы: `pending`, `confirmed`, `cooking`, `ready`, `delivered`, `cancelled`

## Документация API

После запуска сервера документация доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

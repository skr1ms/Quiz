# API Спецификация

Проект предоставляет REST API для работы с данными из внешних источников. API построен на FastAPI и автоматически генерирует документацию через OpenAPI/SwaggerUI.

## Базовый URL

- Локальная разработка: `http://localhost:8081`
- Продакшен: зависит от конфигурации сервера

## Документация API

Интерактивная документация доступна по адресу:
- SwaggerUI: `http://localhost:8081/docs`
- ReDoc: `http://localhost:8081/redoc`
- OpenAPI Schema: `http://localhost:8081/openapi.json`

Документация доступна только в окружениях `local` и `staging`.

## Формат данных

Все запросы и ответы используют формат JSON с кодировкой UTF-8.

## Аутентификация

В текущей версии API не требует аутентификации. Все endpoints доступны публично.

## Эндпоинты

### Health Check

#### GET /health

Проверка работоспособности сервиса.

**Запрос:**
```
GET /health
```

**Ответ:**
```json
{
  "status": "ok"
}
```

**Статусы:**
- `200 OK` - сервис работает

### Работа с данными API

#### POST /api/data/fetch

Получение данных из внешнего API и сохранение в базу данных.

**Запрос:**
```
POST /api/data/fetch
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "number": 42
}
```

**Параметры:**
- `number` (integer, optional) - число для получения вопроса викторины. Если не указано, будет получен случайный вопрос.

**Ответ (успех):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "apininjas",
  "title": "Вопрос викторины (число 42)",
  "content": "Science: What is the answer to life, the universe, and everything? Ответ: 42",
  "external_id": "42",
  "fetched_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Статусы:**
- `201 Created` - данные успешно получены и сохранены
- `500 Internal Server Error` - ошибка при получении данных из внешнего API

**Пример запроса:**
```bash
curl -X POST http://localhost:8081/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{"number": 42}'
```

**Пример запроса без числа (случайный вопрос):**
```bash
curl -X POST http://localhost:8081/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### GET /api/data/{data_id}

Получение данных по уникальному идентификатору.

**Запрос:**
```
GET /api/data/{data_id}
```

**Параметры пути:**
- `data_id` (UUID, required) - уникальный идентификатор записи

**Ответ (успех):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "apininjas",
  "title": "Вопрос викторины (число 42)",
  "content": "Science: What is the answer to life, the universe, and everything? Ответ: 42",
  "external_id": "42",
  "fetched_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Статусы:**
- `200 OK` - данные найдены
- `404 Not Found` - данные с указанным ID не найдены

**Пример запроса:**
```bash
curl http://localhost:8081/api/data/550e8400-e29b-41d4-a716-446655440000
```

#### GET /api/data

Получение списка всех данных с пагинацией.

**Запрос:**
```
GET /api/data?limit=10&offset=0
```

**Параметры запроса:**
- `limit` (integer, optional, default: 10) - максимальное количество записей в ответе. Минимум: 1, максимум: 100
- `offset` (integer, optional, default: 0) - количество записей для пропуска

**Ответ (успех):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "source": "apininjas",
      "title": "Вопрос викторины (число 42)",
      "content": "Science: What is the answer to life, the universe, and everything? Ответ: 42",
      "external_id": "42",
      "fetched_at": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": null
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "source": "apininjas",
      "title": "Случайный интересный вопрос викторины",
      "content": "History: In what year did World War II end? Ответ: 1945",
      "external_id": null,
      "fetched_at": "2024-01-15T10:31:00Z",
      "created_at": "2024-01-15T10:31:00Z",
      "updated_at": null
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

**Статусы:**
- `200 OK` - список успешно получен

**Пример запроса:**
```bash
curl "http://localhost:8081/api/data?limit=20&offset=0"
```

## Схемы данных

### ApiDataResponse

Схема данных, возвращаемых API.

**Поля:**
- `id` (UUID, required) - уникальный идентификатор записи
- `source` (string, required) - источник данных (например, "apininjas")
- `title` (string, required) - заголовок вопроса викторины
- `content` (string, required) - содержание вопроса с ответом
- `external_id` (string, nullable) - внешний идентификатор (например, число для вопроса)
- `fetched_at` (datetime, required) - время получения данных из внешнего API
- `created_at` (datetime, required) - время создания записи в базе данных
- `updated_at` (datetime, nullable) - время последнего обновления записи

### ApiDataListResponse

Схема ответа со списком данных.

**Поля:**
- `items` (array of ApiDataResponse, required) - массив записей
- `total` (integer, required) - общее количество записей в базе данных
- `limit` (integer, required) - максимальное количество записей в ответе
- `offset` (integer, required) - количество пропущенных записей

### FetchApiDataRequest

Схема запроса на получение данных.

**Поля:**
- `number` (integer, optional) - число для получения вопроса викторины. Если не указано, возвращается случайный вопрос.

## Коды ошибок

### 400 Bad Request
Некорректный запрос. Возможные причины:
- Неверный формат данных
- Отсутствие обязательных полей

### 404 Not Found
Запрашиваемый ресурс не найден.

**Пример ответа:**
```json
{
  "detail": "Данные не найдены"
}
```

### 500 Internal Server Error
Внутренняя ошибка сервера. Возможные причины:
- Ошибка подключения к внешнему API
- Ошибка базы данных
- Другие непредвиденные ошибки

**Пример ответа:**
```json
{
  "detail": "Ошибка при получении данных: Connection timeout"
}
```

## Внешние зависимости

### API Ninjas

Приложение использует API Ninjas для получения вопросов викторины.

**Требования:**
- API ключ должен быть установлен в переменной окружения `API_NINJAS`
- Базовый URL настраивается через `API_NINJAS_BASE_URL` (по умолчанию: `https://api.api-ninjas.com/v1`)

**Endpoints API Ninjas:**
- `/trivia?number={number}` - вопрос викторины для конкретного числа
- `/facts` - случайный вопрос викторины

**Формат ответа API Ninjas:**
```json
[
  {
    "question": "What is the answer to life, the universe, and everything?",
    "answer": "42",
    "category": "Science"
  }
]
```

## Rate Limiting

В текущей версии API не имеет ограничений на количество запросов. Для продакшена рекомендуется настроить rate limiting.

## CORS

API настроен для работы с CORS запросами:
- В локальном окружении: разрешены все источники (`*`)
- В продакшене: источники настраиваются через переменную `CORS_ORIGINS`

## Метрики

API автоматически экспортирует метрики Prometheus по адресу `/metrics`.

**Доступные метрики:**
- HTTP запросы по методам и путям
- Время обработки запросов
- Количество ошибок
- Размер ответов

## Версионирование

В текущей версии API не использует версионирование в URL. Все endpoints находятся в корневом пространстве или под префиксом `/api/data`.

Для будущих версий рекомендуется использовать версионирование:
- `/api/v1/data/fetch`
- `/api/v2/data/fetch`

## Примеры использования

### Получение вопроса для числа 42

```bash
curl -X POST http://localhost:8081/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{"number": 42}'
```

### Получение случайного вопроса

```bash
curl -X POST http://localhost:8081/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Получение списка всех записей

```bash
curl "http://localhost:8081/api/data?limit=10&offset=0"
```

### Получение записи по ID

```bash
curl http://localhost:8081/api/data/550e8400-e29b-41d4-a716-446655440000
```

### Использование в JavaScript/TypeScript

```typescript
// Получение вопроса
const response = await fetch('http://localhost:8081/api/data/fetch', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ number: 42 }),
});

const data = await response.json();
console.log(data);

// Получение списка
const listResponse = await fetch('http://localhost:8081/api/data?limit=10&offset=0');
const listData = await listResponse.json();
console.log(listData.items);
```

### Использование в Python

```python
import requests

# Получение вопроса
response = requests.post(
    'http://localhost:8081/api/data/fetch',
    json={'number': 42}
)
data = response.json()
print(data)

# Получение списка
list_response = requests.get(
    'http://localhost:8081/api/data',
    params={'limit': 10, 'offset': 0}
)
list_data = list_response.json()
print(list_data['items'])
```


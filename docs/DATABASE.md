# База данных

Проект использует PostgreSQL в качестве основной базы данных для хранения данных, полученных из внешних API.

## Технологии

- **PostgreSQL 17** - система управления базами данных
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **asyncpg** - асинхронный драйвер для PostgreSQL
- **Alembic** - инструмент для миграций базы данных

## Структура базы данных

### Таблица api_data

Основная таблица для хранения данных, полученных из внешних API.

**Схема таблицы:**

| Колонка | Тип | Ограничения | Описание |
|---------|-----|-------------|----------|
| id | UUID | PRIMARY KEY, NOT NULL | Уникальный идентификатор записи |
| source | VARCHAR(255) | NOT NULL | Источник данных (например, "apininjas") |
| title | VARCHAR(500) | NOT NULL | Заголовок вопроса викторины |
| content | TEXT | NOT NULL | Содержание вопроса с ответом |
| external_id | VARCHAR(255) | NULL | Внешний идентификатор (например, число) |
| fetched_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Время получения данных из внешнего API |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Время создания записи |
| updated_at | TIMESTAMP WITH TIME ZONE | NULL | Время последнего обновления записи |

**SQL схема:**

```sql
CREATE TABLE api_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    external_id VARCHAR(255),
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## Модели SQLAlchemy

### ApiDataModel

Модель, определенная в `backend/src/app/infrastructure/persistence/models/api_data.py`, представляет таблицу `api_data`.

**Особенности:**
- Использует UUID в качестве первичного ключа
- Автоматически генерирует `created_at` при создании
- Автоматически обновляет `updated_at` при изменении
- Использует UTC для всех временных меток

## Миграции базы данных

### Автоматическое создание таблиц

В текущей версии таблицы создаются автоматически при старте приложения через `Base.metadata.create_all()` в `app_factory.py`.

**Важно:** Этот подход подходит для разработки, но для продакшена рекомендуется использовать миграции Alembic.

### Использование Alembic

Alembic настроен в проекте и готов к использованию для миграций.

**Создание миграции:**
```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

**Применение миграций:**
```bash
alembic upgrade head
```

**Откат миграции:**
```bash
alembic downgrade -1
```

**Просмотр истории миграций:**
```bash
alembic history
```

## Подключение к базе данных

### Строка подключения

Формат строки подключения:
```
postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}
```

**Пример:**
```
postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db
```

### Переменные окружения

Настройка подключения через переменные окружения:
- `DB_HOST` - хост базы данных (по умолчанию: localhost)
- `DB_PORT` - порт базы данных (по умолчанию: 5432)
- `DB_USER` - имя пользователя (обязательно)
- `DB_PASSWORD` - пароль (обязательно)
- `DB_NAME` - имя базы данных (обязательно)

### Настройка в Docker

В Docker окружении используется имя сервиса `postgres` как хост:
- `DB_HOST=postgres`

## Работа с базой данных

### Репозиторий

Доступ к данным осуществляется через репозиторий `ApiDataRepository`, который находится в `backend/src/app/infrastructure/persistence/repositories/api_data_repository.py`.

**Основные методы:**
- `create(entity)` - создание новой записи
- `get_by_id(id)` - получение записи по ID
- `get_all(limit, offset)` - получение списка записей с пагинацией
- `count()` - получение общего количества записей

### Unit of Work

Управление транзакциями базы данных осуществляется через SQLAlchemy Session. Каждый HTTP запрос создает новую сессию, которая автоматически закрывается после завершения запроса.

### Асинхронная работа

Все операции с базой данных выполняются асинхронно через `asyncpg` и SQLAlchemy async API.

## Индексы

В текущей версии индексы не создаются автоматически. Для оптимизации производительности рекомендуется добавить индексы:

**Рекомендуемые индексы:**
```sql
-- Индекс для сортировки по времени получения
CREATE INDEX idx_api_data_fetched_at ON api_data(fetched_at DESC);

-- Индекс для поиска по источнику
CREATE INDEX idx_api_data_source ON api_data(source);

-- Индекс для поиска по внешнему идентификатору
CREATE INDEX idx_api_data_external_id ON api_data(external_id) WHERE external_id IS NOT NULL;
```

## Резервное копирование

### Создание резервной копии

```bash
docker exec postgres pg_dump -U postgres fastapi_db > backup_$(date +%Y%m%d).sql
```

Или с использованием переменных окружения:
```bash
docker exec postgres pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql
```

### Восстановление из резервной копии

```bash
docker exec -i postgres psql -U postgres fastapi_db < backup_20240115.sql
```

Или:
```bash
docker exec -i postgres psql -U $DB_USER $DB_NAME < backup_20240115.sql
```

## Мониторинг базы данных

### Postgres Exporter

Метрики PostgreSQL собираются через `postgres-exporter` и доступны в Grafana.

**Мониторируемые метрики:**
- Количество подключений
- Размер базы данных и таблиц
- Производительность запросов
- Количество транзакций
- Статистика по таблицам

### Прямой доступ к базе данных

Подключение через psql:
```bash
docker exec -it postgres psql -U postgres -d fastapi_db
```

Или через переменные окружения:
```bash
docker exec -it postgres psql -U $DB_USER -d $DB_NAME
```

## Производительность

### Оптимизация запросов

1. Используйте индексы для часто используемых полей
2. Ограничивайте количество возвращаемых записей через пагинацию
3. Используйте `SELECT` только нужных колонок
4. Настройте connection pooling

### Connection Pooling

SQLAlchemy автоматически использует connection pooling. Настройка пула происходит в `database.py` через параметры `AsyncEngine`.

**Рекомендуемые настройки:**
- `pool_size` - размер пула соединений (по умолчанию: 5)
- `max_overflow` - максимальное количество дополнительных соединений (по умолчанию: 10)

## Безопасность

### Рекомендации

1. Используйте сильные пароли для пользователя базы данных
2. Ограничьте доступ к базе данных только из необходимых контейнеров
3. Не используйте суперпользователя для приложения
4. Регулярно обновляйте PostgreSQL до последней версии
5. Настройте SSL соединения для продакшена

### Создание пользователя для приложения

```sql
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE fastapi_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

## Очистка данных

### Удаление старых записей

Удаление записей старше 30 дней:
```sql
DELETE FROM api_data 
WHERE created_at < NOW() - INTERVAL '30 days';
```

Или через Python:
```python
from datetime import datetime, timedelta
from src.app.infrastructure.persistence.database import get_db_session

async def cleanup_old_data():
    async for session in get_db_session():
        cutoff_date = datetime.now(UTC) - timedelta(days=30)
        await session.execute(
            delete(ApiDataModel).where(ApiDataModel.created_at < cutoff_date)
        )
        await session.commit()
```

## Тестирование

### Тестовая база данных

Для тестов используется отдельная база данных с настройками:
- `DB_NAME=test_db`
- `DB_USER=test_user`
- `DB_PASSWORD=test_password`

Тестовая база данных создается автоматически при запуске тестов и очищается после завершения.

## Устранение проблем

### База данных недоступна

1. Проверьте статус контейнера:
```bash
docker compose ps postgres
```

2. Проверьте логи:
```bash
docker compose logs postgres
```

3. Проверьте переменные окружения в `.env`

### Ошибки подключения

1. Убедитесь, что контейнер PostgreSQL запущен
2. Проверьте правильность имени хоста (должно быть `postgres` в Docker сети)
3. Проверьте учетные данные
4. Проверьте доступность сети Docker

### Медленные запросы

1. Проверьте наличие индексов
2. Используйте `EXPLAIN ANALYZE` для анализа запросов
3. Проверьте размер таблиц
4. Рассмотрите возможность добавления ограничений на количество записей

### Ошибки миграций

1. Проверьте текущую версию миграций:
```bash
alembic current
```

2. Просмотрите историю:
```bash
alembic history
```

3. При необходимости откатитесь к предыдущей версии:
```bash
alembic downgrade -1
```


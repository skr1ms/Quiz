# Система мониторинга

Проект использует комплексную систему мониторинга на основе Prometheus, Grafana и Loki для отслеживания метрик, логов и производительности приложения.

## Компоненты стека мониторинга

### Prometheus
Система сбора и хранения метрик. Prometheus собирает метрики через HTTP endpoints различных сервисов и хранит их в временной базе данных.

### Grafana
Платформа для визуализации метрик и логов. Grafana предоставляет дашборды для анализа производительности и диагностики проблем.

### Loki
Система агрегации логов. Loki собирает логи из различных источников и предоставляет единый интерфейс для их анализа.

### Promtail
Агент для сбора логов. Promtail читает логи из Docker контейнеров и отправляет их в Loki.

### Экспортеры

#### postgres-exporter
Собирает метрики PostgreSQL и предоставляет их в формате Prometheus. Отслеживает:
- Количество подключений
- Размер базы данных
- Производительность запросов
- Статистику репликации

#### nginx-prometheus-exporter
Собирает метрики Nginx из статусной страницы. Отслеживает:
- Количество запросов
- Активные соединения
- Статусы ответов

#### prometheus-fastapi-instrumentator
Встроенный инструментарий FastAPI для автоматического сбора метрик. Экспортирует метрики с префиксом `http_*`:

**Основные метрики:**
- `http_requests_total` - общее количество HTTP запросов (counter)
- `http_request_duration_seconds` - длительность обработки запросов (histogram и summary)
- `http_request_size_bytes` - размер входящих запросов (histogram)
- `http_response_size_bytes` - размер ответов (histogram)

**Метки (labels):**
- `method` - HTTP метод (GET, POST, PUT, DELETE и т.д.)
- `handler` - путь обработчика (например, `/api/data/fetch`, `/health`)
- `status` - HTTP статус код (200, 404, 500 и т.д.)

**Особенности:**
- Автоматически собирает метрики для всех зарегистрированных эндпоинтов FastAPI
- Экспортирует метрики по эндпоинту `/metrics`
- Поддерживает гистограммы для анализа распределения времени ответа

## Конфигурация

### Prometheus

Конфигурация находится в `monitoring/prometheus/prometheus.yml`.

Настроены следующие targets:
- `prometheus` - сам Prometheus (localhost:9091)
- `fastapi-backend` - метрики FastAPI приложения (backend:8081/metrics)
- `postgres-exporter` - метрики PostgreSQL (postgres-exporter:9188)
- `nginx-exporter` - метрики Nginx (nginx-exporter:9113)

Интервал сбора метрик: 15 секунд.

### Loki

Конфигурация находится в `monitoring/loki/loki-config.yml`.

Loki настроен для:
- Хранения логов на файловой системе
- Периода хранения: 7 дней (168 часов)
- Схема индексации: tsdb
- Период индекса: 24 часа

### Promtail

Конфигурация находится в `monitoring/promtail/promtail-config.yml`.

Promtail настроен на:
- Чтение логов из `/var/lib/docker/containers`
- Отправку логов в Loki по адресу `http://loki:3100/loki/api/v1/push`
- Добавление меток: `job`, `service`, `container_name`

### Grafana

Конфигурация дашбордов находится в `monitoring/grafana/provisioning/`.

#### Источники данных

Автоматически настраиваются:
- Prometheus (тип: prometheus, URL: http://prometheus:9091)
- Loki (тип: loki, URL: http://loki:3100)

#### Дашборды

Все дашборды автоматически загружаются при старте Grafana из директории `monitoring/grafana/dashboards/`.

##### Backend Metrics
Дашборд с метриками бэкенда (`backend/metrics.json`):
- Request Rate - количество запросов в секунду
- Request Duration - время обработки запросов
- HTTP Status Codes - распределение статусов ответов
- Active Requests - количество активных запросов

##### Backend Overall (FastAPI Observability)
Комплексный дашборд для мониторинга FastAPI приложения (`backend/overall.json`), основанный на дашборде ID 16110 с grafana.com. Включает:

**Панели статистики:**
- **Total Requests** - общее количество запросов за последние 24 часа
- **Requests Count** - количество запросов по эндпоинтам (POST /api/data/fetch, GET /health, GET /api/data, GET /api/data/{data_id})
- **Requests Average Duration** - средняя длительность запросов по эндпоинтам, отображается горизонтальными барами с цветовой индикацией (зеленый → желтый → красный)
- **Total Exceptions** - общее количество 5xx ошибок за 24 часа

**Панели процентного соотношения:**
- **Percent of 2xx Requests** - процент успешных запросов (2xx) по эндпоинтам
- **Percent of 5xx Requests** - процент ошибок сервера (5xx) по эндпоинтам

**Панели временных рядов:**
- **PR 99 Requests Duration** - 99-й процентиль длительности запросов
- **Request In Process** - количество запросов в процессе обработки
- **Request Per Sec** - количество запросов в секунду по эндпоинтам

**Панели логов:**
- **Log Type Rate** - частота типов логов (INFO, ERROR, WARNING, CRITICAL, DEBUG)
- **Log of All FastAPI App** - полный журнал логов приложения с возможностью поиска и фильтрации

**Фильтрация эндпоинтов:**
Дашборд автоматически исключает из метрик служебные эндпоинты:
- `/metrics` - эндпоинт метрик Prometheus
- `/docs` - документация Swagger UI
- `/openapi.json` - OpenAPI схема
- `/redoc` - документация ReDoc (если используется)
- Пустые handlers (`none`) - запросы без определенного пути

**Особенности:**
- Использует метрики `http_*` от `prometheus-fastapi-instrumentator`
- Панель "Requests Average Duration" отображает средние значения в секундах с непрерывной цветовой схемой (continuous-GrYlRd)
- Все запросы фильтруются по handler, исключая служебные эндпоинты
- Поддержка поиска в логах через переменную `log_keyword`

##### Backend Logs
Дашборд с логами бэкенда (`backend/logs.json`):
- Логи приложения с фильтрацией по уровню
- Поиск по тексту логов
- Фильтрация по времени

##### Frontend Metrics
Дашборд с метриками фронтенда (`frontend/metrics.json`):
- HTTP Request Rate - количество запросов к Nginx
- Active Connections - активные соединения
- Accepted Connections Rate - скорость принятия соединений
- Handled Connections Rate - скорость обработки соединений

##### Frontend Logs
Дашборд с логами фронтенда (`frontend/logs.json`):
- Логи Nginx
- Запросы и ответы
- Ошибки доступа

##### Postgres Metrics
Дашборд с метриками PostgreSQL (`postgres/metrics.json`):
- Database Size - размер базы данных
- Connections - количество подключений
- Transactions - количество транзакций
- Query Performance - производительность запросов

##### Postgres Logs
Дашборд с логами PostgreSQL (`postgres/logs.json`):
- Логи базы данных
- Запросы и ошибки
- Долгие запросы

## Доступ к интерфейсам

### Grafana
- URL: http://localhost:3000
- Логин по умолчанию: `admin`
- Пароль по умолчанию: `admin` (настраивается через переменную `GRAFANA_PASSWORD`)

После первого входа рекомендуется изменить пароль.

### Prometheus
- URL: http://localhost:9091
- Доступен для просмотра метрик и выполнения запросов PromQL

### Loki
- URL: http://localhost:3100
- API endpoint для запросов логов через Grafana

## Работа с дашбордами

### Просмотр метрик

1. Откройте Grafana
2. Перейдите в раздел Dashboards
3. Выберите нужный дашборд из списка
4. Используйте фильтры времени в верхней части дашборда

### Поиск в логах

1. Откройте дашборд с логами (например, Backend Logs)
2. Используйте поле поиска для фильтрации
3. Применяйте метки для уточнения запроса
4. Экспортируйте результаты при необходимости

### Создание алертов

Grafana позволяет создавать алерты на основе метрик:
1. Откройте панель на дашборде
2. Выберите Edit → Alert
3. Настройте условия срабатывания
4. Укажите каналы уведомлений

**Примеры алертов для бэкенда:**
- Высокий процент 5xx ошибок: `sum(rate(http_requests_total{status=~"5..", handler!="/metrics"}[5m])) / sum(rate(http_requests_total{handler!="/metrics"}[5m])) > 0.05`
- Медленный ответ: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{handler!="/metrics"}[5m])) by (le)) > 1`
- Высокий rate ошибок: `sum(rate(http_requests_total{status=~"5..", handler!="/metrics"}[5m])) > 10`

## Типичные метрики для отслеживания

### Бэкенд

**Основные метрики:**
- `http_requests_total` - общее количество HTTP запросов
- `http_request_duration_seconds` - длительность обработки запросов
- Request rate - количество запросов в секунду
- Request duration (p50, p95, p99) - процентили времени ответа
- Error rate - процент ошибочных запросов (4xx, 5xx)

**Метрики по эндпоинтам:**
- `POST /api/data/fetch` - получение данных из внешнего API
- `GET /api/data` - получение списка всех данных с пагинацией
- `GET /api/data/{data_id}` - получение конкретной записи по ID
- `GET /health` - проверка состояния сервиса

**Исключенные из метрик:**
- `/metrics` - эндпоинт метрик Prometheus (исключается автоматически)
- `/docs` - документация Swagger UI
- `/openapi.json` - OpenAPI схема
- `/redoc` - документация ReDoc
- Пустые handlers - запросы к несуществующим путям (404)

### Фронтенд
- HTTP requests per second - количество HTTP запросов
- Active connections - активные соединения к Nginx
- Response time - время ответа сервера

### База данных
- Database size - размер базы данных
- Active connections - активные подключения
- Slow queries - долгие запросы
- Transaction rate - количество транзакций в секунду

## Хранение данных

### Prometheus
Метрики хранятся в Prometheus в течение 30 дней (настраивается через `--storage.tsdb.retention.time`).

Для долгосрочного хранения рекомендуется использовать:
- Thanos для хранения в объектном хранилище
- VictoriaMetrics для более эффективного хранения

### Loki
Логи хранятся в течение 7 дней (настраивается через `reject_old_samples_max_age`).

## Расширенная настройка

### Добавление новых дашбордов

1. Создайте JSON файл дашборда в `monitoring/grafana/dashboards/`
2. Файл должен соответствовать формату Grafana Dashboard JSON
3. Перезапустите контейнер Grafana для загрузки дашборда

### Добавление новых источников метрик

1. Добавьте новый job в `monitoring/prometheus/prometheus.yml`:
```yaml
- job_name: 'new-service'
  static_configs:
    - targets: ['new-service:9091']
```

2. Перезапустите Prometheus для применения изменений

### Настройка алертов

Алерты настраиваются через:
1. Prometheus Alertmanager (для правил Prometheus)
2. Grafana Alerting (для алертов в дашбордах)

Пример правила для Prometheus можно добавить в `monitoring/prometheus/rules/`.

## Устранение проблем

### Метрики не отображаются
- Проверьте, что сервис доступен для Prometheus
- Убедитесь, что endpoint `/metrics` работает
- Проверьте конфигурацию Prometheus

### Логи не появляются
- Проверьте, что Promtail запущен
- Убедитесь, что логи пишутся в Docker контейнеры
- Проверьте конфигурацию Promtail и доступность Loki

### Дашборды не загружаются
- Проверьте формат JSON файлов дашбордов
- Убедитесь, что файлы находятся в правильной директории
- Проверьте права доступа к файлам

### Высокая нагрузка на систему
- Увеличьте интервал сбора метрик в Prometheus
- Настройте retention для старых данных
- Ограничьте количество собираемых метрик

## Производительность

Для оптимизации производительности мониторинга:
1. Настройте правильные интервалы сбора метрик
2. Используйте агрегацию для уменьшения объема данных
3. Настройте retention политики
4. Мониторьте использование ресурсов компонентами мониторинга

## Используемые метрики

### Метрики FastAPI (http_*)

Все метрики собираются автоматически через `prometheus-fastapi-instrumentator`:

**Счетчики (Counters):**
- `http_requests_total{method, handler, status}` - общее количество запросов

**Гистограммы (Histograms):**
- `http_request_duration_seconds_bucket{method, handler, le}` - buckets для расчета процентилей
- `http_request_duration_seconds_sum{method, handler}` - суммарное время запросов
- `http_request_duration_seconds_count{method, handler}` - количество запросов

**Gauge:**
- `http_requests_in_progress{method, handler}` - количество запросов в процессе (если доступно)

### Примеры PromQL запросов

**Среднее время ответа:**
```promql
sum by(handler, method) (rate(http_request_duration_seconds_sum{handler!="/metrics"}[5m])) 
/ 
sum by(handler, method) (rate(http_request_duration_seconds_count{handler!="/metrics"}[5m]))
```

**99-й процентиль:**
```promql
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{handler!="/metrics"}[5m])) by (handler, le))
```

**Процент 5xx ошибок:**
```promql
sum by(handler) (rate(http_requests_total{status=~"5..", handler!="/metrics"}[5m])) 
/ 
sum by(handler) (rate(http_requests_total{handler!="/metrics"}[5m]))
```

**Количество запросов за 24 часа:**
```promql
sum(increase(http_requests_total{handler!="/metrics", handler!="/docs", handler!="/openapi.json", handler!="/redoc", handler=~".+"}[24h]))
```


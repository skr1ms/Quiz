# Развертывание проекта

Проект развертывается с использованием Docker и Docker Compose. Все компоненты запускаются в отдельных контейнерах.

## Предварительные требования

### Для локального развертывания
- Docker версии 20.10 или выше
- Docker Compose версии 2.0 или выше
- Минимум 4 ГБ свободной оперативной памяти
- Минимум 10 ГБ свободного места на диске

### Для тестирования на виртуальной машине

Для полноценного тестирования CI/CD рекомендуется использовать виртуальную машину:

**Требования к виртуальной машине:**
- **ОС:** Ubuntu 22.04 или Debian (рекомендуется)
- **Ресурсы:** минимум 4 ядра CPU, 4 ГБ RAM
- **Сеть:** настройка сетевого адаптера в режиме **Bridge** (мост)
- **Диск:** минимум 20 ГБ свободного места

**Настройка виртуальной машины:**

1. **Обновите систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Установите GitLab и Docker:**
   - Подробные инструкции по установке GitLab см. в разделе [Развертывание GitLab на локальном сервере](CI-CD.md#развертывание-gitlab-на-локальном-сервере)
   - Инструкции по установке Docker см. в разделе [Установка Docker на сервере GitLab](CI-CD.md#установка-docker-на-сервере-gitlab)

3. **Настройте GitLab Runner:**
   - Инструкции см. в разделе [Установка и настройка GitLab Runner](CI-CD.md#установка-и-настройка-gitlab-runner)

4. **Получите IP адрес виртуальной машины:**
```bash
ip addr show
# Или
hostname -I
```
Запишите IP адрес, полученный через Bridge сеть (например, `192.168.1.100`).

5. **Разверните проект на виртуальной машине:**
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd pz1

# Создайте .env файл (см. раздел "Настройка окружения" ниже)
# Укажите VITE_API_BASE_URL с IP адресом виртуалки:
# VITE_API_BASE_URL=http://192.168.1.100:8081

# Запустите проект
cd deployment/docker
docker compose --env-file ../../.env -f docker-compose.yml up -d
```

6. **Настройте переменные в GitLab CI/CD:**
   - Перейдите в **Settings → CI/CD → Variables**
   - Установите `VITE_API_BASE_URL=http://IP_виртуалки:8081` (например, `http://192.168.1.100:8081`)
   - Установите `DEPLOY_SERVER_IP=IP_виртуалки` (например, `192.168.1.100`)
   - Остальные обязательные переменные см. в [документации CI/CD](CI-CD.md#настройка-переменных-cicd-в-gitlab)

**Важно:** 
- Используйте IP адрес, полученный через Bridge сеть, а не localhost
- Убедитесь, что порты 8081 (backend) и 8000 (frontend) доступны из сети
- При необходимости настройте firewall для разрешения доступа к портам

### Для серверного развертывания
- Сервер с установленным Docker и Docker Compose
- Доступ по SSH для автоматического развертывания
- Настроенный GitLab Runner (для CI/CD)
- Файл `.env` с необходимыми переменными окружения

## Структура развертывания

### Файлы конфигурации

#### docker-compose.yml
Основной файл для локальной разработки и полного развертывания. Включает все сервисы:
- PostgreSQL
- Backend (FastAPI)
- Frontend (Nginx)
- Prometheus
- Grafana
- Loki
- Promtail
- Postgres Exporter
- Nginx Exporter

#### docker-compose-cicd.yml
Файл для развертывания через CI/CD. Содержит только приложения (backend и frontend), предполагая, что остальные сервисы (PostgreSQL, мониторинг) уже запущены.

## Локальное развертывание

### Настройка окружения

1. Создайте файл `.env` в корне проекта:
```bash
# Database
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=fastapi_db
DB_PORT=5432

# Backend
BACKEND_PORT=8081
ENVIRONMENT=local
DEBUG=true

# Frontend
FRONTEND_PORT=8000
# Для локального развертывания используйте localhost
# Для виртуальной машины используйте IP адрес виртуалки (например, http://192.168.1.100:8081)
VITE_API_BASE_URL=http://localhost:8081

# Monitoring
PROMETHEUS_PORT=9091
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
LOKI_PORT=3100
POSTGRES_EXPORTER_PORT=9188
NGINX_EXPORTER_PORT=9113

# External API
API_NINJAS=your_api_ninjas_key
API_NINJAS_BASE_URL=https://api.api-ninjas.com/v1
```

2. Замените значения на ваши собственные, особенно:
- `DB_PASSWORD` - надежный пароль для базы данных
- `API_NINJAS` - ключ API от API Ninjas
- `GRAFANA_PASSWORD` - пароль для Grafana

### Запуск приложения

1. Перейдите в директорию с docker-compose файлом:
```bash
cd deployment/docker
```

2. Запустите все сервисы:
```bash
docker compose --env-file ../../.env -f docker-compose.yml up -d
```

3. Проверьте статус контейнеров:
```bash
docker compose --env-file ../../.env -f docker-compose.yml ps
```

4. Просмотрите логи:
```bash
docker compose --env-file ../../.env -f docker-compose.yml logs -f
```

### Остановка приложения

```bash
docker compose --env-file ../../.env -f docker-compose.yml down
```

Для полной очистки (включая volumes):
```bash
docker compose --env-file ../../.env -f docker-compose.yml down -v
```

## Развертывание на сервере

### Подготовка сервера

1. Установите Docker и Docker Compose:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

2. Создайте пользователя для развертывания:
```bash
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
```

3. Настройте SSH доступ:
```bash
# На локальной машине
ssh-keygen -t rsa -b 4096 -C "deploy@server"
ssh-copy-id deploy@your-server-ip
```

### Первоначальная настройка

1. Подключитесь к серверу:
```bash
ssh deploy@your-server-ip
```

2. Создайте директорию для проекта:
```bash
mkdir -p /opt/fastapi-project
cd /opt/fastapi-project
```

3. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/your-repo.git .
git checkout main
```

4. Создайте файл `.env`:
```bash
nano .env
```

Заполните файл аналогично локальной конфигурации, но измените:
- `ENVIRONMENT=deploy` или `production`
- `DEBUG=false`
- `VITE_API_BASE_URL=http://your-server-ip:8081` или ваш домен

5. Запустите только базовые сервисы (если используете docker-compose-cicd.yml):
```bash
cd deployment/docker
docker compose --env-file ../../.env -f docker-compose.yml up -d postgres prometheus grafana loki promtail postgres-exporter
```

### Развертывание через CI/CD

Развертывание через GitLab CI/CD происходит автоматически при:
- Push в ветку `main`
- Успешном прохождении тестов
- Настроенных переменных окружения в GitLab

Процесс:
1. GitLab Runner собирает Docker образы
2. Загружает образы в GitLab Container Registry
3. Подключается к серверу по SSH
4. Обновляет код на сервере
5. Загружает новые образы
6. Перезапускает контейнеры через docker-compose

### Ручное развертывание

Если нужно развернуть вручную:

1. На сервере перейдите в директорию проекта:
```bash
cd /opt/fastapi-project
```

2. Обновите код:
```bash
git pull origin main
```

3. Загрузите образы из реестра:
```bash
echo $CI_JOB_TOKEN | docker login $CI_REGISTRY -u gitlab-ci-token --password-stdin
export IMAGE_TAG=latest
export REGISTRY_IMAGE=your-registry-image
docker compose --env-file .env -f deployment/docker/docker-compose-cicd.yml pull
```

4. Перезапустите контейнеры:
```bash
docker compose --env-file .env -f deployment/docker/docker-compose-cicd.yml up -d
```

## Обновление приложения

### Обновление через CI/CD

1. Внесите изменения в код
2. Создайте коммит и push в ветку `main`
3. Дождитесь завершения pipeline
4. Приложение автоматически обновится на сервере

### Ручное обновление

1. Обновите код на сервере
2. Пересоберите образы (если нужно) или загрузите новые
3. Перезапустите контейнеры:
```bash
docker compose --env-file .env -f deployment/docker/docker-compose-cicd.yml up -d --force-recreate
```

## Откат к предыдущей версии

Если нужно откатиться к предыдущей версии:

1. Определите SHA коммита предыдущей версии:
```bash
git log --oneline
```

2. Установите соответствующий тег образа:
```bash
export IMAGE_TAG=previous-commit-sha
docker compose --env-file .env -f deployment/docker/docker-compose-cicd.yml up -d
```

## Миграции базы данных

Миграции базы данных выполняются автоматически при старте приложения через `Base.metadata.create_all()`.

Для ручного управления миграциями:

1. Подключитесь к контейнеру бэкенда:
```bash
docker exec -it fastapi-project bash
```

2. Выполните миграции:
```bash
alembic upgrade head
```

## Мониторинг развертывания

### Проверка статуса контейнеров

```bash
docker compose --env-file .env -f docker-compose.yml ps
```

### Просмотр логов

Всех сервисов:
```bash
docker compose --env-file .env -f docker-compose.yml logs -f
```

Конкретного сервиса:
```bash
docker compose --env-file .env -f docker-compose.yml logs -f backend
```

### Проверка здоровья сервисов

Backend:
```bash
curl http://localhost:8081/health
```

Frontend:
```bash
curl http://localhost:8000
```

Grafana:
```bash
curl http://localhost:3000/api/health
```

## Переменные окружения

### Обязательные переменные

- `DB_USER` - пользователь базы данных
- `DB_PASSWORD` - пароль базы данных
- `DB_NAME` - имя базы данных
- `API_NINJAS` - ключ API для API Ninjas

### Опциональные переменные

- `ENVIRONMENT` - окружение (local, deploy, production)
- `DEBUG` - режим отладки (true/false)
- `BACKEND_PORT` - порт бэкенда (по умолчанию: 8081)
- `FRONTEND_PORT` - порт фронтенда (по умолчанию: 8000)
- `GRAFANA_PASSWORD` - пароль Grafana (по умолчанию: admin)

## Безопасность

### Рекомендации для продакшена

1. Используйте сильные пароли для всех сервисов
2. Настройте HTTPS через reverse proxy (Nginx/Traefik)
3. Ограничьте доступ к портам мониторинга
4. Регулярно обновляйте Docker образы
5. Используйте секреты Docker или внешние системы управления секретами
6. Настройте firewall для ограничения доступа

### Backup базы данных

Регулярно создавайте резервные копии:

```bash
docker exec postgres pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql
```

Восстановление:
```bash
docker exec -i postgres psql -U $DB_USER $DB_NAME < backup_20240101.sql
```

## Устранение проблем

### Контейнеры не запускаются

1. Проверьте логи:
```bash
docker compose logs <service-name>
```

2. Проверьте переменные окружения в `.env`
3. Убедитесь, что порты не заняты
4. Проверьте доступное место на диске

### База данных недоступна

1. Проверьте статус контейнера PostgreSQL:
```bash
docker compose ps postgres
```

2. Проверьте логи:
```bash
docker compose logs postgres
```

3. Убедитесь, что переменные окружения правильные
4. Проверьте подключение:
```bash
docker exec -it postgres psql -U $DB_USER -d $DB_NAME
```

### Backend не может подключиться к БД

1. Убедитесь, что используется правильный `DB_HOST` (должен быть `postgres` в Docker сети)
2. Проверьте сеть Docker:
```bash
docker network inspect pz1
```

3. Проверьте, что контейнер PostgreSQL доступен по имени `postgres`

### Фронтенд не может подключиться к бэкенду

1. Проверьте `VITE_API_BASE_URL` в конфигурации
2. Убедитесь, что бэкенд запущен и доступен
3. Проверьте CORS настройки в бэкенде
4. Проверьте логи Nginx:
```bash
docker compose logs frontend
```

## Масштабирование

Для увеличения производительности:

1. Масштабирование бэкенда:
```bash
docker compose --env-file .env -f docker-compose.yml up -d --scale backend=3
```

2. Используйте load balancer (например, Nginx) перед несколькими инстансами бэкенда
3. Настройте connection pooling в базе данных
4. Используйте кэширование (Redis) для часто запрашиваемых данных


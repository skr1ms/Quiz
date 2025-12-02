# CI/CD конфигурация

Проект использует GitLab CI/CD для автоматизации сборки, тестирования и развертывания приложения.

## Развертывание GitLab на локальном сервере

Для работы CI/CD необходимо развернуть GitLab на локальном сервере. Ниже приведена пошаговая инструкция.

### Предварительные требования

- Сервер с Ubuntu 22.04 или выше
- Минимум 4 ГБ оперативной памяти (рекомендуется 8 ГБ)
- Минимум 20 ГБ свободного места на диске
- Root доступ к серверу

### Установка GitLab

#### 1. Подключение к серверу

```bash
ssh root@ip_адрес_сервера
```

При первом подключении подтвердите добавление хоста в known_hosts, введя `yes`.

#### 2. Обновление системы

```bash
apt update && apt upgrade -y
```

#### 3. Установка зависимостей

```bash
sudo apt install -y curl ssh openssh-server ca-certificates tzdata perl
```

#### 4. Установка GitLab

```bash
# Переход в директорию tmp
cd /tmp

# Загрузка установочного скрипта
curl -LO https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh

# Запуск скрипта
sudo bash /tmp/script.deb.sh

# Установка GitLab Community Edition
sudo apt install gitlab-ce
```

Установка может занять несколько минут. После завершения вы увидите сообщение об успешной установке.

#### 5. Настройка GitLab

Откройте конфигурационный файл:

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Добавьте или измените следующие настройки:

```ruby
# Основной URL для доступа к GitLab
external_url 'http://ip_вашего_сервера:9080'

# SSH порт для Git операций
gitlab_rails['gitlab_shell_ssh_port'] = 22

# Настройки NGINX
nginx['enable'] = true
nginx['listen_port'] = 9080
nginx['listen_https'] = false
nginx['redirect_http_to_https'] = false

# Включение Container Registry
gitlab_rails['registry_enabled'] = true
gitlab_rails['registry_host'] = "ip_вашего_сервера"
gitlab_rails['registry_port'] = "5000"
gitlab_rails['registry_api_url'] = "http://ip_вашего_сервера:5000"
gitlab_rails['registry_path'] = "/var/opt/gitlab/gitlab-rails/shared/registry"

# Настройки Registry
registry['enable'] = true
registry_external_url 'http://ip_вашего_сервера:5000'
registry_nginx['enable'] = false
registry['registry_http_addr'] = '0.0.0.0:5000'
registry['storage_delete_enabled'] = true
registry['log_level'] = 'info'

# Отключаем мониторинг gitlab
prometheus_monitoring['enable'] = false
postgres_exporter['enable'] = false
```

**Важно:** Замените `ip_вашего_сервера` на реальный IP адрес вашего сервера.

Примените изменения:

```bash
sudo gitlab-ctl reconfigure
```

Этот процесс может занять 5-10 минут.

#### 6. Настройка firewall

Разрешите доступ к портам GitLab:

```bash
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 9080 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

#### 7. Получение начального пароля

GitLab генерирует начальный пароль для пользователя `root`. Просмотрите его:

```bash
sudo cat /etc/gitlab/initial_root_password
```

**Важно:** Сохраните этот пароль! Файл будет автоматически удален через 24 часа после первой настройки.

#### 8. Первый вход в GitLab

1. Откройте браузер и перейдите по адресу: `http://ip_вашего_сервера:9080`
2. Войдите с учетными данными:
   - **Username:** `root`
   - **Password:** пароль из файла `/etc/gitlab/initial_root_password`
3. **Обязательно измените пароль** при первом входе!

### Настройка SSH ключей

#### 1. Генерация SSH ключа на сервере GitLab

```bash
ssh-keygen -t ed25519 -C "gitlab-server" -f ~/.ssh/id_ed25519
```

Нажмите Enter для использования значений по умолчанию (без парольной фразы для автоматизации).

#### 2. Добавление ключа в SSH agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

#### 3. Добавление публичного ключа в GitLab

1. Скопируйте публичный ключ:
```bash
cat ~/.ssh/id_ed25519.pub
```

2. В GitLab перейдите в **Settings → SSH Keys**
3. Вставьте публичный ключ и сохраните

#### 4. Настройка SSH для деплоя

Для работы автоматического деплоя необходимо настроить SSH доступ от GitLab CI/CD к серверу деплоя.

**Шаг 1: Добавьте приватный ключ в GitLab CI/CD Variables**

```bash
# На сервере GitLab
cat ~/.ssh/id_ed25519
```

В GitLab: **Settings → CI/CD → Variables** → добавьте:
- **Key:** `SSH_PRIVATE_KEY`
- **Value:** содержимое приватного ключа (весь вывод команды выше)
- **Type:** Variable
- **Protected:** ✗
- **Masked:** ✗

**Шаг 2: Добавьте публичный ключ на сервер деплоя**

```bash
# На сервере деплоя
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

Или если используете другого пользователя (например, `deploy`):

```bash
# На сервере деплоя
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
cat ~/.ssh/id_ed25519.pub | sudo tee -a /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

**Шаг 3: Проверьте SSH подключение**

```bash
# С сервера GitLab попробуйте подключиться к серверу деплоя
ssh -i ~/.ssh/id_ed25519 $DEPLOY_USER@$DEPLOY_SERVER
```

**Диагностика проблем с SSH:**

Если деплой не работает с ошибкой "Permission denied":

1. **Проверьте, что ключ правильно добавлен в GitLab:**
   - Убедитесь, что `SSH_PRIVATE_KEY` имеет тип Variable
   - Проверьте, что ключ начинается с `-----BEGIN OPENSSH PRIVATE KEY-----` или `-----BEGIN RSA PRIVATE KEY-----`

2. **Проверьте права доступа на сервере деплоя:**
```bash
# На сервере деплоя
ls -la ~/.ssh/
# Должно быть:
# drwx------ .ssh
# -rw------- authorized_keys
```

3. **Проверьте логи SSH на сервере деплоя:**
```bash
# На сервере деплоя
sudo tail -f /var/log/auth.log
# Попробуйте подключиться и посмотрите логи
```

4. **Проверьте, что пользователь существует:**
```bash
# На сервере деплоя
id $DEPLOY_USER
# Должен показать информацию о пользователе
```

5. **Проверьте, что SSH сервис разрешает подключения:**
```bash
# На сервере деплоя
sudo systemctl status ssh
sudo grep -i "PermitRootLogin\|PasswordAuthentication" /etc/ssh/sshd_config
```

### Создание проекта в GitLab

1. В GitLab нажмите **New project** или **Create project**
2. Выберите **Create blank project**
3. Заполните:
   - **Project name:** `fastapi-project` (или любое другое имя)
   - **Visibility Level:** Private (рекомендуется)
4. Нажмите **Create project**

#### Настройка репозитория

1. Перейдите в **Settings → Repository**
2. Разверните раздел **Protected branches**
3. Найдите ветку `main` и нажмите **Unprotect** (для упрощения настройки)
4. Сохраните изменения

#### Загрузка кода в проект

**Вариант 1: Push через SSH (рекомендуется)**

Если вы работаете с другого устройства:

1. Сгенерируйте SSH ключ на вашем устройстве:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Добавьте публичный ключ в GitLab: **Settings → SSH Keys**

3. Добавьте remote и выполните push:
```bash
git remote add gitlab ssh://git@ip_вашего_сервера:22/username/fastapi-project.git
git push gitlab main
```

**Вариант 2: Push через HTTP**

1. В GitLab перейдите в проект → **Clone** → скопируйте HTTP URL
2. Добавьте remote:
```bash
git remote add gitlab http://ip_вашего_сервера:9080/username/fastapi-project.git
git push gitlab main
```

При запросе используйте логин `root` и пароль, который вы установили.

### Установка Docker на сервере GitLab

Для работы GitLab Runner необходим Docker. Установите его по [официальной инструкции](https://docs.docker.com/engine/install/ubuntu/):

```bash
# Удаление старых версий (если есть)
sudo apt-get remove docker docker-engine docker.io containerd runc

# Установка зависимостей
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Добавление GPG ключа Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Настройка репозитория
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Проверка установки
sudo docker run hello-world
```

#### Добавление пользователя в группу docker

Чтобы запускать Docker команды без `sudo`, добавьте текущего пользователя в группу `docker`:

```bash
# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений группы (или перелогиньтесь)
newgrp docker

# Перезапуск Docker
sudo systemctl restart docker
```

**Важно:** После выполнения этих команд может потребоваться перелогиниться или перезапустить сессию SSH, чтобы изменения вступили в силу.

Проверьте, что Docker работает без sudo:

```bash
docker run hello-world
```

#### Настройка Docker для работы с GitLab Registry

Отредактируйте конфигурацию Docker:

```bash
sudo nano /etc/docker/daemon.json
```

Добавьте следующее содержимое (замените `ip_вашего_сервера` на реальный IP):

```json
{
   "insecure-registries": ["ip_вашего_сервера:5000"]
}
```

Перезапустите Docker:

```bash
sudo systemctl restart docker
```

### Установка и настройка GitLab Runner

#### 1. Установка GitLab Runner

```bash
# Добавление репозитория
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash

# Установка
sudo apt-get install gitlab-runner
```

#### 2. Регистрация Runner

1. В GitLab перейдите в **Settings → CI/CD → Runners**
2. Найдите раздел **Set up a specific runner manually**
3. Скопируйте **Registration token**

4. На сервере выполните регистрацию:

```bash
sudo gitlab-runner register
```

Введите следующие данные:

- **GitLab instance URL:** `http://ip_вашего_сервера:9080` (нажмите Enter)
- **Registration token:** вставьте скопированный токен
- **Description:** `docker-runner` (или любое другое описание)
- **Tags:** нажмите Enter (без тегов)
- **Executor:** `docker`
- **Default Docker image:** `alpine:latest`

#### 3. Настройка Runner для использования хостового Docker

Для работы с insecure registry (например, `172.24.15.252:5000`) необходимо настроить runner для использования хостового Docker daemon через socket. Это позволяет использовать настройки из `/etc/docker/daemon.json`.

**Шаг 1: Добавьте пользователя gitlab-runner в группу docker**

```bash
sudo usermod -aG docker gitlab-runner
```

**Шаг 2: Отредактируйте конфигурацию Runner**

```bash
sudo nano /etc/gitlab-runner/config.toml
```

**Шаг 3: Настройте параметры Runner**

Найдите секцию вашего runner'а (обычно `[[runners]]`) и настройте следующие параметры:

```toml
# Количество одновременных джобов (рекомендуется 5 или более для ускорения пайплайна)
concurrent = 5

[[runners]]
  name = "docker-runner"
  url = "http://ip_вашего_сервера:9080"
  token = "ваш_токен"
  executor = "docker"
  [runners.docker]
    image = "alpine:latest"
    privileged = false
    # Используем хостовый Docker через socket
    # ВАЖНО: Без этого volume runner не сможет напрямую взаимодействовать с docker.sock
    volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]
    # Отключаем TLS для insecure registry
    tls_verify = false
```

**Важно:** 

- **`volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]`** - это **обязательная** настройка, которая позволяет runner'у напрямую взаимодействовать с хостовым Docker daemon через socket. Без этого volume runner не сможет использовать Docker для сборки образов и запуска контейнеров.

- **`concurrent = 5`** (или более) - рекомендуется для ускорения выполнения пайплайна. Это значение определяет, сколько джобов может выполняться одновременно. Увеличение этого значения позволяет параллельно выполнять несколько стадий пайплайна (например, сборку backend и frontend одновременно).

- Настройки `insecure-registries` из `/etc/docker/daemon.json` будут применяться автоматически благодаря использованию хостового Docker socket.

- Без volume для Docker socket runner не сможет использовать настройки хостового Docker и не сможет работать с insecure registry.

**Шаг 4: Перезапустите Runner**

```bash
sudo gitlab-runner restart
```

**Проверка настройки:**

После перезапуска runner'а проверьте, что он может использовать Docker:

```bash
# Проверьте статус runner'а
sudo gitlab-runner status

# Проверьте, что пользователь gitlab-runner в группе docker
groups gitlab-runner
# Должно содержать: gitlab-runner docker
```

**Преимущества использования хостового Docker:**

- Настройки из `/etc/docker/daemon.json` применяются автоматически
- Не нужно настраивать insecure-registries в каждом job
- Быстрее, чем Docker-in-Docker (DinD)
- Проще в настройке и поддержке

### Настройка переменных CI/CD в GitLab

Перейдите в **Settings → CI/CD → Variables** и добавьте следующие переменные:

#### Обязательные переменные

**Важно:** Все переменные должны иметь следующие настройки:
- **Visibility:** `Visible`
- **Protected:** ✗ (не защищенные)
- **Masked:** ✗ (не маскированные, кроме паролей если нужно)
- **Minimum role to use pipeline variables:** `Developer`

1. **SSH_PRIVATE_KEY**
   - **Key:** `SSH_PRIVATE_KEY`
   - **Value:** содержимое файла `~/.ssh/id_ed25519` (приватный ключ, сгенерированный на сервере GitLab)
   - **Type:** Variable (строго Variable, не File!)
   - **Visibility:** `Visible`
   - **Protected:** ✗
   - **Masked:** ✗

2. **DEPLOY_SERVER**
   - **Key:** `DEPLOY_SERVER`
   - **Value:** IP адрес сервера, куда будет происходить деплой (может быть тот же сервер GitLab или другой)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗
   - **Masked:** ✗

3. **DEPLOY_USER**
   - **Key:** `DEPLOY_USER`
   - **Value:** имя пользователя для SSH подключения к серверу деплоя (например, `root` или `deploy`)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗
   - **Masked:** ✗

4. **DEPLOY_PATH**
   - **Key:** `DEPLOY_PATH`
   - **Value:** путь на сервере, куда будет развернуто приложение (например, `/opt/fastapi-project`)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗
   - **Masked:** ✗

5. **VITE_API_BASE_URL**
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** базовый URL API для фронтенда (например, `http://172.24.14.252:8081` или `http://192.168.1.100:8081` для виртуалки)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗
   - **Masked:** ✗
   - **Важно:** Эта переменная передается при сборке фронтенда как build argument и встраивается в собранное приложение. Для виртуальной машины используйте IP адрес виртуалки, полученный через Bridge сеть.

6. **FORCE_BUILD_ALL**
   - **Key:** `FORCE_BUILD_ALL`
   - **Value:** `true` (рекомендуется установить `true` для принудительной сборки)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗
   - **Masked:** ✗

#### Опциональные переменные

7. **ENV_FILE** (опционально)
   - **Key:** `ENV_FILE`
   - **Value:** имя файла с переменными окружения на сервере (по умолчанию: `.env`)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗

8. **BACKEND_PORT** (опционально)
   - **Key:** `BACKEND_PORT`
   - **Value:** порт бэкенда (по умолчанию: `8081`)
   - **Type:** Variable
   - **Visibility:** `Visible`
   - **Protected:** ✗

9. **FORCE_DEPLOY** (опционально)
   - **Key:** `FORCE_DEPLOY`
   - **Value:** `false` (для принудительного деплоя установите `true`)
   - **Type:** Variable

### Подготовка сервера для деплоя

На сервере, куда будет происходить деплой (может быть тот же сервер GitLab или отдельный):

1. **Установите Docker и Docker Compose** (см. инструкцию выше)

   **Важно:** После установки Docker добавьте пользователя в группу docker:

   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   sudo systemctl restart docker
   ```

2. **Настройте Docker для работы с GitLab Registry:**

```bash
sudo nano /etc/docker/daemon.json
```

Добавьте:
```json
{
   "insecure-registries": ["ip_вашего_сервера_gitlab:5000"]
}
```

Перезапустите Docker:
```bash
sudo systemctl restart docker
```

3. **Создайте директорию для проекта:**

```bash
sudo mkdir -p /opt/fastapi-project
sudo chown $USER:$USER /opt/fastapi-project
```

4. **Создайте файл `.env`** с необходимыми переменными окружения (см. [DEPLOYMENT.md](DEPLOYMENT.md))

5. **Создайте Docker сеть:**

```bash
docker network create pz1
```

6. **Настройте SSH доступ:**

SSH доступ должен быть настроен на этапе "Настройка SSH ключей" выше. Убедитесь, что:
- Публичный ключ добавлен в `~/.ssh/authorized_keys` на сервере деплоя
- Приватный ключ добавлен в GitLab CI/CD Variables как `SSH_PRIVATE_KEY` (тип: Variable)
- Переменные `DEPLOY_SERVER` и `DEPLOY_USER` правильно настроены в GitLab CI/CD Variables

### Проверка работы CI/CD

После настройки всех компонентов:

1. Сделайте commit и push в ветку `main`
2. Перейдите в GitLab → **CI/CD → Pipelines**
3. Дождитесь завершения pipeline
4. Проверьте логи каждого job для выявления проблем

## Обзор процесса

CI/CD pipeline состоит из следующих стадий:
1. Build - сборка Docker образов
2. Test - запуск тестов
3. Deploy - развертывание на сервере
4. Cleanup - очистка неиспользуемых образов

## Конфигурационные файлы

### .gitlab-ci.yml
Основной файл конфигурации CI/CD, определяет стадии сборки и тестирования.

### .gitlab-deploy.yml
Файл с конфигурацией развертывания, подключается через `include` в основной конфигурации.

## Стадии pipeline

### Build

Стадия сборки создает Docker образы для бэкенда и фронтенда.

#### build:backend
- Собирает Docker образ бэкенда из `backend/config/Dockerfile`
- Использует кэш из предыдущих сборок для ускорения
- Помечает образ тегами: `CI_COMMIT_SHA`, `branch-${CI_COMMIT_REF_SLUG}`, `latest` (для main ветки)
- Загружает образы в GitLab Container Registry

Триггеры:
- Изменения в файлах бэкенда (`backend/**/*`)
- Изменения в общих файлах (docker-compose, Dockerfile, pyproject.toml)
- Принудительная сборка через `FORCE_BUILD_ALL=true`

#### build:frontend
- Собирает Docker образ фронтенда из `frontend/config/Dockerfile`
- Передает `VITE_API_BASE_URL` как build argument
- Использует кэш и тегирование аналогично бэкенду

Триггеры:
- Изменения в файлах фронтенда (`frontend/**/*`)
- Изменения в общих файлах
- Принудительная сборка

### Test

#### test:backend
- Запускает все тесты из директории `tests/`
- Использует PostgreSQL в качестве сервиса для тестов
- Устанавливает зависимости через pip
- Запускает pytest с подробным выводом

Переменные окружения для тестов:
- `POSTGRES_DB=test_db`
- `POSTGRES_USER=test_user`
- `POSTGRES_PASSWORD=test_password`
- `ENVIRONMENT=test`

Триггеры:
- Изменения в файлах бэкенда
- Изменения в общих файлах
- Принудительная сборка

### Deploy

Стадия развертывания выполняется только для ветки `main`.

Процесс развертывания:
1. Подключается к серверу развертывания по SSH
2. Клонирует или обновляет репозиторий на сервере
3. Авторизуется в GitLab Container Registry
4. Загружает новые образы бэкенда и фронтенда
5. Запускает `docker compose` для обновления контейнеров

### Cleanup

#### docker:gc
- Очищает неиспользуемые Docker образы и кэш
- Выполняется всегда, но с `allow_failure: true`
- Удаляет ресурсы старше 24 часов

## Переменные окружения GitLab CI/CD

### Полный список переменных

Все переменные настраиваются в **Settings → CI/CD → Variables** в GitLab.

#### Обязательные переменные

**Настройки для всех переменных:**
- **Visibility:** `Visible`
- **Protected:** ✗ (не защищенные)
- **Masked:** ✗ (не маскированные)
- **Minimum role to use pipeline variables:** `Developer`

| Переменная | Описание | Тип | Пример значения |
|-----------|----------|-----|-----------------|
| `SSH_PRIVATE_KEY` | Приватный SSH ключ для подключения к серверу деплоя | **Variable** (строго Variable, не File!) | Содержимое `~/.ssh/id_ed25519` |
| `DEPLOY_SERVER` | IP адрес или доменное имя сервера развертывания | Variable | `192.168.1.100` или `172.24.14.252` |
| `DEPLOY_USER` | Имя пользователя для SSH подключения | Variable | `root` или `deploy` |
| `DEPLOY_PATH` | Путь на сервере для развертывания | Variable | `/opt/fastapi-project` |
| `VITE_API_BASE_URL` | Базовый URL API для фронтенда (передается при сборке) | Variable | `http://172.24.14.252:8081` или `http://192.168.1.100:8081` |
| `FORCE_BUILD_ALL` | Принудительная сборка всех компонентов | Variable | `true` (рекомендуется) |

**Важно:** 
- `SSH_PRIVATE_KEY` должен быть типа **Variable** (не File!)
- `VITE_API_BASE_URL` обязательна для правильной сборки фронтенда - она встраивается в приложение при сборке
- Для виртуальной машины используйте IP адрес виртуалки, полученный через Bridge сеть
- Все переменные должны быть `Visible` и `Not Protected`

#### Опциональные переменные

| Переменная | Описание | Значение по умолчанию | Когда использовать |
|-----------|----------|----------------------|-------------------|
| `ENV_FILE` | Имя файла с переменными окружения | `.env` | Если используется другое имя файла |
| `BACKEND_PORT` | Порт бэкенда | `8081` | Если используется другой порт |
| `FORCE_DEPLOY` | Принудительное развертывание | `false` | Для принудительного деплоя установите `true`

#### Переменные для управления pipeline

| Переменная | Описание | Значение по умолчанию | Когда использовать |
|-----------|----------|----------------------|-------------------|
| `FORCE_BUILD_ALL` | Принудительная сборка всех компонентов | `false` | Для полной пересборки |
| `FORCE_DEPLOY` | Принудительное развертывание | `false` | Для принудительного деплоя |

#### Автоматические переменные GitLab

Эти переменные устанавливаются автоматически GitLab и не требуют настройки:

- `CI_REGISTRY` - адрес GitLab Container Registry
- `CI_REGISTRY_USER` - имя пользователя для регистра
- `CI_REGISTRY_PASSWORD` - пароль для регистра
- `CI_REPOSITORY_URL` - URL репозитория
- `CI_COMMIT_SHA` - SHA коммита
- `CI_COMMIT_REF_SLUG` - имя ветки
- `CI_COMMIT_BRANCH` - имя ветки (для main ветки)
- `CI_JOB_TOKEN` - токен для доступа к репозиторию

### Настройка переменных в GitLab

1. Перейдите в **Settings → CI/CD → Variables**
2. Нажмите **Add variable**
3. Заполните:
   - **Key:** имя переменной
   - **Value:** значение переменной
   - **Type:** Variable или File (для SSH ключей)
   - **Environment scope:** оставьте пустым (для всех окружений)
   - **Flags:**
     - **Protect variable:** включите для секретных данных
     - **Mask variable:** включите для текстовых переменных (не для файлов!)
4. Нажмите **Add variable**

### Переменные окружения для .env файла на сервере деплоя

На сервере, куда происходит деплой, должен быть файл `.env` со следующими переменными:

#### Обязательные переменные

```bash
# Database
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=fastapi_db
DB_PORT=5432

# Backend
BACKEND_PORT=8081
ENVIRONMENT=production
DEBUG=false

# External API
API_NINJAS=your_api_ninjas_key
API_NINJAS_BASE_URL=https://api.api-ninjas.com/v1

# Frontend (опционально)
FRONTEND_PORT=8000
```

**Важно:** 
- `DB_PASSWORD` должен быть надежным паролем
- `API_NINJAS` - ваш ключ от API Ninjas
- `ENVIRONMENT` должен быть `production` или `deploy` для продакшена
- `DEBUG` должен быть `false` для продакшена

Подробнее о переменных окружения см. в [DEPLOYMENT.md](DEPLOYMENT.md).

## GitLab Runner

Для работы CI/CD необходим настроенный GitLab Runner.

### Требования к раннеру

1. Установленный Docker
2. Доступ к GitLab Container Registry
3. Доступ к серверу развертывания по SSH (для стадии deploy)

### Регистрация раннера

```bash
gitlab-runner register \
  --url https://gitlab.com/ \
  --registration-token YOUR_TOKEN \
  --executor docker \
  --docker-image docker:28.5.0-cli \
  --description "Docker runner"
```

### Теги раннера

Если раннер имеет теги, укажите их в секции `tags` каждого job:

```yaml
build:backend:
  tags:
    - docker
    - linux
```

## Условия запуска

### Workflow правила

Pipeline не запускается при:
- Изменениях только в `README.md`
- Изменениях только в `docs/**/*`

Pipeline всегда запускается при:
- Push в любую ветку (кроме исключений выше)
- Принудительном запуске через `FORCE_BUILD_ALL=true`

### Правила для стадий

#### Build
Запускается при изменениях в соответствующих файлах или принудительной сборке.

#### Test
Запускается при изменениях в бэкенде или общих файлах.

#### Deploy
Запускается только для ветки `main` при:
- Наличии изменений в коде
- Успешном прохождении стадий build и test
- Принудительном развертывании через `FORCE_DEPLOY=true`

## Локальное тестирование CI/CD

Для тестирования конфигурации локально можно использовать GitLab Runner:

```bash
gitlab-runner exec docker build:backend
gitlab-runner exec docker test:backend
```

## Мониторинг pipeline

Статус pipeline можно отслеживать:
- В интерфейсе GitLab в разделе CI/CD → Pipelines
- Через уведомления (если настроены)
- В логах каждого job

## Отладка проблем

### Сборка не запускается
- Проверьте правила в секции `rules`
- Убедитесь, что изменения в нужных файлах
- Проверьте настройки workflow

### Тесты падают
- Проверьте логи тестового job
- Убедитесь, что PostgreSQL доступен
- Проверьте переменные окружения

### Развертывание не выполняется
- Проверьте, что находитесь в ветке `main`
- Убедитесь, что SSH ключ настроен правильно
- Проверьте доступность сервера развертывания
- Проверьте наличие файла `.env` на сервере

### Проблемы с Docker Registry
- Проверьте токены доступа к регистру
- Убедитесь, что образы загружаются успешно
- Проверьте права доступа к проекту

## Безопасность

1. Не храните секреты в коде
2. Используйте Masked и Protected переменные для паролей и ключей
3. Регулярно ротируйте SSH ключи и токены доступа
4. Ограничьте доступ к CI/CD настройкам только необходимому кругу лиц


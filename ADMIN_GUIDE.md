# Руководство администратора

## Установка

### Автоматическая установка (рекомендуется)

```bash
sudo ./install.sh
```

Скрипт автоматически:
1. Определит дистрибутив и пакетный менеджер
2. Проверит доступность сети
3. Установит необходимые компоненты (git, curl, docker, docker compose)
4. Клонирует репозиторий в `/opt/glass`
5. Запросит порт приложения и пароль администратора
6. Запустит Docker-стек

### Ручная установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app
```

Приложение будет доступно на `http://localhost:5000`.

### Поддерживаемые системы

| Дистрибутив | Версии | Пакетный менеджер |
|-------------|--------|-------------------|
| Ubuntu      | 22.04 LTS, 24.04 LTS, 26.04 LTS | apt |
| Debian      | 12, 13 | apt |
| Linux Mint  | актуальные на базе Ubuntu LTS | apt |
| Arch Linux  | rolling release | pacman |
| Fedora      | 40+ | dnf |
| AlmaLinux   | 9+ | dnf |
| Rocky Linux | 9+ | dnf |

---

## Обновление

### Автоматическое обновление (рекомендуется)

```bash
sudo ./update.sh
# Или глобально:
sudo contour-update
```

Перед обновлением автоматически создаётся резервная копия в `backup/YYYY-MM-DD_HH-MM-SS/`:
- `configs/` — пользовательские конфигурации
- `storage/` — файлы хранилища
- `exports/` — экспортированные файлы
- `.env` — файл окружения

При ошибке обновление останавливается, резервная копия сохраняется.

### Ручное обновление

```bash
cd /opt/glass
git pull
docker compose up -d --build
```

---

## Удаление

```bash
sudo ./uninstall.sh
# Или:
sudo contour-uninstall
```

Перед удалением скрипт предложит сохранить пользовательские данные. Для автоматического удаления без подтверждения:

```bash
sudo ./uninstall.sh --force
```

---

## Смена пароля администратора

```bash
sudo ./change-admin-password.sh
# Или глобально:
sudo contour-change-password
```

Пароль хешируется с использованием werkzeug.security и сохраняется в `.env` как `CONFIG_ADMIN_PASSWORD`.

## Сброс пароля администратора

```bash
sudo ./reset-admin-password.sh
# Или глобально:
sudo contour-reset-password
```

Сброс возможен только локально на сервере. После сброса пароль = `admin`.

---

## Резервное копирование

### Автоматическое резервирование (update.sh)

При каждом запуске `update.sh` автоматически создаётся резервная копия:

```
backup/YYYY-MM-DD_HH-MM-SS/
├── configs/       # пользовательские конфигурации
├── storage/       # файлы хранилища
├── exports/       # экспортированные файлы
└── .env           # файл окружения
```

Резервные копии не удаляются автоматически.

### Ручное резервное копирование

```bash
# Пользовательские конфигурации
cp -r /opt/glass/app/user_configs /backup/user_configs_$(date +%Y%m%d)

# Полное резервирование
cd /opt/glass && docker compose down
tar -czf /backup/glass_$(date +%Y%m%d).tar.gz /opt/glass
docker compose up -d
```

---

## Восстановление

```bash
# Распакуйте архив
tar -xzf /backup/glass_20260616.tar.gz -C /

# Если были сохранены пользовательские конфигурации
cp -r /backup/user_configs_20260616/* /opt/glass/app/user_configs/

# Пересоберите и запустите
cd /opt/glass
docker compose up -d --build
```

---

## Работа с логами

### Логи приложения (Flask + Gunicorn)

```bash
# В реальном времени
docker compose logs -f app

# Последние 100 строк
docker compose logs --tail=100 app
```

### Логи Nginx

```bash
docker compose logs -f nginx
```

### Логи systemd (автообновление)

```bash
journalctl -u contour-update.service -f
```

---

## Проверка работоспособности

```bash
# Проверка статуса контейнеров
docker compose ps

# Проверка HTTP
curl -s http://localhost:5000/ | head -5

# Проверка API
curl -s -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"config":{"j_x":-48,"c_x":-160,"cd_len":65,"de_len":20,"fg_len":20,"gh_len":70,"hi_len":43.5,"jk_len":8.5,"hcor":80},"input_data":{"n1":100,"n2":50,"n4":null,"angle_EF":5}}'
```

Ожидаемый ответ API — JSON с координатами точек.

---

## Запуск тестов

```bash
# Все тесты
python -m pytest tests/ -v

# Только тесты эквивалентности
python -m pytest tests/test_core_calculator.py -v

# Только тесты обёртки
python -m pytest tests/test_calculate_wrapper.py -v
```

Все тесты должны пройти успешно.

---

## Обновление конфигураций

### Системные пресеты

Системные пресеты хранятся в `app/configs/` и доступны только для чтения.
Для добавления нового пресета создайте JSON-файл в этой директории:

```json
{
    "j_x": -48,
    "c_x": -160,
    "cd_len": 65,
    "de_len": 20,
    "fg_len": 20,
    "gh_len": 70,
    "hi_len": 43.5,
    "jk_len": 8.5,
    "hcor": 80,
    "image": null
}
```

Имя файла = имя пресета (без расширения `.json`).

### Пользовательские конфигурации

Хранятся в `app/user_configs/` (в Docker — через volume `data/`).
Управляются через веб-интерфейс (режим администратора) или CLI.

---

## Управление экспортами

### PDF-экспорт

```bash
python -m app.cli export-pdf config.json output.pdf
```

### JSON-экспорт

```bash
python -m app.cli calculate config.json
# Автоматически создаёт config.result.json
```

### CSV-экспорт

```python
from app.core.calculate import calculate
from app.storage.export_csv import export_csv

result = calculate(input_data, config)
export_csv(result, 'output.csv')
```

---

## Автообновление (systemd)

Автообновление настраивается во время установки. Для ручной настройки:

```bash
sudo cp /opt/glass/contour-update.service /opt/glass/contour-update.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now contour-update.timer
```

Таймер запускает `update.sh` раз в сутки.

---

## Структура резервных копий

```
backup/
├── 2026-06-19_12-00-00/
│   ├── configs/       # пользовательские конфигурации
│   ├── storage/       # файлы хранилища
│   ├── exports/       # экспортированные файлы
│   └── .env           # файл окружения
├── 2026-06-20_12-00-00/
│   └── ...
└── ...
```

Резервные копии не удаляются автоматически. Рекомендуется периодически очищать старые копии вручную.
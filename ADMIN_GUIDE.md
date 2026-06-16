# Руководство администратора

## Установка

### Через Docker (рекомендуется)

```bash
sudo apt update && sudo apt install curl -y
curl -O https://raw.githubusercontent.com/tvwoth/glass/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

Скрипт установит Docker, клонирует репозиторий в `/opt/glass`, соберёт и запустит контейнеры.

### Вручную

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app
```

Приложение будет доступно на `http://localhost:5000`.

---

## Обновление

### Через Docker

```bash
cd /opt/glass
sudo ./update.sh
# Или глобально:
sudo glass-update
```

### Вручную

```bash
cd /opt/glass
git pull
pip install -r requirements.txt
```

---

## Резервное копирование

### Пользовательские конфигурации

```bash
# Копирование пользовательских конфигураций
cp -r /opt/glass/app/user_configs /backup/user_configs_$(date +%Y%m%d)

# Или через Docker volume
docker cp glass-app:/app/user_configs /backup/user_configs_$(date +%Y%m%d)
```

### Полное резервное копирование

```bash
# Остановите контейнеры
cd /opt/glass && docker compose down

# Архивируйте
tar -czf /backup/glass_$(date +%Y%m%d).tar.gz /opt/glass

# Запустите обратно
docker compose up -d
```

---

## Восстановление

```bash
# Распакуйте архив
tar -xzf /backup/glass_20260616.tar.gz -C /

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
journalctl -u glass-update.service -f
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

Все 50 тестов должны пройти успешно.

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

## Смена пароля администратора

```bash
cd /opt/glass
sudo ./change-password.sh
# Или глобально:
sudo glass-change-password
```

Пароль хранится в `.env` как `CONFIG_ADMIN_PASSWORD`.

---

## Автообновление (systemd)

```bash
sudo cp glass-update.service glass-update.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now glass-update.timer
```

Таймер запускает `update.sh` раз в сутки.

---

## Полное удаление

```bash
sudo glass-uninstall
# Или:
cd /opt/glass && sudo ./uninstall.sh
```

Скрипт остановит контейнеры, удалит systemd-юниты и директорию `/opt/glass`.
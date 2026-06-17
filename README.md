# Contour App

> Веб-приложение для расчёта и визуализации геометрии конструкции стеклянного навеса (Козырька).
> Расчёт выполняется по трём из четырёх заданных параметров (n1, n2, n3, angle_EF),
> четвёртый вычисляется автоматически.

---

## Основные возможности

* Расчёт контура стеклопакета (точки A–K)
* Работа с системными и пользовательскими конфигурациями
* Экспорт результатов в PDF, JSON и CSV
* Веб-интерфейс на Flask
* REST API (`POST /api/calculate`)
* CLI (`python -m app.cli`)

---

## Быстрый запуск

### Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# или .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Запуск приложения

```bash
python -m app
# Приложение доступно на http://localhost:5000
```

### Запуск через Docker

```bash
docker compose up -d --build
# Приложение доступно на http://localhost
```

---

## Структура проекта

```
contour-app/
├── app/
│   ├── __init__.py              # Flask-приложение
│   ├── cli.py                   # Командная строка (CLI)
│   ├── api/
│   │   └── routes.py            # REST API
│   ├── configs/                 # Единый менеджер конфигураций
│   │   ├── manager.py           # ConfigManager (CRUD)
│   │   └── helpers.py           # parse_h_params, apply_h_params
│   ├── core/
│   │   ├── calculator.py        # Единственный источник математики
│   │   ├── calculate.py         # Обёртка-интерфейс
│   │   └── exceptions.py        # Кастомные исключения
│   ├── legacy/
│   │   └── contour_calculator.py # Оригинальная реализация (для тестов)
│   ├── rendering/
│   │   └── matplotlib_renderer.py # Визуализация графика
│   ├── storage/
│   │   ├── export_json.py       # Экспорт в JSON
│   │   ├── export_csv.py        # Экспорт в CSV
│   │   └── export_pdf.py        # Экспорт в PDF
│   ├── templates/               # HTML-шаблоны
│   ├── static/                  # Статические файлы
│   └── user_configs/            # Пользовательские конфигурации
├── tests/
│   ├── test_calculate_wrapper.py
│   ├── test_contour_calculator.py
│   └── test_core_calculator.py
├── docs/
│   └── API.md                   # Спецификация API
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Ссылки на документацию

| Документ | Назначение |
|----------|-----------|
| [USER_GUIDE.md](USER_GUIDE.md) | Руководство пользователя |
| [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | Руководство администратора |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Руководство разработчика |
| [CONFIG_FORMAT.md](CONFIG_FORMAT.md) | Спецификация формата конфигураций |
| [docs/API.md](docs/API.md) | Спецификация REST API |

---

## Краткая сводка CLI

```bash
python -m app.cli calculate config.json
python -m app.cli render config.json [output.png]
python -m app.cli export-pdf config.json [output.pdf]
python -m app.cli config-list
python -m app.cli config-edit <name> [param=value ...]
```

Подробное описание — в [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#cli).

---

## Лицензия

Проект Glass / Contour App.
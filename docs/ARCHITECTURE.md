# Архитектура проекта Contour

## Общая схема

```
WEB
API
CLI
     ↓
CONFIGS
     ↓
CORE
     ↓
RENDERING
     ↓
EXPORT
```

## Описание каждого модуля

### core

Математическое ядро.

- `app/core/calculator.py` — класс `ContourCalculator`, содержит всю математическую логику расчёта геометрии контура.
- `app/core/calculate.py` — тонкая обёртка над `ContourCalculator`, предоставляет функциональный (stateless) интерфейс для удобства использования из CLI и API.
- `app/core/exceptions.py` — доменные исключения.

**Запрет:** изменение формул, порядка вычислений, обработки углов, работы со знаками, поиска неизвестных параметров и геометрических преобразований в этом модуле запрещено.

### configs

Работа с конфигурациями.

- `app/configs/manager.py` — `ConfigManager`, единый механизм CRUD для системных и пользовательских конфигураций (load, save, list, duplicate, delete, rename).
- `app/configs/helpers.py` — вспомогательные функции для разбора и применения параметров из форм (`parse_h_params`, `apply_h_params`).
- `app/configs/*.json` — системные пресеты.

Все остальные части проекта (Web, API, CLI) обязаны использовать только `ConfigManager` для работы с конфигурациями.

### rendering

Графика.

- `app/rendering/matplotlib_renderer.py` — построение изображения контура через matplotlib.
- `app/rendering/__init__.py` — экспортирует функцию `render`.

Визуализация должна существовать только в этом модуле.

### storage

Экспорт результатов.

- `app/storage/export_json.py` — экспорт в JSON.
- `app/storage/export_csv.py` — экспорт в CSV.
- `app/storage/export_pdf.py` — экспорт в PDF.

### api

REST API.

- `app/api/routes.py` — эндпоинт `/api/calculate`, принимает входные данные и конфигурацию, возвращает результат расчёта.

### web

Веб-интерфейс.

- `app/__init__.py` — Flask-приложение, маршруты, логика работы с конфигурациями и визуализацией в браузере.
- `app/templates/index.html` — основной шаблон.
- `app/static/` — статические файлы.

### cli

Консольный интерфейс.

- `app/cli.py` — команды `calculate`, `render`, `export-pdf`, `config-list`, `config-edit`.

## Принципы

- Единая система конфигураций через `ConfigManager`.
- Единая система визуализации через `rendering`.
- Математическое ядро не изменяется без особой необходимости.
- Legacy-код сохраняется до нескольких стабильных релизов.
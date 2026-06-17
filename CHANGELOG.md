# Changelog

## [1.0.0] - 2026-06-16

### Что изменилось

#### Новая архитектура

- Единый модуль конфигураций `app/configs/` с `ConfigManager` и `helpers.py`.
- Удалён дублирующий `app/config_service.py`, все интерфейсы (Web, API, CLI) используют `ConfigManager`.
- Единая система визуализации в `app/rendering/`.
- Математическое ядро остаётся неизменным в `app/core/calculator.py`.

#### Новое ядро

- `app/core/calculator.py` — единственный источник математической логики.
- `app/core/calculate.py` — тонкая обёртка для CLI и API.
- `app/core/exceptions.py` — доменные исключения.

#### CLI

- Команды: `calculate`, `render`, `export-pdf`, `config-list`, `config-edit`.
- Автоматическое сохранение результатов в JSON с метаданными.

#### PDF

- Экспорт включает версию приложения, дату, имя конфигурации, параметры и координаты.
- Добавлено изображение контура в PDF.

#### API

- REST API на Flask: `POST /api/calculate`.
- Единый формат запроса/ответа.

#### Документация

- `docs/ARCHITECTURE.md` — описание архитектуры.
- Обновлены `README.md`, `DEVELOPER_GUIDE.md`, `USER_GUIDE.md`, `ADMIN_GUIDE.md`, `CONFIG_FORMAT.md`, `docs/API.md`.

#### Очистка

- Удалён неиспользуемый модуль `app/utils/`.
- Удалён дублирующий `app/config_service.py`.
- Удалены неиспользуемые импорты и дубли кода.

#### Обратная совместимость

- Формат JSON-конфигураций не изменён.
- Все существующие пресеты и пользовательские конфигурации работают без изменений.
- Legacy-модуль `app/legacy/contour_calculator.py` сохранён.
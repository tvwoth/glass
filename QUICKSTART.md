# 🚀 Быстрый старт: Использование новой архитектуры

## 1️⃣ Использование функции `calculate()` напрямую

Самый простой способ - использовать ядро расчётов как модуль Python:

```python
from app.core.calculate import calculate

# Подготовка конфигурации
config = {
    "j_x": -48,
    "c_x": -160,
    "cd_len": 65,
    "de_len": 20,
    "fg_len": 20,
    "gh_len": 70,
    "hi_len": 43.5,
    "jk_len": 8.5,
    "hcor": 80,
}

# Подготовка входных данных (3 из 4 параметров)
input_data = {
    "n1": 100,        # дано
    "n2": None,       # найти
    "n4": None,       # найти
    "angle_EF": 5     # дано
}

# Расчёт
result = calculate(input_data, config)

# Результаты
print(f"n1={result['n1']:.2f}")
print(f"n2={result['n2']:.2f}")
print(f"n4={result['n4']:.2f}")
print(f"angle_EF={result['angle_EF']:.2f}°")

# Точки
points = result['points']  # Список 11 кортежей (x, y)
```

## 2️⃣ REST API - HTTP запрос

Используйте endpoint `/api/calculate` для получения результатов через HTTP:

```bash
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "j_x": -48,
      "c_x": -160,
      "cd_len": 65,
      "de_len": 20,
      "fg_len": 20,
      "gh_len": 70,
      "hi_len": 43.5,
      "jk_len": 8.5,
      "hcor": 80
    },
    "input_data": {
      "n1": 100,
      "n2": null,
      "n4": null,
      "angle_EF": 5
    }
  }'
```

**Ответ:**
```json
{
  "n1": 100,
  "n2": 45.23,
  "n4": 120.15,
  "angle_EF": 5,
  "angle_D": 185,
  "points": [
    [0, 0],
    [0, -100],
    [-160, -100],
    ...
  ]
}
```

## 3️⃣ CLI - Командная строка

Используйте CLI для расчётов без запуска веб-приложения:

```bash
# Запуск
python -m app.cli config.json

# Результаты выводятся в консоль + график сохраняется
```

**Формат config.json:**
```json
{
  "config": {
    "j_x": -48,
    "c_x": -160,
    "cd_len": 65,
    "de_len": 20,
    "fg_len": 20,
    "gh_len": 70,
    "hi_len": 43.5,
    "jk_len": 8.5,
    "hcor": 80
  },
  "input_data": {
    "n1": 100,
    "n2": null,
    "n4": null,
    "angle_EF": 5
  }
}
```

## 4️⃣ Визуализация

Генерация графика контура:

```python
from app.core.calculate import calculate
from app.utils.plot import generate_plot

# Расчёт
result = calculate(input_data, config)

# Визуализация
generate_plot(result['points'], 'output.png')
```

Или через CLI:
```bash
python -m app.cli config.json
# Автоматически создаст config_plot.png
```

## 5️⃣ Обработка ошибок

```python
from app.core.calculate import calculate

try:
    result = calculate(input_data, config)
except ValueError as e:
    print(f"Ошибка расчёта: {e}")
    # Возможные ошибки:
    # - "Необходимо ввести ровно три параметра"
    # - "Угол наклона должен быть в диапазоне 0°–10°"
    # - "Длина ... должна быть положительной"
    # - "Выберите конфигурацию или введите значения H"
    # - "Не удалось найти длину ..."
    # - "Не удалось найти угол D"
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

## 📋 Требования к входным данным

### Конфигурация (config)

Все параметры конфигурации ОПЦИОНАЛЬНЫ, если не указаны, используются значения по умолчанию:

```python
config = {
    # Координаты точек (default = 0)
    "a_x": 0,
    "a_y": 0,
    "b_x": 0,
    "c_x": -160,        # H2 - координата C по X
    "d_x": -160,        # = c_x
    "k_x": -48,         # = j_x
    "k_y": 0,           # = a_y
    
    # Длины участков (default = 0)
    "cd_len": 65,       # H3
    "de_len": 20,       # H4
    "fg_len": 20,       # H5
    "gh_len": 70,       # H6
    "hi_len": 43.5,     # H7
    "j_x": -48,         # H1
    "jk_len": 8.5,      # H8
    
    # Коррекции (default = 0)
    "hcor": 80,         # Коррекция для n4
    
    # Флаги (default = False)
    "rev": False,       # Реверс направления
}
```

### Входные данные (input_data)

Ровно ТРЁЙ параметра должны быть не None:

```python
input_data = {
    "n1": 100,          # Может быть число или None
    "n2": 50,           # Может быть число или None
    "n4": None,         # Может быть число или None
    "angle_EF": 5       # Может быть число (0-10) или None
}
```

**Требования:**
- Ровно 3 из 4 параметров должны быть не None
- 1 параметр будет вычислен
- n1, n2, n4 должны быть > 0
- angle_EF должен быть в диапазоне 0-10°

## 🔍 Примеры использования

### Пример 1: Найти n4 и angle_EF

```python
result = calculate({
    "n1": 100,
    "n2": 50,
    "n4": None,
    "angle_EF": None
}, config)

# Результат: n4 и angle_EF будут вычислены
print(f"n4={result['n4']:.2f}, angle_EF={result['angle_EF']:.2f}")
```

### Пример 2: Найти n1 (бинарный поиск)

```python
result = calculate({
    "n1": None,
    "n2": 50,
    "n4": 120,
    "angle_EF": 5
}, config)

# Результат: n1 будет найден с точностью до 0.01
print(f"n1={result['n1']:.2f}")
```

### Пример 3: Все точки

```python
result = calculate(input_data, config)
points = result['points']

# 11 точек: A, B, C, D, E, F, G, H, I, J, K
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

for label, (x, y) in zip(labels, points):
    print(f"{label}: ({x:.2f}, {y:.2f})")
```

## 📂 Где найти код

| Компонент | Файл |
|-----------|------|
| Основная функция | `app/core/calculate.py` |
| REST API | `app/api/routes.py` |
| CLI | `app/cli.py` |
| Визуализация | `app/utils/plot.py` |
| Flask app | `app/__init__.py` |

## ❓ Часто задаваемые вопросы

**Q: Будут ли результаты идентичны старой реализации?**  
A: Да! Все алгоритмы, формулы и порядок вычислений остались неизменными.

**Q: Можно ли использовать старый класс ContourCalculator?**  
A: Да! Он остаётся в проекте для обратной совместимости.

**Q: Какие параметры обязательны в config?**  
A: Все опциональны! По умолчанию используются 0.

**Q: Как передать конфигурацию из JSON файла?**  
A: Используйте `json.load()`:
```python
import json
with open('config.json') as f:
    data = json.load(f)
    result = calculate(data['input_data'], data['config'])
```

**Q: Как сохранить результаты?**  
A: В виде JSON:
```python
import json
with open('result.json', 'w') as f:
    json.dump({
        'n1': result['n1'],
        'n2': result['n2'],
        'n4': result['n4'],
        'points': result['points']
    }, f, indent=2)
```

---

## 📖 Больше информации

Для полного описания архитектуры см. [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)

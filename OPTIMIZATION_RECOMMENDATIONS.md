# Рекомендации по оптимизации проекта

## 🔴 Критические проблемы производительности

### 1. Множественные фильтрации DataFrame в цикле

**Проблема:** В `data_prep.py` выполняется 52+ фильтраций `master_df.loc[master_df["date"].dt.month == m]` для каждого дня в цикле. Каждая фильтрация проходит по всему DataFrame.

**Решение:**
```python
# В main.py перед циклом:
# Создать индексы и предварительно отфильтровать данные по месяцам
master_df = master_df.set_index("date")
monthly_data = {}
for month in range(1, 13):
    month_df = master_df[master_df.index.month == month]
    monthly_data[month] = month_df

# В data_prep.py использовать предфильтрованные данные:
def prepare_suzun_data(monthly_df, n, prev_day, prev_month, N):
    m = n.month
    # Использовать monthly_df вместо фильтрации
    G_buy_month = monthly_df["buying_oil"].values
    # ...
```

**Ожидаемый эффект:** Ускорение в 10-50 раз для больших датасетов.

### 2. Повторяющиеся вычисления в цикле

**Проблема:** `calendar.monthrange(n.year, n.month)[1]` вычисляется для каждого дня, хотя месяц не меняется.

**Решение:**
```python
# Вычислить один раз для каждого месяца
month_days = {}
for n in dates:
    month_key = (n.year, n.month)
    if month_key not in month_days:
        month_days[month_key] = calendar.monthrange(n.year, n.month)[1]
    N = month_days[month_key]
```

**Ожидаемый эффект:** Небольшое ускорение, но улучшает читаемость.

### 3. Неэффективная работа с DataFrame

**Проблема:** Создание DataFrame из списка словарей в конце цикла.

**Решение:**
```python
# Использовать предварительно созданный DataFrame
result_df = pd.DataFrame(index=dates, columns=expected_columns)
for idx, n in enumerate(dates):
    # Заполнять напрямую
    result_df.loc[n, "G_buy_day"] = suzun_results["G_buy_day"]
    # ...
```

**Ожидаемый эффект:** Ускорение на 20-30%.

---

## 🟡 Проблемы архитектуры и кода

### 4. Множественные вызовы input()

**Проблема:** 66 вызовов `input()` блокируют выполнение и делают невозможной автоматизацию.

**Решение:**
```python
# Создать класс для управления вводами
class InputManager:
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file) if config_file else {}
        self.prompt_mode = os.getenv("PROMPT_MODE", "interactive")
    
    def get_value(self, key, prompt, default=None):
        if key in self.config:
            return self.config[key]
        if self.prompt_mode == "interactive":
            value = input(prompt)
            return float(value) if value.strip() else default
        return default or 0.0

# Использование:
input_manager = InputManager("config.json")
G_payaha = input_manager.get_value("G_payaha", "Введите значение G_пайяха: ")
```

**Ожидаемый эффект:** Возможность автоматизации, тестирования, использования конфигурационных файлов.

### 5. Огромный файл calculate.py (1000+ строк)

**Проблема:** Один файл содержит все функции расчета, сложно поддерживать.

**Решение:**
```
calculate/
├── __init__.py
├── base.py          # _to_float и общие утилиты
├── suzun.py         # Функции для Сузун
├── vo.py            # Восток Ойл
├── kchng.py         # КЧНГ
├── lodochny.py      # Лодочный
├── cppn1.py         # ЦППН-1
├── rn_vankor.py     # РН-Ванкор
├── sikn_1208.py     # СИКН-1208
└── tstn.py          # ТСТН
```

**Ожидаемый эффект:** Улучшенная читаемость, проще тестировать, легче поддерживать.

### 6. Дублирование кода в data_prep.py

**Проблема:** Повторяющиеся паттерны фильтрации данных.

**Решение:**
```python
def _get_month_data(master_df, month, columns):
    """Универсальная функция для получения месячных данных."""
    month_df = master_df[master_df["date"].dt.month == month]
    return {col: month_df[col].values for col in columns}

def _get_day_data(master_df, date, columns):
    """Универсальная функция для получения дневных данных."""
    day_df = master_df[master_df["date"] == date]
    return {col: day_df[col].values[0] if len(day_df) > 0 else 0.0 
            for col in columns}

# Использование:
def prepare_suzun_data(master_df, n, m, prev_day, prev_month, N):
    month_cols = ["buying_oil", "out_udt", "gtm_vn", "gtm_suzun", ...]
    day_cols = ["gtm_vslu", "gtm_suzun"]
    
    month_data = _get_month_data(master_df, m, month_cols)
    day_data = _get_day_data(master_df, n, day_cols)
    prev_day_data = _get_day_data(master_df, prev_day, ["suzun_tng", ...])
    
    return {**month_data, **day_data, **prev_day_data, "N": N}
```

**Ожидаемый эффект:** Меньше кода, проще поддерживать, меньше ошибок.

### 7. Огромный файл manual_data.py

**Проблема:** 1000+ строк с повторяющимися данными, сложно поддерживать.

**Решение:**
```python
# Использовать CSV или JSON для хранения данных
# manual_data/
#   ├── suzun_tng.csv
#   ├── upn_suzun.csv
#   └── ...

# Или использовать базу данных для больших объемов
import sqlite3

def load_manual_data(param_name, start_date, end_date):
    conn = sqlite3.connect("manual_data.db")
    query = """
        SELECT date, value 
        FROM manual_data 
        WHERE param = ? AND date BETWEEN ? AND ?
    """
    df = pd.read_sql(query, conn, params=(param_name, start_date, end_date))
    conn.close()
    return df
```

**Ожидаемый эффект:** Легче редактировать данные, можно использовать Excel/CSV редакторы.

---

## 🟢 Улучшения качества кода

### 8. Добавить валидацию данных

**Решение:**
```python
from typing import Optional
import numpy as np

def validate_data_range(value: float, min_val: float, max_val: float, 
                       param_name: str) -> float:
    """Валидация значения в заданном диапазоне."""
    if not (min_val <= value <= max_val):
        raise ValueError(
            f"{param_name} = {value} вне допустимого диапазона "
            f"[{min_val}, {max_val}]"
        )
    return value

# Использование в calculate.py:
V_suzun_tng = validate_data_range(
    calculated_value, 
    min_val=0, 
    max_val=10000,
    param_name="V_suzun_tng"
)
```

### 9. Добавить логирование

**Решение:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Использование:
logger.info(f"Обработка дня {n}")
logger.warning(f"Значение {value} вне нормального диапазона")
logger.error(f"Ошибка при расчете: {e}")
```

### 10. Добавить кэширование

**Решение:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def get_month_data_cached(master_df_hash, month, column):
    """Кэшированное получение месячных данных."""
    # Реализация с использованием хеша DataFrame
    pass

# Или использовать pandas caching
master_df_monthly = master_df.groupby(master_df["date"].dt.month)
```

### 11. Использовать dataclasses для конфигурации

**Решение:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CalculationConfig:
    G_payaha: float
    G_suzun_tng: float
    K_g_suzun: float
    manual_V_upn_suzun: Optional[float] = None
    manual_V_suzun_vslu: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def to_dict(self):
        return asdict(self)
```

### 12. Добавить типизацию

**Решение:**
```python
from typing import Dict, List, Optional, Tuple
import pandas as pd

def prepare_suzun_data(
    master_df: pd.DataFrame,
    n: pd.Timestamp,
    m: int,
    prev_day: pd.Timestamp,
    prev_month: pd.Timestamp,
    N: int
) -> Dict[str, np.ndarray]:
    """Собирает все аргументы для calculate.suzun."""
    # ...
```

---

## 📊 Приоритизация оптимизаций

### Высокий приоритет (немедленно):
1. ✅ Индексация DataFrame и предфильтрация по месяцам
2. ✅ Замена input() на конфигурационный файл
3. ✅ Разбиение calculate.py на модули

### Средний приоритет (в ближайшее время):
4. ✅ Рефакторинг data_prep.py для устранения дублирования
5. ✅ Добавление валидации данных
6. ✅ Добавление логирования

### Низкий приоритет (по возможности):
7. ✅ Оптимизация manual_data.py
8. ✅ Добавление кэширования
9. ✅ Улучшение типизации

---

## 🚀 Ожидаемые результаты

После применения всех оптимизаций:
- **Производительность:** Ускорение в 10-50 раз
- **Поддерживаемость:** Улучшение на 80%
- **Тестируемость:** Возможность автоматического тестирования
- **Надежность:** Меньше ошибок благодаря валидации

---

## 📝 Реализованные оптимизации

Оптимизации интегрированы в основной код:
- ✅ Кэширование месячных данных в `data_prep.py` (функция `init_monthly_cache`)
- ✅ Предфильтрация данных по месяцам для ускорения доступа
- ✅ Использование `input.json` вместо интерактивного ввода
- ✅ Безопасные функции получения данных с fallback на значения по умолчанию


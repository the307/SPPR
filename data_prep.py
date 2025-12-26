"""
МОДУЛЬ ПОДГОТОВКИ ДАННЫХ ДЛЯ РАСЧЕТОВ

Этот модуль извлекает данные из master_df и формирует словари аргументов
для функций расчета из calculate.py.

ЛОГИКА РАБОТЫ:
---------------
1. КЭШИРОВАНИЕ (init_monthly_cache):
   - Предфильтрует master_df по месяцам для ускорения доступа
   - Создает индекс по дате для быстрого поиска дневных значений
   - Вызывается один раз в main.py перед циклом по дням

2. БЕЗОПАСНОЕ ПОЛУЧЕНИЕ ДАННЫХ:
   
   a) _safe_get_month_values() - месячные данные:
      - Сначала проверяет input.json (раздел monthly_data)
      - Если в input.json указано одно число - использует его для всех дней
      - Если указан массив - возвращает массив numpy
      - Если null - берет из master_df (через кэш или напрямую)
      - Если колонка отсутствует - возвращает значение по умолчанию (пустой массив)
   
   b) _safe_get_day_value() - дневные данные:
      - Сначала проверяет input.json (monthly_data с массивом)
      - Если массив - берет значение по индексу дня месяца (день 1 = индекс 0)
      - Если одно число - использует его для всех дней
      - Если null - берет из master_df (через кэшированный индекс)
      - Если колонка отсутствует - возвращает значение по умолчанию (0.0)

3. ФУНКЦИИ ПОДГОТОВКИ ДАННЫХ:
   Каждая функция prepare_*_data() собирает данные для соответствующего блока:
   
   - prepare_suzun_data() - данные для блока СУЗУН
   - prepare_vo_data() - данные для блока ВОСТОК ОЙЛ
   - prepare_kchng_data() - данные для блока КЧНГ
   - prepare_lodochny_data() - данные для блока ЛОДОЧНЫЙ
   - prepare_cppn1_data() - данные для блока ЦППН-1
   - prepare_rn_vankor_data() - данные для блока РН-ВАНКОР
   - prepare_sikn_1208_data() - данные для блока СИКН-1208
   - prepare_TSTN_data() - данные для блока ТСТН

ПРИОРИТЕТ ИСТОЧНИКОВ ДАННЫХ:
----------------------------
1. input.json (monthly_data) - если значение указано явно (не null)
2. master_df (через кэш) - если значение в input.json = null
3. Значение по умолчанию - если колонка отсутствует в master_df

ОПТИМИЗАЦИЯ:
------------
- Кэш месячных данных (_monthly_cache) - предфильтрованные DataFrames по месяцам
- Кэш индексированного DataFrame (_master_df_indexed) - для быстрого поиска по дате
- Кэш предупреждений (_warning_cache) - чтобы не повторять одно и то же предупреждение
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path


# модуль собирает все значения из master_df и формирует словари,
# которые соответствуют аргументам оригинального main.py → calculate.*

# Кэш для конфигурации из input.json
_input_config_cache = None

# Кэш для месячных данных (оптимизация производительности)
_monthly_cache = None
_master_df_indexed = None

# Кэш для выведенных предупреждений (чтобы не повторять одно и то же)
_warning_cache = set()

def _get_input_config():
    """Загружает конфигурацию из input.json."""
    global _input_config_cache
    if _input_config_cache is None:
        config_file = Path("input.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    _input_config_cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке input.json: {e}")
                _input_config_cache = {}
        else:
            _input_config_cache = {}
    return _input_config_cache


def init_monthly_cache(master_df):
    """
    Инициализирует кэш месячных данных для оптимизации производительности.
    
    Эта функция должна быть вызвана один раз в main.py перед циклом по дням.
    
    Args:
        master_df: Исходный DataFrame с данными
    """
    global _monthly_cache, _master_df_indexed
    
    if _monthly_cache is not None:
        return  # Кэш уже инициализирован
    
    # Создаем копию DataFrame с индексом по дате для быстрого доступа
    _master_df_indexed = master_df.copy()
    if "date" not in _master_df_indexed.columns:
        raise ValueError("master_df должен содержать колонку 'date'")
    
    _master_df_indexed["date"] = pd.to_datetime(_master_df_indexed["date"]).dt.normalize()
    
    # Предфильтруем данные по месяцам
    _monthly_cache = {}
    for month in range(1, 13):
        month_mask = _master_df_indexed["date"].dt.month == month
        if month_mask.any():
            _monthly_cache[month] = _master_df_indexed[month_mask].copy()
    
    print(f"Кэш месячных данных инициализирован для {len(_monthly_cache)} месяцев")

def _safe_get_month_values(master_df, month, column_name, default=np.array([])):
    """
    Безопасное получение месячных значений из DataFrame.
    
    ПРИОРИТЕТ ИСТОЧНИКОВ:
    1. input.json (monthly_data) - если значение указано явно (не null)
    2. Кэш месячных данных (_monthly_cache) - если доступен
    3. master_df напрямую - если кэш не доступен
    4. Значение по умолчанию - если колонка отсутствует
    
    Args:
        master_df: Основной DataFrame с данными
        month: Номер месяца (1-12)
        column_name: Имя колонки для извлечения
        default: Значение по умолчанию (пустой numpy array)
    
    Returns:
        numpy.ndarray: Массив значений за указанный месяц
    
    ПРИМЕРЫ:
    - Если в input.json: "gtm_vn": 1000.0 -> вернет array([1000.0])
    - Если в input.json: "gtm_vn": [1000, 1100, ...] -> вернет array([1000, 1100, ...])
    - Если в input.json: "gtm_vn": null -> возьмет из master_df
    """
    # Проверяем input.json для месячных данных
    config = _get_input_config()
    monthly_data = config.get("monthly_data", {})
    
    if column_name in monthly_data and monthly_data[column_name] is not None:
        value = monthly_data[column_name]
        # Если это список, преобразуем в numpy array
        if isinstance(value, list):
            return np.array(value, dtype=float)
        # Если это одно число, создаем массив с одним элементом
        elif isinstance(value, (int, float)):
            return np.array([float(value)], dtype=float)
        else:
            return np.array([float(value)], dtype=float)
    
    # Используем кэш месячных данных, если он доступен (оптимизация)
    global _monthly_cache, _master_df_indexed
    if _monthly_cache is not None and month in _monthly_cache:
        month_df = _monthly_cache[month]
        if column_name in month_df.columns:
            try:
                return month_df[column_name].values
            except Exception as e:
                print(f"Ошибка при получении '{column_name}' из кэша для месяца {month}: {e}")
                return default
        else:
            # Колонка отсутствует в кэше, используем значение по умолчанию
            return default
    
    # Если кэш не доступен, используем master_df напрямую (fallback)
    # НО: если данные уже были в input.json, предупреждение не нужно
    if column_name not in master_df.columns:
        # Проверяем, были ли данные в input.json (если да, предупреждение не нужно)
        config = _get_input_config()
        monthly_data = config.get("monthly_data", {})
        if column_name not in monthly_data or monthly_data[column_name] is None:
            # Данных нет ни в input.json, ни в master_df - выводим предупреждение
            warning_key = f"missing_column_{column_name}"
            global _warning_cache
            if warning_key not in _warning_cache:
                _warning_cache.add(warning_key)
                print(f"Предупреждение: колонка '{column_name}' отсутствует в master_df. Используется значение по умолчанию: {default}")
        return default
    try:
        return master_df.loc[master_df["date"].dt.month == month, column_name].values
    except Exception as e:
        print(f"Ошибка при получении '{column_name}' для месяца {month}: {e}")
        return default


def _safe_get_day_value(master_df, date, column_name, default=0.0):
    """
    Безопасное получение дневного значения из DataFrame.
    
    ПРИОРИТЕТ ИСТОЧНИКОВ:
    1. input.json (monthly_data с массивом) - если указан массив, берет значение по индексу дня
    2. input.json (monthly_data с числом) - если указано одно число, использует для всех дней
    3. Кэшированный DataFrame (_master_df_indexed) - если доступен (оптимизация)
    4. master_df напрямую - если кэш не доступен
    5. Значение по умолчанию - если колонка отсутствует
    
    Args:
        master_df: Основной DataFrame с данными
        date: Дата для извлечения значения (datetime или Timestamp)
        column_name: Имя колонки для извлечения
        default: Значение по умолчанию (0.0)
    
    Returns:
        float: Значение за указанную дату
    
    ПРИМЕРЫ:
    - Если в input.json: "gtm_vn": [1000, 1100, 1200, ...] и date = 2025-12-03
      -> вернет 1200 (индекс 2 для дня 3)
    - Если в input.json: "gtm_vn": 1000.0 -> вернет 1000.0 для всех дней
    - Если в input.json: "gtm_vn": null -> возьмет из master_df
    """
    # Проверяем input.json для дневных данных (через monthly_data с массивом)
    config = _get_input_config()
    monthly_data = config.get("monthly_data", {})
    
    if column_name in monthly_data and monthly_data[column_name] is not None:
        value = monthly_data[column_name]
        # Если это массив, берем значение по индексу дня месяца
        if isinstance(value, list) and len(value) > 0:
            # Определяем день месяца
            if isinstance(date, pd.Timestamp):
                day_index = date.day - 1  # Индекс в массиве (0-based)
            else:
                date_obj = pd.to_datetime(date).normalize()
                day_index = date_obj.day - 1
            
            if 0 <= day_index < len(value):
                val = value[day_index]
                return float(val) if val is not None and pd.notna(val) else default
            # Если индекс выходит за границы, используем последнее значение или default
            return float(value[-1]) if value[-1] is not None and pd.notna(value[-1]) else default
        # Если это одно число, используем его для всех дней
        elif isinstance(value, (int, float)):
            return float(value)
    
    global _master_df_indexed
    
    # Используем кэшированный DataFrame с индексом, если доступен
    df_to_use = _master_df_indexed if _master_df_indexed is not None else master_df
    
    if column_name not in df_to_use.columns:
        # Проверяем, были ли данные в input.json (если да, предупреждение не нужно)
        config = _get_input_config()
        monthly_data = config.get("monthly_data", {})
        if column_name not in monthly_data or monthly_data[column_name] is None:
            # Данных нет ни в input.json, ни в master_df - выводим предупреждение
            warning_key = f"missing_column_day_{column_name}"
            global _warning_cache
            if warning_key not in _warning_cache:
                _warning_cache.add(warning_key)
                print(f"Предупреждение: колонка '{column_name}' отсутствует в master_df. Используется значение по умолчанию: {default}")
        return default
    try:
        # Нормализуем дату для сравнения
        date_normalized = pd.to_datetime(date).normalize() if not isinstance(date, pd.Timestamp) else date.normalize()
        values = df_to_use.loc[df_to_use["date"] == date_normalized, column_name].values
        if len(values) > 0:
            val = values[0]
            return float(val) if pd.notna(val) else default
        return default
    except Exception as e:
        print(f"Ошибка при получении '{column_name}' для даты {date}: {e}")
        return default


def prepare_suzun_data(master_df, n, m, prev_days, prev_month, N):
    """Собирает все аргументы, которые в оригинале передавались в calculate.suzun."""
    # --- Покупка и отгрузка ---
    G_buy_month = _safe_get_month_values(master_df, m, "buying_oil")
    G_out_udt_month = _safe_get_month_values(master_df, m, "out_udt")
    # --- GTM данные ---
    Q_vankor = _safe_get_month_values(master_df, m, "gtm_vn")
    Q_suzun = _safe_get_month_values(master_df, m, "gtm_suzun")
    Q_vslu = _safe_get_month_values(master_df, m, "gtm_vslu")
    Q_tng = _safe_get_month_values(master_df, m, "gtm_taymyr")
    Q_vo = _safe_get_month_values(master_df, m, "gtm_vostok")
    G_per_data = _safe_get_month_values(master_df, m, "per_data")
    G_suzun_vslu_data = _safe_get_month_values(master_df, m, "suzun_vslu_data")
    G_suzun_slu_data = _safe_get_month_values(master_df, m, "suzun_slu_data")
    G_suzun_data = _safe_get_month_values(master_df, m, "suzun_data")

    # --- Данные за текущий день ---
    Q_vslu_day = _safe_get_day_value(master_df, n, "gtm_vslu")
    Q_suzun_day = _safe_get_day_value(master_df, n, "gtm_suzun")
    # --- Предыдущий день ---
    V_suzun_tng_prev = _safe_get_day_value(master_df, prev_days, "suzun_tng")
    V_upn_suzun_prev = _safe_get_day_value(master_df, prev_days, "upn_suzun")
    V_suzun_vslu_prev = _safe_get_day_value(master_df, prev_days, "suzun_vslu")
    # --- Конец прошлого месяца ---
    V_suzun_tng_0 = _safe_get_day_value(master_df, prev_month, "suzun_tng")
    V_upn_suzun_0 = _safe_get_day_value(master_df, prev_month, "upn_suzun")
    V_suzun_vslu_0 = _safe_get_day_value(master_df, prev_month, "suzun_vslu")
    V_suzun_slu_prev = _safe_get_day_value(master_df, prev_days, "suzun_slu")

    return {
        "G_buy_month":G_buy_month,
        "G_out_udt_month":G_out_udt_month,
        "N":N,
        "Q_vankor":Q_vankor,
        "Q_suzun":Q_suzun,
        "Q_vslu":Q_vslu,
        "Q_tng":Q_tng,
        "Q_vo":Q_vo,
        "G_per_data":G_per_data,
        "G_suzun_vslu_data":G_suzun_vslu_data,
        "G_suzun_data":G_suzun_data,
        "G_suzun_slu_data":G_suzun_slu_data,
        "V_suzun_tng_prev":V_suzun_tng_prev,
        "Q_vslu_day":Q_vslu_day,
        "V_upn_suzun_prev":V_upn_suzun_prev,
        "V_suzun_vslu_prev":V_suzun_vslu_prev,
        "Q_suzun_day":Q_suzun_day,
        "V_upn_suzun_0":V_upn_suzun_0,
        "V_suzun_vslu_0":V_suzun_vslu_0,
        "V_suzun_tng_0":V_suzun_tng_0,
        "V_suzun_slu_prev":V_suzun_slu_prev,

    }


def prepare_vo_data(master_df, n, m):
    Q_vo_day = _safe_get_day_value(master_df, n, "gtm_vostok")
    G_upn_lodochny_ichem_data = _safe_get_month_values(master_df, m, "upn_lodochny_ichem_data")

    return {"Q_vo_day": Q_vo_day, "G_upn_lodochny_ichem_data": G_upn_lodochny_ichem_data, "m":m}


def prepare_kchng_data(master_df, n, m):
    Q_kchng = _safe_get_month_values(master_df, m, "kchng")
    Q_kchng_day = _safe_get_day_value(master_df, n, "kchng")
    G_kchng_data = _safe_get_month_values(master_df, m, "kchng_data")

    return {"Q_kchng_day":Q_kchng_day, "Q_kchng":Q_kchng, "G_kchng_data":G_kchng_data}


def prepare_lodochny_data(master_df, n, m, prev_days, prev_month, N, day, kchng_results):
    # Проверяем input.json для значений предыдущего месяца
    config = _get_input_config()
    lodochny_config = config.get("lodochny", {})
    
    # Получаем значения из master_df
    Q_tagulsk_prev_month_df = _safe_get_day_value(master_df, prev_month, "gtm_tagulsk", default=0.0)
    G_lodochni_upsv_yu_prev_month_df = _safe_get_day_value(master_df, prev_month, "lodochni_upsv_yu", default=0.0)
    
    # Используем значения из input.json, если они заданы явно (не null)
    # Иначе используем значение из master_df
    # Если значение из master_df равно 0, используем значение по умолчанию
    Q_tagulsk_prev_month = lodochny_config.get("Q_tagul_prev_month")
    if Q_tagulsk_prev_month is None:
        # Значение не задано в input.json, используем из master_df
        Q_tagulsk_prev_month = Q_tagulsk_prev_month_df
        # Если значение из master_df равно 0, используем значение по умолчанию
        if Q_tagulsk_prev_month == 0.0:
            Q_tagulsk_prev_month = 1000.0  # Значение по умолчанию
            print(f"Предупреждение: Q_tagul_prev_month из master_df равно 0, используется значение по умолчанию: {Q_tagulsk_prev_month}")
    
    G_lodochni_upsv_yu_prev_month = lodochny_config.get("G_lodochni_upsv_yu_prev_month")
    if G_lodochni_upsv_yu_prev_month is None:
        # Значение не задано в input.json, используем из master_df
        G_lodochni_upsv_yu_prev_month = G_lodochni_upsv_yu_prev_month_df
        # Если значение из master_df равно 0, используем значение по умолчанию
        if G_lodochni_upsv_yu_prev_month == 0.0:
            G_lodochni_upsv_yu_prev_month = 100.0  # Значение по умолчанию
            print(f"Предупреждение: G_lodochni_upsv_yu_prev_month из master_df равно 0, используется значение по умолчанию: {G_lodochni_upsv_yu_prev_month}")
    Q_tagulsk = _safe_get_month_values(master_df, m, "gtm_tagulsk")
    Q_lodochny = _safe_get_month_values(master_df, m, "gtm_lodochny")
    Q_lodochny_day = _safe_get_day_value(master_df, n, "gtm_lodochny")
    Q_tagulsk_day = _safe_get_day_value(master_df, n, "gtm_tagulsk")
    V_upn_lodochny_prev = _safe_get_day_value(master_df, prev_days, "upn_lodochny")
    V_ichem_prev = _safe_get_day_value(master_df, prev_days, "ichem")
    G_lodochny_ichem = _safe_get_day_value(master_df, n, "lodochny_ichem")
    V_tagul = _safe_get_day_value(master_df, n, "tagul")
    V_tagul_prev = _safe_get_day_value(master_df, prev_days, "tagul")
    G_lodochny_uspv_yu_data = _safe_get_month_values(master_df, m, "lodochny_uspv_yu_data")
    G_sikn_tagul_data = _safe_get_month_values(master_df, m, "sikn_tagul_data")
    G_tagul_data = _safe_get_month_values(master_df, m, "tagul_data")
    delte_G_tagul_data = _safe_get_month_values(master_df, m, "delte_tagul_data")
    G_lodochny_data = _safe_get_month_values(master_df, m, "lodochny_data")
    delte_G_upn_lodochny_data = _safe_get_month_values(master_df, m, "delte_upn_lodochny_data")
    G_tagul_lodochny_data = _safe_get_month_values(master_df, m, "tagul_lodochny_data")

    return {
        "Q_tagul":Q_tagulsk,
        "Q_lodochny":Q_lodochny,
        "V_upn_lodochny_prev":V_upn_lodochny_prev,
        "V_ichem_prev":V_ichem_prev,
        "G_lodochny_ichem":G_lodochny_ichem,
        "Q_tagul_prev_month":Q_tagulsk_prev_month,
        "G_lodochni_upsv_yu_prev_month":G_lodochni_upsv_yu_prev_month,
        "N":N,
        "Q_vo_day":_safe_get_day_value(master_df, n, "gtm_vostok"),
        "Q_lodochny_day":Q_lodochny_day,
        "Q_tagul_day":Q_tagulsk_day,
        "V_tagul":V_tagul,
        "V_tagul_prev":V_tagul_prev,
        "G_kchng":kchng_results.get("G_kchng", 0),
        "day":day,
        "G_lodochny_uspv_yu_data":G_lodochny_uspv_yu_data,
        "G_sikn_tagul_data":G_sikn_tagul_data,
        "G_tagul_data":G_tagul_data,
        "delte_G_tagul_data":delte_G_tagul_data,
        "G_lodochny_data":G_lodochny_data,
        "delte_G_upn_lodochny_data":delte_G_upn_lodochny_data,
        "G_tagul_lodochny_data":G_tagul_lodochny_data
    }


def prepare_cppn1_data(master_df, n, prev_days, prev_month, lodochny_results):
    flag_list = [0, 0, 0] # Для отслеживания остановки
    V_upsv_yu_0 = _safe_get_day_value(master_df, prev_month, "upsv_yu")
    V_upsv_s_0 = _safe_get_day_value(master_df, prev_month, "upsv_s")
    V_upsv_cps_0 = _safe_get_day_value(master_df, prev_month, "upsv_cps")
    V_upsv_yu_prev = _safe_get_day_value(master_df, prev_days, "upsv_yu")
    V_upsv_s_prev = _safe_get_day_value(master_df, prev_days, "upsv_s")
    V_upsv_cps_prev = _safe_get_day_value(master_df, prev_days, "upsv_cps")
    V_upsv_yu = _safe_get_day_value(master_df, n, "upsv_yu")
    V_upsv_s = _safe_get_day_value(master_df, n, "upsv_s")
    V_upsv_cps = _safe_get_day_value(master_df, n, "upsv_cps")
    V_lodochny_cps_upsv_yu_prev = _safe_get_day_value(master_df, prev_days, "lodochny_cps_upsv_yu")
    V_lodochny_upsv_yu = _safe_get_day_value(master_df, prev_days, "lodochny_upsv_yu")
    return {
        "V_upsv_yu_prev":V_upsv_yu_prev,
        "V_upsv_s_prev":V_upsv_s_prev,
        "V_upsv_cps_prev":V_upsv_cps_prev,
        "V_upsv_yu_0":V_upsv_yu_0,
        "V_upsv_s_0":V_upsv_s_0,
        "V_upsv_cps_0":V_upsv_cps_0,
        "V_upsv_yu":V_upsv_yu,
        "V_upsv_s":V_upsv_s,
        "V_upsv_cps":V_upsv_cps,
        "V_lodochny_cps_upsv_yu_prev":V_lodochny_cps_upsv_yu_prev,
        "G_sikn_tagul":lodochny_results.get("G_sikn_tagul"),
        "V_lodochny_upsv_yu":V_lodochny_upsv_yu,
        "flag_list":flag_list
    }


def prepare_rn_vankor_data(master_df, n, prev_days, N, day,m):
    F_vn = _safe_get_month_values(master_df, m, "volume_vankor")
    F_suzun_obsh = _safe_get_month_values(master_df, m, "volume_suzun")
    F_suzun_vankor = _safe_get_month_values(master_df, m, "suzun_vankor")
    V_ctn_suzun_vslu_norm = _safe_get_day_value(master_df, prev_days, "ctn_suzun_vslu_norm")
    V_ctn_suzun_vslu = _safe_get_day_value(master_df, n, "ctn_suzun_vslu")
    F_tagul_lpu = _safe_get_month_values(master_df, m, "volume_lodochny")
    F_tagul_tpu = _safe_get_month_values(master_df, m, "volume_tagulsk")
    F_skn = _safe_get_day_value(master_df, n, "skn")
    F_vo = _safe_get_month_values(master_df, m, "volume_vostok_oil")
    F_kchng = _safe_get_month_values(master_df, m, "volum_kchng")
    F_bp_data = _safe_get_month_values(master_df, m, "bp_data")
    F_bp_vn_data = _safe_get_month_values(master_df, m, "bp_vn_data")
    F_bp_suzun_data = _safe_get_month_values(master_df, m, "bp_suzun_data")
    F_bp_suzun_vankor_data = _safe_get_month_values(master_df, m, "bp_suzun_vankor_data")
    F_bp_suzun_vslu_data = _safe_get_month_values(master_df, m, "bp_suzun_vslu_data")
    F_bp_tagul_lpu_data = _safe_get_month_values(master_df, m, "bp_tagul_lpu_data")
    F_bp_tagul_tpu_data = _safe_get_month_values(master_df, m, "bp_tagul_tpu_data")
    F_bp_skn_data = _safe_get_month_values(master_df, m, "bp_skn_data")
    F_bp_vo_data = _safe_get_month_values(master_df, m, "bp_vo_data")
    F_bp_kchng_data = _safe_get_month_values(master_df, m, "bp_kchng_data")

    return {
        "F_vn":F_vn,
        "F_suzun_obsh":F_suzun_obsh,
        "F_suzun_vankor":F_suzun_vankor,
        "N":N,
        "day":day,
        "V_ctn_suzun_vslu_norm":V_ctn_suzun_vslu_norm,
        "V_ctn_suzun_vslu":V_ctn_suzun_vslu,
        "F_tagul_lpu":F_tagul_lpu,
        "F_tagul_tpu":F_tagul_tpu,
        "F_skn":F_skn,
        "F_vo":F_vo,
        "F_kchng":F_kchng,
        "F_bp_data":F_bp_data,
        "F_bp_vn_data":F_bp_vn_data,
        "F_bp_suzun_data":F_bp_suzun_data,
        "F_bp_suzun_vankor_data":F_bp_suzun_vankor_data,
        "F_bp_suzun_vslu_data":F_bp_suzun_vslu_data,
        "F_bp_tagul_lpu_data":F_bp_tagul_lpu_data,
        "F_bp_tagul_tpu_data":F_bp_tagul_tpu_data,
        "F_bp_skn_data":F_bp_skn_data,
        "F_bp_vo_data":F_bp_vo_data,
        "F_bp_kchng_data":F_bp_kchng_data,
    }
def prepare_sikn_1208_data(master_df, n, prev_days, m, suzun_results, lodochny_results, G_suzun_tng, cppn1_results):
    G_suzun_sikn_data = _safe_get_month_values(master_df, m, "suzun_sikn_data")
    G_sikn_suzun_data = _safe_get_month_values(master_df, m, "sikn_suzun_data")
    G_suzun_tng_data = _safe_get_month_values(master_df, m, "suzun_tng_data")
    G_sikn_data = _safe_get_month_values(master_df, m, "sikn_data")
    G_sikn_vankor_data = _safe_get_month_values(master_df, m, "sikn_vankor_data")
    G_skn_data = _safe_get_month_values(master_df, m, "skn_data")

    Q_vankor = _safe_get_day_value(master_df, n, "gtm_vn")
    V_upsv_yu = _safe_get_day_value(master_df, n, "upsv_yu")
    V_upsv_s = _safe_get_day_value(master_df, n, "upsv_s")
    V_upsv_cps = _safe_get_day_value(master_df, n, "upsv_cps")
    V_upsv_yu_prev = _safe_get_day_value(master_df, prev_days, "upsv_yu")
    V_upsv_s_prev = _safe_get_day_value(master_df, prev_days, "upsv_s")
    V_upsv_cps_prev = _safe_get_day_value(master_df, prev_days, "upsv_cps")
    return {
        "G_suzun_vslu": suzun_results.get("G_suzun_vslu"),
        "G_sikn_tagul_lod_data": lodochny_results.get("G_sikn_tagul_month"),
        "G_buy_day": suzun_results.get("G_buy_day"),
        "G_per": suzun_results.get("G_per"),
        "G_suzun":suzun_results.get("G_suzun"),
        "G_suzun_sikn_data":G_suzun_sikn_data,
        "G_sikn_suzun_data":G_sikn_suzun_data,
        "G_suzun_tng":G_suzun_tng,
        "G_suzun_tng_data":G_suzun_tng_data,
        "Q_vankor":Q_vankor,
        "V_upsv_yu":V_upsv_yu,
        "V_upsv_s":V_upsv_s,
        "V_upsv_cps":V_upsv_cps,
        "V_upsv_yu_prev":V_upsv_yu_prev,
        "V_upsv_s_prev":V_upsv_s_prev,
        "V_upsv_cps_prev":V_upsv_cps_prev,
        "G_lodochny_uspv_yu":lodochny_results.get("G_lodochny_uspv_yu"),
        "G_sikn_data":G_sikn_data,
        "G_sikn_vankor_data":G_sikn_vankor_data,
        "V_cppn_1":cppn1_results.get("V_cppn_1"),
        "G_skn_data":G_skn_data,
    }
def prepare_TSTN_data (master_df, n,prev_days,prev_month,m,N,sikn_1208_results,lodochny_results,kchng_results, suzun_results,G_ichem,G_suzun_tng):
    V_gnsp_0 = _safe_get_day_value(master_df, prev_month, "gnsp")
    V_nps_1_0 = _safe_get_day_value(master_df, prev_month, "nps_1")
    V_nps_2_0 = _safe_get_day_value(master_df, prev_month, "nps_2")
    V_knps_0 = _safe_get_day_value(master_df, prev_month, "knps")
    V_suzun_put_0 = _safe_get_day_value(master_df, prev_month, "suzun_put")

    V_knps_prev = _safe_get_day_value(master_df, prev_days, "knps")
    V_gnsp_prev = _safe_get_day_value(master_df, prev_days, "gnsp")
    V_nps_1_prev = _safe_get_day_value(master_df, prev_days, "nps_1")
    V_nps_2_prev = _safe_get_day_value(master_df, prev_days, "nps_2")
    V_tstn_suzun_vslu_prev = _safe_get_day_value(master_df, prev_days, "tstn_vslu")
    V_tstn_suzun_vankor_prev = _safe_get_day_value(master_df, prev_days, "tstn_suzun_vankor")
    V_tstn_suzun_prev = _safe_get_day_value(master_df, prev_days, "tstn_suzun")
    V_tstn_skn_prev = _safe_get_day_value(master_df, prev_days, "tstn_skn")
    V_tstn_vo_prev = _safe_get_day_value(master_df, prev_days, "tstn_vo")
    V_tstn_tng_prev = _safe_get_day_value(master_df, prev_days, "tstn_tng")
    V_tstn_tagul_prev = _safe_get_day_value(master_df, prev_days, "tstn_tagul")
    V_tstn_kchng_prev = _safe_get_day_value(master_df, prev_days, "tstn_kchng")
    V_tstn_lodochny_prev = _safe_get_day_value(master_df, prev_days, "tstn_lodochny")
    V_tstn_rn_vn_prev = _safe_get_day_value(master_df, prev_days, "tstn_rn_vn")

    F_kchng = _safe_get_month_values(master_df, m, "volum_kchng")
    G_gpns_data = _safe_get_month_values(master_df, m, "gpns_data")
    F_suzun_vankor = _safe_get_month_values(master_df, m, "suzun_vankor")
    F_vo = _safe_get_month_values(master_df, m, "volume_vostok_oil")
    F_tng = _safe_get_month_values(master_df, m, "volume_taymyr")
    F_tagul_lpu = _safe_get_month_values(master_df, m, "volume_lodochny")

    F_skn = _safe_get_day_value(master_df, n, "_F_skn")
    VN_min_gnsp = 2686.761
    flag_list = [0,0,0,0]
    return {
        "V_gnsp_0":V_gnsp_0,
        "N": N,
        "VN_min_gnsp":VN_min_gnsp,
        "G_sikn":sikn_1208_results.get("G_sikn"),
        "G_gpns_data":G_gpns_data,
        "V_gnsp_prev":V_gnsp_prev,
        "flag_list":flag_list,
        "V_nps_1_prev":V_nps_1_prev,
        "V_nps_2_prev":V_nps_2_prev,
        "G_tagul":lodochny_results.get("G_tagul"),
        "G_upn_lodochny":lodochny_results.get("G_upn_lodochny"),
        "G_kchng":kchng_results.get("G_kchng"),
        "V_knps_prev":V_knps_prev,
        "V_nps_1_0":V_nps_1_0,
        "V_nps_2_0":V_nps_2_0,
        "V_knps_0":V_knps_0,
        "G_suzun_vslu": suzun_results.get("G_suzun_vslu"),
        "V_tstn_suzun_vslu_prev": V_tstn_suzun_vslu_prev,
        "F_suzun_vankor":F_suzun_vankor,
        "V_tstn_suzun_vankor_prev":V_tstn_suzun_vankor_prev,
        "G_buy_day":suzun_results.get("G_buy_day"),
        "G_per":suzun_results.get("G_per"),
        "V_suzun_put_0":V_suzun_put_0,
        "V_tstn_suzun_prev":V_tstn_suzun_prev,
        "G_suzun_slu": suzun_results.get("G_suzun_slu"),
        "V_tstn_skn_prev":V_tstn_skn_prev,
        "F_skn":F_skn,
        "V_tstn_vo_prev":V_tstn_vo_prev,
        "G_ichem":G_ichem,
        "F_vo":F_vo,
        "F_tng":F_tng,
        "G_suzun_tng":G_suzun_tng,
        "V_tstn_tng_prev":V_tstn_tng_prev,
        "V_tstn_tagul_prev":V_tstn_tagul_prev,
        "F_kchng":F_kchng,
        "V_tstn_kchng_prev":V_tstn_kchng_prev,
        "V_tstn_lodochny_prev":V_tstn_lodochny_prev,
        "G_sikn_tagul":sikn_1208_results.get("G_sikn_tagul"),
        "F_tagul_lpu":F_tagul_lpu,
        "V_tstn_rn_vn_prev":V_tstn_rn_vn_prev
    }
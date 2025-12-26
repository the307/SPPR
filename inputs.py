"""
МОДУЛЬ РАБОТЫ С КОНФИГУРАЦИЕЙ input.json

Этот модуль обеспечивает централизованный доступ к конфигурации из input.json.
Все функции input() были заменены на чтение из этого файла.

ЛОГИКА РАБОТЫ:
---------------
1. _load_config() - загружает input.json:
   - Использует глобальный кэш (_config) для однократной загрузки
   - Обрабатывает ошибки чтения файла
   - Возвращает пустой словарь, если файл не найден

2. ФУНКЦИИ ПОЛУЧЕНИЯ ВХОДНЫХ ДАННЫХ:
   Каждая функция get_*_inputs() извлекает данные для соответствующего блока:
   
   - get_suzun_inputs() - параметры для блока СУЗУН
   - get_lodochny_inputs() - параметры для блока ЛОДОЧНЫЙ
   - get_cppn_1_inputs() - параметры для блока ЦППН-1
   - get_rn_vankor_inputs() - параметры для блока РН-ВАНКОР
   - get_sikn_1208_inputs() - параметры для блока СИКН-1208
   - get_TSTN_inputs() - параметры для блока ТСТН

3. ФУНКЦИИ ВАЛИДАЦИИ:
   
   - get_validation_config() - параметры автоматической валидации
   - get_manual_corrections() - значения для ручной коррекции
   - get_validation_value() - получение конкретного значения коррекции
   - get_delivery_period() - периодичность сдачи (e) для блоков

СТРУКТУРА input.json:
---------------------
{
  "suzun": { ... },           # Параметры блока СУЗУН
  "lodochny": { ... },        # Параметры блока ЛОДОЧНЫЙ
  "monthly_data": { ... },    # Месячные данные (используются в data_prep.py)
  "validation": { ... },       # Параметры валидации
  "manual_corrections": { ... } # Ручные коррекции при ошибках валидации
}

ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ:
----------------------
- Если ключ отсутствует в input.json, используется значение по умолчанию
- Если значение = null, используется значение из расчетов или master_df
"""
import json
from pathlib import Path

# Загрузка конфигурации из input.json
_config = None
_config_file = Path("input.json")

def _load_config():
    """Загружает конфигурацию из input.json."""
    global _config
    if _config is None:
        if _config_file.exists():
            try:
                with open(_config_file, 'r', encoding='utf-8') as f:
                    _config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке {_config_file}: {e}")
                _config = {}
        else:
            print(f"Файл {_config_file} не найден. Используются значения по умолчанию.")
            _config = {}
    return _config

def get_suzun_inputs():
    """Получает входные данные для блока SUZUN из input.json.
    Возвращает словарь с ключами, которые ожидает calculate.suzun.
    """
    config = _load_config()
    suzun_config = config.get("suzun", {})
    
    return {
        "G_payaha": suzun_config.get("G_payaha", 0.0),
        "G_suzun_tng": suzun_config.get("G_suzun_tng", 0.0),
        "K_g_suzun": suzun_config.get("K_g_suzun", 0.0),
        "manual_V_upn_suzun": suzun_config.get("manual_V_upn_suzun"),
        "manual_V_suzun_vslu": suzun_config.get("manual_V_suzun_vslu")
    }

def get_lodochny_inputs():
    """Получает входные данные для блока LODOCHNY из input.json."""
    config = _load_config()
    lodochny_config = config.get("lodochny", {})
    
    return {
        "G_ichem": lodochny_config.get("G_ichem", 0.0),
        "K_otkachki": lodochny_config.get("K_otkachki", 0.0),
        "K_gupn_lodochny": lodochny_config.get("K_gupn_lodochny", 0.0),
        "K_g_tagul": lodochny_config.get("K_g_tagul", 0.0),
        "manual_V_upn_lodochny": lodochny_config.get("manual_V_upn_lodochny"),
        "manual_G_sikn_tagul": lodochny_config.get("manual_G_sikn_tagul"),
        "manual_V_tagul": lodochny_config.get("manual_V_tagul"),
    }
def get_cppn_1_inputs():
    """Получает входные данные для блока CPPN_1 из input.json."""
    config = _load_config()
    cppn_config = config.get("cppn_1", {})
    
    return {
        "manual_V_upsv_yu": cppn_config.get("manual_V_upsv_yu"),
        "manual_V_upsv_s": cppn_config.get("manual_V_upsv_s"),
        "manual_V_upsv_cps": cppn_config.get("manual_V_upsv_cps"),
    }
def get_rn_vankor_inputs():
    """Получает входные данные для блока rn_vankor из input.json."""
    config = _load_config()
    rn_config = config.get("rn_vankor", {})
    
    return {
        "manual_F_bp_vn": rn_config.get("manual_F_bp_vn"),
        "manual_F_bp_suzun": rn_config.get("manual_F_bp_suzun"),
        "manual_F_bp_suzun_vankor": rn_config.get("manual_F_bp_suzun_vankor"),
        "manual_F_bp_tagul_tpu": rn_config.get("manual_F_bp_tagul_tpu"),
        "manual_F_bp_tagul_lpu": rn_config.get("manual_F_bp_tagul_lpu"),
        "manual_F_bp_skn": rn_config.get("manual_F_bp_skn"),
        "manual_F_bp_vo": rn_config.get("manual_F_bp_vo"),
        "manual_F_bp_suzun_vslu": rn_config.get("manual_F_bp_suzun_vslu"),
        "manual_F_kchng": rn_config.get("manual_F_kchng"),
    }
def get_sikn_1208_inputs():
    """Получает входные данные для блока СИКН-1208 из input.json."""
    config = _load_config()
    sikn_config = config.get("sikn_1208", {})
    
    return {
        "K_delte_g_sikn": sikn_config.get("K_delte_g_sikn", 0.0),
    }
def get_TSTN_inputs():
    """Получает входные данные для блока ТСТН из input.json."""
    config = _load_config()
    tstn_config = config.get("tstn", {})
    
    return {
        "K_suzun": tstn_config.get("K_suzun", 0.0),
        "K_vankor": tstn_config.get("K_vankor", 0.0),
        "F_suzun_vslu": tstn_config.get("F_suzun_vslu", 0.0),
        "G_skn": tstn_config.get("G_skn", 0.0),
        "K_skn": tstn_config.get("K_skn", 0.0),
        "K_ichem": tstn_config.get("K_ichem", 0.0),
        "K_payaha": tstn_config.get("K_payaha", 0.0),
        "K_tagul": tstn_config.get("K_tagul", 0.0),
        "K_lodochny": tstn_config.get("K_lodochny", 0.0),
    }

def get_validation_config():
    """Получает параметры валидации из input.json."""
    config = _load_config()
    validation_config = config.get("validation", {})
    
    return {
        "auto_accept_validation": validation_config.get("auto_accept_validation", False),
        "auto_replace_K_otkachki": validation_config.get("auto_replace_K_otkachki", False),
        "delivery_period_e_suzun_vankor": validation_config.get("delivery_period_e_suzun_vankor", 7),
        "delivery_period_e_vo": validation_config.get("delivery_period_e_vo", 7),
        "delivery_period_e_kchng": validation_config.get("delivery_period_e_kchng", 7),
    }

def get_manual_corrections():
    """Получает значения для ручной коррекции из input.json."""
    config = _load_config()
    corrections = config.get("manual_corrections", {})
    return corrections

def get_validation_value(key, default=None):
    """Получает значение для валидации из input.json.
    
    Args:
        key: ключ в разделе manual_corrections
        default: значение по умолчанию, если ключ отсутствует
    
    Returns:
        Значение из input.json или default
    """
    config = _load_config()
    corrections = config.get("manual_corrections", {})
    value = corrections.get(key, default)
    if value is not None:
        return value
    return default

def get_delivery_period(block_name):
    """Получает периодичность сдачи (e) для блока из input.json.
    
    Args:
        block_name: имя блока ("suzun_vankor", "vo", "kchng")
    
    Returns:
        Периодичность сдачи (int)
    """
    config = _load_config()
    validation = config.get("validation", {})
    key = f"delivery_period_e_{block_name}"
    return validation.get(key, 7)  # По умолчанию 7
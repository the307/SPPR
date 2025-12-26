"""
МОДУЛЬ ЭКСПОРТА РЕЗУЛЬТАТОВ В JSON

Этот модуль преобразует результаты расчетов (DataFrame) в JSON формат,
соответствующий структуре example_output.json.

ЛОГИКА РАБОТЫ:
---------------
1. МЕСЯЧНЫЕ ИТОГИ (monthly_totals):
   - Вычисляет итоговые значения за месяц для всех месячных полей
   - Для полей *_month берет последнее значение
   - Для остальных полей суммирует значения за месяц
   - Вычисляет производные поля (F_month, F_tagul_month)

2. ОБЪЕКТЫ ВАЛИДАЦИИ (validation_checks):
   - Создает объекты статуса для полей с валидацией
   - Формат: {"value": значение, "status": 0/1, "message": "текст"}
   - status: 0 = OK, 1 = предупреждение/ошибка
   - Если alarm_flag = True, устанавливает статус тревоги

3. ДАННЫЕ ПО ДНЯМ (days_data):
   - Для каждого дня создает объект с полями:
     * Обычные поля - простые значения
     * Поля со статусом - объекты {"value": ..., "status": ..., "message": ...}
   - Вычисляет производные поля (F_tagul = F_tagul_lpu + F_tagul_tpu)
   - Применяет маппинг имен полей (например, V_upsv_cps -> V_cps)

4. МАППИНГ ИМЕН ПОЛЕЙ:
   - field_mapping - для обычных полей
   - status_field_mapping - для полей со статусом
   - Позволяет изменить имена полей при экспорте

СТРУКТУРА ВЫХОДНОГО JSON:
--------------------------
{
  "G_per_month": ...,
  "Q_vankor_month": ...,
  ... (месячные итоги),
  "F_sr": {"value": ..., "status": 0, "message": ""},
  "V_vn_check": {"value": ..., "status": 0, "message": ""},
  ... (объекты валидации),
  "days": [
    {
      "date": "2025-12-01",
      "Q_vankor": 1000,
      "V_cps": {"value": 5000, "status": 0, "message": ""},
      "F_tagul": {"value": 2000, "status": 0, "message": ""},
      ... (остальные поля)
    },
    ... (остальные дни)
  ]
}

СЕРИАЛИЗАЦИЯ:
-------------
- _to_serializable() - преобразует numpy/pandas типы в стандартные Python типы
- _create_status_object() - создает объект статуса с правильной сериализацией
"""
import json
import pandas as pd
from datetime import datetime
import numpy as np


def _to_serializable(value):
    """Преобразует значение в JSON-сериализуемый формат."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime("%Y-%m-%d") if pd.notna(value) else None
    if isinstance(value, (list, np.ndarray)):
        return [_to_serializable(v) for v in value]
    return value


def _create_status_object(value, status=0, message=""):
    """Создает объект статуса для полей с валидацией."""
    return {
        "value": _to_serializable(value),
        "status": status,
        "message": message
    }


def export_to_json(
    master_df: pd.DataFrame,
    output_path: str = "output.json",
    calc_date=None,
    alarm_flag: bool = False,
    alarm_msg: str | None = None
):
    """
    Экспортирует результаты расчетов в JSON формат.
    
    ПРОЦЕСС ЭКСПОРТА:
    1. Вычисляет месячные итоги (последние значения или суммы)
    2. Создает объекты валидации (статусы проверок)
    3. Формирует данные по дням (обычные поля + поля со статусом)
    4. Вычисляет производные поля (F_tagul = F_tagul_lpu + F_tagul_tpu)
    5. Сохраняет в JSON файл
    
    Args:
        master_df: DataFrame с результатами расчетов по дням
        output_path: путь к выходному JSON файлу
        calc_date: дата расчета (необязательно, используется для определения месяца)
        alarm_flag: флаг тревоги (устанавливает статус в validation_checks)
        alarm_msg: сообщение тревоги
    
    ВЫХОДНАЯ СТРУКТУРА:
    {
      "G_per_month": ...,
      "Q_vankor_month": ...,
      ... (месячные итоги),
      "F_sr": {"value": ..., "status": 0, "message": ""},
      ... (объекты валидации),
      "days": [
        {
          "date": "2025-12-01",
          "Q_vankor": 1000,
          "V_cps": {"value": 5000, "status": 0, "message": ""},
          ...
        },
        ...
      ]
    }
    """
    
    # Получаем последний месяц из данных
    if len(master_df) == 0:
        raise ValueError("DataFrame пуст, нет данных для экспорта")
    
    master_df = master_df.copy()
    master_df["date"] = pd.to_datetime(master_df["date"])
    
    # Определяем месяц для агрегации
    last_date = master_df["date"].max()
    month = last_date.month
    year = last_date.year
    
    # Фильтруем данные за последний месяц
    month_data = master_df[master_df["date"].dt.month == month].copy()
    
    # =========================================================
    # 1. Вычисляем месячные итоги
    # =========================================================
    monthly_totals = {}
    
    # Месячные поля (суммы или последние значения)
    monthly_fields = [
        "G_per_month", "Q_vankor_month", "Q_suzun_month", "Q_vslu_month",
        "Q_tng_month", "Q_vo_month", "G_suzun_vslu_month", "G_suzun_slu_month",
        "G_suzun_month", "delta_G_suzun", "G_upn_lodochny_ichem_month",
        "Q_kchng_month", "G_kchng_month", "Q_tagulsk_month", "Q_lodochny_month",
        "K_otkachki_month", "G_lodochny_uspv_yu", "G_upn_lodochny_month",
        "G_tagul_month", "delta_G_tagul_month", "G_tagul_lodochny_month",
        "G_lodochny_month", "G_sikn_vslu_month", "G_sikn_tagul_month",
        "G_sikn_suzun_month", "G_sikn_tng_month", "G_sikn_month",
        "G_sikn_vankor_month", "G_skn_month", "delta_G_sikn_month",
        "F_suzun_vankor_month", "F_suzun_vslu_month", "F_tagul_lpu_month",
        "F_tagul_tpu_month", "F_tagul_month", "F_skn_month", "F_vo_month",
        "F_tng_month", "F_kchng_month", "F_month", "G_gnps_month"
    ]
    
    for field in monthly_fields:
        if field in month_data.columns:
            # Для месячных полей берем последнее значение или сумму
            if field.endswith("_month"):
                value = month_data[field].iloc[-1] if len(month_data) > 0 else None
            else:
                value = month_data[field].sum() if len(month_data) > 0 else None
            monthly_totals[field] = _to_serializable(value)
        else:
            # Пытаемся найти соответствующее поле F_bp_*_month
            if field.startswith("F_") and field.endswith("_month"):
                # Маппинг F_*_month -> F_bp_*_month
                bp_field = field.replace("F_", "F_bp_", 1)
                if bp_field in month_data.columns:
                    value = month_data[bp_field].iloc[-1] if len(month_data) > 0 else None
                    monthly_totals[field] = _to_serializable(value)
                else:
                    monthly_totals[field] = None
            else:
                monthly_totals[field] = None
    
    # Вычисляем F_month из F_bp_month
    if "F_bp_month" in month_data.columns:
        monthly_totals["F_month"] = _to_serializable(month_data["F_bp_month"].iloc[-1] if len(month_data) > 0 else None)
    elif "F_month" not in monthly_totals:
        monthly_totals["F_month"] = None
    
    # Вычисляем F_tagul_month из F_bp_tagul_lpu_month + F_bp_tagul_tpu_month
    if "F_bp_tagul_lpu_month" in month_data.columns and "F_bp_tagul_tpu_month" in month_data.columns:
        F_tagul_lpu_month = month_data["F_bp_tagul_lpu_month"].iloc[-1] if len(month_data) > 0 else 0
        F_tagul_tpu_month = month_data["F_bp_tagul_tpu_month"].iloc[-1] if len(month_data) > 0 else 0
        monthly_totals["F_tagul_month"] = _to_serializable(F_tagul_lpu_month + F_tagul_tpu_month)
    elif "F_tagul_month" not in monthly_totals:
        monthly_totals["F_tagul_month"] = None
    
    # =========================================================
    # 2. Создаем объекты проверок (пока без реальной логики валидации)
    # =========================================================
    validation_checks = {
        "F_sr": _create_status_object(None, 0, ""),
        "V_vn_check": _create_status_object(None, 0, ""),
        "V_suzun_check": _create_status_object(None, 0, ""),
        "V_lodochny_check": _create_status_object(None, 0, ""),
        "V_vo_check": _create_status_object(None, 0, ""),
        "V_tagul_check": _create_status_object(None, 0, ""),
        "V_vn_gtm_check": _create_status_object(None, 0, ""),
        "V_suzun_gtm_check": _create_status_object(None, 0, ""),
        "V_vo_gtm_check": _create_status_object(None, 0, ""),
        "V_lodochny_gtm_check": _create_status_object(None, 0, ""),
        "V_tagul_gtm_check": _create_status_object(None, 0, "")
    }
    
    # Если есть тревога, добавляем информацию
    if alarm_flag:
        validation_checks["F_sr"]["status"] = 1
        validation_checks["F_sr"]["message"] = alarm_msg or "Контрольное условие не выполнено"
    
    # =========================================================
    # 3. Формируем данные по дням
    # =========================================================
    days_data = []
    
    # Поля, которые должны быть в формате статуса (с маппингом имен)
    status_field_mapping = {
        "V_upsv_cps": "V_cps",  # Маппинг имени поля
        "F_bp": "F",  # Маппинг F_bp -> F
        "F_bp_vn": "F_vn",
        "F_bp_suzun": "F_suzun",
        "F_bp_suzun_vankor": "F_suzun_vankor",
        "F_bp_suzun_vslu": "F_suzun_vslu",
        "F_bp_tagul": "F_tagul",  # Если есть такое поле
        "F_bp_tagul_lpu": "F_tagul_lpu",
        "F_bp_tagul_tpu": "F_tagul_tpu",
        "F_bp_skn": "F_skn",
        "F_bp_vo": "F_vo",
        "F_bp_kchng": "F_kchng",
    }
    
    status_fields = [
            "V_upsv_yu", "V_upsv_s", "V_upsv_cps", "V_lodochny_cps_upsv_yu",
            "G_sikn_tagul", "V_upn_suzun", "V_tagul", "V_upn_lodochny",
            "V_ichem", "V_gnps", "V_nps_1", "V_nps_2", "V_knsp",
            "V_tstn_vn", "V_tstn_suzun", "V_tstn_suzun_vankor",
            "V_tstn_suzun_vslu", "V_tstn_tagul_obsh", "V_tstn_lodochny",
            "V_tstn_tagul", "V_tstn_skn", "V_tstn_vo", "V_tstn_tng",
            "V_tstn_kchng", "F_bp", "F_bp_vn", "F_bp_suzun", "F_bp_suzun_vankor",
            "F_bp_suzun_vslu", "F_bp_tagul_lpu", "F_bp_tagul_tpu",
            "F_bp_skn", "F_bp_vo", "F_bp_kchng", "Q_gnps", "Q_nps_1_2", "Q_knps"
        ]
    
    for _, row in master_df.iterrows():
        day_data = {}
        
        # Дата
        day_data["date"] = _to_serializable(row.get("date"))
        
        # Обычные поля (с маппингом имен)
        field_mapping = {
            "G_out_udt_day": "G_out_updt_day",  # Маппинг имени поля
        }
        
        regular_fields = [
            "Q_vankor", "V_cppn_1", "G_sikn", "G_sikn_vankor", "G_sikn_suzun",
            "G_sikn_vslu", "G_sikn_tng", "G_delte_sikn", "Q_suzun", "Q_vslu",
            "V_suzun_slu", "V_suzun_vslu", "V_suzun_tng", "G_suzun",
            "G_suzun_slu", "G_suzun_vslu", "G_suzun_tng", "delta_G_suzun",
            "Q_tng", "G_payaha", "G_buy_day", "G_out_udt_day", "G_per",
            "Q_tagul", "G_tagul", "delta_G_tagul", "Q_lodochny",
            "G_lodochny_uspv_yu", "V_lodochny", "G_upn_lodochny", "G_lodochny",
            "G_ichem", "delta_G_upn_lodochny", "Q_vo", "G_upn_lodochny_ichem",
            "G_tagul_lodochny", "Q_kchng", "G_kchng", "G_skn", "G_gnps",
            "V_tstn", "V_tstn_rn_vn"
        ]
        
        for field in regular_fields:
            # Используем маппинг, если есть
            output_field = field_mapping.get(field, field)
            
            if field in row:
                day_data[output_field] = _to_serializable(row[field])
            else:
                day_data[output_field] = None
        
        # F_tng, F_suzun_vslu, F_suzun_vankor - могут быть входными параметрами
        # Проверяем, есть ли они в данных (добавляем до полей со статусом, чтобы не дублировать)
        if "F_tng" not in day_data:
            day_data["F_tng"] = _create_status_object(row.get("F_tng"), 0, "") if "F_tng" in row else _create_status_object(None, 0, "")
        if "F_suzun_vslu" not in day_data:
            day_data["F_suzun_vslu"] = _create_status_object(row.get("F_suzun_vslu"), 0, "") if "F_suzun_vslu" in row else _create_status_object(None, 0, "")
        if "F_suzun_vankor" not in day_data:
            day_data["F_suzun_vankor"] = _create_status_object(row.get("F_suzun_vankor"), 0, "") if "F_suzun_vankor" in row else _create_status_object(None, 0, "")
        
        # Q_gnps, Q_nps_1_2, Q_knps - вычисляются в rn_vankor_proverka, но могут отсутствовать
        # Добавляем их, если они есть в данных
        for q_field in ["Q_gnps", "Q_nps_1_2", "Q_knps"]:
            if q_field not in day_data:
                if q_field in row:
                    day_data[q_field] = _create_status_object(row[q_field], 0, "")
                else:
                    day_data[q_field] = _create_status_object(None, 0, "")
        
        # Поля со статусом
        for field in status_fields:
            # Используем маппинг, если есть
            output_field = status_field_mapping.get(field, field)
            
            # Пропускаем, если поле уже добавлено выше
            if output_field in day_data:
                continue
            
            if field in row:
                value = row[field]
                # Определяем статус (0 = OK, 1 = предупреждение)
                status = 0
                message = ""
                
                # Здесь можно добавить логику проверки значений
                # Пока просто используем значение
                day_data[output_field] = _create_status_object(value, status, message)
            else:
                day_data[output_field] = _create_status_object(None, 0, "")
        
        # Вычисляем производные поля ПОСЛЕ добавления всех полей со статусом
        # F_tagul = F_tagul_lpu + F_tagul_tpu (из полей со статусом)
        F_tagul_lpu_val = 0
        F_tagul_tpu_val = 0
        
        # Получаем значения из полей со статусом
        if "F_tagul_lpu" in day_data:
            if isinstance(day_data["F_tagul_lpu"], dict):
                F_tagul_lpu_val = day_data["F_tagul_lpu"].get("value") or 0
            else:
                F_tagul_lpu_val = _to_serializable(day_data["F_tagul_lpu"]) or 0
        elif "F_bp_tagul_lpu" in row:
            F_tagul_lpu_val = _to_serializable(row.get("F_bp_tagul_lpu", 0)) or 0
        
        if "F_tagul_tpu" in day_data:
            if isinstance(day_data["F_tagul_tpu"], dict):
                F_tagul_tpu_val = day_data["F_tagul_tpu"].get("value") or 0
            else:
                F_tagul_tpu_val = _to_serializable(day_data["F_tagul_tpu"]) or 0
        elif "F_bp_tagul_tpu" in row:
            F_tagul_tpu_val = _to_serializable(row.get("F_bp_tagul_tpu", 0)) or 0
        
        # Вычисляем F_tagul
        F_tagul_value = (F_tagul_lpu_val if isinstance(F_tagul_lpu_val, (int, float)) else 0) + \
                      (F_tagul_tpu_val if isinstance(F_tagul_tpu_val, (int, float)) else 0)
        day_data["F_tagul"] = _create_status_object(F_tagul_value, 0, "")
        
        days_data.append(day_data)
    
    # =========================================================
    # 4. Формируем итоговую структуру
    # =========================================================
    output = {
        **monthly_totals,
        **validation_checks,
        "days": days_data
    }
    
    # =========================================================
    # 5. Сохраняем в JSON
    # =========================================================
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Результат сохранён в {output_path}")
    if alarm_flag:
        print(f"Внимание: {alarm_msg or 'Обнаружена тревога'}")


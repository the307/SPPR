import pandas as pd
from datetime import datetime, timedelta
import calendar
from typing import List, Dict, Any, Optional
from config import FILE_NAMES, DIR, EXCEL_SETTINGS
# -------------------------
# Вспомогательные функции
# -------------------------
def parse_month(raw):
    """
    Распознаёт дату формата 'Месяц, YYYY'
    Возвращает datetime(year, month, 1)
    """
    if not isinstance(raw, str):
        raw = str(raw)
    # кодировка месяцев
    month_map = {
        'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
        'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
        'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12
    }
    raw = raw.strip().lower()
    if "," in raw:
        parts = raw.split(',')
        month_name = parts[0].strip().lower()
        year = int(parts[1].strip())
        month_number = month_map.get(month_name)
        if month_number:
            return datetime(year, month_number, 1)
    try:
        return pd.to_datetime(raw, errors="coerce")
    except Exception:
        return pd.NaT
def safe_to_datetime(val):
    return pd.to_datetime(val, errors="coerce")
def ensure_list(x):
    return x if isinstance(x, list) else [x]
def get_day():
    """Возвращает список дат для текущего месяца."""
    today = datetime.now().replace(day=1)  # Первый день текущего месяца
    year, month = today.year, today.month
    total_days = calendar.monthrange(year, month)[1]
    dates = [today + timedelta(days=i) for i in range(total_days)]
    return dates
# -------------------------
# Загрузка и подготовка одного файла
# -------------------------
def load_excel(file_path: str,
               sheet_name: str,
               columns: List[int],
               skiprows: Optional[List[int]] = None,
               drop_rows: Optional[List[int]] = None,
               drop_after_rows: Optional[int] = None,
               drop_after_rows_day: Optional[bool] = False,
               transpose: bool = True,
               date_range: Optional[bool] = False) -> pd.DataFrame:
    """
    Читает Excel-лист и возвращает DataFrame с колонками: date, value
    """
    full_path = f"{DIR}/{file_path}"
    df_raw = pd.read_excel(full_path, sheet_name=sheet_name, engine='openpyxl', skiprows=skiprows)
    if transpose:
        df_raw = df_raw.transpose()
    try:
        df_plan = pd.DataFrame(columns=["date", "value"])
        df_plan[["date", "value"]] = df_raw.iloc[:, columns].copy()
    except Exception as e:
        raise ValueError(f"Ошибка выбора колонок {columns} из {file_path}: {e}")
    if date_range:
        df_plan["date"] = df_plan["date"].astype(str).apply(parse_month)
    else:
        df_plan["date"] = pd.to_datetime(df_plan["date"], errors="coerce")
    df_plan.reset_index(drop=True, inplace=True)
    if drop_rows:
        to_drop = [i for i in drop_rows if 0 <= i < len(df_plan)]
        if to_drop:
            df_plan.drop(to_drop, inplace=True)
            df_plan.reset_index(drop=True, inplace=True)
    df_plan["value"] = pd.to_numeric(df_plan["value"], errors="coerce").fillna(0)
    if drop_after_rows is not None and drop_after_rows < len(df_plan):
        df_plan = df_plan.iloc[:drop_after_rows].reset_index(drop=True)
    if drop_after_rows_day and df_plan.shape[0] > 0:
        first_date = df_plan.at[0, 'date']
        if not pd.isna(first_date):
            last_day = calendar.monthrange(first_date.year, first_date.month)[1]
            df_plan = df_plan.iloc[:last_day].reset_index(drop=True)
    return df_plan
# -------------------------
# Ручные данные (список пар в DataFrame)
# -------------------------
def data_from_pairs(pairs: List[List[Any]], param_name: str) -> pd.DataFrame:
    df = pd.DataFrame(pairs, columns=["date", "value"])
    df["date"] = safe_to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce").fillna(0)
    df["param"] = param_name
    df["source_file"] = "manual"
    return df
# -------------------------
# Основная загрузка Excel по ключу
# -------------------------
def processing_data(file_key: str) -> pd.DataFrame:
    if file_key not in EXCEL_SETTINGS:
        raise ValueError(f"Нет конфигурации для ключа: {file_key}")

    config = EXCEL_SETTINGS[file_key]
    file_list = ensure_list(getattr(FILE_NAMES, file_key))
    frames = []
    for f in file_list:
        df_single = load_excel(
            file_path=f,
            sheet_name=config.sheet_name,
            columns=config.columns,
            skiprows=config.skiprows,
            drop_rows=config.drop_rows,
            drop_after_rows=config.drop_after_rows,
            drop_after_rows_day=config.drop_after_rows_day,
            transpose=config.transpose,
            date_range=config.date_range
        )
        df_single["param"] = file_key
        df_single["source_file"] = f
        frames.append(df_single)
    if not frames:
        return pd.DataFrame(columns=["date", "value", "param", "source_file"])
    final = pd.concat(frames, ignore_index=True)
    final = final[["date", "param", "value", "source_file"]]
    final = final.sort_values("date").reset_index(drop=True)
    return final
# -------------------------
# Сборка финальной широкой таблицы
# -------------------------
def build_master_table(long_df: pd.DataFrame) -> pd.DataFrame:
    if long_df.empty:
        return pd.DataFrame()
    long_df = long_df.copy()
    long_df["date"] = pd.to_datetime(long_df["date"], errors="coerce").dt.normalize()
    pivot = long_df.pivot_table(index="date", columns="param", values="value", aggfunc="sum")
    wide = pivot.reset_index().sort_values("date").reset_index(drop=True)
    return wide
# -------------------------
# Полная сборка всех данных
# -------------------------
def build_all_data() -> pd.DataFrame:
    from manual_data import manual_dfs
    all_frames = []
    # 1. Excel
    for key in EXCEL_SETTINGS.keys():
        try:
            df_excel = processing_data(key)
            all_frames.append(df_excel)
        except Exception as e:
            print(f"Ошибка при загрузке '{key}': {e}")
    # 2. Manual
    for df in manual_dfs.values():
        all_frames.append(df)
    if not all_frames:
        return pd.DataFrame()
    combined = pd.concat(all_frames, ignore_index=True)
    master_df = build_master_table(combined)
    return master_df
"""
Оптимизированная версия data_prep.py
Основные улучшения:
1. Предфильтрация данных по месяцам
2. Универсальные функции для получения данных
3. Кэширование результатов
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from functools import lru_cache


class DataPreparator:
    """Класс для подготовки данных с оптимизацией."""
    
    def __init__(self, master_df: pd.DataFrame):
        """
        Инициализация с предобработкой данных.
        
        Args:
            master_df: Исходный DataFrame с данными
        """
        self.master_df = master_df.copy()
        self.master_df["date"] = pd.to_datetime(self.master_df["date"]).dt.normalize()
        
        # Создаем индекс по дате для быстрого доступа
        if "date" not in self.master_df.index.names:
            self.master_df = self.master_df.set_index("date")
        
        # Предфильтруем данные по месяцам
        self._monthly_cache = {}
        self._prepare_monthly_cache()
    
    def _prepare_monthly_cache(self):
        """Предварительная фильтрация данных по месяцам."""
        for month in range(1, 13):
            month_mask = self.master_df.index.month == month
            if month_mask.any():
                self._monthly_cache[month] = self.master_df[month_mask]
    
    def _get_month_data(self, month: int, columns: List[str]) -> Dict[str, np.ndarray]:
        """
        Получить месячные данные для указанных колонок.
        
        Args:
            month: Номер месяца (1-12)
            columns: Список колонок для извлечения
            
        Returns:
            Словарь с массивами значений
        """
        if month not in self._monthly_cache:
            return {col: np.array([]) for col in columns}
        
        month_df = self._monthly_cache[month]
        result = {}
        for col in columns:
            if col in month_df.columns:
                result[col] = month_df[col].values
            else:
                result[col] = np.array([])
        return result
    
    def _get_day_data(self, date: pd.Timestamp, columns: List[str]) -> Dict[str, float]:
        """
        Получить данные за конкретный день.
        
        Args:
            date: Дата
            columns: Список колонок для извлечения
            
        Returns:
            Словарь со скалярными значениями
        """
        if date not in self.master_df.index:
            return {col: 0.0 for col in columns}
        
        day_row = self.master_df.loc[date]
        result = {}
        for col in columns:
            if col in self.master_df.columns:
                value = day_row[col]
                result[col] = float(value) if pd.notna(value) else 0.0
            else:
                result[col] = 0.0
        return result
    
    def prepare_suzun_data(self, n: pd.Timestamp, prev_day: pd.Timestamp, 
                          prev_month: pd.Timestamp, N: int) -> Dict:
        """Оптимизированная подготовка данных для Сузун."""
        m = n.month
        
        # Месячные данные (одна фильтрация вместо множества)
        month_cols = [
            "buying_oil", "out_udt", "gtm_vn", "gtm_suzun", "gtm_vslu",
            "gtm_taymyr", "gtm_vostok", "per_data", "suzun_vslu_data",
            "suzun_slu_data", "suzun_data"
        ]
        month_data = self._get_month_data(m, month_cols)
        
        # Дневные данные
        day_cols = ["gtm_vslu", "gtm_suzun"]
        day_data = self._get_day_data(n, day_cols)
        
        # Данные предыдущего дня
        prev_day_cols = ["suzun_tng", "upn_suzun", "suzun_vslu", "suzun_slu"]
        prev_day_data = self._get_day_data(prev_day, prev_day_cols)
        
        # Данные конца прошлого месяца
        prev_month_cols = ["suzun_tng", "upn_suzun", "suzun_vslu"]
        prev_month_data = self._get_day_data(prev_month, prev_month_cols)
        
        # Объединяем все данные
        return {
            "G_buy_month": month_data.get("buying_oil", np.array([])),
            "G_out_udt_month": month_data.get("out_udt", np.array([])),
            "N": N,
            "Q_vankor": month_data.get("gtm_vn", np.array([])),
            "Q_suzun": month_data.get("gtm_suzun", np.array([])),
            "Q_vslu": month_data.get("gtm_vslu", np.array([])),
            "Q_tng": month_data.get("gtm_taymyr", np.array([])),
            "Q_vo": month_data.get("gtm_vostok", np.array([])),
            "G_per_data": month_data.get("per_data", np.array([])),
            "G_suzun_vslu_data": month_data.get("suzun_vslu_data", np.array([])),
            "G_suzun_data": month_data.get("suzun_data", np.array([])),
            "G_suzun_slu_data": month_data.get("suzun_slu_data", np.array([])),
            "V_suzun_tng_prev": prev_day_data.get("suzun_tng", 0.0),
            "Q_vslu_day": day_data.get("gtm_vslu", 0.0),
            "V_upn_suzun_prev": prev_day_data.get("upn_suzun", 0.0),
            "V_suzun_vslu_prev": prev_day_data.get("suzun_vslu", 0.0),
            "Q_suzun_day": day_data.get("gtm_suzun", 0.0),
            "V_upn_suzun_0": prev_month_data.get("upn_suzun", 0.0),
            "V_suzun_vslu_0": prev_month_data.get("suzun_vslu", 0.0),
            "V_suzun_tng_0": prev_month_data.get("suzun_tng", 0.0),
            "V_suzun_slu_prev": prev_day_data.get("suzun_slu", 0.0),
        }
    
    def prepare_vo_data(self, n: pd.Timestamp, m: int) -> Dict:
        """Оптимизированная подготовка данных для Восток Ойл."""
        month_data = self._get_month_data(m, ["upn_lodochny_ichem_data"])
        day_data = self._get_day_data(n, ["gtm_vostok"])
        
        return {
            "Q_vo_day": day_data.get("gtm_vostok", 0.0),
            "G_upn_lodochny_ichem_data": month_data.get("upn_lodochny_ichem_data", np.array([])),
            "m": m
        }
    
    def prepare_kchng_data(self, n: pd.Timestamp, m: int) -> Dict:
        """Оптимизированная подготовка данных для КЧНГ."""
        month_data = self._get_month_data(m, ["kchng", "kchng_data"])
        day_data = self._get_day_data(n, ["kchng"])
        
        return {
            "Q_kchng_day": day_data.get("kchng", 0.0),
            "Q_kchng": month_data.get("kchng", np.array([])),
            "G_kchng_data": month_data.get("kchng_data", np.array([]))
        }


# Пример использования:
if __name__ == "__main__":
    # Загрузка данных
    from loader import build_all_data
    
    master_df = build_all_data()
    
    # Создание оптимизированного подготовителя
    preparator = DataPreparator(master_df)
    
    # Использование
    from datetime import datetime, timedelta
    import calendar
    
    n = datetime(2025, 12, 15)
    prev_day = n - timedelta(days=1)
    prev_month = n.replace(day=1) - timedelta(days=1)
    N = calendar.monthrange(n.year, n.month)[1]
    
    suzun_data = preparator.prepare_suzun_data(n, prev_day, prev_month, N)
    print("Данные подготовлены:", list(suzun_data.keys()))


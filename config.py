"""
МОДУЛЬ КОНФИГУРАЦИИ ЗАГРУЗКИ ДАННЫХ

Этот модуль содержит настройки для загрузки Excel файлов:
- Имена файлов (FILE_NAMES)
- Настройки чтения Excel (EXCEL_SETTINGS)
- Директория с файлами (DIR)

СТРУКТУРА:
----------
1. FileConfig - dataclass для имен файлов:
   - Список файлов для каждого параметра (gtm_vn, gtm_suzun, ...)
   - Или одно имя файла (buying_oil, out_udt, ...)

2. ExcelConfig - dataclass для настроек чтения:
   - sheet_name - имя листа в Excel
   - columns - индексы колонок [date_index, value_index]
   - skiprows - строки для пропуска
   - drop_rows - строки для удаления
   - drop_after_rows - удалить все строки после указанной
   - drop_after_rows_day - удалить строки после последнего дня месяца
   - transpose - транспонировать лист
   - date_range - парсить даты как "Месяц, YYYY"

3. EXCEL_SETTINGS - словарь настроек для каждого параметра:
   - Ключ - имя параметра (gtm_vn, buying_oil, ...)
   - Значение - объект ExcelConfig с настройками

ПРИМЕР ИСПОЛЬЗОВАНИЯ:
---------------------
Для параметра "gtm_vn":
- Файлы: ["ГТМ_ВН_декабрь.XLSX", "ГТМ_ВН_ноябрь.XLSX"]
- Лист: "Сетевой график план"
- Колонки: [1, 77] (колонка 1 = дата, колонка 77 = значение)
- Удалить строки: [0, 1]
- Удалить строки после последнего дня месяца: True

ПРИМЕЧАНИЕ:
-----------
DIR указывает на директорию с Excel файлами.
При отсутствии файлов программа продолжит работу с значениями по умолчанию.
"""
import os
from datetime import datetime
from dataclasses import dataclass
date = datetime.strptime("22.05.2017", "%d.%m.%Y")
DIR = r"C:\Users\xxxxb\OneDrive\Desktop\test"
@dataclass
# для вызова
class FileConfig:
    gtm_vn: list
    gtm_suzun: list
    gtm_vslu: list
    gtm_taymyr: list
    gtm_tagulsk: list
    gtm_lodochny: list
    gtm_vostok: list
    buying_oil: str
    out_udt: str
    volume_vankor: str
    volume_suzun: str
    suzun_vankor: str
    volume_lodochny: str
    volume_tagulsk: str
    volume_vostok_oil: str
    volume_taymyr: str
@dataclass
# атрибуты для настройки
class ExcelConfig:
    sheet_name: str
    columns: list          # [date_index, fact_index]
    skiprows: list = None
    drop_rows: list = None
    drop_after_rows: int = None
    drop_after_rows_day: bool = None
    transpose: bool = True
    date_range: bool = None


# имена файлов
FILE_NAMES = FileConfig(
    gtm_vn=["ГТМ_ВН_декабрь.XLSX","ГТМ_ВН_ноябрь.XLSX"],
    gtm_suzun=["ГТМ_СУ_декабрь.XLSX","ГТМ_СУ_ноябрь.XLSX"],
    gtm_vslu=["ГТМ_ВСЛУ_декабрь.XLSX","ГТМ_ВСЛУ_ноябрь.XLSX"],
    gtm_taymyr=["ГТМ_ТНГ_декабрь.XLSX","ГТМ_ТНГ_ноябрь.XLSX"],
    gtm_tagulsk=["ГТМ_ТУ_декабрь.XLSX","ГТМ_ТУ_ноябрь.XLSX"],
    gtm_lodochny=["ГТМ_Лод_декабрь.XLSX","ГТМ_Лод_ноябрь.XLSX"],
    gtm_vostok=["ГТМ_ВО_декабрь.XLSX","ГТМ_ВО_ноябрь.XLSX"],
    buying_oil="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    out_udt="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    volume_vankor="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    volume_suzun="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    suzun_vankor="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    volume_lodochny="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    volume_tagulsk="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    volume_vostok_oil="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
    volume_taymyr="Сводная таблица нормативных параметров для Модуля 1.1.XLSX",
)
# Настройки для всех файлов
EXCEL_SETTINGS = {
    "gtm_vn": ExcelConfig(sheet_name="Сетевой график план", columns=[1, 77], drop_rows=[0, 1], drop_after_rows_day = True),
    "gtm_suzun": ExcelConfig(sheet_name="Сетевой график план", columns=[1, 77], drop_rows=[0, 1], drop_after_rows_day = True),
    "gtm_vslu": ExcelConfig(sheet_name="ВСЛУ", columns=[21, 22], drop_rows=[0,1,2], drop_after_rows_day = True),
    "gtm_taymyr": ExcelConfig(sheet_name="Сетевой график план", columns=[1, 77], drop_rows=[0,1], drop_after_rows_day = True),
    "gtm_tagulsk": ExcelConfig(sheet_name="Сетевой график план", columns=[1, 77], drop_rows=[0,1], drop_after_rows_day = True),
    "gtm_lodochny": ExcelConfig(sheet_name="Сетевой график план", columns=[1, 77], drop_rows=[0,1], drop_after_rows_day = True),
    "gtm_vostok": ExcelConfig(sheet_name="Сетевой график план", columns=[1, 77], drop_rows=[0,1], drop_after_rows_day = True),
    "buying_oil": ExcelConfig(sheet_name="Справочная информация", columns=[32, 33],drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "out_udt": ExcelConfig(sheet_name="Справочная информация", columns=[32, 34], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "volume_vankor": ExcelConfig(sheet_name="Справочная информация", columns=[0, 2], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "volume_suzun": ExcelConfig(sheet_name="Справочная информация", columns=[0, 8], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "suzun_vankor": ExcelConfig(sheet_name="Справочная информация", columns=[0, 10], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "volume_lodochny": ExcelConfig(sheet_name="Справочная информация", columns=[0, 12], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "volume_tagulsk": ExcelConfig(sheet_name="Справочная информация", columns=[0, 14], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "volume_vostok_oil": ExcelConfig(sheet_name="Справочная информация", columns=[0, 4], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
    "volume_taymyr": ExcelConfig(sheet_name="Справочная информация", columns=[0, 16], drop_rows=[0,0], drop_after_rows = 12, date_range=True),
}
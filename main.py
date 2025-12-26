"""
ГЛАВНЫЙ МОДУЛЬ ПРОЕКТА - ТОЧКА ВХОДА

Этот модуль является центральным оркестратором всего процесса расчета:
1. Загружает исходные данные из Excel и ручных источников
2. Инициализирует кэш для оптимизации производительности
3. Загружает конфигурацию из input.json
4. Выполняет расчеты по каждому дню месяца в цикле
5. Экспортирует результаты в JSON

ЛОГИКА РАБОТЫ:
---------------
1. ИСХОДНЫЕ ДАННЫЕ (build_all_data):
   - Загружает данные из Excel файлов (через loader.py)
   - Добавляет ручные данные (из manual_data.py)
   - Объединяет все в единый master_df (широкая таблица с колонками по параметрам)

2. ИНИЦИАЛИЗАЦИЯ КЭША (init_monthly_cache):
   - Предфильтрует master_df по месяцам для ускорения доступа
   - Создает индекс по дате для быстрого поиска дневных значений

3. ЗАГРУЗКА КОНФИГУРАЦИИ (inputs.py):
   - Читает параметры из input.json один раз перед циклом
   - Эти параметры используются для всех дней месяца

4. ОСНОВНОЙ ЦИКЛ ПО ДНЯМ:
   Для каждого дня месяца выполняются расчеты в следующем порядке:
   
   a) СУЗУН (calculate.suzun):
      - Расчет покупки и отгрузки нефти
      - Расчет объемов по месторождениям (Ванкор, Сузун, ВСЛУ, Таймыр, Восток Ойл)
      
   b) ВОСТОК ОЙЛ (calculate.VO):
      - Расчет объемов для Восток Ойл
      
   c) КЧНГ (calculate.kchng):
      - Расчет объемов для КЧНГ
      
   d) ЛОДОЧНЫЙ (calculate.lodochny):
      - Расчет откачки нефти Лодочного месторождения
      - Расчет коэффициента откачки
      - Расчет объемов Тагульского месторождения
      
   e) ЦППН-1 (calculate.CPPN_1):
      - Расчет наличия нефти в резервуарах УПСВ-Юг, УПСВ-Север, ЦПС
      - Валидация значений (проверка допустимых диапазонов)
      
   f) РН-ВАНКОР (calculate.rn_vankor):
      - Расчет сдачи нефти по недропользователям
      - Проверка условий для первых 10 дней месяца (alarm_flag)
      
   g) СИКН-1208 (calculate.sikn_1208):
      - Расчет откачки через СИКН-1208
      - Расчет потерь
      
   h) ТСТН (calculate.TSTN):
      - Расчет наличия нефти в резервуарах ЦТН
      - Расчет по недропользователям
      - Валидация значений

5. ЭКСПОРТ РЕЗУЛЬТАТОВ (export_to_json):
   - Формирует JSON структуру с месячными итогами
   - Добавляет данные по каждому дню
   - Создает объекты статуса для полей с валидацией

ЗАВИСИМОСТИ МЕЖДУ БЛОКАМИ:
--------------------------
- СУЗУН -> независимый (базовый блок)
- ВОСТОК ОЙЛ -> независимый
- КЧНГ -> независимый
- ЛОДОЧНЫЙ -> использует результаты КЧНГ
- ЦППН-1 -> использует результаты ЛОДОЧНОГО
- РН-ВАНКОР -> использует результаты СУЗУН
- СИКН-1208 -> использует результаты СУЗУН, ЛОДОЧНОГО, ЦППН-1
- ТСТН -> использует результаты всех предыдущих блоков

ОПТИМИЗАЦИЯ:
------------
- Кэширование месячных данных (init_monthly_cache) ускоряет доступ к данным
- Индексация по дате ускоряет поиск дневных значений
- Конфигурация загружается один раз перед циклом
"""
import pandas as pd
import calculate
from loader import build_all_data, get_day
from data_prep import (
    prepare_suzun_data,
    prepare_vo_data,
    prepare_kchng_data,
    prepare_lodochny_data,
    prepare_cppn1_data,
    prepare_rn_vankor_data,
    prepare_sikn_1208_data,
    prepare_TSTN_data,
    init_monthly_cache,
)
from inputs import (
    get_suzun_inputs,
    get_lodochny_inputs,
    get_cppn_1_inputs,
    get_rn_vankor_inputs,
    get_sikn_1208_inputs,
    get_TSTN_inputs,
)
from json_export import export_to_json
from datetime import timedelta
import calendar


def main():
    """
    Главная функция - точка входа в программу.
    
    Выполняет полный цикл расчета:
    1. Загрузка данных
    2. Инициализация кэша
    3. Загрузка конфигурации
    4. Расчеты по дням
    5. Экспорт результатов
    """
    # ------------------------------------------------------------------
    # 1. Исходные данные
    # ------------------------------------------------------------------
    master_df = build_all_data()

    if "date" not in master_df.columns:
        available_cols = list(master_df.columns)
        raise ValueError(
            f"master_df не содержит колонку 'date'. "
            f"Доступные колонки: {available_cols}"
        )

    master_df["date"] = pd.to_datetime(master_df["date"]).dt.normalize()

    # Выводим информацию о загруженных данных для диагностики
    print(f"Загружено строк: {len(master_df)}")
    print(f"Загружено колонок: {len(master_df.columns)}")
    print(f"Колонки: {list(master_df.columns)[:30]}...")  # Первые 30 колонок

    # Инициализация кэша месячных данных для оптимизации производительности
    init_monthly_cache(master_df)

    dates = get_day()
    dates = [pd.to_datetime(d).normalize() for d in dates]

    # ------------------------------------------------------------------
    # 2. Ручные вводы (ОДИН РАЗ)
    # ------------------------------------------------------------------
    suzun_inputs = get_suzun_inputs()
    lodochny_inputs = get_lodochny_inputs()
    cppn_1_inputs = get_cppn_1_inputs()
    rn_vankor_inputs = get_rn_vankor_inputs()
    sikn_1208_inputs = get_sikn_1208_inputs()
    TSTN_inputs = get_TSTN_inputs()

    # ------------------------------------------------------------------
    # 3. Аккумулятор результатов
    # ------------------------------------------------------------------
    result_rows = []

    alarm_flag = False
    alarm_msg = None

    # ------------------------------------------------------------------
    # 4. Основной цикл по дням
    # ------------------------------------------------------------------
    for n in dates:
        m = n.month
        prev_day = n - timedelta(days=1)
        prev_month = n.replace(day=1) - timedelta(days=1)
        N = calendar.monthrange(n.year, n.month)[1]

        # Словарь результатов за день
        day_result = {"date": n}

        # -------------------- СУЗУН -----------------------------------
        suzun_data = prepare_suzun_data(master_df, n, m, prev_day, prev_month, N)
        suzun_results = calculate.suzun(**suzun_data, **suzun_inputs)
        day_result.update(suzun_results)

        # -------------------- ВОСТОК ОЙЛ -------------------------------
        vo_data = prepare_vo_data(master_df, n, m)
        vo_results = calculate.VO(**vo_data)
        day_result.update(vo_results)

        # -------------------- КЧНГ -------------------------------------
        kchng_data = prepare_kchng_data(master_df, n, m)
        kchng_results = calculate.kchng(**kchng_data)
        day_result.update(kchng_results)

        # -------------------- ЛОДОЧНЫЙ ---------------------------------
        lodochny_data = prepare_lodochny_data(
            master_df, n, m, prev_day, prev_month, N, n.day, kchng_results
        )
        lodochny_results = calculate.lodochny(**lodochny_data, **lodochny_inputs)
        day_result.update(lodochny_results)

        # -------------------- ЦППН-1 -----------------------------------
        cppn1_data = prepare_cppn1_data(
            master_df, n, prev_day, prev_month, lodochny_results
        )
        cppn1_results = calculate.CPPN_1(**cppn1_data, **cppn_1_inputs)
        day_result.update(cppn1_results)

        # -------------------- РН-ВАНКОР --------------------------------
        rn_data = prepare_rn_vankor_data(master_df, n, prev_day, N, n.day, m)
        rn_results = calculate.rn_vankor(**rn_data, **rn_vankor_inputs)

        alarm_flag = rn_results.pop("__alarm_first_10_days", alarm_flag)
        alarm_msg = rn_results.pop("__alarm_first_10_days_msg", alarm_msg)
        day_result.update(rn_results)

        # -------------------- СИКН-1208 --------------------------------
        G_suzun_tng = suzun_inputs["G_suzun_tng"]
        sikn_1208_data = prepare_sikn_1208_data(
            master_df,
            n,
            m,
            prev_month,
            suzun_results,
            lodochny_results,
            G_suzun_tng,
            cppn1_results,
        )
        sikn_1208_results = calculate.sikn_1208(**sikn_1208_data, **sikn_1208_inputs)
        day_result.update(sikn_1208_results)
        # -------------------- ТСТН -------------------------------------
        G_ichem = lodochny_inputs["G_ichem"]

        TSTN_data = prepare_TSTN_data(
            master_df,
            n,
            prev_day,
            prev_month,
            m,
            N,
            sikn_1208_results,
            lodochny_results,
            kchng_results,
            suzun_results,
            G_ichem,
            G_suzun_tng,
        )
        TSTN_results = calculate.TSTN(**TSTN_data, **TSTN_inputs)
        day_result.update(TSTN_results)
        # -------------------- СОХРАНЕНИЕ ДНЯ ---------------------------
        result_rows.append(day_result)
    # ------------------------------------------------------------------
    # 5. Итоговый DataFrame
    # ------------------------------------------------------------------
    result_df = pd.DataFrame(result_rows)
    result_df.sort_values("date", inplace=True)
    result_df.reset_index(drop=True, inplace=True)
    # ------------------------------------------------------------------
    # 6. Экспорт в JSON
    # ------------------------------------------------------------------
    output_path = "output.json"
    export_to_json(
        master_df=result_df,
        output_path=output_path,
        calc_date=dates[-1] if dates else None,
        alarm_flag=alarm_flag,
        alarm_msg=alarm_msg,
    )


if __name__ == "__main__":
    main()

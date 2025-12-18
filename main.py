import pandas as pd
import numpy as np
import calculate
from loader import build_all_data, get_day
from data_prep import (
    prepare_suzun_data, prepare_vo_data, prepare_kchng_data,
    prepare_lodochny_data, prepare_cppn1_data, prepare_rn_vankor_data ,prepare_sikn_1208_data, prepare_TSTN_data
)
from inputs import get_suzun_inputs, get_lodochny_inputs, get_cppn_1_inputs, get_rn_vankor_inputs,get_sikn_1208_inputs, get_TSTN_inputs
from excel_export import export_to_excel

def assign_results_to_master(master_df, n, results):
    mask = master_df["date"] == n
    # 1. Преобразуем results в DataFrame (1 строка)
    row_df = pd.DataFrame([results])
    row_df["date"] = n
    # 2. Объединяем по колонкам
    master_df = master_df.merge(
        row_df,
        on="date",
        how="left",
        suffixes=("", "_new")
    )
    # 3. Перезаписываем значения только для текущей даты
    for col in results.keys():
        new_col = f"{col}_new"
        if new_col in master_df.columns:
            master_df.loc[mask, col] = master_df.loc[mask, new_col]
            master_df.drop(columns=[new_col], inplace=True)
    return master_df


def main():
    # Загружаем все данные
    master_df = build_all_data()
    if "date" not in master_df.columns:
        print("master_df не содержит колонки 'date' — проверь входные данные.")
        return
    master_df["date"] = pd.to_datetime(master_df["date"], errors="coerce").dt.normalize()

    # Получаем даты
    n, N, m, prev_days, prev_month, day = get_day()
    n = pd.to_datetime(n).normalize()
    prev_days = pd.to_datetime(prev_days).normalize()
    prev_month = pd.to_datetime(prev_month).normalize()

    # -------------------- СУЗУН -----------------------------------
    suzun_data = prepare_suzun_data(master_df, n, m, prev_days, prev_month, N)
    suzun_inputs = get_suzun_inputs()
    suzun_results = calculate.suzun(**suzun_data, **suzun_inputs)
    master_df = assign_results_to_master(master_df, n, suzun_results)

    # -------------------- ВОСТОК ОЙЛ -------------------------------
    vo_data = prepare_vo_data(master_df, n, m)
    vo_results = calculate.VO(**vo_data)
    master_df = assign_results_to_master(master_df, n, vo_results)

    # -------------------- КЧНГ -------------------------------------
    kchng_data = prepare_kchng_data(master_df, n, m)
    kchng_results = calculate.kchng(**kchng_data)
    master_df = assign_results_to_master(master_df, n, kchng_results)

    # -------------------- ЛОДОЧНЫЙ ---------------------------------
    # для подготовки lodochny передаём результаты kchng (нужны G_kchng)
    lodochny_data = prepare_lodochny_data(master_df, n, m, prev_days, prev_month, N, day, kchng_results)
    lodochny_inputs = get_lodochny_inputs()
    lodochny_results = calculate.lodochny(**lodochny_data, **lodochny_inputs)
    master_df = assign_results_to_master(master_df, n, lodochny_results)

    # -------------------- Блок «ЦППН-1» ----------------------------
    cppn1_data = prepare_cppn1_data(master_df, n, prev_days, prev_month, lodochny_results)
    cppn_1_inputs = get_cppn_1_inputs()
    cppn1_results = calculate.CPPN_1(**cppn1_data, **cppn_1_inputs)
    master_df = assign_results_to_master(master_df, n, cppn1_results)

    # ------------------ Блок «Сдача ООО «РН-Ванкор»: ---------------
    rn_data = prepare_rn_vankor_data(master_df, n, prev_days, N, day,m)
    rn_vankor_inputs = get_rn_vankor_inputs()
    rn_vankor_result = calculate.rn_vankor(**rn_data, **rn_vankor_inputs)
    alarm_flag = rn_vankor_result.pop("__alarm_first_10_days", False)
    alarm_msg = rn_vankor_result.pop("__alarm_first_10_days_msg", None)
    master_df = assign_results_to_master(master_df, n, rn_vankor_result)
    # -------------------- Блок «СИКН №1208» ----------------------------
    G_suzun_tng = suzun_inputs["G_suzun_tng"]
    sikn_1208_data = prepare_sikn_1208_data(master_df, n, m, prev_month, suzun_results, lodochny_results, G_suzun_tng, cppn1_results)
    sikn_1208_inputs =get_sikn_1208_inputs()
    sikn_1208_results = calculate.sikn_1208(**sikn_1208_data,**sikn_1208_inputs)
    master_df = assign_results_to_master(master_df, n, sikn_1208_results)
    # -------------------- Блок «Наличие и откачка ЦТН» ----------------------------
    G_ichem = lodochny_inputs["G_ichem"]
    G_suzun_tng = suzun_inputs["G_suzun_tng"]
    TSTN_data = prepare_TSTN_data(master_df, n,prev_days,prev_month,m,N,sikn_1208_results,lodochny_results,kchng_results,suzun_results,G_ichem,G_suzun_tng)
    TSTN_inputs = get_TSTN_inputs()
    TSTN_results = calculate.TSTN(**TSTN_data, **TSTN_inputs)
    master_df = assign_results_to_master(master_df, n, TSTN_results)
    # --- вывод результата в excel---
    output_path = "output.xlsx"
    export_to_excel(master_df=master_df, output_path=output_path, calc_date=n, alarm_flag=alarm_flag, alarm_msg=alarm_msg, month_column_name="F_bp_month"
    )


if __name__ == "__main__":
    main()
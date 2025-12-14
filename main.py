import pandas as pd
import numpy as np
import calculate
from loader import build_all_data, get_day
from data_prep import (
    prepare_suzun_data, prepare_vo_data, prepare_kchng_data,
    prepare_lodochny_data, prepare_cppn1_data
)
from inputs import get_suzun_inputs, get_lodochny_inputs

def assign_results_to_master(master_df, n, results):
    """Безопасно записывает результаты в master_df (берёт скаляр из массива)."""
    mask = master_df["date"] == n
    for k, v in results.items():
        # создаём колонку, если её нет
        if k not in master_df.columns:
            master_df[k] = np.nan
        # если v — массив numpy или список → берём первое значение
        if isinstance(v, (list, np.ndarray)):
            if len(v) > 0:
                v = float(v[0])
            else:
                v = np.nan
        master_df.loc[mask, k] = v
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
    vo_data = prepare_vo_data(master_df, n)
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
    cppn1_results = calculate.CPPN_1(**cppn1_data)
    master_df = assign_results_to_master(master_df, n, cppn1_results)

    # # ------------------ Блок «Сдача ООО «РН-Ванкор»: ---------------
    # rn_data = prepare_rn_vankor_data(master_df, n, prev_days, N, day)
    # rn_vankor_result = calculate.rn_vankor(**rn_data)
    # master_df = assign_results_to_master(master_df, n, rn_vankor_result)

    # --- вывод результата в excel---
    output_path = "output.xlsx"  # имя выходного файла
    master_df.to_excel(output_path, index=False)
    print(f"Результат сохранён в {output_path}")


if __name__ == "__main__":
    main()
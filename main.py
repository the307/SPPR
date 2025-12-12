import pandas as pd
import numpy as np
import calculate
from calculate import rn_vankor
from loader import build_all_data, get_day


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
    # вынести всю подгрузку по блокам по разным файлам
    #flag_alarm=[0,0,0,0,0,0,0,0,0,0,0,0,] – сигнализация булевый массив
    # Загружаем все данные
    master_df = build_all_data()
    master_df["date"] = pd.to_datetime(master_df["date"], errors="coerce").dt.normalize()
    # Получаем даты
    n, N, m, prev_days, prev_month,day = get_day()
    n = pd.to_datetime(n).normalize()
    prev_days = pd.to_datetime(prev_days).normalize()
    prev_month = pd.to_datetime(prev_month).normalize()

    # ===============================================================
    # -------------------- СУЗУН -----------------------------------
    # ===============================================================
    # --- Покупка и отгрузка ---
    G_buy_month = master_df.loc[master_df["date"].dt.month == m, "buying_oil"].values
    G_out_udt_month = master_df.loc[master_df["date"].dt.month == m, "out_udt"].values
    # --- GTM данные ---
    Q_vankor = master_df.loc[master_df["date"].dt.month == m, "gtm_vn"].values
    Q_suzun = master_df.loc[master_df["date"].dt.month == m, "gtm_suzun"].values
    Q_vslu = master_df.loc[master_df["date"].dt.month == m, "gtm_vslu"].values
    Q_tng = master_df.loc[master_df["date"].dt.month == m, "gtm_taymyr"].values
    Q_vo = master_df.loc[master_df["date"].dt.month == m, "gtm_vostok"].values
    # --- Ввод вручную ---
    G_payaha = float(input("Введите значение G_пайяха: "))
    G_suzun_tng = float(input("Введите значение G_сузун_тнг: "))
    # --- Данные за текущий день ---
    Q_vslu_day = master_df.loc[master_df["date"] == n, "gtm_vslu"].values
    Q_suzun_day = master_df.loc[master_df["date"] == n, "gtm_suzun"].values
    Q_vo_day = master_df.loc[master_df["date"] == n, "gtm_vostok"].values
    # --- Предыдущий день ---
    V_suzun_tng_prev = master_df.loc[master_df["date"] == prev_days, "suzun_tng"].values
    V_upn_suzun_prev = master_df.loc[master_df["date"] == prev_days, "upn_suzun"].values
    V_suzun_vslu_prev = master_df.loc[master_df["date"] == prev_days, "suzun_vslu"].values
    # --- Ручной ввод ---
    # if buttom_1:
    #     V_suzun_tng_prev = float(input("Введите V_сузун_тнг (вчера): "))
    # if buttom_2:
    #     V_upn_suzun_prev = float(input("Введите V_упн_сузун (вчера): "))
    # if buttom_3:
    #     V_suzun_vslu_prev = float(input("Введите V_сузун_вслу (вчера): "))
    # --- Конец прошлого месяца ---
    V_suzun_tng_0 = master_df.loc[master_df["date"] == prev_month, "suzun_tng"].values
    V_upn_suzun_0 = master_df.loc[master_df["date"] == prev_month, "upn_suzun"].values
    V_suzun_vslu_0 = master_df.loc[master_df["date"] == prev_month, "suzun_vslu"].values
    V_suzun_slu_prev = master_df.loc[master_df["date"] == prev_days, "suzun_slu"].values
    # --- Ручной ввод ---
    # if buttom_4:
    #     V_suzun_tng_0 = float(input("Введите V_сузун_тнг (конец прошлого месяца): "))
    # if buttom_5:
    #     V_upn_suzun_0 = float(input("Введите V_упн_сузун (конец прошлого месяца): "))
    # if buttom_6:
    #     V_suzun_vslu_0 = float(input("Введите V_сузун_вслу (конец прошлого месяца): "))
    K_g_suzun = float(input("Введите K_g_сузун: "))
    # --- Передача данных в расчет ---
    suzun_results = calculate.suzun(
        G_buy_month=G_buy_month, G_out_udt_month=G_out_udt_month,
        N=N, n=n, Q_vankor=Q_vankor, Q_suzun=Q_suzun, Q_vslu=Q_vslu,
        Q_tng=Q_tng, Q_vo=Q_vo, G_payaha=G_payaha, G_suzun_tng=G_suzun_tng,
        V_suzun_tng_prev=V_suzun_tng_prev, Q_vslu_day=Q_vslu_day, V_upn_suzun_prev=V_upn_suzun_prev,
        V_suzun_vslu_prev=V_suzun_vslu_prev, Q_suzun_day=Q_suzun_day, V_upn_suzun_0=V_upn_suzun_0,
        V_suzun_vslu_0=V_suzun_vslu_0, V_suzun_tng_0=V_suzun_tng_0, K_g_suzun=K_g_suzun, V_suzun_slu_prev=V_suzun_slu_prev
    )
    master_df = assign_results_to_master(master_df, n, suzun_results)

    # ===============================================================
    # -------------------- ВОСТОК ОЙЛ -------------------------------
    # ===============================================================
    vo_results = calculate.VO(Q_vo_day=Q_vo_day)
    master_df = assign_results_to_master(master_df, n, vo_results)

    # ===============================================================
    # -------------------- КЧНГ -------------------------------------
    # ===============================================================
    Q_kchng = master_df.loc[master_df["date"].dt.month == m, "kchng"].values if "kchng" in master_df.columns else np.array([])
    Q_kchng_day = master_df.loc[master_df["date"] == n, "kchng"].values if "kchng" in master_df.columns else np.array([])
    kchng_results = calculate.kchng(Q_kchng_day=Q_kchng_day, Q_kchng=Q_kchng)
    master_df = assign_results_to_master(master_df, n, kchng_results)

    # ===============================================================
    # -------------------- ЛОДОЧНЫЙ ---------------------------------
    # ===============================================================
    Q_tagulsk_prev_month = master_df.loc[master_df["date"].dt.month == prev_month, "gtm_tagulsk"].values
    G_lodochni_upsv_yu_prev_month = master_df.loc[master_df["date"].dt.month == prev_month, "lodochni_upsv_yu"].values
    Q_tagulsk = master_df.loc[master_df["date"].dt.month == m, "gtm_tagulsk"].values
    Q_lodochny = master_df.loc[master_df["date"].dt.month == m, "gtm_lodochny"].values
    Q_lodochny_day = master_df.loc[master_df["date"] == n, "gtm_lodochny"].values
    Q_tagulsk_day = master_df.loc[master_df["date"] == n, "gtm_tagulsk"].values
    V_upn_lodochny_prev = master_df.loc[master_df["date"] == prev_days, "upn_lodochny"].values
    # Ручной ввод
    # if buttom_7:
    #     V_upn_lodochny_prev = float(input("Введите V_упн_лодочная (вчера): "))

    G_ichem = float(input("Введите G_ичем: "))
    V_ichem_prev = master_df.loc[master_df["date"] == prev_days, "ichem"].values
    G_lodochny_ichem = master_df.loc[master_df["date"] == n, "lodochny_ichem"].values
    K_otkachki = float(input("Введите K_откачки: "))
    K_gupn_lodochny = float(input("Введите K_G_УПН_Лодочный: "))
    V_tagul = master_df.loc[master_df["date"] == n, "tagul"].values
    V_tagul_prev = master_df.loc[master_df["date"] == prev_days, "tagul"].values
    K_g_tagul = float(input("Введите K_g_tagul: "))

    lodochny_results = calculate.lodochny(
        Q_tagul=Q_tagulsk, Q_lodochny=Q_lodochny, V_upn_lodochny_prev=V_upn_lodochny_prev, G_ichem=G_ichem,
        V_ichem_prev=V_ichem_prev, G_lodochny_ichem=G_lodochny_ichem, Q_tagul_prev_month=Q_tagulsk_prev_month,
        G_lodochni_upsv_yu_prev_month=G_lodochni_upsv_yu_prev_month, K_otkachki=K_otkachki, K_gupn_lodochny=K_gupn_lodochny,
        N=N, Q_vo_day=Q_vo_day, Q_lodochny_day=Q_lodochny_day, Q_tagul_day=Q_tagulsk_day, V_tagul=V_tagul,
        V_tagul_prev=V_tagul_prev, K_g_tagul=K_g_tagul, G_kchng=kchng_results.get("G_kchng", 0), day=day
    )
    master_df = assign_results_to_master(master_df, n, lodochny_results)

    V_upsv_yu_prev = master_df.loc[master_df["date"] == prev_days, "upsv_yu"].values
    V_upsv_s_prev = master_df.loc[master_df["date"] == prev_days, "upsv_s"].values
    V_upsv_cps_prev = master_df.loc[master_df["date"] == prev_days, "upsv_cps"].values
    # Ручной ввод
    # if buttom_8:
    #     V_upsv_yu_prev = int(input("Введите значение V_УПСВ-Ю: "))
    # if buttom_9:
    #     V_upsv_s_prev = int(input("Введите значение V_УПСВ-С: "))
    # if buttom_10:
    #     V_upsv_cps_prev = int(input("Введите значение V_УПСВ-ЦПС: "))

    # ===============================================================
    # -------------------- Блок «ЦППН-1»: ---------------------------
    # ===============================================================
    flag_list = [0,0,0] # флаг остановки
    V_upsv_yu_0 = master_df.loc[master_df["date"] == prev_month, "upsv_yu"].values
    V_upsv_s_0 = master_df.loc[master_df["date"] == prev_month, "upsv_s"].values
    V_upsv_cps_0 = master_df.loc[master_df["date"] == prev_month, "upsv_cps"].values
    V_upsv_yu = master_df.loc[master_df["date"] == n, "upsv_yu"].values
    V_upsv_s = master_df.loc[master_df["date"] == n, "upsv_s"].values
    V_upsv_cps = master_df.loc[master_df["date"] == n, "upsv_cps"].values
    V_lodochny_cps_upsv_yu_prev = master_df.loc[master_df["date"] == prev_days, "lodochny_cps_upsv_yu"].values
    CPPN_1_results = calculate.CPPN_1(
        V_upsv_yu_prev=V_upsv_yu_prev, V_upsv_s_prev=V_upsv_s_prev, V_upsv_cps_prev=V_upsv_cps_prev, V_upsv_yu_0=V_upsv_yu_0,
        V_upsv_s_0=V_upsv_s_0, V_upsv_cps_0=V_upsv_cps_0, V_upsv_yu=V_upsv_yu, V_upsv_s=V_upsv_s,
        V_upsv_cps=V_upsv_cps,  flag_list=flag_list, V_lodochny_cps_upsv_yu_prev=V_lodochny_cps_upsv_yu_prev,
        G_sikn_tagul = lodochny_results.get("G_sikn_tagul", 0), G_lodochni_upsv_yu = lodochny_results.get("G_lodochni_upsv_yu", 0)
    )
    master_df = assign_results_to_master(master_df, n, CPPN_1_results)

    # ===============================================================
    # ------------------ Блок «Сдача ООО «РН-Ванкор»: ---------------
    # ===============================================================
    F_vn = master_df.loc[master_df["date"] == n, "volume_vankor"].values
    F_suzun_obsh = master_df.loc[master_df["date"] == n, "volume_suzun"].values
    F_suzun_vankor = master_df.loc[master_df["date"] == n, "suzun_vankor"].values
    # Ручной ввод
    # if buttom_11:
    #     F_bn_vn = int(input("Введите значение F_бн_вн: "))
    # if buttom_12:
    #     F_suzun = int(input("Введите значение F_suzun: "))
    # if buttom_12:
    #     F_bp_suzun_vankor = int(input("Введите значение F_bn_suzun_vankor: "))



    rn_vankor_result = calculate.rn_vankor(
        F_vn=F_vn, F_suzun_obsh=F_suzun_obsh, F_suzun_vankor=F_suzun_vankor, N=N,
    )
    # --- вывод результата в excel---
    output_path = "output.xlsx"  # имя выходного файла
    master_df.to_excel(output_path, index=False)
if __name__ == "__main__":
    main()
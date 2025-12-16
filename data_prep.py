import numpy as np
import pandas as pd

# модуль собирает все значения из master_df и формирует словари,
# которые соответствуют аргументам оригинального main.py → calculate.*


def prepare_suzun_data(master_df, n, m, prev_days, prev_month, N):
    """Собирает все аргументы, которые в оригинале передавались в calculate.suzun."""
    # --- Покупка и отгрузка ---
    G_buy_month = master_df.loc[master_df["date"].dt.month == m, "buying_oil"].values
    G_out_udt_month = master_df.loc[master_df["date"].dt.month == m, "out_udt"].values
    # --- GTM данные ---
    Q_vankor = master_df.loc[master_df["date"].dt.month == m, "gtm_vn"].values
    Q_suzun = master_df.loc[master_df["date"].dt.month == m, "gtm_suzun"].values
    Q_vslu = master_df.loc[master_df["date"].dt.month == m, "gtm_vslu"].values
    Q_tng = master_df.loc[master_df["date"].dt.month == m, "gtm_taymyr"].values
    Q_vo = master_df.loc[master_df["date"].dt.month == m, "gtm_vostok"].values
    # --- Данные за текущий день ---
    Q_vslu_day = master_df.loc[master_df["date"] == n, "gtm_vslu"].values
    Q_suzun_day = master_df.loc[master_df["date"] == n, "gtm_suzun"].values
    # --- Предыдущий день ---
    V_suzun_tng_prev = master_df.loc[master_df["date"] == prev_days, "suzun_tng"].values
    V_upn_suzun_prev = master_df.loc[master_df["date"] == prev_days, "upn_suzun"].values
    V_suzun_vslu_prev = master_df.loc[master_df["date"] == prev_days, "suzun_vslu"].values
    # --- Конец прошлого месяца ---
    V_suzun_tng_0 = master_df.loc[master_df["date"] == prev_month, "suzun_tng"].values
    V_upn_suzun_0 = master_df.loc[master_df["date"] == prev_month, "upn_suzun"].values
    V_suzun_vslu_0 = master_df.loc[master_df["date"] == prev_month, "suzun_vslu"].values
    V_suzun_slu_prev = master_df.loc[master_df["date"] == prev_days, "suzun_slu"].values

    return {
        "G_buy_month": G_buy_month,
        "G_out_udt_month": G_out_udt_month,
        "N": N,
        "Q_vankor": Q_vankor,
        "Q_suzun": Q_suzun,
        "Q_vslu": Q_vslu,
        "Q_tng": Q_tng,
        "Q_vo": Q_vo,
        "V_suzun_tng_prev": V_suzun_tng_prev,
        "Q_vslu_day": Q_vslu_day,
        "V_upn_suzun_prev": V_upn_suzun_prev,
        "V_suzun_vslu_prev": V_suzun_vslu_prev,
        "Q_suzun_day": Q_suzun_day,
        "V_upn_suzun_0": V_upn_suzun_0,
        "V_suzun_vslu_0": V_suzun_vslu_0,
        "V_suzun_tng_0": V_suzun_tng_0,
        "V_suzun_slu_prev": V_suzun_slu_prev,

    }


def prepare_vo_data(master_df, n):
    Q_vo_day = master_df.loc[master_df["date"] == n, "gtm_vostok"].values
    return {"Q_vo_day": Q_vo_day}


def prepare_kchng_data(master_df, n, m):
    Q_kchng = master_df.loc[master_df["date"].dt.month == m, "kchng"].values if "kchng" in master_df.columns else np.array([])
    Q_kchng_day = master_df.loc[master_df["date"] == n, "kchng"].values if "kchng" in master_df.columns else np.array([])
    return {"Q_kchng_day": Q_kchng_day, "Q_kchng": Q_kchng}


def prepare_lodochny_data(master_df, n, m, prev_days, prev_month, N, day, kchng_results):
    # Внимание: в оригинальном main иногда использовался prev_month как дата/месяц — воспроизводим точно
    Q_tagulsk_prev_month = master_df.loc[master_df["date"] == prev_month, "gtm_tagulsk"].values
    G_lodochni_upsv_yu_prev_month = master_df.loc[master_df["date"] == prev_month, "lodochni_upsv_yu"].values
    Q_tagulsk = master_df.loc[master_df["date"].dt.month == m, "gtm_tagulsk"].values
    Q_lodochny = master_df.loc[master_df["date"].dt.month == m, "gtm_lodochny"].values
    Q_lodochny_day = master_df.loc[master_df["date"] == n, "gtm_lodochny"].values
    Q_tagulsk_day = master_df.loc[master_df["date"] == n, "gtm_tagulsk"].values
    V_upn_lodochny_prev = master_df.loc[master_df["date"] == prev_days, "upn_lodochny"].values
    V_ichem_prev = master_df.loc[master_df["date"] == prev_days, "ichem"].values
    G_lodochny_ichem = master_df.loc[master_df["date"] == n, "lodochny_ichem"].values
    V_tagul = master_df.loc[master_df["date"] == n, "tagul"].values
    V_tagul_prev = master_df.loc[master_df["date"] == prev_days, "tagul"].values

    return {
        "Q_tagul": Q_tagulsk,
        "Q_lodochny": Q_lodochny,
        "V_upn_lodochny_prev": V_upn_lodochny_prev,
        "V_ichem_prev": V_ichem_prev,
        "G_lodochny_ichem": G_lodochny_ichem,
        "Q_tagul_prev_month": Q_tagulsk_prev_month,
        "G_lodochni_upsv_yu_prev_month": G_lodochni_upsv_yu_prev_month,
        "N": N,
        "Q_vo_day": master_df.loc[master_df["date"] == n, "gtm_vostok"].values,
        "Q_lodochny_day": Q_lodochny_day,
        "Q_tagul_day": Q_tagulsk_day,
        "V_tagul": V_tagul,
        "V_tagul_prev": V_tagul_prev,
        "G_kchng": kchng_results.get("G_kchng", 0),
        "day": day
    }


def prepare_cppn1_data(master_df, n, prev_days, prev_month, lodochny_results):
    flag_list = [0, 0, 0] # Для отслеживания остановки
    V_upsv_yu_0 = master_df.loc[master_df["date"] == prev_month, "upsv_yu"].values
    V_upsv_s_0 = master_df.loc[master_df["date"] == prev_month, "upsv_s"].values
    V_upsv_cps_0 = master_df.loc[master_df["date"] == prev_month, "upsv_cps"].values
    V_upsv_yu_prev = master_df.loc[master_df["date"] == prev_days, "upsv_yu"].values
    V_upsv_s_prev = master_df.loc[master_df["date"] == prev_days, "upsv_s"].values
    V_upsv_cps_prev = master_df.loc[master_df["date"] == prev_days, "upsv_cps"].values
    V_upsv_yu = master_df.loc[master_df["date"] == n, "upsv_yu"].values
    V_upsv_s = master_df.loc[master_df["date"] == n, "upsv_s"].values
    V_upsv_cps = master_df.loc[master_df["date"] == n, "upsv_cps"].values
    V_lodochny_cps_upsv_yu_prev = master_df.loc[master_df["date"] == prev_days, "lodochny_cps_upsv_yu"].values

    return {
        "V_upsv_yu_prev": V_upsv_yu_prev,
        "V_upsv_s_prev": V_upsv_s_prev,
        "V_upsv_cps_prev": V_upsv_cps_prev,
        "V_upsv_yu_0": V_upsv_yu_0,
        "V_upsv_s_0": V_upsv_s_0,
        "V_upsv_cps_0": V_upsv_cps_0,
        "V_upsv_yu": V_upsv_yu,
        "V_upsv_s": V_upsv_s,
        "V_upsv_cps": V_upsv_cps,
        "V_lodochny_cps_upsv_yu_prev": V_lodochny_cps_upsv_yu_prev,
        "G_sikn_tagul": lodochny_results.get("G_sikn_tagul", 0),
        "G_lodochni_upsv_yu": lodochny_results.get("G_lodochni_upsv_yu", 0),
        "flag_list": flag_list
    }


def prepare_rn_vankor_data(master_df, n, prev_days, N, day,m):
    F_vn = master_df.loc[master_df["date"].dt.month == m, "volume_vankor"].values
    F_suzun_obsh = master_df.loc[master_df["date"].dt.month == m, "volume_suzun"].values
    F_suzun_vankor = master_df.loc[master_df["date"].dt.month == m, "suzun_vankor"].values
    V_ctn_suzun_vslu_norm = master_df.loc[master_df["date"] == prev_days, "ctn_suzun_vslu_norm"].values
    V_ctn_suzun_vslu = master_df.loc[master_df["date"] == n, "ctn_suzun_vslu"].values
    F_tagul_lpu = master_df.loc[master_df["date"].dt.month == m, "volume_lodochny"].values
    F_tagul_tpu = master_df.loc[master_df["date"].dt.month == m, "volume_tagulsk"].values
    F_skn = master_df.loc[master_df["date"] == n, "skn"].values
    F_vo = master_df.loc[master_df["date"].dt.month == m, "volume_vostok_oil"].values

    return {
        "F_vn": F_vn,
        "F_suzun_obsh": F_suzun_obsh,
        "F_suzun_vankor": F_suzun_vankor,
        "N": N,
        "day": day,
        "V_ctn_suzun_vslu_norm": V_ctn_suzun_vslu_norm,
        "V_ctn_suzun_vslu": V_ctn_suzun_vslu,
        "F_tagul_lpu": F_tagul_lpu,
        "F_tagul_tpu": F_tagul_tpu,
        "F_skn": F_skn,
        "F_vo": F_vo
    }
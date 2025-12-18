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
    G_per_data = master_df.loc[master_df["date"].dt.month == m, "per_data"].values
    G_suzun_vslu_data = master_df.loc[master_df["date"].dt.month == m, "suzun_vslu_data"].values
    G_suzun_slu_data = master_df.loc[master_df["date"].dt.month == m, "suzun_slu_data"].values
    G_suzun_data = master_df.loc[master_df["date"].dt.month == m, "suzun_data"].values

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
        "G_buy_month":G_buy_month,
        "G_out_udt_month":G_out_udt_month,
        "N":N,
        "Q_vankor":Q_vankor,
        "Q_suzun":Q_suzun,
        "Q_vslu":Q_vslu,
        "Q_tng":Q_tng,
        "Q_vo":Q_vo,
        "G_per_data":G_per_data,
        "G_suzun_vslu_data":G_suzun_vslu_data,
        "G_suzun_data":G_suzun_data,
        "G_suzun_slu_data":G_suzun_slu_data,
        "V_suzun_tng_prev":V_suzun_tng_prev,
        "Q_vslu_day":Q_vslu_day,
        "V_upn_suzun_prev":V_upn_suzun_prev,
        "V_suzun_vslu_prev":V_suzun_vslu_prev,
        "Q_suzun_day":Q_suzun_day,
        "V_upn_suzun_0":V_upn_suzun_0,
        "V_suzun_vslu_0":V_suzun_vslu_0,
        "V_suzun_tng_0":V_suzun_tng_0,
        "V_suzun_slu_prev":V_suzun_slu_prev,

    }


def prepare_vo_data(master_df, n, m):
    Q_vo_day = master_df.loc[master_df["date"] == n, "gtm_vostok"].values
    G_upn_lodochny_ichem_data = master_df.loc[master_df["date"].dt.month == m, "upn_lodochny_ichem_data"].values

    return {"Q_vo_day": Q_vo_day, "G_upn_lodochny_ichem_data": G_upn_lodochny_ichem_data, "m":m}


def prepare_kchng_data(master_df, n, m):
    Q_kchng = master_df.loc[master_df["date"].dt.month == m, "kchng"].values if "kchng" in master_df.columns else np.array([])
    Q_kchng_day = master_df.loc[master_df["date"] == n, "kchng"].values if "kchng" in master_df.columns else np.array([])
    G_kchng_data = master_df.loc[master_df["date"].dt.month == m, "kchng_data"].values

    return {"Q_kchng_day":Q_kchng_day, "Q_kchng":Q_kchng, "G_kchng_data":G_kchng_data}


def prepare_lodochny_data(master_df, n, m, prev_days, prev_month, N, day, kchng_results):
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
    G_lodochny_uspv_yu_data = master_df.loc[master_df["date"].dt.month == m, "lodochny_uspv_yu_data"].values
    G_sikn_tagul_data = master_df.loc[master_df["date"].dt.month == m, "sikn_tagul_data"].values
    G_tagul_data = master_df.loc[master_df["date"].dt.month == m, "tagul_data"].values
    delte_G_tagul_data = master_df.loc[master_df["date"].dt.month == m, "delte_tagul_data"].values
    G_lodochny_data = master_df.loc[master_df["date"].dt.month == m, "lodochny_data"].values
    delte_G_upn_lodochny_data = master_df.loc[master_df["date"].dt.month == m, "delte_upn_lodochny_data"].values
    G_tagul_lodochny_data = master_df.loc[master_df["date"].dt.month == m, "tagul_lodochny_data"].values

    return {
        "Q_tagul":Q_tagulsk,
        "Q_lodochny":Q_lodochny,
        "V_upn_lodochny_prev":V_upn_lodochny_prev,
        "V_ichem_prev":V_ichem_prev,
        "G_lodochny_ichem":G_lodochny_ichem,
        "Q_tagul_prev_month":Q_tagulsk_prev_month,
        "G_lodochni_upsv_yu_prev_month":G_lodochni_upsv_yu_prev_month,
        "N":N,
        "Q_vo_day":master_df.loc[master_df["date"] == n, "gtm_vostok"].values,
        "Q_lodochny_day":Q_lodochny_day,
        "Q_tagul_day":Q_tagulsk_day,
        "V_tagul":V_tagul,
        "V_tagul_prev":V_tagul_prev,
        "G_kchng":kchng_results.get("G_kchng", 0),
        "day":day,
        "G_lodochny_uspv_yu_data":G_lodochny_uspv_yu_data,
        "G_sikn_tagul_data":G_sikn_tagul_data,
        "G_tagul_data":G_tagul_data,
        "delte_G_tagul_data":delte_G_tagul_data,
        "G_lodochny_data":G_lodochny_data,
        "delte_G_upn_lodochny_data":delte_G_upn_lodochny_data,
        "G_tagul_lodochny_data":G_tagul_lodochny_data
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
    V_lodochny_upsv_yu = master_df.loc[master_df["date"] == prev_days, "lodochny_upsv_yu"].values
    return {
        "V_upsv_yu_prev":V_upsv_yu_prev,
        "V_upsv_s_prev":V_upsv_s_prev,
        "V_upsv_cps_prev":V_upsv_cps_prev,
        "V_upsv_yu_0":V_upsv_yu_0,
        "V_upsv_s_0":V_upsv_s_0,
        "V_upsv_cps_0":V_upsv_cps_0,
        "V_upsv_yu":V_upsv_yu,
        "V_upsv_s":V_upsv_s,
        "V_upsv_cps":V_upsv_cps,
        "V_lodochny_cps_upsv_yu_prev":V_lodochny_cps_upsv_yu_prev,
        "G_sikn_tagul":lodochny_results.get("G_sikn_tagul"),
        "V_lodochny_upsv_yu":V_lodochny_upsv_yu,
        "flag_list":flag_list
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
    F_kchng = master_df.loc[master_df["date"].dt.month == m, "volum_kchng"].values
    F_bp_data = master_df.loc[master_df["date"].dt.month == m, "bp_data"].values
    F_bp_vn_data = master_df.loc[master_df["date"].dt.month == m, "bp_vn_data"].values
    F_bp_suzun_data = master_df.loc[master_df["date"].dt.month == m, "bp_suzun_data"].values
    F_bp_suzun_vankor_data = master_df.loc[master_df["date"].dt.month == m, "bp_suzun_vankor_data"].values
    F_bp_suzun_vslu_data = master_df.loc[master_df["date"].dt.month == m, "bp_suzun_vslu_data"].values
    F_bp_tagul_lpu_data = master_df.loc[master_df["date"].dt.month == m, "bp_tagul_lpu_data"].values
    F_bp_tagul_tpu_data = master_df.loc[master_df["date"].dt.month == m, "bp_tagul_tpu_data"].values
    F_bp_skn_data = master_df.loc[master_df["date"].dt.month == m, "bp_skn_data"].values
    F_bp_vo_data = master_df.loc[master_df["date"].dt.month == m, "bp_vo_data"].values
    F_bp_kchng_data = master_df.loc[master_df["date"].dt.month == m, "bp_kchng_data"].values

    return {
        "F_vn":F_vn,
        "F_suzun_obsh":F_suzun_obsh,
        "F_suzun_vankor":F_suzun_vankor,
        "N":N,
        "day":day,
        "V_ctn_suzun_vslu_norm":V_ctn_suzun_vslu_norm,
        "V_ctn_suzun_vslu":V_ctn_suzun_vslu,
        "F_tagul_lpu":F_tagul_lpu,
        "F_tagul_tpu":F_tagul_tpu,
        "F_skn":F_skn,
        "F_vo":F_vo,
        "F_kchng":F_kchng,
        "F_bp_data":F_bp_data,
        "F_bp_vn_data":F_bp_vn_data,
        "F_bp_suzun_data":F_bp_suzun_data,
        "F_bp_suzun_vankor_data":F_bp_suzun_vankor_data,
        "F_bp_suzun_vslu_data":F_bp_suzun_vslu_data,
        "F_bp_tagul_lpu_data":F_bp_tagul_lpu_data,
        "F_bp_tagul_tpu_data":F_bp_tagul_tpu_data,
        "F_bp_skn_data":F_bp_skn_data,
        "F_bp_vo_data":F_bp_vo_data,
        "F_bp_kchng_data":F_bp_kchng_data,
    }
def prepare_sikn_1208_data(master_df, n, prev_days, m, suzun_results, lodochny_results, G_suzun_tng, cppn1_results):
    G_suzun_sikn_data = master_df.loc[master_df["date"].dt.month == m, "suzun_sikn_data"].values
    G_sikn_suzun_data = master_df.loc[master_df["date"].dt.month == m, "sikn_suzun_data"].values
    G_suzun_tng_data = master_df.loc[master_df["date"].dt.month == m, "suzun_tng_data"].values
    G_sikn_data = master_df.loc[master_df["date"].dt.month == m, "sikn_data"].values
    G_sikn_vankor_data = master_df.loc[master_df["date"].dt.month == m, "sikn_vankor_data"].values
    G_skn_data = master_df.loc[master_df["date"].dt.month == m, "skn_data"].values

    Q_vankor = master_df.loc[master_df["date"] == n, "gtm_vn"].values
    V_upsv_yu = master_df.loc[master_df["date"] == n, "upsv_yu"].values
    V_upsv_s = master_df.loc[master_df["date"] == n, "upsv_s"].values
    V_upsv_cps = master_df.loc[master_df["date"] == n, "upsv_cps"].values
    V_upsv_yu_prev = master_df.loc[master_df["date"] == prev_days, "upsv_yu"].values
    V_upsv_s_prev = master_df.loc[master_df["date"] == prev_days, "upsv_s"].values
    V_upsv_cps_prev = master_df.loc[master_df["date"] == prev_days, "upsv_cps"].values
    return {
        "G_suzun_vslu": suzun_results.get("G_suzun_vslu"),
        "G_sikn_tagul_lod_data": lodochny_results.get("G_sikn_tagul_month"),
        "G_buy_day": suzun_results.get("G_buy_day"),
        "G_per": suzun_results.get("G_per"),
        "G_suzun":suzun_results.get("G_suzun"),
        "G_suzun_sikn_data":G_suzun_sikn_data,
        "G_sikn_suzun_data":G_sikn_suzun_data,
        "G_suzun_tng":G_suzun_tng,
        "G_suzun_tng_data":G_suzun_tng_data,
        "Q_vankor":Q_vankor,
        "V_upsv_yu":V_upsv_yu,
        "V_upsv_s":V_upsv_s,
        "V_upsv_cps":V_upsv_cps,
        "V_upsv_yu_prev":V_upsv_yu_prev,
        "V_upsv_s_prev":V_upsv_s_prev,
        "V_upsv_cps_prev":V_upsv_cps_prev,
        "G_lodochny_uspv_yu":lodochny_results.get("G_lodochny_uspv_yu"),
        "G_sikn_data":G_sikn_data,
        "G_sikn_vankor_data":G_sikn_vankor_data,
        "V_cppn_1":cppn1_results.get("V_cppn_1"),
        "G_skn_data":G_skn_data,
    }
def prepare_TSTN_data (master_df, n,prev_days,prev_month,m,N,sikn_1208_results,lodochny_results,kchng_results, suzun_results,G_ichem,G_suzun_tng):
    V_gnsp_0 = master_df.loc[master_df["date"] == prev_month, "gnsp"].values
    V_nps_1_0 = master_df.loc[master_df["date"] == prev_month, "nps_1"].values
    V_nps_2_0 = master_df.loc[master_df["date"] == prev_month, "nps_2"].values
    V_knps_0 = master_df.loc[master_df["date"] == prev_month, "knps"].values
    V_suzun_put_0 = master_df.loc[master_df["date"] == prev_month, "suzun_put"].values

    V_knps_prev = master_df.loc[master_df["date"] == prev_days, "knps"].values
    V_gnsp_prev = master_df.loc[master_df["date"] == prev_days, "gnsp"].values
    V_nps_1_prev = master_df.loc[master_df["date"] == prev_days, "nps_1"].values
    V_nps_2_prev = master_df.loc[master_df["date"] == prev_days, "nps_2"].values
    V_tstn_suzun_vslu_prev = master_df.loc[master_df["date"] == prev_days, "tstn_vslu"].values
    V_tstn_suzun_vankor_prev = master_df.loc[master_df["date"] == prev_days, "tstn_suzun_vankor"].values
    V_tstn_suzun_prev = master_df.loc[master_df["date"] == prev_days, "tstn_suzun"].values
    V_tstn_skn_prev = master_df.loc[master_df["date"] == prev_days, "tstn_skn"].values
    V_tstn_vo_prev = master_df.loc[master_df["date"] == prev_days, "tstn_vo"].values
    V_tstn_tng_prev = master_df.loc[master_df["date"] == prev_days, "tstn_tng"].values
    V_tstn_tagul_prev = master_df.loc[master_df["date"] == prev_days, "tstn_tagul"].values
    V_tstn_kchng_prev = master_df.loc[master_df["date"] == prev_days, "tstn_kchng"].values
    V_tstn_lodochny_prev = master_df.loc[master_df["date"] == prev_days, "tstn_lodochny"].values
    V_tstn_rn_vn_prev = master_df.loc[master_df["date"] == prev_days, "tstn_rn_vn"].values

    F_kchng = master_df.loc[master_df["date"].dt.month == m, "volum_kchng"].values
    G_gpns_data = master_df.loc[master_df["date"].dt.month == m, "gpns_data"].values
    F_suzun_vankor = master_df.loc[master_df["date"].dt.month == m, "suzun_vankor"].values
    F_vo = master_df.loc[master_df["date"].dt.month == m, "volume_vostok_oil"].values
    F_tng = master_df.loc[master_df["date"].dt.month == m, "volume_taymyr"].values
    F_tagul_lpu = master_df.loc[master_df["date"].dt.month == m, "volume_lodochny"].values

    F_skn = master_df.loc[master_df["date"]== n, "_F_skn"].values
    VN_min_gnsp = 2686.761
    flag_list = [0,0,0,0]
    return {
        "V_gnsp_0":V_gnsp_0,
        "N": N,
        "VN_min_gnsp":VN_min_gnsp,
        "G_sikn":sikn_1208_results.get("G_sikn"),
        "G_gpns_data":G_gpns_data,
        "V_gnsp_prev":V_gnsp_prev,
        "flag_list":flag_list,
        "V_nps_1_prev":V_nps_1_prev,
        "V_nps_2_prev":V_nps_2_prev,
        "G_tagul":lodochny_results.get("G_tagul"),
        "G_upn_lodochny":lodochny_results.get("G_upn_lodochny"),
        "G_kchng":kchng_results.get("G_kchng"),
        "V_knps_prev":V_knps_prev,
        "V_nps_1_0":V_nps_1_0,
        "V_nps_2_0":V_nps_2_0,
        "V_knps_0":V_knps_0,
        "G_suzun_vslu": suzun_results.get("G_suzun_vslu"),
        "V_tstn_suzun_vslu_prev": V_tstn_suzun_vslu_prev,
        "F_suzun_vankor":F_suzun_vankor,
        "V_tstn_suzun_vankor_prev":V_tstn_suzun_vankor_prev,
        "G_buy_day":suzun_results.get("G_buy_day"),
        "G_per":suzun_results.get("G_per"),
        "V_suzun_put_0":V_suzun_put_0,
        "V_tstn_suzun_prev":V_tstn_suzun_prev,
        "G_suzun_slu": suzun_results.get("G_suzun_slu"),
        "V_tstn_skn_prev":V_tstn_skn_prev,
        "F_skn":F_skn,
        "V_tstn_vo_prev":V_tstn_vo_prev,
        "G_ichem":G_ichem,
        "F_vo":F_vo,
        "F_tng":F_tng,
        "G_suzun_tng":G_suzun_tng,
        "V_tstn_tng_prev":V_tstn_tng_prev,
        "V_tstn_tagul_prev":V_tstn_tagul_prev,
        "F_kchng":F_kchng,
        "V_tstn_kchng_prev":V_tstn_kchng_prev,
        "V_tstn_lodochny_prev":V_tstn_lodochny_prev,
        "G_sikn_tagul":sikn_1208_results.get("G_sikn_tagul"),
        "F_tagul_lpu":F_tagul_lpu,
        "V_tstn_rn_vn_prev":V_tstn_rn_vn_prev
    }
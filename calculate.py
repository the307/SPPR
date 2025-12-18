import numpy as np
def _to_float(val):
    """Безопасное извлечение скаляра из массива."""
    if isinstance(val, (list, np.ndarray)):
        if len(val) == 0:
            return 0.0
        return float(val[0])
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0
# ===============================================================
# -------------------- СУЗУН -----------------------------------
# ===============================================================
def suzun(
    G_buy_month, G_out_udt_month, N, Q_vankor, Q_suzun, Q_vslu, Q_tng, Q_vo, G_payaha,
    G_suzun_tng, V_suzun_tng_prev, Q_vslu_day, V_upn_suzun_prev, V_suzun_vslu_prev, Q_suzun_day,
    V_upn_suzun_0, V_suzun_vslu_0, V_suzun_tng_0, K_g_suzun, V_suzun_slu_prev, manual_V_upn_suzun, manual_V_suzun_vslu,G_per_data,
    G_suzun_vslu_data,G_suzun_slu_data,G_suzun_data
):
    # Приведение всех данных к скалярам
    G_buy_month = _to_float(G_buy_month)
    G_out_udt_month = _to_float(G_out_udt_month)
    Q_vankor = np.array(Q_vankor, dtype=float)
    Q_suzun = np.array(Q_suzun, dtype=float)
    Q_vslu = np.array(Q_vslu, dtype=float)
    Q_tng = np.array(Q_tng, dtype=float)
    Q_vo = np.array(Q_vo, dtype=float)
    G_per_data = np.array(G_per_data , dtype=float)
    G_suzun_vslu_data = np.array(G_suzun_vslu_data, dtype=float)
    G_suzun_slu_data = np.array(G_suzun_slu_data, dtype=float)
    G_suzun_data = np.array(G_suzun_data, dtype=float)

    Q_vslu_day = _to_float(Q_vslu_day)
    Q_suzun_day = _to_float(Q_suzun_day)
    V_suzun_tng_prev = _to_float(V_suzun_tng_prev)
    V_upn_suzun_prev = _to_float(V_upn_suzun_prev)
    V_suzun_vslu_prev = _to_float(V_suzun_vslu_prev)
    V_upn_suzun_0 = _to_float(V_upn_suzun_0)
    V_suzun_vslu_0 = _to_float(V_suzun_vslu_0)
    V_suzun_tng_0 = _to_float(V_suzun_tng_0)
    V_suzun_slu_prev = _to_float(V_suzun_slu_prev)

    N = int(N) if N else 1.0

    # --- 1. Суточное значение покупки нефти
    G_buy_day = G_buy_month / N
    # --- 2. Суточный выход с УПДТ
    G_out_udt_day = G_out_udt_month / N

    # --- 3. Расход на переработку (Gпер)
    G_per = G_buy_day - G_out_udt_day
    print(G_per)
    G_per_month = sum(G_per_data)+G_per # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 4–8. Суммарные месячные значения
    Q_vankor_month = Q_vankor.sum()
    Q_suzun_month = Q_suzun.sum()
    Q_vslu_month = Q_vslu.sum()
    Q_tng_month = Q_tng.sum()
    Q_vo_month = Q_vo.sum()

    # --- 9. Наличие нефти Таймыр в РП УПН Сузун
    V_suzun_tng = G_payaha + V_suzun_tng_prev - G_suzun_tng

    # --- 10. Откачка нефти Сузун (ВСЛУ)
    G_suzun_vslu = Q_vslu_day
    G_suzun_vslu_month = sum(G_suzun_vslu_data)+G_suzun_vslu # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 11–12. Наличие нефти
    if manual_V_upn_suzun is not None:
        V_upn_suzun = manual_V_upn_suzun
    else:
        V_upn_suzun = V_upn_suzun_prev
    if manual_V_suzun_vslu is not None:
        V_suzun_vslu = manual_V_suzun_vslu
    else:
        V_suzun_vslu = V_suzun_vslu_prev + Q_vslu_day - G_suzun_vslu

    # --- 13. Расчёт наличия нефти (СЛУ)
    V_suzun_slu_0 = V_upn_suzun_0 - V_suzun_vslu_0 - V_suzun_tng_0
    V_suzun_slu = V_upn_suzun - V_suzun_vslu - V_suzun_tng

    # --- 14. Откачка нефти Сузун (СЛУ)
    G_suzun_slu = Q_suzun_day - Q_vslu_day - (V_suzun_slu - V_suzun_slu_prev) - K_g_suzun
    G_suzun_slu_month = G_suzun_slu_data.sum()+G_suzun_slu # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 15. Общая откачка нефти Сузун
    G_suzun = G_suzun_vslu + G_suzun_tng + G_suzun_slu
    G_suzun_month = G_suzun_data.sum()+G_suzun # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 16. Потери при откачке нефти
    G_suzun_delta = Q_suzun_day - G_suzun_slu - G_suzun_vslu - (V_upn_suzun - V_upn_suzun_prev) + G_payaha

    return {
        "G_buy_day": G_buy_day, "G_out_udt_day": G_out_udt_day, "G_per": G_per, "G_per_month": G_per_month, "Q_vankor_month": Q_vankor_month,
        "Q_suzun_month": Q_suzun_month, "Q_vslu_month": Q_vslu_month, "Q_tng_month": Q_tng_month, "Q_vo_month": Q_vo_month,
        "V_suzun_tng": V_suzun_tng, "G_suzun_vslu": G_suzun_vslu, "G_suzun_vslu_month": G_suzun_vslu_month, "V_upn_suzun": V_upn_suzun,
        "V_suzun_vslu": V_suzun_vslu, "V_suzun_slu_0": V_suzun_slu_0, "V_suzun_slu": V_suzun_slu, "G_suzun_slu": G_suzun_slu,
        "G_suzun_slu_month": G_suzun_slu_month, "G_suzun": G_suzun,"G_suzun_month": G_suzun_month, "G_suzun_delta": G_suzun_delta,
    }


# ===============================================================
# -------------------- ВОСТОК ОЙЛ -------------------------------
# ===============================================================
def VO(Q_vo_day, G_upn_lodochny_ichem_data, m):
    Q_vo_day = _to_float(Q_vo_day)
    G_upn_lodochny_ichem = Q_vo_day
    G_upn_lodochny_ichem_month = G_upn_lodochny_ichem_data.sum()+G_upn_lodochny_ichem # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    return {
        "G_upn_lod": G_upn_lodochny_ichem,
        "G_upn_lod_month": G_upn_lodochny_ichem_month,
    }


# ===============================================================
# -------------------- КЧНГ -------------------------------------
# ===============================================================
def kchng(Q_kchng_day, Q_kchng, G_kchng_data):
    Q_kchng = np.array(Q_kchng, dtype=float)
    Q_kchng_day = _to_float(Q_kchng_day)

    Q_kchng_month = Q_kchng.sum()
    G_kchng = Q_kchng_day
    G_kchng_month = G_kchng_data.sum() + G_kchng # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    return {
        "Q_kchng_month": Q_kchng_month,
        "G_kchng": G_kchng,
        "G_kchng_month": G_kchng_month,
        "G_kchng_data":G_kchng_data
    }


# ===============================================================
# -------------------- ЛОДОЧНЫЙ ---------------------------------
# ===============================================================
def lodochny(
    Q_tagul, Q_lodochny, V_upn_lodochny_prev, G_ichem, V_ichem_prev, G_lodochny_ichem,
    Q_tagul_prev_month, G_lodochni_upsv_yu_prev_month, K_otkachki, K_gupn_lodochny, N, Q_vo_day,
    Q_lodochny_day, Q_tagul_day, V_tagul, V_tagul_prev, K_g_tagul, G_kchng, day, manual_V_upn_lodochny, manual_G_sikn_tagul,
    manual_V_tagul, G_lodochny_uspv_yu_data, G_sikn_tagul_data, G_tagul_data, delte_G_tagul_data,G_lodochny_data, delte_G_upn_lodochny_data,
    G_tagul_lodochny_data
):
    # Преобразование входных данных
    Q_tagul = np.array(Q_tagul, dtype=float)
    Q_lodochny = np.array(Q_lodochny, dtype=float)
    Q_vo_day = _to_float(Q_vo_day)
    Q_lodochny_day = _to_float(Q_lodochny_day)
    V_upn_lodochny_prev = _to_float(V_upn_lodochny_prev)
    V_ichem_prev = _to_float(V_ichem_prev)
    G_ichem = _to_float(G_ichem)
    G_lodochny_ichem = _to_float(G_lodochny_ichem)
    G_lodochni_upsv_yu_prev_month = _to_float(G_lodochni_upsv_yu_prev_month)
    Q_tagul_prev_month = _to_float(Q_tagul_prev_month)
    V_tagul = _to_float(V_tagul)
    V_tagul_prev = _to_float(V_tagul_prev)
    K_otkachki = float(K_otkachki)
    K_gupn_lodochny = float(K_gupn_lodochny)
    K_g_tagul = float(K_g_tagul)
    G_kchng = _to_float(G_kchng)
    Q_tagul_day = _to_float(Q_tagul_day)
    N = int(N) if N else 1.0
    # --- 20–21. Месячные значения добычи ---
    Q_tagulsk_month = Q_tagul.sum()
    Q_lodochny_month = Q_lodochny.sum()

    # --- 22–24. Наличие нефти ---
    if manual_V_upn_lodochny is not None:
        V_upn_lodochny = manual_V_upn_lodochny
    else:
        V_upn_lodochny = V_upn_lodochny_prev
    V_ichem = V_ichem_prev + G_lodochny_ichem - G_ichem
    V_lodochny = V_upn_lodochny - V_ichem

    # --- 25. Коэффициент откачки ---
    K_otkachki_month = (G_lodochni_upsv_yu_prev_month / Q_tagul_prev_month)
    if abs(K_otkachki - K_otkachki_month) >= 0.01:
        in_1 = input(
            f"Заменить K_откачки {K_otkachki} "
            f"на {K_otkachki_month}? (y/n): "
        )
        if in_1.lower() == "y":
            K_otkachki = K_otkachki_month
    # --- 26. Откачка нефти Лодочного месторождения на УПСВ-Юг ---
    G_lodochny_uspv_yu = Q_lodochny_day * (1 - K_otkachki) - (K_gupn_lodochny / 2)
    G_lodochny_uspv_yu_month = G_lodochny_uspv_yu_data.sum() + G_lodochny_uspv_yu # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
    # --- 27 расчет откачки нефти
    if manual_G_sikn_tagul is not None:
        G_sikn_tagul = manual_G_sikn_tagul
    else:
        if day <= N-2:
            G_sikn_tagul = round(G_lodochny_uspv_yu_month / N / 10) * 10
        else:
            value = round(G_lodochny_uspv_yu_month / N / 10) * 10
            G_sikn_tagul_N = [value for _ in range(N - 2)]
            G_sikn_tagul = (G_lodochny_uspv_yu_month - sum(G_sikn_tagul_N))/2
        if 900 <= G_sikn_tagul <= 1500:
            alarm = False # заменить на переменную из массива
        else:
            G_sikn_tagul = int(input(f"Необходимо откорректировать значение откачки {G_sikn_tagul}"))
    G_sikn_tagul_month = G_sikn_tagul_data.sum()+G_sikn_tagul # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
    # --- 28–29. Откачка в МН Тагульского месторождения ---
    if manual_V_tagul is not None:
        V_tagul = manual_V_tagul
    else:
        V_tagul = V_tagul_prev
    G_tagul = Q_tagul_day - (V_tagul - V_tagul_prev) - K_g_tagul
    G_tagul_month = G_tagul_data.sum()+G_tagul # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 30. Потери ---
    delte_G_tagul = Q_tagul_day - G_tagul - (V_tagul - V_tagul_prev)
    delte_G_tagul_month = delte_G_tagul_data.sum()+delte_G_tagul # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 31–32. Откачка нефти в МН ---
    G_upn_lodochny = Q_lodochny_day * K_otkachki - (V_upn_lodochny-V_upn_lodochny_prev) - (K_gupn_lodochny / 2) + Q_vo_day
    G_lodochny = G_upn_lodochny - G_ichem
    G_lodochny_month = G_lodochny_data.sum()+G_lodochny # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # --- 33–34. Сводные потери и суммарная откачка ---
    delte_G_upn_lodochny = Q_lodochny_day + Q_vo_day - G_lodochny_uspv_yu - G_lodochny - (V_upn_lodochny - V_upn_lodochny_prev)
    G_upn_lodochny_month = delte_G_upn_lodochny_data.sum() + delte_G_upn_lodochny # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
    G_tagul_lodochny = G_tagul + G_upn_lodochny + G_kchng
    G_tagul_lodochny_month = G_tagul_lodochny_data.sum()+G_tagul_lodochny # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    return {
        "Q_tagulsk_month": Q_tagulsk_month, "Q_lodochny_month": Q_lodochny_month, "V_upn_lodochny": V_upn_lodochny,
        "V_ichem": V_ichem, "V_lodochny": V_lodochny, "K_otkachki_month": K_otkachki_month, "G_lodochny_uspv_yu": G_lodochny_uspv_yu,
        "G_lodochny_uspv_yu_month": G_lodochny_uspv_yu_month, "G_sikn_tagul": G_sikn_tagul, "G_sikn_tagul_month": G_sikn_tagul_month,
        "delte_G_tagul": delte_G_tagul, "delte_G_tagul_month": delte_G_tagul_month, "G_upn_lodochny": G_upn_lodochny,
        "G_lodochny": G_lodochny, "G_lodochny_month": G_lodochny_month, "delte_G_upn_lodochny": delte_G_upn_lodochny,
        "G_upn_lodochny_month": G_upn_lodochny_month, "G_tagul_lodochny": G_tagul_lodochny, "G_tagul_lodochny_month": G_tagul_lodochny_month,
        "G_tagul_month":G_tagul_month,"G_tagul":G_tagul
    }

# ===============================================================
# -------------------- Блок «ЦППН-1»: ---------------------------
# ===============================================================
def CPPN_1 (
    V_upsv_yu_prev, V_upsv_s_prev, V_upsv_cps_prev, V_upsv_yu_0, V_upsv_s_0, V_upsv_cps_0,
    V_upsv_yu, V_upsv_s, V_upsv_cps,  V_lodochny_cps_upsv_yu_prev, V_lodochny_upsv_yu,
    G_sikn_tagul, flag_list, manual_V_upsv_yu, manual_V_upsv_s, manual_V_upsv_cps,
):
    V_upsv_yu_prev=_to_float(V_upsv_yu_prev)
    V_upsv_s_prev = _to_float(V_upsv_s_prev)
    V_upsv_cps_prev = _to_float(V_upsv_cps_prev)
    V_upsv_yu_0 = _to_float(V_upsv_yu_0)
    V_upsv_s_0 = _to_float(V_upsv_s_0)
    V_upsv_cps_0 = _to_float(V_upsv_cps_0)
    V_upsv_yu = _to_float(V_upsv_yu)
    V_upsv_s = _to_float(V_upsv_s)
    V_upsv_cps = _to_float(V_upsv_cps)
    V_lodochny_cps_upsv_yu_prev = _to_float(V_lodochny_cps_upsv_yu_prev)
    G_sikn_tagul = _to_float(G_sikn_tagul)
    V_lodochny_upsv_yu =_to_float(V_lodochny_upsv_yu)

# 35. Расчет наличия нефти в РВС УПСВ-Юг, т:
    if manual_V_upsv_yu is not None:
        V_upsv_yu = manual_V_upsv_yu
    else:
        V_upsv_yu = V_upsv_yu_prev
    if not flag_list[0]:
        if V_upsv_yu_prev-1500 <= V_upsv_yu <= V_upsv_yu_prev+1500:
            V_upsv_yu = V_upsv_yu
        else:
            V_upsv_yu = int(input("Введите корректное заначение для V_upsv_yu"))
    else:
        if V_upsv_yu_prev-2000 <= V_upsv_yu <= V_upsv_yu_prev+4000:
            print("f")
# 36. Расчет наличия нефти в РВС УПСВ-Север, т:
    if manual_V_upsv_s is not None:
        V_upsv_s = manual_V_upsv_s
    else:
        V_upsv_s = V_upsv_s_prev
    if not flag_list[1]:
        if V_upsv_s_prev-1500 <= V_upsv_s <= V_upsv_s_prev+1500:
            V_upsv_s:V_upsv_s
        else:
            V_upsv_s = int(input("Введите корректное заначение для V_upsv_s"))
    else:
        if V_upsv_s_prev-1500 <= V_upsv_s <= V_upsv_s_prev+2000:
            print("f")
# 37. Расчет наличия нефти в РВС ЦПС, т:
    if manual_V_upsv_cps is not None:
        V_upsv_cps = V_upsv_cps
    else:
        V_upsv_cps = V_upsv_cps_prev
    if not flag_list[2]:
        if V_upsv_cps_prev - 1500 <= V_upsv_cps <= V_upsv_cps_prev + 1500:
            V_upsv_cps = V_upsv_cps
        else:
            V_upsv_cps = int(input("Введите корректное заначение для V_upsv_cps"))
    else:
        if V_upsv_cps_prev - 2000 <= V_upsv_cps <= V_upsv_cps_prev + 3300:
            print("f")
# 38. Расчет суммарного наличия нефти в РП ЦППН-1, т:
    V_cppn_1_0 = V_upsv_yu_0+V_upsv_s_0+V_upsv_cps_0
    V_cppn_1 = V_upsv_yu + V_upsv_s + V_upsv_cps

#39. Расчет наличия нефти Лодочного ЛУ в РП на ЦПС и УПСВ - Юг, т:
    V_lodochny_cps_upsv_yu = V_lodochny_cps_upsv_yu_prev + V_lodochny_upsv_yu - G_sikn_tagul
    return {
        "V_upsv_yu":V_upsv_yu, "V_upsv_s": V_upsv_s, "V_upsv_cps": V_upsv_cps, "V_cppn_1_0": V_cppn_1_0,
        "V_cppn_1": V_cppn_1, "V_lodochny_cps_upsv_yu": V_lodochny_cps_upsv_yu,
    }
# ===============================================================
# ------------------ Блок «Сдача ООО «РН-Ванкор»: ---------------
# ===============================================================
def rn_vankor(
    F_vn, F_suzun_obsh, F_suzun_vankor, N, day,
    V_ctn_suzun_vslu_norm, V_ctn_suzun_vslu,
    F_tagul_lpu, F_tagul_tpu, F_skn, F_vo,
    manual_F_bp_vn, manual_F_bp_suzun, manual_F_bp_suzun_vankor,
    manual_F_bp_tagul_lpu, manual_F_bp_tagul_tpu, manual_F_bp_skn,
    manual_F_bp_vo, manual_F_bp_suzun_vslu, F_kchng,F_bp_data,manual_F_kchng, F_bp_vn_data,
    F_bp_suzun_data,F_bp_suzun_vankor_data, F_bp_suzun_vslu_data, F_bp_tagul_lpu_data,F_bp_tagul_tpu_data,
    F_bp_skn_data,F_bp_vo_data,F_bp_kchng_data
):

    # ---------- Приведение типов ----------
    F_vn = _to_float(F_vn)
    F_suzun_obsh = _to_float(F_suzun_obsh)
    F_suzun_vankor = _to_float(F_suzun_vankor)
    V_ctn_suzun_vslu_norm = _to_float(V_ctn_suzun_vslu_norm)
    V_ctn_suzun_vslu = _to_float(V_ctn_suzun_vslu)
    F_tagul_lpu = _to_float(F_tagul_lpu)
    F_tagul_tpu = _to_float(F_tagul_tpu)
    F_skn = _to_float(F_skn)
    F_vo = _to_float(F_vo)
    F_kchng = _to_float(F_kchng)

    # ---------- Инициализация  ----------
    F_bp_suzun_vankor = 0 # для расчета с e если дата не попадет в диапозон где дата должна быть кратной e выведет число 0
    F_bp_suzun_vslu = 0 # для расчета с e если дата не попадет в диапозон где дата должна быть кратной e выведет число 0
    F_bp_vo = 0 # для расчета с e если дата не попадет в диапозон где дата должна быть кратной e выведет число 0
    F_bp_kchng = 0# для расчета с e если дата не попадет в диапозон где дата должна быть кратной e выведет число 0
    alarm_first_10_days = False
    alarm_first_10_days_msg = None
    # =========================================================
    # 40. Ванкорнефть
    if manual_F_bp_vn is not None:
        F_bp_vn = manual_F_bp_vn
    else:
        base = round((F_vn / N) / 50) * 50
        if day < N:
            F_bp_vn = base
        else:
            F_bp_vn = F_vn - base * (N - 1)
    F_bp_vn_month = F_bp_vn_data.sum()+F_bp_vn # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 41. Сузун (общий)
    F_suzun = F_suzun_obsh - F_suzun_vankor
    if manual_F_bp_suzun is not None:
        F_bp_suzun = manual_F_bp_suzun
    else:
        base = round((F_suzun / N) / 50) * 50
        if day < N:
            F_bp_suzun = base
        else:
            F_bp_suzun = F_suzun - base * (N - 1)
    F_bp_suzun_month = F_bp_suzun_data.sum()+F_bp_suzun # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 42. Сузун → Ванкор (через e)
    if manual_F_bp_suzun_vankor is not None:
        F_bp_suzun_vankor = manual_F_bp_suzun_vankor
    elif F_suzun_vankor < 20000:
        e = int(input("Введите e (периодичность сдачи): "))
        delivery_days = [d for d in range(1, N + 1) if d % e == 0]
        if delivery_days:
            delivery_count = len(delivery_days)
            last_day = delivery_days[-1]
            base = round((F_suzun_vankor / delivery_count) / 50) * 50
            if day in delivery_days:
                if day != last_day:
                    F_bp_suzun_vankor = base
                else:
                    F_bp_suzun_vankor = F_suzun_vankor - base * (delivery_count - 1)
    elif F_suzun_vankor >= 20000:
        base = round((F_suzun_vankor / N) / 50) * 50
        if day < N-2:
            F_bp_suzun_vankor = base
        else:
            F_bp_suzun_vankor = (F_suzun_vankor - base * (N - 2))/2
    F_bp_suzun_vankor_month = F_bp_suzun_vankor_data.sum()+F_bp_suzun_vankor # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 43. Сузун → ВСЛУ
    if manual_F_bp_suzun_vslu is not None:
        F_bp_suzun_vslu = manual_F_bp_suzun_vslu
    elif V_ctn_suzun_vslu > V_ctn_suzun_vslu_norm + 1000:
        F_bp_suzun_vslu = 1000
    F_bp_suzun_vslu_month = F_bp_suzun_vslu_data.sum()+F_bp_suzun_vslu # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 44. Тагульское — ЛПУ
    if manual_F_bp_tagul_lpu is not None:
        F_bp_tagul_lpu = manual_F_bp_tagul_lpu
    else:
        base = round((F_tagul_lpu / N) / 50) * 50
        if day < N-2:
            F_bp_tagul_lpu = base
        else:
            F_bp_tagul_lpu = (F_tagul_lpu - base * (N - 2))/2

    F_bp_tagul_lpu_month = F_bp_tagul_lpu_data.sum()+F_bp_tagul_lpu # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 45. Тагульское — ТПУ
    if manual_F_bp_tagul_tpu is not None:
        F_bp_tagul_tpu = manual_F_bp_tagul_tpu
    else:
        base = round((F_tagul_tpu / N) / 50) * 50
        if day < N-2:
            F_bp_tagul_tpu = base
        else:
            F_bp_tagul_tpu = (F_tagul_tpu - base * (N - 2))/2

    F_bp_tagul_tpu_month = F_bp_tagul_tpu_data.sum()+F_bp_tagul_tpu# данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 47. СКН
    if manual_F_bp_skn is not None:
        F_bp_skn = manual_F_bp_skn
    else:
        base = round((F_skn / N) / 50) * 50
        F_bp_skn = base if day < (N-2) else (F_skn - base * (N - 1))/2
    F_bp_skn_month = F_bp_skn_data.sum()+F_bp_skn # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 48. Восток Ойл (через e)
    if manual_F_bp_vo is not None:
        F_bp_vo = manual_F_bp_vo
    elif F_vo < 20000:
        e = int(input("Введите e (периодичность сдачи): "))
        delivery_days = [d for d in range(1, N + 1) if d % e == 0]
        if delivery_days:
            delivery_count = len(delivery_days)
            last_day = delivery_days[-1]
            base = round((F_vo / delivery_count) / 50) * 50

            if day in delivery_days:
                if day != last_day:
                    F_bp_vo = base
                else:
                    F_bp_vo = F_vo - base * (delivery_count - 1)
    else:
        base = round((F_vo / N) / 50) * 50
        F_bp_vo = base if day < N else F_vo - base * (N - 1)
    F_bp_vo_month = F_bp_vo_data.sum()+F_bp_vo# данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
    """
    Для формулы 49 уточнить Knраб 
    """
    F_bp_tng = 0 # в дальнейшим заменить расчетной формулой
    # =========================================================
    #  50.	Определение посуточной сдачи нефти ООО «КЧНГ» через СИКН № 1209, т/сут:
    if manual_F_kchng is not None:
        F_kchng = manual_F_kchng
    elif F_kchng < 20000:
        e = int(input("Введите e (периодичность сдачи): "))
        delivery_days = [d for d in range(1, N + 1) if d % e == 0]
        if delivery_days:
            delivery_count = len(delivery_days)
            last_day = delivery_days[-1]
            base = round((F_kchng / delivery_count) / 50) * 50

            if day in delivery_days:
                if day != last_day:
                    F_bp_kchng = base
                else:
                    F_bp_kchng = (F_kchng - base * (delivery_count - 2))/2
    else:
        base = round((F_vo / N) / 50) * 50
        F_bp_kchng = base if day < N else F_kchng - base * (N - 1)
    F_bp_kchng_month = F_bp_kchng_data.sum()+F_bp_kchng# данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
    # 51.	Расчет суммарной сдачи через СИКН № 1209:
    F_bp = F_bp_vn + F_bp_tagul_lpu + F_bp_tagul_lpu + F_bp_suzun_vankor + F_bp_suzun_vslu + F_bp_skn + F_bp_vo + F_bp_tng + F_bp_kchng
    F_bp_month = sum(F_bp_data)+F_bp # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
    F_bp_sr = F_bp_month/N
    if F_bp_data[:10].sum() < F_bp_sr:
        alarm_first_10_days = True
        alarm_first_10_days_msg = (
            "Сдача нефти за первые 10 суток меньше "
            "среднесуточного значения за месяц"
        )
    return {
        "F_bp_vn": F_bp_vn, "F_bp_vn_month": F_bp_vn_month, "F_bp_suzun": F_bp_suzun, "F_bp_suzun_month": F_bp_suzun_month,
        "F_bp_suzun_vankor": F_bp_suzun_vankor, "F_bp_suzun_vankor_month": F_bp_suzun_vankor_month, "F_bp_suzun_vslu": F_bp_suzun_vslu,
        "F_bp_suzun_vslu_month": F_bp_suzun_vslu_month, "F_bp_tagul_lpu": F_bp_tagul_lpu, "F_bp_tagul_lpu_month": F_bp_tagul_lpu_month,
        "F_bp_tagul_tpu": F_bp_tagul_tpu, "F_bp_tagul_tpu_month": F_bp_tagul_tpu_month, "F_bp_skn": F_bp_skn, "F_bp_skn_month": F_bp_skn_month,
        "F_bp_vo": F_bp_vo, "F_bp_vo_month": F_bp_vo_month, "F_bp_kchng":F_bp_kchng, "F_bp_kchng_month":F_bp_kchng_month, "F_bp": F_bp,
        "F_bp_month":F_bp_month, "F_bp_sr":F_bp_sr, "__alarm_first_10_days": alarm_first_10_days, "__alarm_first_10_days_msg": alarm_first_10_days_msg
    }

# ===============================================================
# ---------------------- Блок «СИКН-1208»: ----------------------
# ===============================================================
def sikn_1208 (
    G_suzun_vslu, G_suzun_sikn_data, G_sikn_tagul_lod_data, G_buy_day, G_per, G_suzun, G_sikn_suzun_data, G_suzun_tng_data,
    G_suzun_tng, Q_vankor, V_upsv_yu, V_upsv_s, V_upsv_cps, V_upsv_yu_prev, V_upsv_s_prev, V_upsv_cps_prev,G_lodochny_uspv_yu,
    K_delte_g_sikn, G_sikn_data, G_sikn_vankor_data, V_cppn_1, G_skn_data
):
    G_suzun_vslu = _to_float(G_suzun_vslu)
    G_buy_day = _to_float(G_buy_day)
    G_per = _to_float(G_per)
    Q_vankor = _to_float(Q_vankor)
    G_suzun = _to_float(G_suzun)
    V_upsv_yu = _to_float(V_upsv_yu)
    V_upsv_s = _to_float(V_upsv_s)
    V_upsv_cps = _to_float(V_upsv_cps)
    V_upsv_yu_prev = _to_float(V_upsv_yu_prev)
    V_upsv_s_prev = _to_float(V_upsv_s_prev)
    V_upsv_cps_prev = _to_float(V_upsv_cps_prev)
    # ---------- Инициализация  ----------
    V_cppn_1_prev = 123 # Для расчета в будущем подтягиваем из бд
# 52.	Определение откачки нефти АО «Сузун» (ВСЛУ) через СИКН № 1208, т/сут:
    G_sikn_vslu = G_suzun_vslu
    G_sikn_vslu_month = G_suzun_sikn_data.sum()+G_sikn_vslu # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
# 53.	Определение суммарного месячного значения откачки нефти ООО «Тагульское» через СИКН № 1208, т/сут:
    G_sikn_tagul = G_sikn_tagul_lod_data
# 54.	Расчет суммарной откачки нефти АО «Сузун» (СЛУ+ВСЛУ) через СИКН № 1208, т/сут:
    G_sikn_suzun = G_suzun + G_buy_day - G_per
    G_sikn_suzun_month = G_sikn_suzun_data.sum()+G_sikn_suzun # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
# 55.	Расчет откачки нефти АО «Таймырнефтегаз» (Пайяха) через СИКН № 1208, т/сут:
    G_sikn_tng = G_suzun_tng
    G_sikn_tng_month = G_suzun_tng_data.sum() + G_suzun_tng # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
# 57.	Расчет суммарной откачки нефти через СИКН № 1208, т/сут:
    G_sikn = Q_vankor + G_suzun - (V_upsv_yu - V_upsv_yu_prev) - (V_upsv_s - V_upsv_s_prev) - (V_upsv_cps - V_upsv_cps_prev) + G_lodochny_uspv_yu + K_delte_g_sikn + G_buy_day + G_per
    G_sikn_month = G_sikn_data.sum() + G_sikn # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
# 58.	Расчет откачки нефти АО «Ванкорнефть» через СИКН № 1208, т/сут:
    G_sikn_vankor = G_sikn - G_sikn_tagul - G_sikn_suzun - G_sikn_tng
    G_sikn_vankor_month = G_sikn_vankor_data.sum() + G_sikn_vankor # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня
# 59.	Определение суммарного месячного значения передачи нефти ООО «СКН» на транспортировку КНПС, т/сут:
    G_skn_month = G_skn_data.sum() # пока значения подгружаются из manual_data, в дальнейшем предусмотреть ручной ввод
# 60.	Расчет потерь при откачке через СИКН № 1208 (потери+отпуск+прочее), т/сут:
    G_delta_sikn = Q_vankor + G_suzun + G_lodochny_uspv_yu - G_sikn - (V_cppn_1 - V_cppn_1_prev) + G_buy_day - G_per
    return {
        "G_sikn_vslu":G_sikn_vslu, "G_sikn_vslu_month":G_sikn_vslu_month, "G_sikn_tagul":G_sikn_tagul, "G_sikn_suzun":G_sikn_suzun,
        "G_sikn_suzun_month":G_sikn_suzun_month, "G_sikn_tng":G_sikn_tng, "G_sikn_tng_month":G_sikn_tng_month, "G_sikn":G_sikn, "G_sikn_month":G_sikn_month,
        "G_sikn_vankor":G_sikn_vankor, "G_sikn_vankor_month":G_sikn_vankor_month, "G_skn_month":G_skn_month, "G_delta_sikn":G_delta_sikn,
    }

def TSTN (
        V_gnsp_0,V_gnsp_prev, N, VN_min_gnsp, G_sikn, G_gpns_data, flag_list, V_nps_1_prev, V_nps_2_prev, G_tagul, G_upn_lodochny, G_skn, G_kchng,
        V_knps_prev, V_nps_1_0, V_nps_2_0, V_knps_0, G_suzun_vslu, K_suzun,  V_tstn_suzun_vslu_prev, F_suzun_vankor, V_tstn_suzun_vankor_prev, K_vankor,
        G_buy_day, G_per, F_suzun_vslu, V_suzun_put_0, V_tstn_suzun_prev, G_suzun_slu, V_tstn_skn_prev, F_skn, K_skn, G_ichem, F_vo, V_tstn_vo_prev,
        K_ichem, F_tng, G_suzun_tng, V_tstn_tng_prev,K_payaha, V_tstn_tagul_prev, F_kchng, K_tagul,V_tstn_kchng_prev, V_tstn_lodochny_prev,
        G_sikn_tagul, F_tagul_lpu, K_lodochny, V_tstn_rn_vn_prev
          ):
    F_suzun_vankor = _to_float(F_suzun_vankor)
    F_tng = _to_float(F_tng)
    F_vo = _to_float(F_vo)
    F_kchng = _to_float(F_kchng)
    V_gnsp_0 = _to_float(V_gnsp_0)
    V_gnsp_prev = _to_float(V_gnsp_prev)
    VN_min_gnsp = _to_float(VN_min_gnsp)
    G_sikn = _to_float(G_sikn)
    V_nps_1_prev = _to_float(V_nps_1_prev)
    V_nps_2_prev = _to_float(V_nps_2_prev)
    G_tagul = _to_float(G_tagul)
    G_upn_lodochny = _to_float(G_upn_lodochny)
    G_skn = _to_float(G_skn)
    G_kchng = _to_float(G_kchng)
    V_knps_prev = _to_float(V_knps_prev)
    V_nps_1_0 = _to_float(V_nps_1_0)
    V_nps_2_0 = _to_float(V_nps_2_0)
    V_knps_0 = _to_float(V_knps_0)
    G_suzun_vslu = _to_float(G_suzun_vslu)
    K_suzun = _to_float(K_suzun)
    V_tstn_suzun_vslu_prev = _to_float( V_tstn_suzun_vslu_prev)
    V_tstn_suzun_vankor_prev = _to_float(V_tstn_suzun_vankor_prev)
    K_vankor = _to_float(K_vankor)
    F_suzun_vslu = _to_float(F_suzun_vslu)
    V_suzun_put_0 = _to_float(V_suzun_put_0)
    V_tstn_suzun_prev = _to_float(V_tstn_suzun_prev)
    G_suzun_slu = _to_float(G_suzun_slu)
    V_tstn_skn_prev = _to_float(V_tstn_skn_prev)
    F_skn = _to_float(F_skn)
    K_skn = _to_float(K_skn)
    F_vo = _to_float(F_vo)
    V_tstn_vo_prev = _to_float(V_tstn_vo_prev)
    G_suzun_tng = _to_float(G_suzun_tng)
    V_tstn_tng_prev = _to_float(V_tstn_tng_prev)
    V_tstn_tagul_prev = _to_float(V_tstn_tagul_prev)
    V_tstn_kchng_prev = _to_float(V_tstn_kchng_prev)
    V_tstn_lodochny_prev = _to_float(V_tstn_lodochny_prev)
    F_tagul_lpu = _to_float(F_tagul_lpu)
    G_sikn_tagul = _to_float(G_sikn_tagul)
    V_tstn_rn_vn_prev = _to_float(V_tstn_rn_vn_prev)
    # ---------- Инициализация-------------
    V_tsnt_suzun_vankor_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_vslu_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_tagul_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_lodochny_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_rn_vn_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_suzun_vankor_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_suzun_vslu_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_skn_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_vo_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_tng_0 = 123 # Для расчета в будущем подтягиваем из бд
    V_tstn_kchng_0 = 123 # Для расчета в будущем подтягиваем из бд

    F_suzun = 123 # в таблице параметров нет упоминания откуда брать значения для переменной
    F = 0 # в таблице параметров нет упоминания откуда брать значения для переменной
    F_tagul = 123 # в таблице параметров нет упоминания откуда брать значения для переменной
# 61.	Расчет откачки нефти с ГНПС, т/сут:
    G_gpns_i = G_sikn + (V_gnsp_0 - VN_min_gnsp)/N
    G_gpns_month = G_gpns_data.sum() + G_gpns_i
    G_gpns = G_gpns_month/N
# 62.	Расчет наличия нефти в РП ГНПС, т:
    V_gnsp = V_gnsp_prev + G_sikn - G_gpns
    if not flag_list[0]:
        if V_gnsp_prev-1500 <= V_gnsp <= V_gnsp_prev+1500:
            V_gnsp = V_gnsp
        else:
            V_gnsp = int(input("Введите корректное значение для V_gnsp"))
    else:
        if V_gnsp_prev - 2000 <= V_gnsp <= V_gnsp_prev + 3000:
            V_gnsp = V_gnsp
        else:
            V_gnsp = int(input("Введите корректное значение для V_gnsp"))
# 63.	Расчет наличия нефти в РП НПС-1, т:
    V_nps_1 = V_nps_1_prev
    if not flag_list[1]:
        if V_nps_1_prev - 700 <= V_nps_1 <= V_nps_1_prev + 700:
            V_nps_1 = V_nps_1
        else:
            V_nps_1 = int(input("Введите корректное значение для V_nps_1"))
    else:
        if V_nps_1_prev - 2000 <= V_nps_1 <= V_nps_1_prev + 4000:
            V_nps_1 = V_nps_1
        else:
            V_nps_1 = int(input("Введите корректное значение для V_nps_1"))
# 64.	Расчет наличия нефти в РП НПС-2, т:
    V_nps_2 = V_nps_2_prev
    if not flag_list[1]:
        if V_nps_2_prev - 700 <= V_nps_2 <= V_nps_2_prev + 700:
            V_nps_2 = V_nps_2
        else:
            V_nps_2 = int(input("Введите корректное значение для V_nps_1"))
    else:
        if V_nps_2_prev - 2000 <= V_nps_2 <= V_nps_2_prev + 4000:
            V_nps_2 = V_nps_2
        else:
            V_nps_2 = int(input("Введите корректное значение для V_nps_1"))
#65.	Расчет наличия нефти в РП КНПС
    V_knsp = (G_gpns - F + V_knps_prev + G_tagul + G_upn_lodochny + G_skn + G_kchng) - (V_nps_2 - V_nps_2_prev) - (V_nps_1-V_nps_1_prev)
    if not flag_list[2]:
        if V_knps_prev - 1500 <= V_knsp <= V_knps_prev + 1500:
            V_knsp = V_knsp
        else:
            V_knsp = int(input("Введите корректное значение для V_nps_1"))
    else:
        if V_knps_prev - 2000 <= V_knsp <= V_knps_prev + 3000:
            V_knsp = V_knsp
        else:
            V_knsp = int(input("Введите корректное значение для V_knsp"))
# 66.	Расчет суммарного наличия нефти в резервуарах ЦТН, т:
    V_tstn_0 = V_gnsp_0 + V_nps_1_0 + V_nps_2_0 + V_knps_0
    V_tstn = V_gnsp_prev + V_nps_1_prev + V_nps_2_prev + V_knps_prev
# 67.	Расчет наличия нефти АО «Сузун» (ВСЛУ) в резервуарах ЦТН, т:
    V_tstn_suzun_vslu =  V_tstn_suzun_vslu_prev - F_suzun_vslu + G_suzun_vslu - F_suzun_vslu * (K_suzun/100)
    if 900 <=  V_tstn_suzun_vslu <= 4000:
        V_tstn_suzun_vslu =  V_tstn_suzun_vslu
    else:
        V_tstn_suzun_vslu = int(input("Введите корректное значение V_tstn_vslu "))
# 68.	 Расчет наличия нефти АО «Сузун» (Ванкор) в резервуарах ЦТН, т:
    V_tstn_suzun_vankor = V_tstn_suzun_vankor_prev - F_suzun_vankor + (G_buy_day - G_per) - F_suzun_vankor * (K_vankor/100)
    if 900 <= V_tstn_suzun_vankor <= 5000:
        V_tstn_suzun_vankor = V_tstn_suzun_vankor
    else:
        V_tstn_suzun_vankor = int(input("Введите корректное значение V_tstn_suzun_vankor "))
# 69.	Расчет наличия нефти АО «Сузун» (Сузун) в резервуарах ЦТН, т:
    V_tstn_suzun_0 = V_suzun_put_0 - V_tstn_vslu_0 -  V_tsnt_suzun_vankor_0
    if 2000 <= V_tstn_suzun_0 <= 6000:
        V_tstn_suzun_0 = V_tstn_suzun_0
    else:
        V_tstn_suzun_0 = int(input("Введите корректное значение V_tstn_suzun_0 "))
    V_tstn_suzun = V_tstn_suzun_prev - F_suzun + G_suzun_slu - F_suzun *(K_suzun/100)
    if 2000 <= V_tstn_suzun <= 6000:
        V_tstn_suzun=V_tstn_suzun
    else:
        V_tstn_suzun = int(input("Введите корректное значение V_tstn_suzun "))
# 70.	Расчет наличия нефти ООО «СевКомНефтегаз» в резервуарах ЦТН, т:
    V_tstn_skn = V_tstn_skn_prev - F_skn + G_skn - F_skn * (K_skn/100)
    if 3000 <= V_tstn_skn <= 8000:
        V_tstn_skn=V_tstn_skn
    else:
        V_tstn_skn = int(input("Введите корректное значение V_tstn_skn "))
 # 71. Расчет наличия нефти ООО «Восток Оил» в резервуарах ЦТН, т:
    V_tstn_vo = V_tstn_vo_prev + G_ichem - F_vo - F_vo * (K_ichem/100)
    if 1000 <= V_tstn_vo <= 6000:
        V_tstn_vo = V_tstn_vo
    else:
        V_tstn_vo = int(input("Введите корректное значение V_tstn_vo "))
# 72.	Расчет наличия нефти АО «Таймырнефтегаз» в резервуарах ЦТН, т:
    V_tstn_tng = V_tstn_tng_prev + G_suzun_tng - F_tng - F_tng * (K_payaha/100)
    if 300 <= V_tstn_tng <= 6000:
        V_tstn_tng = V_tstn_tng
    else:
        V_tstn_tng = int(input("Введите корректное значение V_tstn_tng "))
# 73.	Расчет наличия нефти ООО «КЧНГ» (Русско-Реченское месторождение) в резервуарах ЦТН, т:
    V_tstn_kchng = V_tstn_kchng_prev + G_kchng - F_kchng - F_kchng * (K_tagul/100)
    if 1000 <= V_tstn_kchng <= 6000:
        V_tstn_kchng = V_tstn_kchng
    else:
        V_tstn_kchng = int(input("Введите корректное значение V_tstn_kchng "))
# 74.	Расчет наличия нефти ООО «Тагульское» (Тагульский ЛУ) в резервуарах ЦТН, т:
    V_tstn_tagul = V_tstn_tagul_prev + G_tagul - F_tagul - F_tagul * (K_tagul/100)
    if 4000 <= V_tstn_tagul <= 12000:
        V_tstn_tagul = V_tstn_tagul
    else:
        V_tstn_tagul = int(input("Введите корректное значение V_tstn_tagul "))
# 75.	Расчет наличия нефти ООО «Тагульское» (Лодочный ЛУ) в резервуарах ЦТН, т:
    V_tstn_lodochny = V_tstn_lodochny_prev + G_sikn_tagul - F_tagul_lpu - F_tagul_lpu * (K_lodochny/100)
    if 3000 <= V_tstn_lodochny <= 11000:
        V_tstn_lodochny = V_tstn_lodochny
    else:
        V_tstn_lodochny = int(input("Введите корректное значение V_tstn_lodochny "))
# 76.	Расчет наличия нефти ООО «Тагульское» (Всего) в резервуарах ЦТН, т:
    V_tstn_tagul_obsh_0 = V_tstn_tagul_0 + V_tstn_lodochny_0
    V_tstn_tagul_obsh = V_tstn_tagul + V_tstn_lodochny
    if 3000 <= V_tstn_tagul <= 11000:
        V_tstn_tagul = V_tstn_tagul
    else:
        V_tstn_tagul = int(input("Введите корректное значение V_tstn_tagul "))
# 77.	Расчет наличия нефти ООО «РН-Ванкор» в резервуарах ЦТН (мертвые остатки в резервуарах), т:
    V_tstn_rn_vn = V_tstn_rn_vn_prev
# 78.	Расчет наличия нефти АО «Ванкорнефть» в резервуарах ЦТН, т:
    V_tstn_vn_0 = V_tstn_0 - V_tstn_rn_vn_0 - V_tstn_suzun_0 - V_tstn_tagul_obsh_0 - V_tstn_suzun_vankor_0 - V_tstn_suzun_vslu_0 - V_tstn_skn_0 - V_tstn_vo_0 - V_tstn_tng_0 - V_tstn_kchng_0
    if 4000 <= V_tstn_vn_0 <= 11000:
        V_tstn_vn_0 = V_tstn_vn_0
    else:
        V_tstn_vn_0 = int(input("Введите корректное значение V_tstn_vn_0 "))
    V_tstn_vn = V_tstn - V_tstn_rn_vn - V_tstn_suzun - V_tstn_tagul_obsh - V_tstn_suzun_vankor -  V_tstn_suzun_vslu - V_tstn_skn - V_tstn_vo - V_tstn_tng - V_tstn_kchng
    if 4000 <= V_tstn_vn <= 11000:
        V_tstn_vn = V_tstn_vn
    else:
        V_tstn_vn = int(input("Введите корректное значение V_tstn_vn "))
    return {
        "G_gpns_i":G_gpns_i, "G_gpns_month":G_gpns_month, "G_gpns":G_gpns, "V_gnsp":V_gnsp, "V_nps_1":V_nps_1, "V_nps_2":V_nps_2, "V_knsp":V_knsp,
        "V_tstn_0":V_tstn_0, "V_tstn":V_tstn, " V_tstn_suzun_vslu": V_tstn_suzun_vslu, "V_tstn_suzun_vankor":V_tstn_suzun_vankor, "V_tstn_suzun_0":V_tstn_suzun_0,
        "V_tstn_suzun":V_tstn_suzun, "V_tstn_skn":V_tstn_skn,"V_tstn_vo":V_tstn_vo, "V_tstn_tng":V_tstn_tng, "V_tstn_kchng":V_tstn_kchng,
        "V_tstn_tagul":V_tstn_tagul, "V_tstn_lodochny":V_tstn_lodochny, "V_tstn_tagul_obsh":V_tstn_tagul_obsh, "V_tstn_tagul_obsh_0":V_tstn_tagul_obsh_0,
        "V_tstn_rn_vn":V_tstn_rn_vn, "V_tstn_vn":V_tstn_vn, "V_tstn_vn_0":V_tstn_vn_0
    }

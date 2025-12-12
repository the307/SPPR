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
    G_buy_month,
    G_out_udt_month,
    N,
    n,
    Q_vankor,
    Q_suzun,
    Q_vslu,
    Q_tng,
    Q_vo,
    G_payaha,
    G_suzun_tng,
    V_suzun_tng_prev,
    Q_vslu_day,
    V_upn_suzun_prev,
    V_suzun_vslu_prev,
    Q_suzun_day,
    V_upn_suzun_0,
    V_suzun_vslu_0,
    V_suzun_tng_0,
    K_g_suzun,
    V_suzun_slu_prev,
):
    # Приведение всех данных к скалярам
    G_buy_month = _to_float(G_buy_month)
    G_out_udt_month = _to_float(G_out_udt_month)
    Q_vankor = np.array(Q_vankor, dtype=float)
    Q_suzun = np.array(Q_suzun, dtype=float)
    Q_vslu = np.array(Q_vslu, dtype=float)
    Q_tng = np.array(Q_tng, dtype=float)
    Q_vo = np.array(Q_vo, dtype=float)
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
    # массивы для хранения
    list_g_per = []
    list_g_suzun_vslu = []
    list_g_suzun_slu = []
    list_g_suzun = []
    # --- 1. Суточное значение покупки нефти
    G_buy_day = G_buy_month / N
    # --- 2. Суточный выход с УПДТ
    G_out_udt_day = G_out_udt_month / N

    # --- 3. Расход на переработку (Gпер)
    G_per = G_buy_day - G_out_udt_day
    list_g_per.append(G_per)
    G_per_month = sum(list_g_per)

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
    list_g_suzun_vslu.append(G_suzun_vslu)
    G_suzun_vslu_month = sum(list_g_suzun_vslu)

    # --- 11–12. Наличие нефти
    V_upn_suzun = V_upn_suzun_prev
    V_suzun_vslu = V_suzun_vslu_prev + Q_vslu_day - G_suzun_vslu

    # --- 13. Расчёт наличия нефти (СЛУ)
    V_suzun_slu_0 = V_upn_suzun_0 - V_suzun_vslu_0 - V_suzun_tng_0
    V_suzun_slu = V_upn_suzun - V_suzun_vslu - V_suzun_tng

    # --- 14. Откачка нефти Сузун (СЛУ)
    G_suzun_slu = Q_suzun_day - Q_vslu_day - (V_suzun_slu - V_suzun_slu_prev) - K_g_suzun
    list_g_suzun_slu.append(G_suzun_slu)
    G_suzun_slu_month = sum(list_g_suzun_slu)

    # --- 15. Общая откачка нефти Сузун
    G_suzun = G_suzun_vslu + G_suzun_tng + G_suzun_slu
    list_g_suzun.append(G_suzun)
    G_suzun_month = sum(list_g_suzun)

    # --- 16. Потери при откачке нефти
    G_suzun_delta = Q_suzun_day - G_suzun_slu - G_suzun_vslu - (V_upn_suzun - V_upn_suzun_prev) + G_payaha

    return {
        "G_buy_day": G_buy_day,
        "G_out_udt_day": G_out_udt_day,
        "G_per": G_per,
        "G_per_month": G_per_month,
        "Q_vankor_month": Q_vankor_month,
        "Q_suzun_month": Q_suzun_month,
        "Q_vslu_month": Q_vslu_month,
        "Q_tng_month": Q_tng_month,
        "Q_vo_month": Q_vo_month,
        "V_suzun_tng": V_suzun_tng,
        "G_suzun_vslu": G_suzun_vslu,
        "G_suzun_vslu_month": G_suzun_vslu_month,
        "V_upn_suzun": V_upn_suzun,
        "V_suzun_vslu": V_suzun_vslu,
        "V_suzun_slu_0": V_suzun_slu_0,
        "V_suzun_slu": V_suzun_slu,
        "G_suzun_slu": G_suzun_slu,
        "G_suzun_slu_month": G_suzun_slu_month,
        "G_suzun": G_suzun,
        "G_suzun_month": G_suzun_month,
        "G_suzun_delta": G_suzun_delta,
    }


# ===============================================================
# -------------------- ВОСТОК ОЙЛ -------------------------------
# ===============================================================
def VO(Q_vo_day):
    Q_vo_day = _to_float(Q_vo_day)
    list_g_upn_lodochny_ichem = []
    G_upn_lodochny_ichem = Q_vo_day
    list_g_upn_lodochny_ichem.append(G_upn_lodochny_ichem)
    G_upn_lodochny_ichem_month = sum(list_g_upn_lodochny_ichem)

    return {
        "G_upn_lod": G_upn_lodochny_ichem,
        "G_upn_lod_month": G_upn_lodochny_ichem_month,
    }


# ===============================================================
# -------------------- КЧНГ -------------------------------------
# ===============================================================
def kchng(Q_kchng_day, Q_kchng):
    Q_kchng = np.array(Q_kchng, dtype=float)
    Q_kchng_day = _to_float(Q_kchng_day)

    Q_kchng_month = Q_kchng.sum()
    G_kchng = Q_kchng_day
    G_kchng_month = Q_kchng_month

    return {
        "Q_kchng_month": Q_kchng_month,
        "G_kchng": G_kchng,
        "G_kchng_month": G_kchng_month,
    }


# ===============================================================
# -------------------- ЛОДОЧНЫЙ ---------------------------------
# ===============================================================
def lodochny(
    Q_tagul, Q_lodochny, V_upn_lodochny_prev, G_ichem, V_ichem_prev, G_lodochny_ichem,
    Q_tagul_prev_month, G_lodochni_upsv_yu_prev_month, K_otkachki, K_gupn_lodochny, N, Q_vo_day,
    Q_lodochny_day, Q_tagul_day, V_tagul, V_tagul_prev, K_g_tagul, G_kchng, day
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
    N = int(N) if N else 1.0
    list_g_lodochny_uspv_yu = []
    list_g_skin_tagul = []
    list_g_tagul = []
    list_delte_g_tagul = []
    list_g_lodochny = []
    list_delte_g_upn_lodochny = []
    list_g_tagul_lodochny = []
    # --- 20–21. Месячные значения добычи ---
    Q_tagulsk_month = Q_tagul.sum()
    Q_lodochny_month = Q_lodochny.sum()

    # --- 22–24. Наличие нефти ---
    V_upn_lodochny = V_upn_lodochny_prev
    V_ichem = V_ichem_prev + G_lodochny_ichem - G_ichem
    V_lodochny = V_upn_lodochny - V_ichem

    # --- 25. Коэффициент откачки ---
    K_otkachki_month = (G_lodochni_upsv_yu_prev_month / Q_tagul_prev_month)
    if (K_otkachki-K_otkachki_month) >= 0.01:
        in_1 = int(input(f"Заменить коэффициент откачки K_otkachki: {K_otkachki} = K_otkachki_month: {K_otkachki_month}"))
        if in_1 == 1:
            K_otkachki = K_otkachki_month
    # --- 26. Откачка нефти Лодочного месторождения на УПСВ-Юг ---
    G_lodochny_uspv_yu = Q_lodochny_day * (1 - K_otkachki) - (K_gupn_lodochny / 2)
    list_g_lodochny_uspv_yu.append(G_lodochny_uspv_yu)
    G_lodochny_uspv_yu_month = sum(list_g_lodochny_uspv_yu)
    # --- 27 расчет откачки нефти
    if day <= N-2:
        G_sikn_tagul = round(G_lodochny_uspv_yu_month / N / 10) * 10
    else:
        value = round(G_lodochny_uspv_yu_month / N / 10) * 10
        G_sikn_tagul_N = [value for _ in range(N - 2)]
        G_sikn_tagul = (G_lodochny_uspv_yu_month - sum(G_sikn_tagul_N))/2
    if 900 <= G_sikn_tagul <= 1500:
        alarm = False # заменить на переменную из массива
    else:
        in_2 = int(input(f"Необходимо откорректировать значение откачки {G_sikn_tagul}"))
        G_sikn_tagul = in_2
        alarm = True # заменить на переменную из массива
    list_g_skin_tagul. append(G_sikn_tagul)
    G_sikn_tagul_month = sum(list_g_skin_tagul)
    # --- 28–29. Откачка в МН Тагульского месторождения ---
    V_tagul = V_tagul_prev
    G_tagul = Q_tagul_day - (V_tagul - V_tagul_prev) - K_g_tagul
    list_g_tagul.append(G_tagul)
    G_tagul_month = sum(list_g_tagul)

    # --- 30. Потери ---
    delte_G_tagul = Q_tagul_day - G_tagul - (V_tagul - V_tagul_prev)
    list_delte_g_tagul.append(delte_G_tagul)
    delte_G_tagul_month = sum(list_delte_g_tagul)

    # --- 31–32. Откачка нефти в МН ---
    G_upn_lodochny = Q_lodochny_day * K_otkachki - (V_upn_lodochny-V_upn_lodochny_prev) - (K_gupn_lodochny / 2) + Q_vo_day
    G_lodochny = G_upn_lodochny - G_ichem
    list_g_lodochny.append(G_lodochny)
    G_lodochny_month = sum(list_g_lodochny)

    # --- 33–34. Сводные потери и суммарная откачка ---
    delte_G_upn_lodochny = Q_lodochny_day + Q_vo_day - G_lodochny_uspv_yu - G_lodochny - (V_upn_lodochny - V_upn_lodochny_prev)
    list_delte_g_upn_lodochny.append(delte_G_upn_lodochny)
    G_upn_lodochny_month = sum(list_delte_g_upn_lodochny)
    G_tagul_lodochny = G_tagul + G_upn_lodochny + G_kchng
    list_g_tagul_lodochny.append(G_tagul_lodochny)
    G_tagul_lodochny_month = sum(list_g_tagul_lodochny)

    return {
        "Q_tagulsk_month": Q_tagulsk_month, "Q_lodochny_month": Q_lodochny_month, "V_upn_lodochny": V_upn_lodochny,
        "V_ichem": V_ichem, "V_lodochny": V_lodochny, "K_otkachki_month": K_otkachki_month, "G_lodochny_uspv_yu": G_lodochny_uspv_yu,
        "G_lodochny_uspv_yu_month": G_lodochny_uspv_yu_month, "G_sikn_tagul": G_sikn_tagul, "G_sikn_tagul_month": G_sikn_tagul_month,
        "delte_G_tagul": delte_G_tagul, "delte_G_tagul_month": delte_G_tagul_month, "G_upn_lodochny": G_upn_lodochny,
        "G_lodochny": G_lodochny, "G_lodochny_month": G_lodochny_month, "delte_G_upn_lodochny": delte_G_upn_lodochny,
        "G_upn_lodochny_month": G_upn_lodochny_month, "G_tagul_lodochny": G_tagul_lodochny, "G_tagul_lodochny_month": G_tagul_lodochny_month,
        "G_tagul_month":G_tagul_month,
    }

# ===============================================================
# -------------------- Блок «ЦППН-1»: ---------------------------
# ===============================================================
def CPPN_1 (
    V_upsv_yu_prev, V_upsv_s_prev, V_upsv_cps_prev, V_upsv_yu_0, V_upsv_s_0, V_upsv_cps_0,
    V_upsv_yu, V_upsv_s, V_upsv_cps,  V_lodochny_cps_upsv_yu_prev, G_lodochni_upsv_yu,
    G_sikn_tagul, flag_list
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
    V_lodochni_upsv_yu = _to_float(G_lodochni_upsv_yu)
    G_sikn_tagul = _to_float(G_sikn_tagul)
# 35. Расчет наличия нефти в РВС УПСВ-Юг, т:
    V_upsv_yu = V_upsv_yu_prev
    if not flag_list[0]:
        if V_upsv_yu_prev-1500 <= V_upsv_yu <= V_upsv_yu_prev+1500:
            V_upsv_yu = int(input("Введите корректное заначение для V_upsv_yu"))
    else:
        if V_upsv_yu_prev-2000 <= V_upsv_yu <= V_upsv_yu_prev+4000:
            print("f")
# 36. Расчет наличия нефти в РВС УПСВ-Север, т:
    V_upsv_s = V_upsv_s_prev
    if not flag_list[1]:
        if V_upsv_s_prev-1500 <= V_upsv_s <= V_upsv_s_prev+1500:
            V_upsv_s = int(input("Введите корректное заначение для V_upsv_s"))
    else:
        if V_upsv_s_prev-1500 <= V_upsv_s <= V_upsv_s_prev+2000:
            print("f")
# 37. Расчет наличия нефти в РВС ЦПС, т:
    V_upsv_cps = V_upsv_cps_prev
    if not flag_list[2]:
        if V_upsv_cps_prev - 1500 <= V_upsv_cps <= V_upsv_cps_prev + 1500:
            V_upsv_cps = int(input("Введите корректное заначение для V_upsv_cps"))
    else:
        if V_upsv_cps_prev - 2000 <= V_upsv_cps <= V_upsv_cps_prev + 3300:
            print("f")
# 38. Расчет суммарного наличия нефти в РП ЦППН-1, т:
    V_cppn_1_0 = V_upsv_yu_0+V_upsv_s_0+V_upsv_cps_0
    V_cppn_1 = V_upsv_yu + V_upsv_s + V_upsv_cps

#39. Расчет наличия нефти Лодочного ЛУ в РП на ЦПС и УПСВ - Юг, т:
    V_lodochny_cps_upsv_yu = V_lodochny_cps_upsv_yu_prev + V_lodochni_upsv_yu - G_sikn_tagul
    return {
        "V_upsv_yu":V_upsv_yu, "V_upsv_s": V_upsv_s, "V_upsv_cps": V_upsv_cps, "V_cppn_1_0": V_cppn_1_0,
        "V_cppn_1": V_cppn_1, "V_lodochny_cps_upsv_yu": V_lodochny_cps_upsv_yu,
    }
# ===============================================================
# ------------------ Блок «Сдача ООО «РН-Ванкор»: ---------------
# ===============================================================
def rn_vankor (
        F_vn, F_suzun_obsh, F_suzun_vankor, N, day
):
    F_vn = _to_float(F_vn)
    F_suzun_obsh = _to_float(F_suzun_obsh)
    F_suzun_vankor = _to_float(F_suzun_vankor)
    sum_value = 0


    list_f_vn_bn = []
    list_f_bn_suzun = []
    list_f_bn_suzun_vankor = []
# 40. Определение посуточной сдачи нефти АО «Ванкорнефть» через СИКН № 1209, т/сут:
    if day <= N-2:
        F_bn_vn = 50*round(F_vn/N/50)
    else:
        value = 50 * round(F_vn / N / 50)
        F_bn_vn_N = [value for _ in range(N - 2)]
        F_bn_vn = (F_vn - sum(F_bn_vn_N)) / 2
    list_f_vn_bn.append(F_bn_vn)
    F_bn_vn_month = sum(list_f_vn_bn)
# 41. Определение посуточной сдачи нефти АО «Сузун» (Сузун) через СИКН № 1209, т/сут:
    F_suzun = F_suzun_obsh - F_suzun_vankor
    if day < N-2:
        F_bn_suzun =50*round(F_suzun/N/50)
    else:
        value = 50 * round(F_suzun/N / 50)
        F_bn_suzun_N = [value for _ in range(N - 2)]
        F_bn_suzun = (F_suzun - sum(F_bn_suzun_N))/2
    list_f_bn_suzun.append(F_bn_suzun)
    F_bn_suzun_month = sum(list_f_bn_suzun)
# 42. Определение посуточной сдачи нефти АО «Сузун» (Ванкор) через СИКН № 1209, т/сут:
    if F_suzun_vankor < 20000:
        e = int(input("Введите на сколько дней распределить сдачу нефти: "))
        last_multiple_day = 0
        # Находим последний кратный день
        for days in range(N, 0, -1):
            if days % e == 0:
                last_multiple_day = days
                break
        # Рассчитываем значения для текущего дня
        if day % e == 0:
            if day != last_multiple_day:
                F_bp_suzun_vankor = 50 * round(F_suzun_vankor / e / 50)
                sum_value += F_bp_suzun_vankor
            else:
                value = F_suzun_vankor - sum_value
                F_bp_suzun_vankor = 50 * round(value / 50)
    else:
        if day <= N - 2:
            F_bp_suzun_vankor = 50 * round(F_suzun_vankor / N / 50)
        else:
            value = 50 * round(F_suzun_vankor / N / 50)
            F_bp_suzun_vankor_N = [value] * (N - 2)
            remaining_value = F_suzun_vankor - sum(F_bp_suzun_vankor_N)
            F_bp_suzun_vankor = 50 * round(remaining_value / 2 / 50)
    list_f_bn_suzun_vankor.append(F_bp_suzun_vankor)





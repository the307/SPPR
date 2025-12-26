"""
МОДУЛЬ РАСЧЕТОВ

Этот модуль содержит все функции расчета для различных блоков системы.
Каждая функция реализует бизнес-логику расчета для соответствующего блока.

СТРУКТУРА МОДУЛЯ:
-----------------
1. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ:
   - _to_float() - безопасное преобразование в float (из массива или скаляра)

2. БЛОКИ РАСЧЕТОВ:
   - suzun() - расчет блока СУЗУН
   - VO() - расчет блока ВОСТОК ОЙЛ
   - kchng() - расчет блока КЧНГ
   - lodochny() - расчет блока ЛОДОЧНЫЙ
   - CPPN_1() - расчет блока ЦППН-1
   - rn_vankor() - расчет блока РН-ВАНКОР
   - sikn_1208() - расчет блока СИКН-1208
   - TSTN() - расчет блока ТСТН
   - rn_vankor_proverka() - проверки и валидация для блока РН-ВАНКОР

ЛОГИКА РАБОТЫ КАЖДОГО БЛОКА:
-----------------------------
1. СУЗУН (suzun):
   - Расчет покупки и отгрузки нефти (G_buy_day, G_out_udt_day)
   - Расчет расхода на переработку (G_per)
   - Расчет объемов по месторождениям (Q_vankor, Q_suzun, Q_vslu, Q_tng, Q_vo)
   - Расчет объемов в резервуарах (V_upn_suzun, V_suzun_vslu, V_suzun_tng)
   - Расчет месячных накопленных значений

2. ВОСТОК ОЙЛ (VO):
   - Расчет объемов для Восток Ойл
   - Расчет накопленных данных за месяц

3. КЧНГ (kchng):
   - Расчет объемов для КЧНГ
   - Расчет накопленных данных за месяц

4. ЛОДОЧНЫЙ (lodochny):
   - Расчет коэффициента откачки (K_otkachki)
   - Валидация K_otkachki (сравнение с расчетным значением)
   - Расчет откачки нефти на УПСВ-Юг (G_lodochny_uspv_yu)
   - Расчет откачки в МН Тагульского месторождения (G_sikn_tagul)
   - Расчет объемов Тагульского месторождения (V_tagul, G_tagul)
   - Расчет потерь (delte_G_tagul)

5. ЦППН-1 (CPPN_1):
   - Расчет наличия нефти в РВС УПСВ-Юг (V_upsv_yu)
   - Расчет наличия нефти в РВС УПСВ-Север (V_upsv_s)
   - Расчет наличия нефти в РВС ЦПС (V_upsv_cps)
   - Валидация значений (проверка допустимых диапазонов ±1500 или ±2000)
   - Использование ручных коррекций из input.json при ошибках валидации

6. РН-ВАНКОР (rn_vankor):
   - Расчет сдачи нефти по недропользователям (F_bp_vn, F_bp_suzun, ...)
   - Проверка условий для первых 10 дней месяца (alarm_flag)
   - Расчет месячных накопленных значений

7. СИКН-1208 (sikn_1208):
   - Расчет откачки через СИКН-1208 (G_sikn)
   - Расчет потерь (delte_G_sikn)
   - Расчет объемов по различным направлениям

8. ТСТН (TSTN):
   - Расчет наличия нефти в резервуарах ЦТН (V_tstn_*)
   - Расчет по недропользователям
   - Валидация значений (проверка допустимых диапазонов)
   - Использование ручных коррекций из input.json

ВАЛИДАЦИЯ:
----------
- Проверка допустимых диапазонов значений
- Использование get_validation_value() для получения коррекций из input.json
- Вывод предупреждений при выходе значений за допустимые пределы
- Автоматическая замена значений (если настроено в input.json)

ОБРАБОТКА ОШИБОК:
-----------------
- ZeroDivisionError - проверка деления на ноль (например, в lodochny для K_otkachki)
- Использование значений по умолчанию при отсутствии данных
- Предупреждения вместо исключений для некритичных ошибок
"""
import numpy as np
from inputs import get_validation_value, get_delivery_period, get_validation_config



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
    # Обработка деления на ноль
    if Q_tagul_prev_month == 0 or abs(Q_tagul_prev_month) < 1e-10:
        print(f"Предупреждение: Q_tagul_prev_month = {Q_tagul_prev_month}, деление на ноль невозможно.")
        print(f"Используется текущее значение K_otkachki = {K_otkachki}")
        K_otkachki_month = K_otkachki
    else:
        K_otkachki_month = (G_lodochni_upsv_yu_prev_month / Q_tagul_prev_month)
    
    if abs(K_otkachki - K_otkachki_month) >= 0.01:
        # Используем значение из input.json для автоматической валидации
        from inputs import get_validation_config
        validation_config = get_validation_config()
        auto_replace = validation_config.get("auto_replace_K_otkachki", False)
        
        if auto_replace:
            print(f"Автоматически заменяем K_откачки {K_otkachki} на {K_otkachki_month}")
            K_otkachki = K_otkachki_month
        else:
            # Используем значение из input.json для автоматической замены
            validation_config = get_validation_config()
            if validation_config.get("auto_replace_K_otkachki", False):
                print(f"Автоматически заменяем K_откачки {K_otkachki} на {K_otkachki_month}")
                K_otkachki = K_otkachki_month
            else:
                # Если не задано автоматическое принятие, используем расчетное значение
                print(f"Предупреждение: K_откачки отличается от расчетного. Используется расчетное значение: {K_otkachki_month}")
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
            # G_sikn_tagul вне допустимого диапазона [900, 1500]
            pass
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
            # Получаем значение из input.json
            V_upsv_yu_correction = get_validation_value("V_upsv_yu", None)
            if V_upsv_yu_correction is not None:
                V_upsv_yu = int(V_upsv_yu_correction)
                print(f"Используется значение V_upsv_yu из input.json: {V_upsv_yu}")
            else:
                print(f"Предупреждение: V_upsv_yu вне допустимого диапазона. Используется расчетное значение: {V_upsv_yu}")
    else:
        if V_upsv_yu_prev-2000 <= V_upsv_yu <= V_upsv_yu_prev+4000:
            pass  # Значение в допустимом диапазоне
# 36. Расчет наличия нефти в РВС УПСВ-Север, т:
    if manual_V_upsv_s is not None:
        V_upsv_s = manual_V_upsv_s
    else:
        V_upsv_s = V_upsv_s_prev
    if not flag_list[1]:
        if V_upsv_s_prev-1500 <= V_upsv_s <= V_upsv_s_prev+1500:
            V_upsv_s:V_upsv_s
        else:
            # Получаем значение из input.json
            V_upsv_s_correction = get_validation_value("V_upsv_s", None)
            if V_upsv_s_correction is not None:
                V_upsv_s = int(V_upsv_s_correction)
                print(f"Используется значение V_upsv_s из input.json: {V_upsv_s}")
            else:
                print(f"Предупреждение: V_upsv_s вне допустимого диапазона. Используется расчетное значение: {V_upsv_s}")
    else:
        if V_upsv_s_prev-1500 <= V_upsv_s <= V_upsv_s_prev+2000:
            pass  # Значение в допустимом диапазоне
# 37. Расчет наличия нефти в РВС ЦПС, т:
    if manual_V_upsv_cps is not None:
        V_upsv_cps = V_upsv_cps
    else:
        V_upsv_cps = V_upsv_cps_prev
    if not flag_list[2]:
        if V_upsv_cps_prev - 1500 <= V_upsv_cps <= V_upsv_cps_prev + 1500:
            V_upsv_cps = V_upsv_cps
        else:
            # Получаем значение из input.json
            V_upsv_cps_correction = get_validation_value("V_upsv_cps", None)
            if V_upsv_cps_correction is not None:
                V_upsv_cps = int(V_upsv_cps_correction)
                print(f"Используется значение V_upsv_cps из input.json: {V_upsv_cps}")
            else:
                print(f"Предупреждение: V_upsv_cps вне допустимого диапазона. Используется расчетное значение: {V_upsv_cps}")
    else:
        if V_upsv_cps_prev - 2000 <= V_upsv_cps <= V_upsv_cps_prev + 3300:
            pass  # Значение в допустимом диапазоне
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
        if day < (N-2):
            F_bp_vn = base
        else:
            F_bp_vn = (F_vn - base * (N - 2))/2
    F_bp_vn_month = F_bp_vn_data.sum()+F_bp_vn # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 41. Сузун (общий)
    F_suzun = F_suzun_obsh - F_suzun_vankor
    if manual_F_bp_suzun is not None:
        F_bp_suzun = manual_F_bp_suzun
    else:
        base = round((F_suzun / N) / 50) * 50
        if day < (N-2):
            F_bp_suzun = base
        else:
            F_bp_suzun = F_suzun - (base * (N - 2))/2
    F_bp_suzun_month = F_bp_suzun_data.sum()+F_bp_suzun # данные отражены за 2 месяца (ноябрь, декабрь), чтобы расчет был корректен необходимо выбрать день расчета и снести ручные данные в manual_data.py до этого дня

    # =========================================================
    # 42. Сузун → Ванкор (через e)
    if manual_F_bp_suzun_vankor is not None:
        F_bp_suzun_vankor = manual_F_bp_suzun_vankor
    elif F_suzun_vankor < 20000:
        # Получаем периодичность сдачи из input.json
        e = get_delivery_period("suzun_vankor")
        print(f"Используется периодичность сдачи e={e} из input.json")
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
        # Получаем периодичность сдачи из input.json
        e = get_delivery_period("suzun_vankor")
        print(f"Используется периодичность сдачи e={e} из input.json")
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
        # Получаем периодичность сдачи из input.json
        e = get_delivery_period("suzun_vankor")
        print(f"Используется периодичность сдачи e={e} из input.json")
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
            V_gnsp_correction = get_validation_value("V_gnsp", None)
            if V_gnsp_correction is not None:
                V_gnsp = int(V_gnsp_correction)
                print(f"Используется значение V_gnsp из input.json: {V_gnsp}")
            else:
                print(f"Предупреждение: V_gnsp вне допустимого диапазона. Используется расчетное значение: {V_gnsp}")
    else:
        if V_gnsp_prev - 2000 <= V_gnsp <= V_gnsp_prev + 3000:
            V_gnsp = V_gnsp
        else:
            V_gnsp_correction = get_validation_value("V_gnsp", None)
            if V_gnsp_correction is not None:
                V_gnsp = int(V_gnsp_correction)
                print(f"Используется значение V_gnsp из input.json: {V_gnsp}")
            else:
                print(f"Предупреждение: V_gnsp вне допустимого диапазона. Используется расчетное значение: {V_gnsp}")
# 63.	Расчет наличия нефти в РП НПС-1, т:
    V_nps_1 = V_nps_1_prev
    if not flag_list[1]:
        if V_nps_1_prev - 700 <= V_nps_1 <= V_nps_1_prev + 700:
            V_nps_1 = V_nps_1
        else:
            V_nps_1_correction = get_validation_value("V_nps_1", None)
            if V_nps_1_correction is not None:
                V_nps_1 = int(V_nps_1_correction)
                print(f"Используется значение V_nps_1 из input.json: {V_nps_1}")
            else:
                print(f"Предупреждение: V_nps_1 вне допустимого диапазона. Используется расчетное значение: {V_nps_1}")
    else:
        if V_nps_1_prev - 2000 <= V_nps_1 <= V_nps_1_prev + 4000:
            V_nps_1 = V_nps_1
        else:
            V_nps_1_correction = get_validation_value("V_nps_1", None)
            if V_nps_1_correction is not None:
                V_nps_1 = int(V_nps_1_correction)
                print(f"Используется значение V_nps_1 из input.json: {V_nps_1}")
            else:
                print(f"Предупреждение: V_nps_1 вне допустимого диапазона. Используется расчетное значение: {V_nps_1}")
# 64.	Расчет наличия нефти в РП НПС-2, т:
    V_nps_2 = V_nps_2_prev
    if not flag_list[1]:
        if V_nps_2_prev - 700 <= V_nps_2 <= V_nps_2_prev + 700:
            V_nps_2 = V_nps_2
        else:
            V_nps_2_correction = get_validation_value("V_nps_2", None)
            if V_nps_2_correction is not None:
                V_nps_2 = int(V_nps_2_correction)
                print(f"Используется значение V_nps_2 из input.json: {V_nps_2}")
            else:
                print(f"Предупреждение: V_nps_2 вне допустимого диапазона. Используется расчетное значение: {V_nps_2}")
    else:
        if V_nps_2_prev - 2000 <= V_nps_2 <= V_nps_2_prev + 4000:
            V_nps_2 = V_nps_2
        else:
            V_nps_2_correction = get_validation_value("V_nps_2", None)
            if V_nps_2_correction is not None:
                V_nps_2 = int(V_nps_2_correction)
                print(f"Используется значение V_nps_2 из input.json: {V_nps_2}")
            else:
                print(f"Предупреждение: V_nps_2 вне допустимого диапазона. Используется расчетное значение: {V_nps_2}")
#65.	Расчет наличия нефти в РП КНПС
    V_knsp = (G_gpns - F + V_knps_prev + G_tagul + G_upn_lodochny + G_skn + G_kchng) - (V_nps_2 - V_nps_2_prev) - (V_nps_1-V_nps_1_prev)
    if not flag_list[2]:
        if V_knps_prev - 1500 <= V_knsp <= V_knps_prev + 1500:
            V_knsp = V_knsp
        else:
            V_knsp_correction = get_validation_value("V_knsp", None)
            if V_knsp_correction is not None:
                V_knsp = int(V_knsp_correction)
                print(f"Используется значение V_knsp из input.json: {V_knsp}")
            else:
                print(f"Предупреждение: V_knsp вне допустимого диапазона. Используется расчетное значение: {V_knsp}")
    else:
        if V_knps_prev - 2000 <= V_knsp <= V_knps_prev + 3000:
            V_knsp = V_knsp
        else:
            V_knsp_correction = get_validation_value("V_knsp", None)
            if V_knsp_correction is not None:
                V_knsp = int(V_knsp_correction)
                print(f"Используется значение V_knsp из input.json: {V_knsp}")
            else:
                print(f"Предупреждение: V_knsp вне допустимого диапазона. Используется расчетное значение: {V_knsp}")
# 66.	Расчет суммарного наличия нефти в резервуарах ЦТН, т:
    V_tstn_0 = V_gnsp_0 + V_nps_1_0 + V_nps_2_0 + V_knps_0
    V_tstn = V_gnsp_prev + V_nps_1_prev + V_nps_2_prev + V_knps_prev
# 67.	Расчет наличия нефти АО «Сузун» (ВСЛУ) в резервуарах ЦТН, т:
    V_tstn_suzun_vslu =  V_tstn_suzun_vslu_prev - F_suzun_vslu + G_suzun_vslu - F_suzun_vslu * (K_suzun/100)
    if 900 <=  V_tstn_suzun_vslu <= 4000:
        V_tstn_suzun_vslu =  V_tstn_suzun_vslu
    else:
        V_tstn_suzun_vslu_correction = get_validation_value("V_tstn_suzun_vslu", None)
        if V_tstn_suzun_vslu_correction is not None:
            V_tstn_suzun_vslu = int(V_tstn_suzun_vslu_correction)
            print(f"Используется значение V_tstn_suzun_vslu из input.json: {V_tstn_suzun_vslu}")
        else:
            print(f"Предупреждение: V_tstn_suzun_vslu вне допустимого диапазона. Используется расчетное значение: {V_tstn_suzun_vslu}")
# 68.	 Расчет наличия нефти АО «Сузун» (Ванкор) в резервуарах ЦТН, т:
    V_tstn_suzun_vankor = V_tstn_suzun_vankor_prev - F_suzun_vankor + (G_buy_day - G_per) - F_suzun_vankor * (K_vankor/100)
    if 900 <= V_tstn_suzun_vankor <= 5000:
        V_tstn_suzun_vankor = V_tstn_suzun_vankor
    else:
        V_tstn_suzun_vankor_correction = get_validation_value("V_tstn_suzun_vankor", None)
        if V_tstn_suzun_vankor_correction is not None:
            V_tstn_suzun_vankor = int(V_tstn_suzun_vankor_correction)
            print(f"Используется значение V_tstn_suzun_vankor из input.json: {V_tstn_suzun_vankor}")
        else:
            print(f"Предупреждение: V_tstn_suzun_vankor вне допустимого диапазона. Используется расчетное значение: {V_tstn_suzun_vankor}")
# 69.	Расчет наличия нефти АО «Сузун» (Сузун) в резервуарах ЦТН, т:
    V_tstn_suzun_0 = V_suzun_put_0 - V_tstn_vslu_0 -  V_tsnt_suzun_vankor_0
    if 2000 <= V_tstn_suzun_0 <= 6000:
        V_tstn_suzun_0 = V_tstn_suzun_0
    else:
        V_tstn_suzun_0_correction = get_validation_value("V_tstn_suzun_0", None)
        if V_tstn_suzun_0_correction is not None:
            V_tstn_suzun_0 = int(V_tstn_suzun_0_correction)
            print(f"Используется значение V_tstn_suzun_0 из input.json: {V_tstn_suzun_0}")
        else:
            print(f"Предупреждение: V_tstn_suzun_0 вне допустимого диапазона. Используется расчетное значение: {V_tstn_suzun_0}")
    V_tstn_suzun = V_tstn_suzun_prev - F_suzun + G_suzun_slu - F_suzun *(K_suzun/100)
    if 2000 <= V_tstn_suzun <= 6000:
        V_tstn_suzun=V_tstn_suzun
    else:
        V_tstn_suzun_correction = get_validation_value("V_tstn_suzun", None)
        if V_tstn_suzun_correction is not None:
            V_tstn_suzun = int(V_tstn_suzun_correction)
            print(f"Используется значение V_tstn_suzun из input.json: {V_tstn_suzun}")
        else:
            print(f"Предупреждение: V_tstn_suzun вне допустимого диапазона. Используется расчетное значение: {V_tstn_suzun}")
# 70.	Расчет наличия нефти ООО «СевКомНефтегаз» в резервуарах ЦТН, т:
    V_tstn_skn = V_tstn_skn_prev - F_skn + G_skn - F_skn * (K_skn/100)
    if 3000 <= V_tstn_skn <= 8000:
        V_tstn_skn=V_tstn_skn
    else:
        V_tstn_skn_correction = get_validation_value("V_tstn_skn", None)
        if V_tstn_skn_correction is not None:
            V_tstn_skn = int(V_tstn_skn_correction)
            print(f"Используется значение V_tstn_skn из input.json: {V_tstn_skn}")
        else:
            print(f"Предупреждение: V_tstn_skn вне допустимого диапазона. Используется расчетное значение: {V_tstn_skn}")
 # 71. Расчет наличия нефти ООО «Восток Оил» в резервуарах ЦТН, т:
    V_tstn_vo = V_tstn_vo_prev + G_ichem - F_vo - F_vo * (K_ichem/100)
    if 1000 <= V_tstn_vo <= 6000:
        V_tstn_vo = V_tstn_vo
    else:
        V_tstn_vo_correction = get_validation_value("V_tstn_vo", None)
        if V_tstn_vo_correction is not None:
            V_tstn_vo = int(V_tstn_vo_correction)
            print(f"Используется значение V_tstn_vo из input.json: {V_tstn_vo}")
        else:
            print(f"Предупреждение: V_tstn_vo вне допустимого диапазона. Используется расчетное значение: {V_tstn_vo}")
# 72.	Расчет наличия нефти АО «Таймырнефтегаз» в резервуарах ЦТН, т:
    V_tstn_tng = V_tstn_tng_prev + G_suzun_tng - F_tng - F_tng * (K_payaha/100)
    if 300 <= V_tstn_tng <= 6000:
        V_tstn_tng = V_tstn_tng
    else:
        V_tstn_tng_correction = get_validation_value("V_tstn_tng", None)
        if V_tstn_tng_correction is not None:
            V_tstn_tng = int(V_tstn_tng_correction)
            print(f"Используется значение V_tstn_tng из input.json: {V_tstn_tng}")
        else:
            print(f"Предупреждение: V_tstn_tng вне допустимого диапазона. Используется расчетное значение: {V_tstn_tng}")
# 73.	Расчет наличия нефти ООО «КЧНГ» (Русско-Реченское месторождение) в резервуарах ЦТН, т:
    V_tstn_kchng = V_tstn_kchng_prev + G_kchng - F_kchng - F_kchng * (K_tagul/100)
    if 1000 <= V_tstn_kchng <= 6000:
        V_tstn_kchng = V_tstn_kchng
    else:
        V_tstn_kchng_correction = get_validation_value("V_tstn_kchng", None)
        if V_tstn_kchng_correction is not None:
            V_tstn_kchng = int(V_tstn_kchng_correction)
            print(f"Используется значение V_tstn_kchng из input.json: {V_tstn_kchng}")
        else:
            print(f"Предупреждение: V_tstn_kchng вне допустимого диапазона. Используется расчетное значение: {V_tstn_kchng}")
# 74.	Расчет наличия нефти ООО «Тагульское» (Тагульский ЛУ) в резервуарах ЦТН, т:
    V_tstn_tagul = V_tstn_tagul_prev + G_tagul - F_tagul - F_tagul * (K_tagul/100)
    if 4000 <= V_tstn_tagul <= 12000:
        V_tstn_tagul = V_tstn_tagul
    else:
        V_tstn_tagul_correction = get_validation_value("V_tstn_tagul", None)
        if V_tstn_tagul_correction is not None:
            V_tstn_tagul = int(V_tstn_tagul_correction)
            print(f"Используется значение V_tstn_tagul из input.json: {V_tstn_tagul}")
        else:
            print(f"Предупреждение: V_tstn_tagul вне допустимого диапазона. Используется расчетное значение: {V_tstn_tagul}")
# 75.	Расчет наличия нефти ООО «Тагульское» (Лодочный ЛУ) в резервуарах ЦТН, т:
    V_tstn_lodochny = V_tstn_lodochny_prev + G_sikn_tagul - F_tagul_lpu - F_tagul_lpu * (K_lodochny/100)
    if 3000 <= V_tstn_lodochny <= 11000:
        V_tstn_lodochny = V_tstn_lodochny
    else:
        V_tstn_lodochny_correction = get_validation_value("V_tstn_lodochny", None)
        if V_tstn_lodochny_correction is not None:
            V_tstn_lodochny = int(V_tstn_lodochny_correction)
            print(f"Используется значение V_tstn_lodochny из input.json: {V_tstn_lodochny}")
        else:
            print(f"Предупреждение: V_tstn_lodochny вне допустимого диапазона. Используется расчетное значение: {V_tstn_lodochny}")
# 76.	Расчет наличия нефти ООО «Тагульское» (Всего) в резервуарах ЦТН, т:
    V_tstn_tagul_obsh_0 = V_tstn_tagul_0 + V_tstn_lodochny_0
    V_tstn_tagul_obsh = V_tstn_tagul + V_tstn_lodochny
    if 3000 <= V_tstn_tagul <= 11000:
        V_tstn_tagul = V_tstn_tagul
    else:
        V_tstn_tagul_correction = get_validation_value("V_tstn_tagul", None)
        if V_tstn_tagul_correction is not None:
            V_tstn_tagul = int(V_tstn_tagul_correction)
            print(f"Используется значение V_tstn_tagul из input.json: {V_tstn_tagul}")
        else:
            print(f"Предупреждение: V_tstn_tagul вне допустимого диапазона. Используется расчетное значение: {V_tstn_tagul}")
# 77.	Расчет наличия нефти ООО «РН-Ванкор» в резервуарах ЦТН (мертвые остатки в резервуарах), т:
    V_tstn_rn_vn = V_tstn_rn_vn_prev
# 78.	Расчет наличия нефти АО «Ванкорнефть» в резервуарах ЦТН, т:
    V_tstn_vn_0 = V_tstn_0 - V_tstn_rn_vn_0 - V_tstn_suzun_0 - V_tstn_tagul_obsh_0 - V_tstn_suzun_vankor_0 - V_tstn_suzun_vslu_0 - V_tstn_skn_0 - V_tstn_vo_0 - V_tstn_tng_0 - V_tstn_kchng_0
    if 4000 <= V_tstn_vn_0 <= 11000:
        V_tstn_vn_0 = V_tstn_vn_0
    else:
        V_tstn_vn_0_correction = get_validation_value("V_tstn_vn_0", None)
        if V_tstn_vn_0_correction is not None:
            V_tstn_vn_0 = int(V_tstn_vn_0_correction)
            print(f"Используется значение V_tstn_vn_0 из input.json: {V_tstn_vn_0}")
        else:
            print(f"Предупреждение: V_tstn_vn_0 вне допустимого диапазона. Используется расчетное значение: {V_tstn_vn_0}")
    V_tstn_vn = V_tstn - V_tstn_rn_vn - V_tstn_suzun - V_tstn_tagul_obsh - V_tstn_suzun_vankor -  V_tstn_suzun_vslu - V_tstn_skn - V_tstn_vo - V_tstn_tng - V_tstn_kchng
    if 4000 <= V_tstn_vn <= 11000:
        V_tstn_vn = V_tstn_vn
    else:
        V_tstn_vn_correction = get_validation_value("V_tstn_vn", None)
        if V_tstn_vn_correction is not None:
            V_tstn_vn = int(V_tstn_vn_correction)
            print(f"Используется значение V_tstn_vn из input.json: {V_tstn_vn}")
        else:
            print(f"Предупреждение: V_tstn_vn вне допустимого диапазона. Используется расчетное значение: {V_tstn_vn}")
    return {
        "G_gpns_i":G_gpns_i, "G_gpns_month":G_gpns_month, "G_gpns":G_gpns, "V_gnsp":V_gnsp, "V_nps_1":V_nps_1, "V_nps_2":V_nps_2, "V_knsp":V_knsp,
        "V_tstn_0":V_tstn_0, "V_tstn":V_tstn, " V_tstn_suzun_vslu": V_tstn_suzun_vslu, "V_tstn_suzun_vankor":V_tstn_suzun_vankor, "V_tstn_suzun_0":V_tstn_suzun_0,
        "V_tstn_suzun":V_tstn_suzun, "V_tstn_skn":V_tstn_skn,"V_tstn_vo":V_tstn_vo, "V_tstn_tng":V_tstn_tng, "V_tstn_kchng":V_tstn_kchng,
        "V_tstn_tagul":V_tstn_tagul, "V_tstn_lodochny":V_tstn_lodochny, "V_tstn_tagul_obsh":V_tstn_tagul_obsh, "V_tstn_tagul_obsh_0":V_tstn_tagul_obsh_0,
        "V_tstn_rn_vn":V_tstn_rn_vn, "V_tstn_vn":V_tstn_vn, "V_tstn_vn_0":V_tstn_vn_0
    }
# ===============================================================
# ---------------------- Блок «РН Ванкор» автобаланс: ----------------------
# ===============================================================
def rn_vankor_balance (
        V_upn_cuzun_prev, V_upn_suzun_0, VN_upn_suzun_min, N, V_upn_lodochny_prev, V_upn_lodochny_0, VN_upn_lodochny_min, V_upsv_yu_prev,
        V_upsv_yu_0, VN_upsv_yu_min, V_upsv_s_prev, V_upsv_s_0, VN_upsv_s_min, V_cps_prev, V_cps_0, VN_cps_min,
             ):
    V_upn_suzun = V_upn_cuzun_prev - (V_upn_suzun_0 - VN_upn_suzun_min)/N
    V_upn_lodochny = V_upn_lodochny_prev - (V_upn_lodochny_0 - VN_upn_lodochny_min)/N
    V_upsv_yu = V_upsv_yu_prev - (V_upsv_yu_0 - VN_upsv_yu_min)/N
    V_upsv_s = V_upsv_s_prev - (V_upsv_s_0 - VN_upsv_s_min)/N
    V_cps = V_cps_prev - (V_cps_0 - VN_cps_min)/N

# ===============================================================
# ---------------------- Блок «РН Ванкор» проверка: ----------------------
# ===============================================================
def rn_vankor_proverka(
        VA_upsv_yu_min, V_upsv_yu, VA_upsv_yu_max, V_upsv_yu_prev, V_delta_upsv_yu_max, flag_alarm, VO_delta_upsv_yu_max, VA_upsv_s_min, V_upsv_s,
        VA_upsv_s_max,V_upsv_s_prev, V_delta_upsv_s_max, VO_delta_upsv_s_max, VA_cps_min, V_cps, VA_cps_max, V_cps_prev, V_delta_cps_max,
        VO_delta_cps_max, VA_upn_suzun_min, V_upn_suzun, VA_upn_suzun_max, V_upn_suzun_prev, V_delta_upn_suzun_max, VO_delta_upn_suzun_max,
        VA_upn_lodochny_min, V_upn_lodochny, VA_upn_lodochny_max, V_upn_lodochny_prev, V_delta_upn_lodochny_max, VO_delta_upn_lodochny_max,
        VA_tagul_tr_min, V_tagul_tr, VA_tagul_tr_max, VA_gnps_min, V_gnps, VA_gnps__max, V_gnps_prev, VA_gnps_max, V_delta_gnps_max,
        VO_delta_gnps_max, VA_nps_1_min, V_nps_1, VA_nps_1_max, V_nps_1_prev, V_delta_nps_1_max, VO_delta_nps_1_max, VA_nps_2_min,
        V_nps_2, VA_nps_2_max, V_nps_2_prev, V_delta_nps_2_max, VO_delta_nps_2_max, VA_knps_min, V_knps, VA_knps_max, V_knps_prev, V_delta_knps_max,
        VO_delta_knps_max, V_ichem_min, V_ichem, V_ichem_max, V_lodochny_cps_uspv_yu, G_sikn_tagul, V_ctn_vn_min, V_ctn_vn, V_ctn_vn_max,
        V_ctn_suzun_min, V_ctn_suzun, V_ctn_suzun_max, V_ctn_suzun_vankor, V_ctn_suzun_vankor_max, V_ctn_suzun_vankor_min, V_ctn_suzun_vsly,
        V_ctn_suzun_vsly_min, V_ctn_suzun_vsly_max, V_ctn_tagul_obch, V_ctn_tagul_obch_max, V_ctn_tagul_obch_min, V_ctn_lodochny_min,
        V_ctn_lodochny, V_ctn_lodochny_max, V_ctn_tagul, V_ctn_tagul_min, V_ctn_tagul_max, V_ctn_skn, V_ctn_skn_min, V_ctn_skn_max,
        V_ctn_vo_min, V_ctn_vo, V_ctn_vo_max, V_ctn_tng_min, V_ctn_tng, V_ctn_tng_max, V_ctn_kchng_min, V_ctn_kchng, V_ctn_kchng_max,
        G_gnps, p_gnps, Q_gnps_min1, Q_gnps_max2, Q_gnps_max1, G_tagul_lodochny, p_nps_1_2, Q_nps_1_2_min1, Q_nps_1_2_max2, Q_nps_1_2_max1,
        G_knps, p_knps, Q_knps_min1, Q_knps_max2, Q_knps_max1,
              ):

# --- 83. Проверка выполнения условий по наличию нефти на УПСВ-Юг
    if (VA_upsv_yu_min <= V_upsv_yu or V_upsv_yu <= VA_upsv_yu_max):
        print("Проверка выполнения условий по наличию нефти на УПСВ-Юг выполнена")
    else:
        if (V_upsv_yu < VA_upsv_yu_min):
            print("Наличие нефти в РП УПСВ-Юг ниже минимального допустимого значения, необходимо уменьшить откачку нефти на СИКН-1208 путем увеличения (ручным вводом) наличия нефти в РП УПСВ-Юг (столбец F) до нужного значения")
        elif (V_upsv_yu > VA_upsv_yu_max):
            print("Наличие нефти в РП УПСВ-Юг выше максимально допустимого значения, необходимо увеличить откачку нефти на СИКН-1208 путем уменьшения (ручным вводом) наличия нефти в РП УПСВ-Юг (столбец F) до нужного значения")
    if (V_upsv_yu - V_upsv_yu_prev >= 0):
        if (abs(V_upsv_yu - V_upsv_yu_prev) <= V_delta_upsv_yu_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПСВ-Юг выполнена")
        else:
            print("Скорость наполнения РП УПСВ-Юг больше допустимой величины, необходимо увеличить откачку нефти на СИКН-1208 путем уменьшения (ручным вводом) наличия нефти в РП УПСВ-Юг (столбец F) до нужного значения")
    else:
        if (abs(V_upsv_yu_prev - V_upsv_yu) <= VO_delta_upsv_yu_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПСВ-Юг выполнена")
        else:
            print("Скорость опорожнения РП УПСВ-Юг больше допустимой величины, необходимо уменьшить откачку нефти на СИКН-1208 путем увеличения (ручным вводом) наличия нефти в РП УПСВ-Юг (столбец F) до нужного значения")


# --- 84. Проверка выполнения условий по наличию нефти на УПСВ-Север
    if (VA_upsv_s_min <= V_upsv_s or V_upsv_s <= VA_upsv_s_max):
        print("Проверка выполнения условий по наличию нефти на УПСВ-Север выполнена")
    else:
        if (V_upsv_s < VA_upsv_s_min):
            print("Наличие нефти в РП УПСВ-Север ниже минимального допустимого значения, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП УПСВ-Север (столбец G) до нужного значения")
        elif (V_upsv_s > VA_upsv_s_max):
            print("Наличие нефти в РП УПСВ-Север выше максимально допустимого значения, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП УПСВ-Север (столбец G) до нужного значения")

    if (V_upsv_s - V_upsv_s_prev >= 0):
        if (abs(V_upsv_s - V_upsv_s_prev) <= V_delta_upsv_s_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПСВ-Север выполнена")
        else:
            print("Скорость наполнения РП УПСВ Север больше допустимой величины, необходимо увеличить откачку нефти на СИКН 1208 путем уменьшения (ручным вводом) наличия нефти в РП УПСВ Север (столбец G) до нужного значения")
    else:
        if (abs(V_upsv_s_prev - V_upsv_s) <= VO_delta_upsv_s_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПСВ-Север выполнена")
        else:
            print("Скорость опорожнения РП УПСВ Север больше допустимой величины, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП УПСВ Север (столбец G) до нужного значения")
# --- 85. Проверка выполнения условий по наличию нефти на ЦПС
    if (VA_cps_min <= V_cps or V_cps <= VA_cps_max):
        print("Проверка выполнения условий по наличию нефти на ЦПС выполнена")
    else:
        if (V_cps < VA_cps_min):
            print("Наличие нефти в РП ЦПС ниже минимального допустимого значения, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП ЦПС (столбец H) до нужного значения")
        elif (V_cps > VA_cps_max):
            print("Наличие нефти в РП ЦПС выше максимально допустимого значения, необходимо увеличить откачку нефти на СИКН 1208 путем уменьшения (ручным вводом) наличия нефти в РП ЦПС (столбец H) до нужного значения")
    if (V_cps - V_cps_prev >= 0):
        if (abs(V_cps - V_cps_prev) <= V_delta_cps_max):
            print("Проверка выполнения условий по скорости наполнения РП на ЦПС выполнена")
        else:
            print("Скорость наполнения РП ЦПС больше допустимой величины, необходимо увеличить откачку нефти на СИКН 1208 путем уменьшения (ручным вводом) наличия нефти в РП ЦПС (столбец H) до нужного значения")
    else:
        if (abs(V_cps_prev - V_cps) <= VO_delta_cps_max):
            print("Проверка выполнения условий по скорости наполнения РП на ЦПС выполнена")
        else:
            print("Скорость опорожнения РП ЦПС больше допустимой величины, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП ЦПС (столбец H) до нужного значения")

# --- 86. Проверка выполнения условий по наличию нефти на УПН Сузун
    if (VA_upn_suzun_min <= V_upn_suzun or V_upn_suzun <= VA_upn_suzun_max):
        print("Проверка выполнения условий по наличию нефти на УПН Сузун выполнена")
    else:
        if (V_upn_suzun < VA_upn_suzun_min):
            print("Наличие нефти в РП УПН Сузун ниже минимального допустимого значения, необходимо уменьшить откачку нефти на СИКН-1208 путем увеличения (ручным вводом) наличия нефти в РП УПН Сузун (столбец V) до нужного значения")
        elif (V_upn_suzun > VA_upn_suzun_max):
            print("Наличие нефти в РП УПН Сузун выше максимально допустимого значения, необходимо увеличить откачку нефти на СИКН 1208 путем уменьшения (ручным вводом) наличия нефти в РП УПН Сузун (столбец V) до нужного значения")
    if (V_upn_suzun - V_upn_suzun_prev >= 0):
        if (abs(V_upn_suzun - V_upn_suzun_prev) <= V_delta_upn_suzun_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПН Сузун выполнена")
        else:
            print("Скорость наполнения РП УПН Сузун больше допустимой величины, необходимо увеличить откачку нефти на СИКН 1208 путем уменьшения (ручным вводом) наличия нефти в РП УПН Сузун (столбец V) до нужного значения")
    else:
        if (abs(V_upn_suzun_prev - V_upn_suzun) <= VO_delta_upn_suzun_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПН Сузун выполнена")
        else:
            print("Скорость опорожнения РП УПН Сузун больше допустимой величины, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП УПН Сузун (столбец V) до нужного значения")


# --- 87. Проверка выполнения условий по наличию нефти на УПН Лодочное
    if (VA_upn_lodochny_min <= V_upn_lodochny or V_upn_lodochny <= VA_upn_lodochny_max):
        print("Проверка выполнения условий по наличию нефти на УПН Лодочное выполнена")
    else:
        if (V_upn_lodochny < VA_upn_lodochny_min):
            print("Наличие нефти в РП УПН Лодочное ниже минимально допустимого значения, необходимо уменьшить откачку нефти на СИКН-1208 путем увеличения (ручным вводом) наличия нефти в РП УПН Лодочное (столбец AR) до нужного значения")
        elif (V_upn_lodochny > VA_upn_lodochny_max):
            print("Наличие нефти в РП УПН Лодочное выше максимально допустимого значения, необходимо увеличить откачку нефти на СИКН-1208 путем уменьшения (ручным вводом) наличия нефти в РП УПН Лодочное (столбец AR) до нужного значения")

    if (V_upn_lodochny-V_upn_lodochny_prev >= 0):
        if (abs(V_upn_lodochny-V_upn_lodochny_prev) <= V_delta_upn_lodochny_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПН Лодочное выполнена")
        else:
            print("Скорость наполнения РП УПН Лодочное больше допустимой величины, необходимо увеличить откачку нефти на СИКН 1208 путем уменьшения (ручным вводом) наличия нефти в РП УПН Лодочное (столбец AR) до нужного значения")
    else:
        if (abs(V_upn_lodochny_prev-V_upn_lodochny) <= VO_delta_upn_lodochny_max):
            print("Проверка выполнения условий по скорости наполнения РП на УПН Лодочное выполнена")
        else:
            print("Скорость опорожнения РП УПН Лодочное больше допустимой величины, необходимо уменьшить откачку нефти на СИКН 1208 путем увеличения (ручным вводом) наличия нефти в РП УПН Лодочное (столбец AR) до нужного значения")
# --- 88. Проверка выполнения условий по наличию нефти на Тагульском месторождении
    if (VA_tagul_tr_min <= V_tagul_tr or V_tagul_tr <= VA_tagul_tr_max):
        print("Проверка выполнения условий по наличию нефти на Тагульском месторождении")
    else:
        if (V_tagul_tr < VA_tagul_tr_min):
            print("Наличие нефти в трубопроводах и аппаратах ООО «Тагульское» ниже минимально допустимого значения, необходимо уменьшить откачку нефти в магистральный нефтепровод путем увеличения (ручным вводом) наличия нефти в трубопроводах и аппаратах ООО «Тагульское» (столбец AL) до нужного значения")
        elif (V_tagul_tr > VA_tagul_tr_max):
            print("Наличие нефти в трубопроводах и аппаратах ООО «Тагульское» выше максимально допустимого значения, необходимо увеличить откачку нефти в магистральный нефтепровод путем уменьшения (ручным вводом) наличия нефти в трубопроводах и аппаратах ООО «Тагульское» (столбец AL) до нужного значения")
# --- 89. Проверка выполнения условий по наличию нефти на ГНПС
    if (VA_gnps_min <= V_gnps or V_gnps <= VA_gnps__max):
        print("Проверка выполнения условий по наличию нефти на ГНПС выполнена")
    else:
        if (V_gnps < VA_gnps_min):
            print(
                "Наличие нефти в РП ГНПС ниже минимального допустимого значения, необходимо либо уменьшить (путем ручного ввода нужного значения) откачку нефти с ГНПС (столбец BE), либо увеличить поступление нефти через СИКН-1208 [путем уменьшения ручным вводом наличия нефти в РП УПСВ-Ю (столбец F), УПСВ-С (столбец G), ЦПС (столбец H) до нужных показателей]")
        elif (V_gnps > VA_gnps_max):
            print(
                "Наличие нефти в РП ГНПС выше максимально допустимого значения, необходимо либо увеличить (путем ручного ввода нужного значения) откачку нефти с ГНПС (столбец BE), либо уменьшить поступление нефти через СИКН-1208 [путем уменьшения ручным вводом наличия нефти в РП УПСВ-Ю (столбец F), УПСВ-С (столбец G), ЦПС (столбец H) до нужных показателей]")
    if (V_gnps - V_gnps_prev >= 0):
        if (abs(V_gnps - V_gnps_prev) <= V_delta_gnps_max):
            print("Проверка выполнения условий по скорости наполнения РП на ГНПС выполнена")
        else:
            print("Скорость наполнения РП ГНПС больше допустимой величины, необходимо либо увеличить (путем ручного ввода нужного значения) откачку нефти с ГНПС (столбец BE), либо уменьшить поступление нефти через СИКН-1208 [путем увеличения ручным вводом наличия нефти в РП УПСВ-Ю (столбец F), УПСВ-С (столбец G), ЦПС (столбец H) до нужных показателей]")
    else:
        if (abs(V_gnps_prev - V_gnps) <= VO_delta_gnps_max):
            print("Проверка выполнения условий по скорости наполнения РП на ГНПС выполнена")
        else:
            print("Скорость опорожнения РП больше допустимой величины, необходимо либо уменьшить (путем ручного ввода нужного значения) откачку нефти с ГНПС (столбец BE), либо увеличить поступление нефти через СИКН-1208 [путем увеличения ручным вводом наличия нефти в РП УПСВ-Ю (столбец F), УПСВ-С (столбец G), ЦПС (столбец H) до нужных показателей]")

# --- 90. Проверка выполнения условий по наличию нефти на НПС-1
    if (VA_nps_1_min <= V_nps_1 or V_nps_1 <= VA_nps_1_max):
        print("Проверка выполнения условий по наличию нефти на НПС-1 выполнена")
    else:
        if (V_nps_1 < VA_nps_1_min):
            print(
                "Наличие нефти в РП НПС-1 ниже минимального допустимого значения, необходимо уменьшить откачку нефти с НПС-1 на НПС-2 путем увеличения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
        elif (V_nps_1 > VA_nps_1_max):
            print(
                "Наличие нефти в РП НПС-1 выше максимально допустимого значения, необходимо увеличить откачку нефти с НПС-1 на НПС-2 путем увеличения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
    if (V_nps_1 - V_nps_1_prev >= 0):
        if (abs(V_nps_1 - V_nps_1_prev) <= V_delta_nps_1_max):
            print("Проверка выполнения условий по скорости наполнения РП на НПС-1 выполнена")
        else:
            print("Скорость наполнения РП НПС-1 больше допустимой величины, необходимо увеличить откачку нефти с НПС-1 на НПС-2 путем уменьшения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
    else:
        if (abs(V_nps_1_prev - V_nps_1) <= VO_delta_nps_1_max):
            print("Проверка выполнения условий по скорости наполнения РП на НПС-1 выполнена")
        else:
            print("Скорость опорожнения РП НПС-1 больше допустимой величины, необходимо уменьшить откачку нефти с НПС-1 на НПС-2 путем увеличения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
# --- 91. Проверка выполнения условий по наличию нефти на НПС-2
    if (VA_nps_2_min <= V_nps_2 or V_nps_2 <= VA_nps_2_max):
        print("Проверка выполнения условий по наличию нефти на НПС-1 выполнена")
    else:
        if (V_nps_2 < VA_nps_2_min):
            print(
                "Наличие нефти в РП НПС-1 ниже минимального допустимого значения, необходимо уменьшить откачку нефти с НПС-1 на НПС-2 путем увеличения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
        elif (V_nps_2 > VA_nps_2_max):
            print(
                "Наличие нефти в РП НПС-1 выше максимально допустимого значения, необходимо увеличить откачку нефти с НПС-1 на НПС-2 путем увеличения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
    if (V_nps_2 - V_nps_2_prev >= 0):
        if (abs(V_nps_2 - V_nps_2_prev) <= V_delta_nps_2_max):
            print("Проверка выполнения условий по скорости наполнения РП на НПС-1 выполнена")
        else:
            print("Скорость наполнения РП НПС-1 больше допустимой величины, необходимо увеличить откачку нефти с НПС-1 на НПС-2 путем уменьшения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
    else:
        if (abs(V_nps_2_prev - V_nps_2) <= VO_delta_nps_2_max):
            print("Проверка выполнения условий по скорости наполнения РП на НПС-1 выполнена")
        else:
            print("Скорость опорожнения РП НПС-1 больше допустимой величины, необходимо уменьшить откачку нефти с НПС-1 на НПС-2 путем увеличения (ручным вводом) наличия нефти в РП НПС-1 (столбец BG) до требуемого значения")
# --- 92. Проверка выполнения условий по наличию нефти на КНПС
    if (VA_knps_min <= V_knps or V_knps <= VA_knps_max):
        print("Проверка выполнения условий по наличию нефти на КНПС выполнена")
    else:
        if (V_knps < VA_knps_min):
            print("Наличие нефти в РП КНПС ниже минимального допустимого значения, необходимо уменьшить (ручным вводом) сдачу нефти АО «ВН» (столбец BX) в магистральный нефтепровод через СИКН 1209 ")
        elif (V_knps > VA_knps_max):
            print("Наличие нефти в РП КНПС выше максимально допустимого значения, необходимо увеличить (ручным вводом) сдачу нефти АО «ВН» (столбец BX) в магистральный нефтепровод через СИКН 1209 ")
    if (V_knps-V_knps_prev >= 0):
        if (abs(V_knps-V_knps_prev) <= V_delta_knps_max):
            print("Проверка выполнения условий по скорости наполнения РП на КНПС выполнена")
        else:
            print("Скорость наполнения РП КНПС больше допустимой величины, необходимо увеличить (ручным вводом) сдачу нефти АО «ВН» (столбец BX) в магистральный нефтепровод через СИКН 1209 ")
    else:
        if (abs(V_knps_prev-V_knps) <= VO_delta_knps_max):
            print("Проверка выполнения условий по скорости наполнения РП на КНПС выполнена")
        else:
            print("Скорость опорожнения РП КНПС больше допустимой величины, необходимо уменьшить (ручным вводом) сдачу нефти АО «ВН» (столбец BX) в магистральный нефтепровод через СИКН 1209 ")
# --- 93. Проверка наличия нефти ООО «Восток Ойл» (Ичемминский ЛУ) в РВС УПН Лодочное
    if (V_ichem_min <= V_ichem or V_ichem <= V_ichem_max):
        print("Проверка выполнения условий по наличию нефти ООО «Восток Ойл» (Ичемминский ЛУ) в РВС УПН Лодочное")
    else:
        if (V_ichem < V_ichem_min):
            print("Наличие нефти ООО «Восток Ойл» (Ичемминский ЛУ) в РВС УПН Лодочное ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) откачку нефти Ичемминского ЛУ в магистральный нефтепровод (столбец AW)")
        elif (V_ichem > V_ichem_max):
            print("Наличие нефти ООО «Восток Ойл» (Ичемминский ЛУ) в РВС УПН Лодочное больше максимально допустимого значения. Необходимо увеличить (ручным вводом) откачку нефти Ичемминского ЛУ в магистральный нефтепровод (столбец AW)")
# --- 94. Проверка выполнения условий наличия нефти Лодочного ЛУ в РП на ЦПС и УПСВ-Юг
    if (V_lodochny_cps_uspv_yu >= 0):
        print("Проверка выполнения условий по наличию нефти Лодочного ЛУ в РП на ЦПС и УПСВ-ЮГ")
    else:
        print("Значение наличия нефти Лодочного ЛУ на ЦПС и на УПСВ-Юг меньше нуля. Необходимо уменьшить откачку нефти ООО «Тагульское» на СИНК-1208 (столбец Р).")
        G_sikn_tagul = G_sikn_tagul - abs(V_lodochny_cps_uspv_yu)
# --- 95.	Проверка наличия нефти на объектах ЦТН по недропользователям
    if (V_ctn_vn_min <= V_ctn_vn or V_ctn_vn <= V_ctn_vn_max):
        print("Проверка выполнения условий по наличию нефти АО «Ванкорнефть» на ЦТН")
    else:
        if (V_ctn_vn < V_ctn_vn_min):
            print("Наличие нефти АО «Ванкорнефть» в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти АО «ВН» через СИКН-1209 (столбец BX) до нужного значения")
        elif (V_ctn_vn > V_ctn_vn_max):
            print("Наличие нефти АО «Ванкорнефть» в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти АО «ВН» через СИКН-1209 (столбец BX) до нужного значения")
    if (V_ctn_suzun_min <= V_ctn_suzun or V_ctn_suzun <= V_ctn_suzun_max):
        print("Проверка выполнения условий по наличию нефти АО «Сузун» на ЦТН")
    else:
        if (V_ctn_suzun < V_ctn_suzun_min):
            print("Наличие нефти АО «Сузун» (Сузун) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти АО «Сузун» (Сузун) через СИКН-1209 (столбец BY) до нужного значения")
        elif (V_ctn_suzun > V_ctn_suzun_max):
            print("Наличие нефти АО «Сузун» (Сузун) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти АО «Сузун» (Сузун) через СИКН-1209 (столбец BY) до нужного значения")
    if (V_ctn_suzun_vankor_min <= V_ctn_suzun_vankor or V_ctn_suzun_vankor <= V_ctn_suzun_vankor_max):
        print("Проверка выполнения условий по наличию нефти АО «Сузун» (Ванкор) на ЦТН")
    else:
        if (V_ctn_suzun_vankor < V_ctn_suzun_vankor_min):
            print("Наличие нефти АО «Сузун» (Ванкор) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти АО «Сузун» (Ванкор) через СИКН-1209 (столбец BZ) до нужного значения")
        elif (V_ctn_suzun_vankor > V_ctn_suzun_vankor_max):
            print("Наличие нефти АО «Сузун» (Ванкор) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти АО «Сузун» (Ванкор) через СИКН-1209 (столбец BZ) до нужного значения")
    if (V_ctn_suzun_vsly_min <= V_ctn_suzun_vsly or V_ctn_suzun_vsly <= V_ctn_suzun_vsly_max):
        print("Проверка выполнения условий по наличию нефти АО «Сузун» (ВСЛУ) на ЦТН")
    else:
        if (V_ctn_suzun_vsly < V_ctn_suzun_vsly_min):
            print("Наличие нефти АО «Сузун» (ВСЛУ) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти АО «Сузун» (ВСЛУ) через СИКН-1209 (столбец CA) до нужного значения")
        elif (V_ctn_suzun_vsly > V_ctn_suzun_vsly_max):
            print("Наличие нефти АО «Сузун» (ВСЛУ) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти АО «Сузун» (ВСЛУ) через СИКН-1209 (столбец CA) до нужного значения")
    if (V_ctn_tagul_obch_min <= V_ctn_tagul_obch or V_ctn_tagul_obch <= V_ctn_tagul_obch_max):
        print("Проверка выполнения условий по наличию нефти ООО «Тагульское» (всего) на ЦТН")
    else:
        if (V_ctn_tagul_obch < V_ctn_tagul_obch_min):
            print("Наличие нефти ООО «Тагульское» (всего) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти ООО «Тагульское» (Лодочный ЛУ) (столбец CC), ООО «Тагульское» (Тагульский ЛУ) (столбец CD)   через СИКН-1209 до нужного значения")
        elif (V_ctn_tagul_obch > V_ctn_tagul_obch_max):
            print("Наличие нефти ООО «Тагульское» (всего) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти ООО «Тагульское» (Лодочный ЛУ) (столбец CC), ООО «Тагульское» (Тагульский ЛУ) (столбец CD)   через СИКН-1209 до нужного значения")
    if (V_ctn_lodochny_min <= V_ctn_lodochny or V_ctn_lodochny <= V_ctn_lodochny_max):
        print("Проверка выполнения условий по наличию нефти ООО «Тагульское» (Лодочный ЛУ) на ЦТН")
    else:
        if (V_ctn_lodochny < V_ctn_lodochny_min):
            print("Наличие нефти ООО «Тагульское» (Лодочный ЛУ) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти ООО «Тагульское» (Лодочный ЛУ) (столбец CC) через СИКН-1209 до нужного значения")
        elif (V_ctn_lodochny > V_ctn_lodochny_max):
            print("Наличие нефти ООО «Тагульское» (Лодочный ЛУ) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти ООО «Тагульское» (Лодочный ЛУ) (столбец CC)  через СИКН-1209 до нужного значения")
    if (V_ctn_tagul_min <= V_ctn_tagul or V_ctn_tagul <= V_ctn_tagul_max):
        print("Проверка выполнения условий по наличию нефти ООО «Тагульское» (Тагульский ЛУ) на ЦТН")
    else:
        if (V_ctn_tagul < V_ctn_tagul_min):
            print("Наличие нефти ООО «Тагульское» (Тагульский ЛУ) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти ООО «Тагульское» (Тагульский ЛУ) (столбец CD)   через СИКН-1209 до нужного значения")
        elif (V_ctn_tagul > V_ctn_tagul_max):
            print("Наличие нефти ООО «Тагульское» (Тагульский ЛУ) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти ООО «Тагульское» (Тагульский ЛУ) (столбец CD)   через СИКН-1209 до нужного значения")
    if (V_ctn_skn_min <= V_ctn_skn or V_ctn_skn <= V_ctn_skn_max):
        print("Проверка выполнения условий по наличию нефти ООО «СевКомНефтегаз» на ЦТН")
    else:
        if (V_ctn_skn < V_ctn_skn_min):
            print("Наличие нефти ООО «СевКомНефтегаз» в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти ООО «СевКомНефтегаз» через СИКН-1209 (столбец CE) до нужного значения.")
        elif (V_ctn_skn > V_ctn_skn_max):
            print("Наличие нефти ООО «СевКомНефтегаз» в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти ООО «СевКомНефтегаз» через СИКН-1209 (столбец CE) до нужного значения.")
    if (V_ctn_vo_min <= V_ctn_vo or V_ctn_vo <= V_ctn_vo_max):
        print("Проверка выполнения условий по наличию нефти ООО «Восток Ойл» (Ичемминский ЛУ) на ЦТН")
    else:
        if (V_ctn_vo < V_ctn_vo_min):
            print("Наличие нефти ООО «Восток Ойл» (Ичемминский ЛУ) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти ООО «Восток Ойл» (Ичемминский ЛУ) через СИКН-1209 (столбец CF) до нужного значения")
        elif (V_ctn_vo > V_ctn_vo_max):
            print("Наличие нефти ООО «Восток Ойл» (Ичемминский ЛУ) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти ООО «Восток Ойл» (Ичемминский ЛУ) через СИКН-1209 (столбец CF) до нужного значения")
    if (V_ctn_tng_min <= V_ctn_tng or V_ctn_tng <= V_ctn_tng_max):
        print("Проверка выполнения условий по наличию нефти АО «Таймырнефтегаз» (Пайяхский ЛУ) на ЦТН")
    else:
        if (V_ctn_tng < V_ctn_tng_min):
            print("Наличие нефти АО «Таймырнефтегаз» (Пайяхский ЛУ) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти АО «Таймырнефтегаз» (Пайяхский ЛУ) через СИКН-1209 (столбец CG) до нужного значения")
        elif (V_ctn_tng > V_ctn_tng_max):
            print("Наличие нефти АО «Таймырнефтегаз» (Пайяхский ЛУ) в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти АО «Таймырнефтегаз» (Пайяхский ЛУ) через СИКН-1209 (столбец CG) до нужного значения")
    if (V_ctn_kchng_min <= V_ctn_kchng or V_ctn_kchng <= V_ctn_kchng_max):
        print("Проверка выполнения условий по наличию нефти ООО «КЧНГ» (Русско-Реченское месторождение) на ЦТН")
    else:
        if (V_ctn_kchng < V_ctn_kchng_min):
            print("Наличие нефти ООО «КЧНГ» (Русско-Реченское месторождение) в РП ЦТН ниже минимального допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти ООО «КЧНГ» (Русско-Реченское месторождение) через СИКН-1209 (столбец CH) до нужного значения.")
        elif (V_ctn_kchng > V_ctn_kchng_max):
            print("Наличие нефти ООО «КЧНГ» (Русско-Реченское месторождение)в РП ЦТН больше максимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти ООО «КЧНГ» (Русско-Реченское месторождение) через СИКН-1209 (столбец CH) до нужного значения")
# --- 96. Проверка соблюдения нормативных значений насосного оборудования ГНПС
    Q_gnps = G_gnps / (p_gnps / 100 * 24)
    if (Q_gnps < Q_gnps_min1):
        print("Расход нефти на насосы ГНПС ниже минимально допустимого значения. Необходимо увеличить (ручным вводом) откачку нефти с ГНПС (столбец BE) до нужного значения")
    elif (Q_gnps > Q_gnps_max2):
        print("Расход нефти на насосы ГНПС больше максимально допустимого значения. Необходимо уменьшить (ручным вводом) откачку нефти с ГНПС (столбец BE) до нужного значения")
    elif (Q_gnps <= Q_gnps_max1):
        print("Режим работы насосного оборудования 1-1-1")
    else:
        print("Режим работы насосного оборудования 2-2-2. Рекомендуется перераспределить объемы перекачиваемой нефти.")
    # --- 97. Проверка соблюдения нормативных значений насосного оборудования ГНПС
    Q_nps_1_2 = (G_gnps + G_tagul_lodochny + V_nps_1 - V_nps_1_prev + V_nps_2 - V_nps_2_prev) / (p_nps_1_2 / 100 * 24)
    if (Q_nps_1_2 < Q_nps_1_2_min1):
        print("Расход нефти на насосы НПС-1, НПС-2 больше максимально допустимого значения. Необходимо уменьшить (ручным вводом) откачку нефти с ГНПС (столбец BE) до нужного значения")
    elif (Q_nps_1_2 > Q_nps_1_2_max2):
        print("Расход нефти на насосы НПС-1, НПС-2 больше максимально допустимого значения. Необходимо уменьшить (ручным вводом) откачку нефти с ГНПС (столбец BE) до нужного значения")
    elif (Q_nps_1_2 <= Q_nps_1_2_max1):
        print("Режим работы насосного оборудования 1-1-1")
    else:
        print("Режим работы насосного оборудования 2-2-2. Рекомендуется перераспределить объемы перекачиваемой нефти.")
    # --- 98. Проверка соблюдения нормативных значений насосного оборудования КНПС
    Q_knps = G_knps / (p_knps / 100 * 24)
    if (Q_knps < Q_knps_min1):
        print("Расход нефти на насосы КНПС ниже минимально допустимого значения. Необходимо увеличить (ручным вводом) сдачу нефти через СИКН-1209 (столбцы BX-CH) до нужного значения ")
    elif (Q_knps > Q_knps_max2):
        print("Расход нефти на насосы КНПС больше максимально допустимого значения. Необходимо уменьшить (ручным вводом) сдачу нефти через СИКН-1209 (столбцы BX-CH) до нужного значения ")
    elif (Q_knps <= Q_knps_max1):
        print("Режим работы насосного оборудования 1-1-1")
    else:
        print("Режим работы насосного оборудования 2-2-2. Рекомендуется рассмотреть возможность перераспределения перекачиваемой нефти по дням.")
# ===============================================================
# ---------------------- Блок «Сравнения плановой сдачи нефти с бизнес-планом» ----------------------
# ===============================================================
# --- 99.	Расчет суммарной плановой сдачи нефти по недропользователям и расчет отклонений от БП:
def plan_sdacha (F_vn, F_vn_plan, F_suzun, F_suzun_vankor, F_suzun_plan, F_suzun_vankor_plan,
        F_suzun_vsly, F_suzun_vsly_plan, F_tagul_lpy, F_tagul_lpy_plan, F_tagul_tpy, F_tagul_tpy_plan, F_skn, F_vo_plan, F_vo, F_tng,
        F_tng_plan, F_kchng, F_kchng_plan):
    def delta(F, F_plan):
        return F.sum() - F_plan
    F_vn_delta = delta(F_vn, F_vn_plan)
    F_suzun_delta = delta(F_suzun, F_suzun_plan)
    F_suzun_vankor_delta = delta(F_suzun_vankor, F_suzun_vankor_plan)
    F_suzun_vsly_delta = delta(F_suzun_vsly, F_suzun_vsly_plan)
    F_tagul_lpy_delta = delta(F_tagul_lpy, F_tagul_lpy_plan)
    F_tagul_tpy_delta = delta(F_tagul_tpy, F_tagul_tpy_plan)
    F_tagul_delta = F_tagul_lpy_delta + F_tagul_tpy_delta
    F_skn_delta = delta(F_skn, F_vo_plan)
    F_vo_delta = delta(F_vo, F_vo_plan)
    F_tng_delta = delta(F_tng, F_tng_plan)
    F_kchng_delta = delta(F_kchng, F_kchng_plan)
    F_delta = F_vn_delta + F_suzun_delta + F_tagul_lpy_delta + F_tagul_tpy_delta + F_suzun_vankor_delta + F_suzun_vsly_delta + F_skn_delta + F_vo_delta + F_tng_delta + F_kchng_delta
# ===============================================================
# ---------------------- Блок «Сравнения плановой сдачи нефти с бизнес-планом» ----------------------
# ===============================================================
def balance_po_business_plan (
        V_vn_nm_ost_np, V_vn_nm_ost_app, V_vn_nm_ost_texn, V_vn_nm_path, Q_vn_condensate, Q_vn_oil, V_vn_oil, V_vn_condensate,
        V_vn_transport, G_vn_release_rn_drillig, G_vn_release_suzun, G_vn_release_well_service, V_vn_km_ost_np, V_vn_km_ost_app,
        V_vn_km_ost_texn, V_vn_km_path, F_vn_total, V_suzun_nm_ost_np, V_suzun_nm_ost_app, V_suzun_nm_ost_texn, V_suzun_nm_path,
        Q_suzun_oil, Q_suzun_condensate, V_suzun_oil, V_suzun_condensate, V_suzun_transport_suzun, V_suzun_transport_vankor,
        G_suzun_mupn, G_suzun_release_rn_drillig, F_suzun_vankor, F_suzun_total, V_suzun_km_path, V_vo_nm_ost_np, V_vo_nm_ost_app,
        V_vo_nm_ost_texn, V_vo_nm_path, Q_vo_oil, Q_vo_condensate, V_vo_oil, V_vo_condensate, V_vo_transport, G_vo_fuel, G_vo_fill,
        G_vn_fuel, G_vn_fill, V_vo_km_ost_np, V_vo_km_ost_app, V_vo_km_ost_texn, V_vo_km_path, G_vo_release, F_vo_total,
        V_lodochny_nm_ost_np, V_lodochny_nm_ost_app, V_lodochny_nm_ost_texn, V_lodochny_nm_path, Q_lodochny_oil, Q_lodochny_condensate,
        V_lodochny_oil, V_lodochny_transport, G_lodochny_fuel, G_lodochny_release_rn_drillig, V_lodochny_km_ost_np,
):

# Остатки нефти на ВПУ на начало месяца
    V_vn_nm_ost_vpy = V_vn_nm_ost_np + V_vn_nm_ost_app + V_vn_nm_ost_texn
# Остатки нефти (газового конденсата) на начало месяца, всего
    V_vn_nm_ost = V_vn_nm_ost_vpy + V_vn_nm_path
# Добыча нефти (газового конденсата)
    Q_vn_total = Q_vn_oil + Q_vn_condensate
#  Технологические потери нефти (газового конденсата)
    V_vn_lost = V_vn_oil + V_vn_condensate + V_vn_transport
# Расход нефти (газового конденсата) на собственные производственно-технологические нужды и топливо
    G_vn_own = G_vn_fuel + G_vn_fill
# Отпуск нефти (газового конденсата), всего
    G_vn_release = G_vn_release_rn_drillig + G_vn_release_suzun + G_vn_release_well_service
# Остатки нефти на ВПУ на конец месяца
    V_vn_km_ost_vpy = V_vn_km_ost_np + V_vn_km_ost_app + V_vn_km_ost_texn
# Остатки нефти (газового конденсата) на конец месяца, всего
    V_vn_km_ost = V_vn_km_ost_vpy + V_vn_km_path
# Изменение остатков нефти (газового конденсата) собственных, всего
    delte_V_vn_ost = V_vn_km_ost - V_vn_nm_ost
# Выполнение процедуры проверки
    V_vn_check = (V_vn_nm_ost + Q_vn_total) - (V_vn_lost + G_vn_own + G_vn_release + F_vn_total + V_vn_km_ost)
    if (V_vn_check == 0):
        print("Проверка пройдена.")
    else:
        print("Проверка не пройдена. Необходимо уточнить корректность введенных данных")
# _____________Формирование планового баланса добычи-сдачи нефти по АО «Сузун» (Бизнес-план)_____________
# Остатки нефти на СПУ на начало месяца
    V_suzun_nm_ost_spy = V_suzun_nm_ost_np + V_suzun_nm_ost_app + V_suzun_nm_ost_texn
# Остатки нефти (газового конденсата) на начало месяца, всего
    V_suzun_nm_ost = V_suzun_nm_ost_spy + V_suzun_nm_path
# Добыча нефти (газового конденсата)
    Q_suzun_total = Q_suzun_oil + Q_suzun_condensate
# Технологические потери нефти (газового конденсата)
    V_suzun_lost = V_suzun_oil + V_suzun_condensate + V_suzun_transport_suzun + V_suzun_transport_vankor
# Расход нефти (газового конденсата) на собственные производственно-технологические нужды и топливо
    G_suzun_own = G_suzun_mupn
# Отпуск нефти (газового конденсата), всего
    G_suzun_release = G_suzun_release_rn_drillig
# Сдача нефти (газового конденсата) АО «Сузун» (Сузунское м/р)
    F_suzun_suzun = F_suzun_total + F_suzun_vankor
# Остатки нефти на СПУ на конец месяца
    V_suzun_km_ost_spy = V_vn_km_ost_np + V_vn_km_ost_app + V_vn_km_ost_texn
# Остатки нефти (газового конденсата) на конец месяца, всего
    V_suzun_km_ost = V_suzun_km_ost_spy + V_suzun_km_path
# Изменение остатков нефти (газового конденсата) собственных, всего
    V_suzun_delta_ost = V_suzun_km_ost - V_suzun_nm_ost
# Выполнение процедуры проверки
    V_suzun_check = (V_suzun_nm_ost + Q_suzun_total) - (V_suzun_lost + G_suzun_own + G_suzun_release + F_suzun_suzun + V_suzun_km_ost)
    if (V_suzun_check == 0):
        print("Проверка пройдена.")
    else:
        print("Проверка не пройдена. Необходимо уточнить корректность введенных данных")
# _____________Формирование планового баланса добычи-сдачи нефти по ООО «Восток Ойл» (Бизнес-план)_____________
# Остатки нефти на ВПУ на начало месяца
    V_vo_nm_ost_vpy = V_vo_nm_ost_np + V_vo_nm_ost_app + V_vo_nm_ost_texn
# Остатки нефти (газового конденсата) на начало месяца, всего
    V_vo_nm_ost = V_vo_nm_ost_vpy + V_vo_nm_path
# Добыча нефти (газового конденсата)
    Q_vo_total = Q_vo_oil + Q_vo_condensate
# Технологические потери нефти (газового конденсата)
    V_vo_lost = V_vo_oil + V_vo_condensate + V_vo_transport
# Расход нефти (газового конденсата) на собственные производственно-технологические нужды и топливо
    G_vo_own = G_vo_fuel + G_vo_fill
# Остатки нефти на ВПУ на конец месяца
    V_vo_km_ost_vpy = V_vo_km_ost_np + V_vo_km_ost_app + V_vo_km_ost_texn
# Остатки нефти (газового конденсата) на конец месяца, всего
    V_vo_km_ost = V_vo_km_ost_vpy + V_vo_km_path
# Изменение остатков нефти (газового конденсата) собственных, всего
    delte_V_vo_ost = V_vo_km_ost - V_vo_nm_ost
# Выполнение процедуры проверки
    V_vo_check = (V_vo_nm_ost + Q_vo_total) - (V_vo_lost + G_vo_own + G_vo_release + F_vo_total + V_vo_km_ost)
    if (V_vo_check == 0):
        print("Проверка пройдена.")
    else:
        print("Проверка не пройдена. Необходимо уточнить корректность введенных данных")
#  Формирование планового баланса добычи-сдачи нефти по ООО «Тагульское» Лодочное месторождение (Бизнес-план)
# Остатки нефти на ЛПУ на начало месяца
    V_lodochny_nm_ost_lpy = V_lodochny_nm_ost_np + V_lodochny_nm_ost_app + V_lodochny_nm_ost_texn
# Остатки нефти (газового конденсата) на начало месяца, всего
    V_lodochny_nm_ost = V_lodochny_nm_ost_lpy + V_lodochny_nm_path
# Добыча нефти (газового конденсата)
    Q_lodochny_total = Q_lodochny_oil + Q_lodochny_condensate
# Технологические потери нефти (газового конденсата)
    V_lodochny_lost = V_lodochny_oil + V_lodochny_transport
# Расход нефти (газового конденсата) на собственные производственно-технологические нужды и топливо
    G_lodochny_release = G_lodochny_fuel
# Отпуск нефти (газового конденсата), всего
    G_lodochny_sobst = G_lodochny_release_rn_drillig
# Остатки нефти на ЛПУ на конец месяца
    V_lodochny_km_ost_lpy = V_lodochny_km_ost_np + V_lodochny_km_ost_app + V_lodochny_km_ost_texn


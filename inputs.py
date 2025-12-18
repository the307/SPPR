def get_suzun_inputs():
    """Централизует input() для блока SUZUN.
    Возвращает словарь с ключами, которые ожидает calculate.suzun.
    """
    G_payaha = float(input("Введите значение G_пайяха: "))
    G_suzun_tng = float(input("Введите значение G_сузун_тнг: "))
    K_g_suzun = float(input("Введите K_g_сузун: "))
    manual_V_upn_suzun = input( "Введите V_upn_suzun (Enter — оставить по предыдущим суткам): ")
    manual_V_suzun_vslu = input("Введите manual_V_suzun_vslu (Enter — оставить по предыдущим суткам): ")
    return {
        "G_payaha": G_payaha,
        "G_suzun_tng": G_suzun_tng,
        "K_g_suzun": K_g_suzun,
        "manual_V_upn_suzun": (
            float(manual_V_upn_suzun) if manual_V_upn_suzun.strip() != "" else None
        ),
        "manual_V_suzun_vslu": (
            float(manual_V_suzun_vslu) if manual_V_suzun_vslu.strip() != "" else None
        )

    }

def get_lodochny_inputs():
    """Централизует input() для блока LODOCHNY."""
    G_ichem = float(input("Введите G_ичем: "))
    K_otkachki = float(input("Введите K_откачки: "))
    K_gupn_lodochny = float(input("Введите K_G_УПН_Лодочный: "))
    K_g_tagul = float(input("Введите K_g_tagul: "))
    manual_V_upn_lodochny = input("Введите manual_V_upn_lodochny (Enter — оставить по предыдущим суткам): ")
    manual_G_sikn_tagul = input("Введите manual_G_sikn_tagul (Enter — оставить по предыдущим суткам): ")
    manual_V_tagul = input("Введите manual_V_tagul (Enter — оставить по предыдущим суткам): ")

    return {
        "G_ichem": G_ichem,
        "K_otkachki": K_otkachki,
        "K_gupn_lodochny": K_gupn_lodochny,
        "K_g_tagul": K_g_tagul,
        "manual_V_upn_lodochny": (
            float(manual_V_upn_lodochny) if manual_V_upn_lodochny.strip() != "" else None
        ),
        "manual_G_sikn_tagul": (
            float(manual_G_sikn_tagul) if manual_G_sikn_tagul.strip() != "" else None
        ),
        "manual_V_tagul": (
            float(manual_V_tagul) if manual_V_tagul.strip() != "" else None
        ),
    }
def get_cppn_1_inputs():
    """Централизует input() для блока CPPN_1."""
    manual_V_upsv_yu = input("Введите mmanual_V_upsv_yu (Enter — оставить по предыдущим суткам): ")
    manual_V_upsv_s = input("Введите manual_V_upsv_s (Enter — оставить по предыдущим суткам): ")
    manual_V_upsv_cps = input("Введите V_upsv_cps (Enter — оставить по предыдущим суткам): ")
    return {
        "manual_V_upsv_yu": (
            float(manual_V_upsv_yu) if manual_V_upsv_yu.strip() != "" else None
        ),
        "manual_V_upsv_s": (
            float(manual_V_upsv_s) if manual_V_upsv_s.strip() != "" else None
        ),
        "manual_V_upsv_cps": (
            float(manual_V_upsv_cps) if manual_V_upsv_cps.strip() != "" else None
        ),
    }
def get_rn_vankor_inputs():
    """Централизует input() для блока rn_vankor."""
    manual_F_bp_vn = input("Введите manual_F_bn_vn (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_suzun = input("Введите manual_F_bn_suzun (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_suzun_vankor = input("Введите manual_F_bp_suzun_vankor (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_tagul_tpu = input("Введите manual_F_bp_tagul_tpu (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_tagul_lpu = input("Введите manual_F_bp_tagul_lpu (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_skn = input("Введите manual_F_bp_skn (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_vo = input("Введите manual_F_pb_vo (Enter — оставить по предыдущим суткам): ")
    manual_F_bp_suzun_vslu = input("Введите manual_F_pb_vo (Enter — оставить по предыдущим суткам): ")
    manual_F_kchng = input("Введите manual_F_kchng (Enter — оставить по предыдущим суткам): ")

    return {
        "manual_F_bp_vn": (
            float(manual_F_bp_vn) if manual_F_bp_vn.strip() != "" else None
        ),
        "manual_F_bp_suzun": (
            float(manual_F_bp_suzun) if manual_F_bp_suzun.strip() != "" else None
        ),
        "manual_F_bp_suzun_vankor": (
            float(manual_F_bp_suzun_vankor) if manual_F_bp_suzun_vankor.strip() != "" else None
        ),
        "manual_F_bp_tagul_tpu": (
            float(manual_F_bp_tagul_tpu) if manual_F_bp_tagul_tpu.strip() != "" else None
        ),
        "manual_F_bp_tagul_lpu": (
            float(manual_F_bp_tagul_lpu) if manual_F_bp_tagul_lpu.strip() != "" else None
        ),
        "manual_F_bp_skn": (
            float(manual_F_bp_skn) if manual_F_bp_skn.strip() != "" else None
        ),
        "manual_F_bp_vo": (
            float(manual_F_bp_vo) if manual_F_bp_vo.strip() != "" else None
        ),
        "manual_F_bp_suzun_vslu": (
            float(manual_F_bp_suzun_vslu) if manual_F_bp_suzun_vslu.strip() != "" else None
        ),
        "manual_F_kchng": (
            float(manual_F_kchng) if manual_F_kchng.strip() != "" else None
        )

    }
def get_sikn_1208_inputs():
    K_delte_g_sikn = float(input("Введите К_G_sikn: "))
    return{
        "K_delte_g_sikn":K_delte_g_sikn,
    }
def get_TSTN_inputs():
    F_suzun_vslu = float(input("Введите F_suzun_vslu : "))
    K_suzun = float(input("Введите K_сузун: "))
    K_vankor = float(input("Введите K_vankor: "))
    G_skn = float(input("Введите G_skn: "))
    K_skn = float(input("Введите K_skn: "))
    K_ichem = float(input("Введите K_ichem: "))
    K_payaha = float(input("Введите K_payaha: "))
    K_tagul = float(input("Введите K_tagul: "))
    K_lodochny = float(input("Введите K_lodochny: "))
    return {
        "K_suzun":K_suzun,
        "K_vankor":K_vankor,
        "F_suzun_vslu":F_suzun_vslu,
        "G_skn":G_skn,
        "K_skn":K_skn,
        "K_ichem":K_ichem,
        "K_payaha":K_payaha,
        "K_tagul":K_tagul,
        "K_lodochny":K_lodochny,
    }
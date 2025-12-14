def get_suzun_inputs():
    """Централизует input() для блока SUZUN.
    Возвращает словарь с ключами, которые ожидает calculate.suzun.
    """
    G_payaha = float(input("Введите значение G_пайяха: "))
    G_suzun_tng = float(input("Введите значение G_сузун_тнг: "))
    K_g_suzun = float(input("Введите K_g_сузун: "))
    return {
        "G_payaha": G_payaha,
        "G_suzun_tng": G_suzun_tng,
        "K_g_suzun": K_g_suzun
    }

def get_lodochny_inputs():
    """Централизует input() для блока LODOCHNY."""
    G_ichem = float(input("Введите G_ичем: "))
    K_otkachki = float(input("Введите K_откачки: "))
    K_gupn_lodochny = float(input("Введите K_G_УПН_Лодочный: "))
    K_g_tagul = float(input("Введите K_g_tagul: "))
    return {
        "G_ichem": G_ichem,
        "K_otkachki": K_otkachki,
        "K_gupn_lodochny": K_gupn_lodochny,
        "K_g_tagul": K_g_tagul
    }
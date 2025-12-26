"""
Менеджер для управления вводом данных.
Позволяет использовать конфигурационные файлы вместо интерактивного ввода.
"""
import json
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class InputConfig:
    """Конфигурация входных данных."""
    # Сузун
    G_payaha: float = 0.0
    G_suzun_tng: float = 0.0
    K_g_suzun: float = 0.0
    manual_V_upn_suzun: Optional[float] = None
    manual_V_suzun_vslu: Optional[float] = None
    
    # Лодочный
    G_ichem: float = 0.0
    K_otkachki: float = 0.0
    K_gupn_lodochny: float = 0.0
    K_g_tagul: float = 0.0
    manual_V_upn_lodochny: Optional[float] = None
    manual_G_sikn_tagul: Optional[float] = None
    manual_V_tagul: Optional[float] = None
    
    # ЦППН-1
    manual_V_upsv_yu: Optional[float] = None
    manual_V_upsv_s: Optional[float] = None
    manual_V_upsv_cps: Optional[float] = None
    
    # РН-Ванкор
    manual_F_bp_vn: Optional[float] = None
    manual_F_bp_suzun: Optional[float] = None
    manual_F_bp_suzun_vankor: Optional[float] = None
    manual_F_bp_tagul_tpu: Optional[float] = None
    manual_F_bp_tagul_lpu: Optional[float] = None
    manual_F_bp_skn: Optional[float] = None
    manual_F_bp_vo: Optional[float] = None
    manual_F_bp_suzun_vslu: Optional[float] = None
    manual_F_kchng: Optional[float] = None
    
    # СИКН-1208
    K_delte_g_sikn: float = 0.0
    
    # ТСТН
    F_suzun_vslu: float = 0.0
    K_suzun: float = 0.0
    K_vankor: float = 0.0
    G_skn: float = 0.0
    K_skn: float = 0.0
    K_ichem: float = 0.0
    K_payaha: float = 0.0
    K_tagul: float = 0.0
    K_lodochny: float = 0.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputConfig':
        """Создать из словаря."""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return asdict(self)
    
    def save(self, filepath: str):
        """Сохранить в JSON файл."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: str) -> 'InputConfig':
        """Загрузить из JSON файла."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class InputManager:
    """Менеджер для управления вводом данных."""
    
    def __init__(self, config_file: Optional[str] = None, 
                 prompt_mode: str = "interactive"):
        """
        Инициализация менеджера ввода.
        
        Args:
            config_file: Путь к файлу конфигурации (JSON)
            prompt_mode: Режим работы ("interactive", "silent", "prompt")
        """
        self.prompt_mode = prompt_mode or os.getenv("PROMPT_MODE", "interactive")
        self.config = InputConfig()
        
        if config_file and Path(config_file).exists():
            self.config = InputConfig.load(config_file)
        elif config_file:
            # Создать файл с дефолтными значениями
            self.config.save(config_file)
            print(f"Создан файл конфигурации: {config_file}")
    
    def get_value(self, key: str, prompt: str, default: Optional[float] = None,
                  value_type: type = float) -> Any:
        """
        Получить значение параметра.
        
        Args:
            key: Ключ параметра
            prompt: Текст запроса
            default: Значение по умолчанию
            value_type: Тип значения
            
        Returns:
            Значение параметра
        """
        # Проверяем конфигурацию
        if hasattr(self.config, key):
            config_value = getattr(self.config, key)
            if config_value is not None:
                return config_value
        
        # Если режим silent, возвращаем default
        if self.prompt_mode == "silent":
            return default or 0.0
        
        # Интерактивный режим
        if self.prompt_mode == "interactive":
            try:
                value = input(f"{prompt} (по умолчанию: {default}): ").strip()
                if not value:
                    return default or 0.0
                return value_type(value)
            except (ValueError, KeyboardInterrupt):
                return default or 0.0
        
        return default or 0.0
    
    def get_suzun_inputs(self) -> Dict[str, Any]:
        """Получить входные данные для Сузун."""
        return {
            "G_payaha": self.get_value("G_payaha", "Введите значение G_пайяха"),
            "G_suzun_tng": self.get_value("G_suzun_tng", "Введите значение G_сузун_тнг"),
            "K_g_suzun": self.get_value("K_g_suzun", "Введите K_g_сузун"),
            "manual_V_upn_suzun": self.get_value(
                "manual_V_upn_suzun",
                "Введите V_upn_suzun (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_V_suzun_vslu": self.get_value(
                "manual_V_suzun_vslu",
                "Введите manual_V_suzun_vslu (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
        }
    
    def get_lodochny_inputs(self) -> Dict[str, Any]:
        """Получить входные данные для Лодочный."""
        return {
            "G_ichem": self.get_value("G_ichem", "Введите G_ичем"),
            "K_otkachki": self.get_value("K_otkachki", "Введите K_откачки"),
            "K_gupn_lodochny": self.get_value("K_gupn_lodochny", "Введите K_G_УПН_Лодочный"),
            "K_g_tagul": self.get_value("K_g_tagul", "Введите K_g_tagul"),
            "manual_V_upn_lodochny": self.get_value(
                "manual_V_upn_lodochny",
                "Введите manual_V_upn_lodochny (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_G_sikn_tagul": self.get_value(
                "manual_G_sikn_tagul",
                "Введите manual_G_sikn_tagul (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_V_tagul": self.get_value(
                "manual_V_tagul",
                "Введите manual_V_tagul (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
        }
    
    def get_cppn_1_inputs(self) -> Dict[str, Any]:
        """Получить входные данные для ЦППН-1."""
        return {
            "manual_V_upsv_yu": self.get_value(
                "manual_V_upsv_yu",
                "Введите manual_V_upsv_yu (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_V_upsv_s": self.get_value(
                "manual_V_upsv_s",
                "Введите manual_V_upsv_s (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_V_upsv_cps": self.get_value(
                "manual_V_upsv_cps",
                "Введите V_upsv_cps (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
        }
    
    def get_rn_vankor_inputs(self) -> Dict[str, Any]:
        """Получить входные данные для РН-Ванкор."""
        return {
            "manual_F_bp_vn": self.get_value(
                "manual_F_bp_vn",
                "Введите manual_F_bn_vn (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_suzun": self.get_value(
                "manual_F_bp_suzun",
                "Введите manual_F_bn_suzun (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_suzun_vankor": self.get_value(
                "manual_F_bp_suzun_vankor",
                "Введите manual_F_bp_suzun_vankor (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_tagul_tpu": self.get_value(
                "manual_F_bp_tagul_tpu",
                "Введите manual_F_bp_tagul_tpu (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_tagul_lpu": self.get_value(
                "manual_F_bp_tagul_lpu",
                "Введите manual_F_bp_tagul_lpu (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_skn": self.get_value(
                "manual_F_bp_skn",
                "Введите manual_F_bp_skn (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_vo": self.get_value(
                "manual_F_bp_vo",
                "Введите manual_F_pb_vo (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_bp_suzun_vslu": self.get_value(
                "manual_F_bp_suzun_vslu",
                "Введите manual_F_pb_vo (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
            "manual_F_kchng": self.get_value(
                "manual_F_kchng",
                "Введите manual_F_kchng (Enter — оставить по предыдущим суткам)",
                value_type=lambda x: float(x) if x.strip() else None
            ),
        }
    
    def get_sikn_1208_inputs(self) -> Dict[str, Any]:
        """Получить входные данные для СИКН-1208."""
        return {
            "K_delte_g_sikn": self.get_value("K_delte_g_sikn", "Введите К_G_sikn"),
        }
    
    def get_TSTN_inputs(self) -> Dict[str, Any]:
        """Получить входные данные для ТСТН."""
        return {
            "F_suzun_vslu": self.get_value("F_suzun_vslu", "Введите F_suzun_vslu"),
            "K_suzun": self.get_value("K_suzun", "Введите K_сузун"),
            "K_vankor": self.get_value("K_vankor", "Введите K_vankor"),
            "G_skn": self.get_value("G_skn", "Введите G_skn"),
            "K_skn": self.get_value("K_skn", "Введите K_skn"),
            "K_ichem": self.get_value("K_ichem", "Введите K_ichem"),
            "K_payaha": self.get_value("K_payaha", "Введите K_payaha"),
            "K_tagul": self.get_value("K_tagul", "Введите K_tagul"),
            "K_lodochny": self.get_value("K_lodochny", "Введите K_lodochny"),
        }


# Пример использования:
if __name__ == "__main__":
    # Создание менеджера с конфигурационным файлом
    manager = InputManager("config.json", prompt_mode="interactive")
    
    # Получение входных данных
    suzun_inputs = manager.get_suzun_inputs()
    print("Входные данные для Сузун:", suzun_inputs)
    
    # Сохранение конфигурации
    manager.config.save("config.json")


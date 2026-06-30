import hashlib
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()


def hash_pin(pin: str) -> str:
    salt = os.getenv('SECRET_KEY', 'fallback_seguro')
    return hashlib.sha256(f"{pin}{salt}".encode()).hexdigest()


def verificar_pin(pin: str, pin_hash: str) -> bool:
    return hash_pin(pin) == pin_hash


def fmt_br(valor: float) -> str:
    if valor is None:
        valor = 0
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_data_br(data_str: str) -> str:
    partes = data_str.split("/")
    if len(partes) == 3:
        return f"{partes[2]}-{partes[1]}-{partes[0]}"
    return data_str


def hoje_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def mes_atual_str() -> str:
    return date.today().strftime("%Y-%m")


def primeiro_dia_mes() -> str:
    return date.today().replace(day=1).strftime("%Y-%m-%d")


def ultimo_dia_mes() -> str:
    import calendar
    hoje = date.today()
    ultimo = calendar.monthrange(hoje.year, hoje.month)[1]
    return hoje.replace(day=ultimo).strftime("%Y-%m-%d")

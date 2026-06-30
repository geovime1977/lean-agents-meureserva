import os
from datetime import datetime, timedelta
from src.utils.db import get_connection

VALOR_ASSINATURA = 9.90
CHAVE_PIX_ASSINATURA = os.getenv('PIX_KEY', '')


def verificar_premium(usuario_id):
    conn = get_connection()
    usuario = conn.execute(
        "SELECT premium_until FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    conn.close()
    if not usuario or not usuario["premium_until"]:
        return False
    try:
        until = datetime.strptime(usuario["premium_until"], "%Y-%m-%d")
        return until >= datetime.now()
    except ValueError:
        return False


def ativar_premium(usuario_id, dias=30):
    conn = get_connection()
    until = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
    conn.execute(
        "UPDATE usuarios SET premium_until = ? WHERE id = ?",
        (until, usuario_id),
    )
    conn.commit()
    conn.close()
    return until

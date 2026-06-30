from datetime import datetime, date
from src.utils.db import get_connection
from src.utils.helpers import hoje_str


def agendar_pix(usuario_id, valor, chave_pix, descricao, data_agendamento):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pix_agendados (usuario_id, valor, chave_pix, descricao, data_agendamento) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, valor, chave_pix, descricao, data_agendamento),
    )
    conn.commit()
    conn.close()


def listar_pix_agendados(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM pix_agendados WHERE usuario_id = ? ORDER BY data_agendamento DESC, id DESC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_pix_pendentes_hoje(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM pix_agendados WHERE usuario_id = ? AND status = 'pendente' AND data_agendamento <= ? ORDER BY data_agendamento",
        (usuario_id, hoje_str()),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def marcar_realizado(pix_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "UPDATE pix_agendados SET status = 'realizado' WHERE id = ? AND usuario_id = ?",
        (pix_id, usuario_id),
    )
    conn.commit()
    conn.close()


def cancelar_pix(pix_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "UPDATE pix_agendados SET status = 'cancelado' WHERE id = ? AND usuario_id = ?",
        (pix_id, usuario_id),
    )
    conn.commit()
    conn.close()


def calcular_crc16(payload: str) -> str:
    crc = 0xFFFF
    for byte in payload.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def gerar_qrcode_copia_cola(chave_pix, valor, descricao=""):
    payload = f"00020126"
    gui = "0014br.gov.bcb.pix"
    payload += f"{len(gui):02d}{gui}"
    chave_len = len(chave_pix)
    payload += f"01{chave_len:02d}{chave_pix}"
    if descricao:
        payload += f"02{len(descricao):02d}{descricao}"
    valor_str = f"{valor:.2f}"
    payload += f"54{len(valor_str):02d}{valor_str}"
    payload += "5802BR"
    payload += "59" + f"{len('Usuario'):02d}Usuario"
    payload += "60" + f"{len('BR'):02d}BR"
    payload += "62070503***"
    payload += "6304"
    crc = calcular_crc16(payload)
    return payload + crc

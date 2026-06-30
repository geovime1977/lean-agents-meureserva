import os
import io
import hashlib
import base64
from datetime import datetime, timedelta
import qrcode
from src.utils.db import get_connection
from src.services.pix_scheduler import calcular_crc16
from src.services.subscription import ativar_premium, VALOR_ASSINATURA

CHAVE_PIX = "21970237295"

def gerar_payload_pix(valor, descricao, txid):
    payload = "00020126"
    gui = "0014br.gov.bcb.pix"
    payload += f"{len(gui):02d}{gui}"
    chave_len = len(CHAVE_PIX)
    payload += f"01{chave_len:02d}{CHAVE_PIX}"
    payload += f"02{len(descricao):02d}{descricao}"
    valor_str = f"{valor:.2f}"
    payload += f"54{len(valor_str):02d}{valor_str}"
    payload += "5802BR"
    payload += f"59{len('MeuReserva'):02d}MeuReserva"
    payload += "60" + f"{len('BR'):02d}BR"
    txid_curto = txid[:25]
    payload += f"62{len(txid_curto)+8:02d}05{len(txid_curto):02d}{txid_curto}"
    payload += "6304"
    crc = calcular_crc16(payload)
    return payload + crc

def gerar_qrcode_base64(payload):
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def criar_cobranca(usuario_id):
    conn = get_connection()
    txid = hashlib.md5(f"{usuario_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:25]
    conn.execute(
        "INSERT INTO cobrancas (usuario_id, txid, valor, status, criado_em) VALUES (?, ?, ?, 'pendente', ?)",
        (usuario_id, txid, VALOR_ASSINATURA, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    payload = gerar_payload_pix(VALOR_ASSINATURA, "Premium MeuReserva 30d", txid)
    qrcode_b64 = gerar_qrcode_base64(payload)
    return {"txid": txid, "payload": payload, "qrcode": qrcode_b64, "valor": VALOR_ASSINATURA, "chave_pix": CHAVE_PIX}

def verificar_cobranca_pendente(usuario_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM cobrancas WHERE usuario_id = ? AND status = 'pendente' ORDER BY id DESC LIMIT 1",
        (usuario_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def cobrancas_do_usuario(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM cobrancas WHERE usuario_id = ? ORDER BY criado_em DESC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def confirmar_pagamento(usuario_id, txid):
    conn = get_connection()
    cobranca = conn.execute(
        "SELECT * FROM cobrancas WHERE txid = ? AND usuario_id = ?", (txid, usuario_id)
    ).fetchone()
    if not cobranca:
        conn.close()
        return False
    conn.execute(
        "UPDATE cobrancas SET status = 'pago', pago_em = ? WHERE id = ?",
        (datetime.now().isoformat(), cobranca["id"]),
    )
    conn.commit()
    conn.close()
    ativar_premium(usuario_id)
    return True

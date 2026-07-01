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


def tlv(tag, valor):
    return f"{tag}{len(valor):02d}{valor}"


def gerar_payload_pix(valor, descricao, txid):
    gui = tlv("00", "br.gov.bcb.pix")
    chave = tlv("01", CHAVE_PIX)
    desc = tlv("02", descricao[:20])
    merchant_account = gui + chave + desc
    merchant_account_field = f"26{len(merchant_account):02d}{merchant_account}"

    valor_str = f"{valor:.2f}"
    amount = tlv("54", valor_str)
    country = "5802BR"
    merchant_name = tlv("59", "MeuReserva")
    merchant_city = tlv("60", "BR")

    txid_curto = txid[:25]
    txid_field = tlv("05", txid_curto)
    additional = tlv("62", txid_field)

    payload = (
        "000201"
        + merchant_account_field
        + "52040000"
        + "5303986"
        + amount
        + country
        + merchant_name
        + merchant_city
        + additional
        + "6304"
    )

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

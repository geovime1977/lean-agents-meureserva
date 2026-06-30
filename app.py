import os
import hashlib
from datetime import date
import streamlit as st
from src.utils.db import init_db
from src.utils.helpers import fmt_br
from src.views.auth import tela_login, tela_registro
from src.views.dashboard import renderizar as dashboard
from src.views.budget import renderizar as budget
from src.views.transactions import renderizar as transactions
from src.views.pix import renderizar as pix
from src.views.goals import renderizar as goals
from src.services.subscription import verificar_premium, ativar_premium, VALOR_ASSINATURA
from src.services.pagamento import criar_cobranca, verificar_cobranca_pendente, cobrancas_do_usuario, confirmar_pagamento
from src.models.user import atualizar_renda
from src.models.achievements import BADGES_INFO

st.set_page_config(
    page_title="Assistente Financeiro",
    page_icon="💰",
    layout="wide",
)

if "modo" not in st.session_state:
    st.session_state["modo"] = "login"

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

init_db()

if st.session_state["usuario"] is None:
    if st.session_state["modo"] == "login":
        tela_login()
    else:
        tela_registro()
    st.stop()

usuario = st.session_state["usuario"]
premium = verificar_premium(usuario["id"])

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/money.png", width=60)
    st.write(f"**{usuario['nome']}**")
    st.write(f"Renda: {fmt_br(usuario['renda_mensal'])}")

    with st.form("renda_form"):
        nova_renda = st.number_input(
            "Renda mensal", min_value=0.0, step=100.0,
            format="%.2f", value=usuario["renda_mensal"],
            label_visibility="collapsed",
        )
        if st.form_submit_button("Atualizar renda", use_container_width=True):
            atualizar_renda(usuario["id"], nova_renda)
            usuario["renda_mensal"] = nova_renda
            st.session_state["usuario"] = usuario
            st.rerun()

    st.divider()

    if premium:
        st.success("✅ Premium")
    else:
        st.warning("🔒 Gratuito")
        with st.expander(f"⭐ Premium R$ 9,90/mês"):
            pendente = verificar_cobranca_pendente(usuario["id"])
            if pendente:
                st.info("Pagamento pendente")
                from src.services.pagamento import gerar_qrcode_base64, gerar_payload_pix
                payload = gerar_payload_pix(VALOR_ASSINATURA, "Premium MeuReserva 30d", pendente["txid"])
                qrcode_b64 = gerar_qrcode_base64(payload)
                from PIL import Image
                import io, base64
                st.image(f"data:image/png;base64,{qrcode_b64}", width=200)
                st.code(payload, language="text", label="Pix copia-e-cola")
                if st.button("Ja paguei!", use_container_width=True, type="primary"):
                    if confirmar_pagamento(usuario["id"], pendente["txid"]):
                        st.success("Premium ativado!")
                        st.rerun()
                    else:
                        st.error("Nao encontramos o pagamento. Tente novamente.")
                if st.button("Cancelar"):
                    from src.utils.db import get_connection
                    conn = get_connection()
                    conn.execute("UPDATE cobrancas SET status='expirado' WHERE id=?", (pendente["id"],))
                    conn.commit()
                    conn.close()
                    st.rerun()
            else:
                if st.button("Assinar agora", use_container_width=True, type="primary"):
                    cobranca = criar_cobranca(usuario["id"])
                    st.rerun()
                cobrancas = cobrancas_do_usuario(usuario["id"])
                if cobrancas:
                    for c in cobrancas[:3]:
                        status = "✅ Pago" if c["status"] == "pago" else "❌ Expirado" if c["status"] == "expirado" else "⏳ Pendente"
                        st.caption(f"{status} - {c['criado_em'][:10]}")

    st.divider()

    paginas = {
        "📊 Dashboard": dashboard,
        "💰 Orçamento": budget,
        "💳 Transações": transactions,
        "💸 Micro-reserva Pix": pix,
        "🎯 Metas": goals,
    }

    pagina = st.radio("Navegação", list(paginas.keys()), label_visibility="collapsed")

    st.divider()
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state["usuario"] = None
        st.session_state["modo"] = "login"
        st.rerun()

paginas[pagina](usuario)

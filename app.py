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
from src.services.subscription import verificar_premium, ativar_premium, CHAVE_PIX_ASSINATURA, VALOR_ASSINATURA
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
        with st.expander("Assinar R$ 9,90/mês"):
            st.write(f"Chave Pix: {CHAVE_PIX_ASSINATURA}")
            st.code(
                f"Pix copia-e-cola:\n{CHAVE_PIX_ASSINATURA}",
                language="text",
            )
            st.write("Após pagar, solicite ativação manual.")
            chave = st.text_input("Chave de ativação", placeholder="Código recebido")
            if st.button("Ativar", use_container_width=True):
                secret_key = os.getenv('SECRET_PREMIUM_KEY')
                if secret_key:
                    valida = chave.strip() == secret_key
                else:
                    token = hashlib.sha256(f"{usuario['email']}_{date.today()}".encode()).hexdigest()[:12]
                    valida = chave.strip() == token
                if valida:
                    until = ativar_premium(usuario["id"])
                    st.success(f"Premium ativo até {until}")
                    st.rerun()
                else:
                    st.error("Chave inválida")

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

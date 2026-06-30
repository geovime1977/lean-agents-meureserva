import time
import streamlit as st
from src.models.user import criar_usuario, autenticar_usuario
from src.models.achievements import iniciar_achievs


def tela_login():
    if "login_tentativas" not in st.session_state:
        st.session_state["login_tentativas"] = 0
    if "login_bloqueado_ate" not in st.session_state:
        st.session_state["login_bloqueado_ate"] = 0
    st.title("💰 Assistente Financeiro")
    st.subheader("Faça seu login")

    agora = time.time()
    if st.session_state["login_bloqueado_ate"] > agora:
        restante = int(st.session_state["login_bloqueado_ate"] - agora)
        st.error(f"Muitas tentativas. Aguarde {restante}s.")
    else:
        st.session_state["login_tentativas"] = 0

    with st.form("login_form"):
        email = st.text_input("E-mail")
        pin = st.text_input("PIN de 4 dígitos", type="password", max_chars=4)
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Entrar", use_container_width=True)
        with col2:
            go_register = st.form_submit_button("Criar conta", use_container_width=True)

    if submitted:
        if st.session_state["login_bloqueado_ate"] > time.time():
            st.error("Aguarde o bloqueio.")
            return None
        if not email or not pin:
            st.error("Preencha e-mail e PIN")
            return None
        if len(pin) != 4 or not pin.isdigit():
            st.error("PIN deve ter exatamente 4 dígitos numéricos")
            return None
        usuario, erro = autenticar_usuario(email, pin)
        if usuario:
            st.session_state["login_tentativas"] = 0
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.session_state["login_tentativas"] += 1
            if st.session_state["login_tentativas"] >= 5:
                st.session_state["login_bloqueado_ate"] = time.time() + 30
                st.error("Muitas tentativas. Bloqueado por 30s.")
            else:
                st.error(erro)

    if go_register:
        st.session_state["modo"] = "registrar"
        st.rerun()

    return None


def tela_registro():
    st.title("💰 Assistente Financeiro")
    st.subheader("Criar nova conta")

    with st.form("register_form"):
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        pin = st.text_input("Crie um PIN de 4 dígitos", type="password", max_chars=4)
        pin_confirm = st.text_input("Confirme o PIN", type="password", max_chars=4)
        renda = st.number_input(
            "Renda mensal (R$)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            value=1621.0,
        )
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Criar conta", use_container_width=True)
        with col2:
            voltar = st.form_submit_button("Voltar", use_container_width=True)

    if submitted:
        if not nome or not email or not pin:
            st.error("Preencha todos os campos")
            return
        if len(pin) != 4 or not pin.isdigit():
            st.error("PIN deve ter exatamente 4 dígitos numéricos")
            return
        if pin != pin_confirm:
            st.error("PINs não conferem")
            return
        usuario_id, erro = criar_usuario(nome, email, pin, renda)
        if usuario_id:
            iniciar_achievs(usuario_id)
            st.success("Conta criada! Faça login.")
            st.session_state["modo"] = "login"
            st.rerun()
        else:
            st.error(f"Erro: {erro}")

    if voltar:
        st.session_state["modo"] = "login"
        st.rerun()

import streamlit as st
from src.utils.helpers import fmt_br, hoje_str
from src.services.pix_scheduler import (
    agendar_pix, listar_pix_agendados, listar_pix_pendentes_hoje,
    marcar_realizado, cancelar_pix, gerar_qrcode_copia_cola,
)
from src.services.subscription import verificar_premium


def renderizar(usuario):
    st.title("💸 Micro-reserva Pix")

    premium = verificar_premium(usuario["id"])
    if not premium:
        st.warning("🔒 Agendamento Pix é um recurso premium. Assine por R$ 9,90/mês.")
        return

    tabs = st.tabs(["Agendar", "Agendamentos", "Pendentes hoje"])

    with tabs[0]:
        st.subheader("Agendar micro-reserva Pix")
        with st.form("pix_form"):
            valor = st.number_input("Valor (R$)", min_value=0.01, step=1.0, format="%.2f", value=10.0)
            chave_pix = st.text_input("Chave Pix (CPF, e-mail, celular ou aleatória)", value="")
            descricao = st.text_input("Descrição (opcional)", placeholder="Ex: reserva emergencial")
            data_agendamento = st.date_input("Data do agendamento")
            submitted = st.form_submit_button("Agendar", use_container_width=True)
            if submitted:
                if not chave_pix:
                    st.error("Informe a chave Pix")
                elif valor <= 0:
                    st.error("Valor deve ser maior que zero")
                else:
                    agendar_pix(
                        usuario["id"], valor, chave_pix,
                        descricao, data_agendamento.strftime("%Y-%m-%d"),
                    )
                    st.success("Micro-reserva agendada!")
                    st.rerun()

    with tabs[1]:
        st.subheader("Agendamentos")
        agendados = listar_pix_agendados(usuario["id"])
        if agendados:
            for p in agendados:
                st.write(
                    f"{'✅' if p['status'] == 'realizado' else '⏳' if p['status'] == 'pendente' else '❌'} "
                    f"{fmt_br(p['valor'])} → {p['chave_pix'][:20]}... "
                    f"em {p['data_agendamento']} ({p['status']})"
                )
                if p['status'] == 'pendente':
                    col1, col2, col3 = st.columns([2, 2, 6])
                    with col1:
                        qr = gerar_qrcode_copia_cola(p['chave_pix'], p['valor'], p['descricao'])
                        with st.expander("🔗 Copia-e-cola"):
                            st.code(qr, language="text")
                            st.caption("Copie o código acima no seu app do banco")
                    with col2:
                        if st.button("✅ Realizado", key=f"real_{p['id']}"):
                            marcar_realizado(p["id"], usuario["id"])
                            st.rerun()
                    with col3:
                        if st.button("❌ Cancelar", key=f"cancel_{p['id']}"):
                            cancelar_pix(p["id"], usuario["id"])
                            st.rerun()
                st.divider()
        else:
            st.info("Nenhum agendamento encontrado.")

    with tabs[2]:
        st.subheader("Pendentes para hoje")
        pendentes = listar_pix_pendentes_hoje(usuario["id"])
        if pendentes:
            for p in pendentes:
                st.warning(
                    f"🔔 {fmt_br(p['valor'])} para {p['chave_pix']} - "
                    f"Agendado em: {p['data_agendamento']}"
                )
                st.caption(p["descricao"] if p["descricao"] else "Sem descrição")
                if st.button("✅ Marcar como realizado", key=f"pend_real_{p['id']}"):
                    marcar_realizado(p["id"], usuario["id"])
                    st.rerun()
        else:
            st.info("Nenhum Pix pendente para hoje.")

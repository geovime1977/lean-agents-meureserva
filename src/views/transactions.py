import streamlit as st
import pandas as pd
from io import StringIO
from src.utils.helpers import fmt_br, parse_data_br, hoje_str, mes_atual_str
from src.models.transaction import (
    adicionar_transacao, listar_transacoes, total_despesas, importar_csv, deletar_transacao,
)
from src.services.categorizer import categorizar
from src.services.budget_calc import todas_categorias
from src.services.subscription import verificar_premium
from src.services.gamification import verificar_streak, verificar_achievs_transacao


def renderizar(usuario):
    st.title("💳 Transações")
    mes = mes_atual_str()

    tabs = st.tabs(["Registrar", "Histórico", "Importar CSV"])

    with tabs[0]:
        with st.form("transacao_form"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["despesa", "receita"])
            with col2:
                data = st.date_input("Data")

            descricao = st.text_input("Descrição")
            categoria_auto = categorizar(descricao)

            if categoria_auto != "outros":
                st.caption(f"Categoria sugerida: {categoria_auto}")

            categorias = todas_categorias()
            categoria = st.selectbox(
                "Categoria",
                categorias,
                index=categorias.index(categoria_auto) if categoria_auto in categorias else 0,
            )

            valor = st.number_input("Valor (R$)", min_value=0.01, step=1.0, format="%.2f")

            if st.form_submit_button("Salvar", use_container_width=True):
                adicionar_transacao(
                    usuario["id"], tipo, categoria, valor,
                    descricao, data.strftime("%Y-%m-%d"),
                )
                verificar_achievs_transacao(usuario["id"])
                verificar_streak(usuario["id"])
                st.success("Transação registrada!")
                st.rerun()

    with tabs[1]:
        transacoes = listar_transacoes(usuario["id"], mes)
        if transacoes:
            total = total_despesas(usuario["id"], mes)
            st.write(f"Total de despesas no mês: **{fmt_br(total)}**")

            df = pd.DataFrame(transacoes)
            df["data"] = pd.to_datetime(df["data"])
            df["data"] = df["data"].dt.strftime("%d/%m/%Y")
            df["valor_fmt"] = df["valor"].apply(fmt_br)
            df["tipo_icone"] = df["tipo"].apply(lambda x: "📤" if x == "despesa" else "📥")
            df["exibir"] = df.apply(
                lambda r: f"{r['tipo_icone']} {r['data']} | {r['descricao'][:40]} | "
                          f"{r['categoria']} | {r['valor_fmt']}",
                axis=1,
            )
            for _, row in df.iterrows():
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.text(row["exibir"])
                with col_b:
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        deletar_transacao(row["id"], usuario["id"])
                        st.rerun()
        else:
            st.info("Nenhuma transação registrada este mês.")

    with tabs[2]:
        premium = verificar_premium(usuario["id"])
        if not premium:
            st.warning("🔒 Importação CSV é um recurso premium. Assine por R$ 9,90/mês.")
            return

        st.write("Formato: Data, Valor, Identificador, Descrição")
        st.write("Exemplo: 01/01/2024,-25,51ABCDE,Almoço")
        arquivo = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
        if arquivo:
            try:
                content = arquivo.read().decode("utf-8")
                linhas = [line.split(",") for line in content.strip().split("\n")]
                if not linhas:
                    st.error("Arquivo vazio")
                    return
                count = importar_csv(usuario["id"], linhas)
                if count > 0:
                    verificar_achievs_transacao(usuario["id"])
                    verificar_streak(usuario["id"])
                    st.success(f"{count} transações importadas!")
                    st.rerun()
                else:
                    st.warning("Nenhuma transação válida encontrada.")
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

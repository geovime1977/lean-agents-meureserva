import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.utils.helpers import fmt_br, mes_atual_str
from src.models.transaction import total_gastos_por_categoria, total_despesas, total_receitas
from src.models.achievements import listar_badges, BADGES_INFO
from src.services.budget_calc import calcular_orcamento
from src.services.gamification import obter_streak, get_badges_data


def renderizar(usuario):
    st.title("📊 Dashboard")
    renda = usuario["renda_mensal"]
    mes = mes_atual_str()
    gastos_cat = total_gastos_por_categoria(usuario["id"], mes)
    total_gasto = total_despesas(usuario["id"], mes)
    total_ganho = total_receitas(usuario["id"], mes)

    orc = calcular_orcamento(renda)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Renda declarada", fmt_br(renda))
    with col2:
        saldo = total_ganho - total_gasto
        st.metric("Saldo do mês", fmt_br(saldo), delta_color="off")
    with col3:
        st.metric("Total gasto", fmt_br(total_gasto))

    st.divider()

    st.subheader("📈 Orçamento 50/30/20 vs Real")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        gasto_nesse = sum(
            v for k, v in gastos_cat.items()
            if k in ["alimentação", "moradia", "transporte", "saúde", "educação"]
        )
        pct_nesse = (gasto_nesse / orc["necessidades"] * 100) if orc["necessidades"] else 0
        st.metric("Necessidades", fmt_br(gasto_nesse), f"{pct_nesse:.0f}% do orçado")
    with col_b:
        gasto_desejos = sum(
            v for k, v in gastos_cat.items()
            if k in ["lazer", "restaurante", "compras", "assinaturas", "viagem"]
        )
        pct_desejos = (gasto_desejos / orc["desejos"] * 100) if orc["desejos"] else 0
        st.metric("Desejos", fmt_br(gasto_desejos), f"{pct_desejos:.0f}% do orçado")
    with col_c:
        gasto_poupanca = sum(
            v for k, v in gastos_cat.items() if k == "poupança"
        )
        pct_poup = (gasto_poupanca / orc["poupanca"] * 100) if orc["poupanca"] else 0
        st.metric("Poupança", fmt_br(gasto_poupanca), f"{pct_poup:.0f}% do orçado")

    if gastos_cat:
        st.subheader("Gastos por categoria")
        df = pd.DataFrame(
            list(gastos_cat.items()), columns=["Categoria", "Valor"]
        )
        fig = px.bar(
            df, x="Categoria", y="Valor", text="Valor",
            title="Distribuição de gastos",
            color="Categoria",
        )
        fig.update_traces(texttemplate="R$ %{text:.2f}")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.pie(
            df, values="Valor", names="Categoria",
            title="Gastos por categoria (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    streak = obter_streak(usuario["id"])
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("🔥 Streak atual", f"{streak['streak_atual']} dias")
    with col_s2:
        st.metric("🏆 Streak máxima", f"{streak['streak_maxima']} dias")

    st.divider()
    st.subheader("🏅 Conquistas")
    badges_data = get_badges_data(usuario["id"])
    cols = st.columns(3)
    for i, badge in enumerate(badges_data):
        with cols[i % 3]:
            if badge["desbloqueado"]:
                st.success(f"{badge['icone']} {badge['nome']}")
                st.caption(badge["descricao"])
            else:
                st.markdown(f"🔒 {badge['nome']}")
                st.caption(badge["descricao"])

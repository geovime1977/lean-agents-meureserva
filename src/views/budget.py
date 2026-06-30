import streamlit as st
import plotly.graph_objects as go
from src.utils.helpers import fmt_br, mes_atual_str
from src.models.transaction import total_gastos_por_categoria
from src.services.budget_calc import calcular_orcamento, sugestao_por_categoria


def renderizar(usuario):
    st.title("💰 Orçamento 50/30/20")
    renda = usuario["renda_mensal"]

    st.info(
        f"Baseado na sua renda de {fmt_br(renda)} "
        f"(referência salário mínimo R$ 1.621,00)"
    )

    orc = calcular_orcamento(renda)
    sugestoes = sugestao_por_categoria(renda)
    mes = mes_atual_str()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Necessidades (50%)", fmt_br(orc["necessidades"]))
    with col2:
        st.metric("Desejos (30%)", fmt_br(orc["desejos"]))
    with col3:
        st.metric("Poupança (20%)", fmt_br(orc["poupanca"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Orçado",
        x=["Necessidades", "Desejos", "Poupança"],
        y=[orc["necessidades"], orc["desejos"], orc["poupanca"]],
        marker_color=["#1f77b4", "#ff7f0e", "#2ca02c"],
    ))

    gastos_cat = total_gastos_por_categoria(usuario["id"], mes)
    gasto_nesse = sum(
        v for k, v in gastos_cat.items()
        if k in ["alimentação", "moradia", "transporte", "saúde", "educação"]
    )
    gasto_desejos = sum(
        v for k, v in gastos_cat.items()
        if k in ["lazer", "restaurante", "compras", "assinaturas", "viagem"]
    )
    gasto_poup = sum(v for k, v in gastos_cat.items() if k == "poupança")

    fig.add_trace(go.Bar(
        name="Gasto",
        x=["Necessidades", "Desejos", "Poupança"],
        y=[gasto_nesse, gasto_desejos, gasto_poup],
        marker_color=["#aec7e8", "#ffbb78", "#98df8a"],
    ))
    fig.update_layout(
        barmode="group",
        title="Orçado vs Gasto no mês",
        yaxis_title="Valor (R$)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Sugestão de valores por categoria")

    cat_necessidades = {k: v for k, v in sugestoes.items() if k != "poupança" and k not in [
        "lazer", "restaurante", "compras", "assinaturas", "viagem"
    ]}
    cat_desejos = {k: v for k, v in sugestoes.items() if k in [
        "lazer", "restaurante", "compras", "assinaturas", "viagem"
    ]}

    st.write("**Necessidades**")
    cols = st.columns(len(cat_necessidades))
    for i, (cat, valor) in enumerate(cat_necessidades.items()):
        with cols[i]:
            st.metric(cat.capitalize(), fmt_br(valor))

    st.write("**Desejos**")
    cols = st.columns(len(cat_desejos))
    for i, (cat, valor) in enumerate(cat_desejos.items()):
        with cols[i]:
            st.metric(cat.capitalize(), fmt_br(valor))

    st.metric("Poupança", fmt_br(sugestoes.get("poupança", 0)))

    st.divider()
    st.subheader("Como funciona a regra 50/30/20")
    st.markdown("""
    - **50% Necessidades**: alimentação, moradia, transporte, saúde, educação
    - **30% Desejos**: lazer, restaurante, compras, assinaturas, viagem
    - **20% Poupança**: metas, reserva de emergência, investimentos
    """)

import streamlit as st
from src.utils.helpers import fmt_br, hoje_str
from src.utils.db import get_connection
from src.services.gamification import verificar_streak, verificar_achievs_meta


def criar_meta(usuario_id, nome, valor_meta, data_limite):
    conn = get_connection()
    conn.execute(
        "INSERT INTO metas (usuario_id, nome, valor_meta, data_limite) VALUES (?, ?, ?, ?)",
        (usuario_id, nome, valor_meta, data_limite),
    )
    conn.commit()
    conn.close()


def listar_metas(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM metas WHERE usuario_id = ? ORDER BY concluida ASC, data_limite ASC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def atualizar_meta(meta_id, usuario_id, valor):
    conn = get_connection()
    meta = conn.execute(
        "SELECT * FROM metas WHERE id = ? AND usuario_id = ?", (meta_id, usuario_id)
    ).fetchone()
    if not meta:
        conn.close()
        return
    novo_valor = meta["valor_atual"] + valor
    concluida = 1 if novo_valor >= meta["valor_meta"] else 0
    novo_valor = min(novo_valor, meta["valor_meta"])
    conn.execute(
        "UPDATE metas SET valor_atual = ?, concluida = ? WHERE id = ? AND usuario_id = ?",
        (novo_valor, concluida, meta_id, usuario_id),
    )
    conn.commit()
    conn.close()


def deletar_meta(meta_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM metas WHERE id = ? AND usuario_id = ?",
        (meta_id, usuario_id),
    )
    conn.commit()
    conn.close()


def renderizar(usuario):
    st.title("🎯 Metas Financeiras")

    with st.expander("➕ Nova meta"):
        with st.form("meta_form"):
            nome = st.text_input("Nome da meta")
            valor_meta = st.number_input("Valor necessário (R$)", min_value=1.0, step=50.0, format="%.2f")
            data_limite = st.date_input("Data limite")
            if st.form_submit_button("Criar meta", use_container_width=True):
                if nome and valor_meta > 0:
                    criar_meta(usuario["id"], nome, valor_meta, data_limite.strftime("%Y-%m-%d"))
                    verificar_achievs_meta(usuario["id"])
                    st.success("Meta criada!")
                    st.rerun()
                else:
                    st.error("Preencha nome e valor")

    st.divider()
    metas = listar_metas(usuario["id"])
    if not metas:
        st.info("Nenhuma meta cadastrada. Crie a primeira!")
        return

    for meta in metas:
        progresso = meta["valor_atual"] / meta["valor_meta"] * 100 if meta["valor_meta"] > 0 else 0
        status = "✅ Concluída" if meta["concluida"] else "⏳ Em andamento"
        with st.container():
            col1, col2, col3 = st.columns([4, 4, 2])
            with col1:
                st.write(f"**{meta['nome']}**")
                st.write(f"{status} | {fmt_br(meta['valor_atual'])} / {fmt_br(meta['valor_meta'])}")
                if meta["data_limite"]:
                    st.caption(f"Limite: {meta['data_limite']}")
            with col2:
                st.progress(min(progresso / 100, 1.0), text=f"{progresso:.1f}%")
            with col3:
                if not meta["concluida"]:
                    with st.form(key=f"add_{meta['id']}"):
                        add_valor = st.number_input(
                            "Adicionar (R$)", min_value=0.01, step=10.0,
                            format="%.2f", key=f"val_{meta['id']}",
                            label_visibility="collapsed",
                        )
                        if st.form_submit_button("+", use_container_width=True):
                            atualizar_meta(meta["id"], usuario["id"], add_valor)
                            verificar_achievs_meta(usuario["id"])
                            verificar_streak(usuario["id"])
                            st.rerun()
                if st.button("🗑️", key=f"del_meta_{meta['id']}"):
                    deletar_meta(meta["id"], usuario["id"])
                    st.rerun()
            st.divider()

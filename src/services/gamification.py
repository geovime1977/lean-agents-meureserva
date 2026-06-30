from datetime import datetime, date
from src.utils.db import get_connection
from src.models.achievements import (
    desbloquear, atualizar_progresso,
    listar_achievs, listar_badges, BADGES_INFO,
)


def obter_streak(usuario_id):
    conn = get_connection()
    streak = conn.execute(
        "SELECT streak_atual, streak_maxima, ultima_data FROM streaks WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()
    conn.close()
    if not streak:
        return {"streak_atual": 0, "streak_maxima": 0, "ultima_data": None}
    return dict(streak)


def verificar_streak(usuario_id):
    conn = get_connection()
    streak = conn.execute(
        "SELECT * FROM streaks WHERE usuario_id = ?", (usuario_id,)
    ).fetchone()
    if not streak:
        conn.execute(
            "INSERT INTO streaks (usuario_id) VALUES (?)", (usuario_id,)
        )
        conn.commit()
        conn.close()
        return {"atual": 0, "maxima": 0, "ultima": None}

    hoje = date.today()
    if streak["ultima_data"]:
        ultima = datetime.strptime(streak["ultima_data"], "%Y-%m-%d").date()
        diff = (hoje - ultima).days
        if diff == 1:
            novo_streak = streak["streak_atual"] + 1
            nova_maxima = max(novo_streak, streak["streak_maxima"])
            conn.execute(
                "UPDATE streaks SET streak_atual = ?, streak_maxima = ?, ultima_data = ? WHERE usuario_id = ?",
                (novo_streak, nova_maxima, hoje.strftime("%Y-%m-%d"), usuario_id),
            )
            if novo_streak >= 3:
                desbloquear(usuario_id, "streak_3")
            if novo_streak >= 7:
                desbloquear(usuario_id, "streak_7")
            if novo_streak >= 30:
                desbloquear(usuario_id, "streak_30")
        elif diff > 1:
            conn.execute(
                "UPDATE streaks SET streak_atual = 0, ultima_data = ? WHERE usuario_id = ?",
                (hoje.strftime("%Y-%m-%d"), usuario_id),
            )
    else:
        conn.execute(
            "UPDATE streaks SET streak_atual = 1, streak_maxima = 1, ultima_data = ? WHERE usuario_id = ?",
            (hoje.strftime("%Y-%m-%d"), usuario_id),
        )
    conn.commit()
    streak = conn.execute(
        "SELECT * FROM streaks WHERE usuario_id = ?", (usuario_id,)
    ).fetchone()
    conn.close()
    return dict(streak)


def verificar_achievs_transacao(usuario_id):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) as c FROM transacoes WHERE usuario_id = ?",
        (usuario_id,),
    ).fetchone()["c"]
    conn.close()

    if count >= 1:
        desbloquear(usuario_id, "primeiro_registro")
    if count >= 5:
        desbloquear(usuario_id, "cinco_despesas")
    if count >= 10:
        desbloquear(usuario_id, "dez_despesas")


def verificar_achievs_meta(usuario_id):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) as c FROM metas WHERE usuario_id = ?", (usuario_id,)
    ).fetchone()["c"]
    meta_concluida = conn.execute(
        "SELECT COUNT(*) as c FROM metas WHERE usuario_id = ? AND concluida = 1",
        (usuario_id,),
    ).fetchone()["c"]
    conn.close()
    if count >= 1:
        desbloquear(usuario_id, "meta_criada")
    if meta_concluida >= 1:
        desbloquear(usuario_id, "meta_concluida")


def verificar_achievs_orcamento(usuario_id, dentro_orcamento):
    if dentro_orcamento:
        desbloquear(usuario_id, "orcamento_respeitado")


def get_badges_data(usuario_id):
    achievs = listar_achievs(usuario_id)
    badges = listar_badges(usuario_id)
    badge_ids = {b["badge_id"] for b in badges}
    resultado = []
    for a in achievs:
        info = BADGES_INFO.get(a["achiev_id"], {"nome": a["achiev_id"], "icone": "🎯", "descricao": ""})
        resultado.append({
            "id": a["achiev_id"],
            "nome": info["nome"],
            "icone": info["icone"],
            "descricao": info["descricao"],
            "desbloqueado": a["achiev_id"] in badge_ids,
        })
    return resultado

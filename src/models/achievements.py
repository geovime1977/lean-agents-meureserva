from src.utils.db import get_connection


def iniciar_achievs(usuario_id):
    achievs = [
        "primeiro_registro", "cinco_despesas", "dez_despesas",
        "meta_criada", "meta_concluida", "orcamento_respeitado",
        "streak_3", "streak_7", "streak_30",
    ]
    conn = get_connection()
    for a_id in achievs:
        conn.execute(
            "INSERT OR IGNORE INTO achievs (usuario_id, achiev_id) VALUES (?, ?)",
            (usuario_id, a_id),
        )
    conn.commit()
    conn.close()


def atualizar_progresso(usuario_id, achiev_id, progresso):
    conn = get_connection()
    conn.execute(
        "UPDATE achievs SET progresso = MAX(progresso, ?) WHERE usuario_id = ? AND achiev_id = ?",
        (progresso, usuario_id, achiev_id),
    )
    conn.commit()
    conn.close()


def desbloquear(usuario_id, achiev_id):
    conn = get_connection()
    conn.execute(
        "UPDATE achievs SET desbloqueado = 1 WHERE usuario_id = ? AND achiev_id = ?",
        (usuario_id, achiev_id),
    )
    if not conn.execute(
        "SELECT id FROM badges WHERE usuario_id = ? AND badge_id = ?",
        (usuario_id, achiev_id),
    ).fetchone():
        conn.execute(
            "INSERT INTO badges (usuario_id, badge_id) VALUES (?, ?)",
            (usuario_id, achiev_id),
        )
    conn.commit()
    conn.close()


def listar_achievs(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM achievs WHERE usuario_id = ?", (usuario_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_badges(usuario_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM badges WHERE usuario_id = ? ORDER BY earned_date DESC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


BADGES_INFO = {
    "primeiro_registro": {"nome": "Primeiro Passo", "icone": "🌟", "descricao": "Registrou a primeira transação"},
    "cinco_despesas": {"nome": "Controle Iniciado", "icone": "📊", "descricao": "Registrou 5 despesas"},
    "dez_despesas": {"nome": "Mestre dos Gastos", "icone": "👑", "descricao": "Registrou 10 despesas"},
    "meta_criada": {"nome": "Sonhador", "icone": "🎯", "descricao": "Criou a primeira meta"},
    "meta_concluida": {"nome": "Realizador", "icone": "🏆", "descricao": "Concluiu uma meta"},
    "orcamento_respeitado": {"nome": "Disciplinado", "icone": "🧠", "descricao": "Respeitou o orçamento do mês"},
    "streak_3": {"nome": "Consistente", "icone": "🔥", "descricao": "3 dias consecutivos economizando"},
    "streak_7": {"nome": "Determinado", "icone": "💪", "descricao": "7 dias consecutivos economizando"},
    "streak_30": {"nome": "Lendário", "icone": "⚡", "descricao": "30 dias consecutivos economizando"},
}

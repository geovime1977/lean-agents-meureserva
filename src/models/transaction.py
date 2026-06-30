from src.utils.db import get_connection
from src.utils.helpers import hoje_str
from src.services.categorizer import categorizar


def adicionar_transacao(usuario_id, tipo, categoria, valor, descricao, data=None):
    if data is None:
        data = hoje_str()
    conn = get_connection()
    conn.execute(
        "INSERT INTO transacoes (usuario_id, tipo, categoria, valor, descricao, data) VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, tipo, categoria, valor, descricao, data),
    )
    conn.commit()
    conn.close()


def listar_transacoes(usuario_id, mes=None, limite=100):
    conn = get_connection()
    if mes:
        query = """
            SELECT * FROM transacoes
            WHERE usuario_id = ? AND strftime('%Y-%m', data) = ?
            ORDER BY data DESC, id DESC LIMIT ?
        """
        rows = conn.execute(query, (usuario_id, mes, limite)).fetchall()
    else:
        query = """
            SELECT * FROM transacoes
            WHERE usuario_id = ?
            ORDER BY data DESC, id DESC LIMIT ?
        """
        rows = conn.execute(query, (usuario_id, limite)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def total_gastos_por_categoria(usuario_id, mes):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT categoria, SUM(valor) as total
        FROM transacoes
        WHERE usuario_id = ? AND tipo = 'despesa' AND strftime('%Y-%m', data) = ?
        GROUP BY categoria ORDER BY total DESC
        """,
        (usuario_id, mes),
    ).fetchall()
    conn.close()
    return {r["categoria"]: r["total"] for r in rows}


def total_receitas(usuario_id, mes):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT COALESCE(SUM(valor), 0) as total
        FROM transacoes
        WHERE usuario_id = ? AND tipo = 'receita' AND strftime('%Y-%m', data) = ?
        """,
        (usuario_id, mes),
    ).fetchone()
    conn.close()
    return row["total"]


def total_despesas(usuario_id, mes):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT COALESCE(SUM(valor), 0) as total
        FROM transacoes
        WHERE usuario_id = ? AND tipo = 'despesa' AND strftime('%Y-%m', data) = ?
        """,
        (usuario_id, mes),
    ).fetchone()
    conn.close()
    return row["total"]


def importar_csv(usuario_id, linhas):
    conn = get_connection()
    count = 0
    for linha in linhas:
        try:
            if len(linha) < 4:
                continue
            data, valor, _, descricao = linha[:4]
            valor = float(valor.replace(",", ".")) if isinstance(valor, str) else float(valor)
            tipo = "receita" if valor > 0 else "despesa"
            valor = abs(valor)
            categoria = categorizar(descricao.strip())
            conn.execute(
                "INSERT INTO transacoes (usuario_id, tipo, categoria, valor, descricao, data) VALUES (?, ?, ?, ?, ?, ?)",
                (usuario_id, tipo, categoria, valor, descricao.strip(), data.strip()),
            )
            count += 1
        except (ValueError, IndexError):
            continue
    conn.commit()
    conn.close()
    return count


def deletar_transacao(transacao_id, usuario_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM transacoes WHERE id = ? AND usuario_id = ?",
        (transacao_id, usuario_id),
    )
    conn.commit()
    conn.close()

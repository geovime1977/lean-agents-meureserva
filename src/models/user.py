from src.utils.db import get_connection
from src.utils.helpers import hash_pin


def criar_usuario(nome, email, pin, renda_mensal=0):
    conn = get_connection()
    try:
        pin_hash = hash_pin(pin)
        conn.execute(
            "INSERT INTO usuarios (nome, email, pin_hash, renda_mensal) VALUES (?, ?, ?, ?)",
            (nome, email, pin_hash, renda_mensal),
        )
        conn.commit()
        usuario_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            "INSERT INTO streaks (usuario_id) VALUES (?)", (usuario_id,)
        )
        conn.commit()
        return usuario_id, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def buscar_usuario(email):
    conn = get_connection()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return dict(usuario) if usuario else None


def autenticar_usuario(email, pin):
    usuario = buscar_usuario(email)
    if not usuario:
        return None, "Usuário não encontrado"
    from src.utils.helpers import verificar_pin

    if verificar_pin(pin, usuario["pin_hash"]):
        return usuario, None
    return None, "PIN inválido"


def atualizar_renda(usuario_id, renda):
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET renda_mensal = ? WHERE id = ?",
        (renda, usuario_id),
    )
    conn.commit()
    conn.close()


def listar_usuarios():
    conn = get_connection()
    usuarios = conn.execute("SELECT id, nome, email FROM usuarios").fetchall()
    conn.close()
    return [dict(u) for u in usuarios]

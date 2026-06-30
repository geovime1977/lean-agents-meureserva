import sqlite3
import os
from pathlib import Path

DB_DIR = Path.home() / ".assistente_financeiro"
DB_PATH = DB_DIR / "database.db"


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            renda_mensal REAL DEFAULT 0,
            premium_until TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('receita','despesa')),
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            descricao TEXT DEFAULT '',
            data TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            valor_meta REAL NOT NULL,
            valor_atual REAL DEFAULT 0,
            data_limite TEXT,
            concluida INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS pix_agendados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            chave_pix TEXT NOT NULL,
            descricao TEXT DEFAULT '',
            data_agendamento TEXT NOT NULL,
            status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente','realizado','cancelado')),
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            streak_atual INTEGER DEFAULT 0,
            streak_maxima INTEGER DEFAULT 0,
            ultima_data TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            badge_id TEXT NOT NULL,
            earned_date TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS achievs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            achiev_id TEXT NOT NULL,
            progresso REAL DEFAULT 0,
            desbloqueado INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)
    conn.commit()
    conn.close()

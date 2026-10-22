import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loja.db")
ESTOQUE_BAIXO = 5


def conectar(caminho=DB_PATH):
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL CHECK (preco >= 0),
            estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
            imagem TEXT
        )
        """
    )
    # Bancos criados antes da coluna de imagem existir
    colunas = [c["name"] for c in conn.execute("PRAGMA table_info(produtos)")]
    if "imagem" not in colunas:
        with conn:
            conn.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
    return conn


def criar_produto(conn, nome, preco, estoque, imagem=None):
    with conn:
        cur = conn.execute(
            "INSERT INTO produtos (nome, preco, estoque, imagem) VALUES (?, ?, ?, ?)",
            (nome, preco, estoque, imagem),
        )
    return cur.lastrowid


def listar_produtos(conn, busca=None):
    if busca:
        return conn.execute(
            "SELECT * FROM produtos WHERE nome LIKE ? ORDER BY id",
            (f"%{busca}%",),
        ).fetchall()
    return conn.execute("SELECT * FROM produtos ORDER BY id").fetchall()


def resumo(conn):
    return conn.execute(
        """
        SELECT COUNT(*) AS total_produtos,
               COALESCE(SUM(estoque), 0) AS total_itens,
               COALESCE(SUM(preco * estoque), 0) AS valor_estoque,
               COALESCE(SUM(estoque < ?), 0) AS estoque_baixo
        FROM produtos
        """,
        (ESTOQUE_BAIXO,),
    ).fetchone()


def buscar_produto(conn, produto_id):
    return conn.execute(
        "SELECT * FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()


def atualizar_produto(conn, produto_id, nome, preco, estoque):
    with conn:
        cur = conn.execute(
            "UPDATE produtos SET nome = ?, preco = ?, estoque = ? WHERE id = ?",
            (nome, preco, estoque, produto_id),
        )
    return cur.rowcount > 0


def definir_imagem(conn, produto_id, imagem):
    with conn:
        conn.execute(
            "UPDATE produtos SET imagem = ? WHERE id = ?", (imagem, produto_id)
        )


def remover_produto(conn, produto_id):
    with conn:
        cur = conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    return cur.rowcount > 0

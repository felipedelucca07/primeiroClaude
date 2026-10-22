import os
import uuid

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

import loja

PASTA_UPLOADS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
TAMANHO_MAXIMO_MB = 5

# Assinatura (primeiros bytes) de cada formato de imagem aceito
FORMATOS_IMAGEM = {
    "png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
    "jpg": lambda b: b.startswith(b"\xff\xd8\xff"),
    "gif": lambda b: b[:6] in (b"GIF87a", b"GIF89a"),
    "webp": lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP",
}

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"
app.config["MAX_CONTENT_LENGTH"] = TAMANHO_MAXIMO_MB * 1024 * 1024
os.makedirs(PASTA_UPLOADS, exist_ok=True)


def get_conn():
    if "conn" not in g:
        g.conn = loja.conectar()
    return g.conn


@app.teardown_appcontext
def fechar_conn(_erro):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.close()


@app.template_filter("reais")
def formatar_reais(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "_").replace(".", ",").replace("_", ".")


@app.template_filter("preco_partes")
def separar_preco(valor):
    inteiro, centavos = formatar_reais(valor)[3:].split(",")
    return inteiro, centavos


def identificar_imagem(arquivo):
    """Retorna a extensão do formato da imagem, ou None se não for uma imagem aceita."""
    cabecalho = arquivo.stream.read(12)
    arquivo.stream.seek(0)
    for extensao, confere in FORMATOS_IMAGEM.items():
        if confere(cabecalho):
            return extensao
    return None


def salvar_imagem(arquivo, extensao):
    nome = f"{uuid.uuid4().hex}.{extensao}"
    arquivo.save(os.path.join(PASTA_UPLOADS, nome))
    return nome


def apagar_imagem(nome):
    if nome:
        try:
            os.remove(os.path.join(PASTA_UPLOADS, nome))
        except FileNotFoundError:
            pass


def validar_formulario(form, files):
    dados = {
        "nome": form.get("nome", "").strip(),
        "preco": form.get("preco", "").strip(),
        "estoque": form.get("estoque", "").strip(),
    }
    erros = {}
    if not dados["nome"]:
        erros["nome"] = "Informe o nome do produto."
    try:
        preco = float(dados["preco"].replace(",", "."))
        if preco < 0:
            erros["preco"] = "O preço não pode ser negativo."
    except ValueError:
        erros["preco"] = "Informe um preço válido."
        preco = None
    try:
        estoque = int(dados["estoque"])
        if estoque < 0:
            erros["estoque"] = "O estoque não pode ser negativo."
    except ValueError:
        erros["estoque"] = "Informe uma quantidade inteira."
        estoque = None

    imagem = files.get("imagem")
    extensao = None
    if imagem and imagem.filename:
        extensao = identificar_imagem(imagem)
        if extensao is None:
            erros["imagem"] = "Envie uma imagem PNG, JPG, GIF ou WEBP."
    else:
        imagem = None
    return dados, erros, (dados["nome"], preco, estoque), (imagem, extensao)


@app.route("/")
def index():
    busca = request.args.get("q", "").strip()
    conn = get_conn()
    return render_template(
        "index.html",
        produtos=loja.listar_produtos(conn, busca),
        resumo=loja.resumo(conn),
        busca=busca,
        estoque_baixo=loja.ESTOQUE_BAIXO,
    )


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo():
    dados, erros = {}, {}
    if request.method == "POST":
        dados, erros, valores, (imagem, extensao) = validar_formulario(request.form, request.files)
        if not erros:
            nome_imagem = salvar_imagem(imagem, extensao) if imagem else None
            loja.criar_produto(get_conn(), *valores, imagem=nome_imagem)
            flash(f"Produto “{valores[0]}” cadastrado.", "sucesso")
            return redirect(url_for("index"))
    return render_template("form.html", dados=dados, erros=erros, produto=None)


@app.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
def editar(produto_id):
    conn = get_conn()
    produto = loja.buscar_produto(conn, produto_id)
    if produto is None:
        abort(404)
    dados, erros = dict(produto), {}
    if request.method == "POST":
        dados, erros, valores, (imagem, extensao) = validar_formulario(request.form, request.files)
        if not erros:
            loja.atualizar_produto(conn, produto_id, *valores)
            if imagem:
                loja.definir_imagem(conn, produto_id, salvar_imagem(imagem, extensao))
                apagar_imagem(produto["imagem"])
            elif request.form.get("remover_imagem"):
                loja.definir_imagem(conn, produto_id, None)
                apagar_imagem(produto["imagem"])
            flash(f"Produto “{valores[0]}” atualizado.", "sucesso")
            return redirect(url_for("index"))
    return render_template("form.html", dados=dados, erros=erros, produto=produto)


@app.route("/produtos/<int:produto_id>/remover", methods=["POST"])
def remover(produto_id):
    conn = get_conn()
    produto = loja.buscar_produto(conn, produto_id)
    if produto is None:
        abort(404)
    loja.remover_produto(conn, produto_id)
    apagar_imagem(produto["imagem"])
    flash(f"Produto “{produto['nome']}” removido.", "sucesso")
    return redirect(url_for("index"))


@app.errorhandler(404)
def nao_encontrado(_erro):
    return render_template("404.html"), 404


@app.errorhandler(413)
def arquivo_grande(_erro):
    flash(f"A imagem é muito grande. O limite é {TAMANHO_MAXIMO_MB} MB.", "erro")
    return redirect(request.url)


if __name__ == "__main__":
    app.run(debug=True)

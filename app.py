from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

import loja

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-em-producao"


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


def validar_formulario(form):
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
    return dados, erros, (dados["nome"], preco, estoque)


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
        dados, erros, valores = validar_formulario(request.form)
        if not erros:
            loja.criar_produto(get_conn(), *valores)
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
        dados, erros, valores = validar_formulario(request.form)
        if not erros:
            loja.atualizar_produto(conn, produto_id, *valores)
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
    flash(f"Produto “{produto['nome']}” removido.", "sucesso")
    return redirect(url_for("index"))


@app.errorhandler(404)
def nao_encontrado(_erro):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

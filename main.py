import loja


def ler_texto(mensagem, padrao=None):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        if padrao is not None:
            return padrao
        print("Valor obrigatório.")


def ler_numero(mensagem, tipo, padrao=None):
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        if not valor and padrao is not None:
            return padrao
        try:
            numero = tipo(valor)
        except ValueError:
            print("Número inválido.")
            continue
        if numero < 0:
            print("O valor não pode ser negativo.")
            continue
        return numero


def mostrar(produto):
    print(
        f"[{produto['id']}] {produto['nome']} - "
        f"R$ {produto['preco']:.2f} - estoque: {produto['estoque']}"
    )


def cadastrar(conn):
    nome = ler_texto("Nome: ")
    preco = ler_numero("Preço: ", float)
    estoque = ler_numero("Estoque: ", int)
    produto_id = loja.criar_produto(conn, nome, preco, estoque)
    print(f"Produto cadastrado com id {produto_id}.")


def listar(conn):
    produtos = loja.listar_produtos(conn)
    if not produtos:
        print("Nenhum produto cadastrado.")
    for produto in produtos:
        mostrar(produto)


def buscar(conn):
    produto = loja.buscar_produto(conn, ler_numero("Id: ", int))
    if produto:
        mostrar(produto)
    else:
        print("Produto não encontrado.")


def editar(conn):
    produto_id = ler_numero("Id: ", int)
    produto = loja.buscar_produto(conn, produto_id)
    if not produto:
        print("Produto não encontrado.")
        return
    print("Deixe em branco para manter o valor atual.")
    nome = ler_texto(f"Nome [{produto['nome']}]: ", produto["nome"])
    preco = ler_numero(f"Preço [{produto['preco']:.2f}]: ", float, produto["preco"])
    estoque = ler_numero(f"Estoque [{produto['estoque']}]: ", int, produto["estoque"])
    loja.atualizar_produto(conn, produto_id, nome, preco, estoque)
    print("Produto atualizado.")


def remover(conn):
    if loja.remover_produto(conn, ler_numero("Id: ", int)):
        print("Produto removido.")
    else:
        print("Produto não encontrado.")


OPCOES = {
    "1": ("Cadastrar produto", cadastrar),
    "2": ("Listar produtos", listar),
    "3": ("Buscar produto", buscar),
    "4": ("Editar produto", editar),
    "5": ("Remover produto", remover),
}


def main():
    conn = loja.conectar()
    try:
        while True:
            print("\n=== Loja ===")
            for chave, (descricao, _) in OPCOES.items():
                print(f"{chave}. {descricao}")
            print("0. Sair")
            escolha = input("Opção: ").strip()
            if escolha == "0":
                break
            if escolha in OPCOES:
                OPCOES[escolha][1](conn)
            else:
                print("Opção inválida.")
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()

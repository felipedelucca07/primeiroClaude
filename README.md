# primeiroClaude — CRUD de Loja

CRUD simples de produtos de uma loja, feito em Python e executado no terminal.
Os dados ficam salvos em um banco SQLite local (`loja.db`).

## Requisitos

- Python 3.8 ou superior

Não há dependências externas: o projeto usa apenas a biblioteca padrão.

## Como executar

```bash
git clone https://github.com/felipedelucca07/primeiroClaude.git
cd primeiroClaude
python3 main.py
```

O arquivo `loja.db` é criado automaticamente na primeira execução, na pasta
de onde o programa foi chamado.

## Menu

```
=== Loja ===
1. Cadastrar produto
2. Listar produtos
3. Buscar produto
4. Editar produto
5. Remover produto
0. Sair
```

| Opção | O que faz |
|-------|-----------|
| 1 | Pede nome, preço e estoque e cadastra o produto, informando o id gerado. |
| 2 | Lista todos os produtos cadastrados. |
| 3 | Mostra um produto a partir do id. |
| 4 | Edita um produto pelo id. Deixe um campo em branco para manter o valor atual. |
| 5 | Remove um produto pelo id. |
| 0 | Encerra o programa (`Ctrl+C` ou `Ctrl+D` também funcionam). |

Preços aceitam vírgula ou ponto como separador decimal (`49,90` ou `49.90`).
Preço e estoque não podem ser negativos.

## Exemplo

```
Opção: 1
Nome: Camiseta
Preço: 49,90
Estoque: 10
Produto cadastrado com id 1.

Opção: 2
[1] Camiseta - R$ 49.90 - estoque: 10
```

## Estrutura

- `main.py` — menu interativo e leitura dos dados digitados.
- `loja.py` — acesso ao banco SQLite (criar, listar, buscar, atualizar e remover produtos).

## Usando como módulo

As funções de `loja.py` podem ser usadas diretamente em outro código:

```python
import loja

conn = loja.conectar()
produto_id = loja.criar_produto(conn, "Caneca", 25.0, 5)
print(dict(loja.buscar_produto(conn, produto_id)))
conn.close()
```

# primeiroClaude — CRUD de Loja

CRUD simples de produtos de uma loja, feito em Python com **Flask** e **SQLite**.
Tem uma interface web interativa e também um menu no terminal; os dois usam o
mesmo banco de dados (`loja.db`).

## Funcionalidades

- Painel com resumo: total de produtos, itens em estoque, valor do estoque e
  produtos com estoque baixo
- Visual inspirado no Mercado Livre: cabeçalho amarelo com busca, botões azuis
  e produtos em cartões com o preço em destaque
- Busca instantânea pelo cabeçalho e seletor "Ordenar por" (recentes, preço,
  nome e estoque)
- Indicação de estoque nos cartões (em estoque, últimas unidades e esgotado)
- Cadastro e edição com validação e mensagens de erro por campo
- Botões +/− para o estoque e prévia do valor total enquanto digita
- Confirmação antes de remover um produto
- Layout adaptado para celular

## Requisitos

- Python 3.8 ou superior
- Pacote `python3-venv` (no Ubuntu/Debian: `sudo apt install python3-venv`)

## Instalação

```bash
git clone https://github.com/felipedelucca07/primeiroClaude.git
cd primeiroClaude
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Versão web

```bash
.venv/bin/python app.py
```

Abra http://127.0.0.1:5000 no navegador.

| Página | Endereço |
|--------|----------|
| Lista de produtos (com busca) | `/` ou `/?q=termo` |
| Novo produto | `/produtos/novo` |
| Editar produto | `/produtos/<id>/editar` |

Preços aceitam vírgula ou ponto (`49,90` ou `49.90`). Preço e estoque não podem
ser negativos. Produtos com menos de 5 unidades aparecem como "Últimas unidades!".

## Versão de terminal

```bash
python3 main.py
```

```
=== Loja ===
1. Cadastrar produto
2. Listar produtos
3. Buscar produto
4. Editar produto
5. Remover produto
0. Sair
```

Na edição, deixe um campo em branco para manter o valor atual. A versão de
terminal não precisa do Flask.

## Banco de dados

Os dados ficam em `loja.db`, um arquivo SQLite criado automaticamente na pasta
do projeto na primeira execução. Para começar do zero, basta apagá-lo.

Tabela `produtos`:

| Coluna | Tipo | Regra |
|--------|------|-------|
| `id` | INTEGER | chave primária, automática |
| `nome` | TEXT | obrigatório |
| `preco` | REAL | maior ou igual a 0 |
| `estoque` | INTEGER | maior ou igual a 0 |

## Estrutura

```
app.py            rotas da aplicação web (Flask)
loja.py           acesso ao banco SQLite
main.py           menu interativo no terminal
templates/        páginas HTML (Jinja2)
static/style.css  estilos
static/app.js     interações (busca, ordenação, confirmação, prévia)
requirements.txt  dependências
```

## Usando como módulo

```python
import loja

conn = loja.conectar()
produto_id = loja.criar_produto(conn, "Caneca", 25.0, 5)
print(dict(loja.buscar_produto(conn, produto_id)))
print(dict(loja.resumo(conn)))
conn.close()
```

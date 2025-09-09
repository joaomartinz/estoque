import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

# carregar variáveis do .env
load_dotenv()

# === Configuração de conexão com Railway ===
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

# === Carregar tabelas ===
produtos = pd.read_sql("SELECT * FROM produtos", engine)
fornecedores = pd.read_sql("SELECT * FROM Fornecedores", engine)
movimentacoes = pd.read_sql("SELECT * FROM Movimentacao", engine)

# === Funções de Estoque e Relatórios ===

def exportar_relatorio():
    print("\n Exportar Relatórios")
    print("1 - Exportar produtos")
    print("2 - Exportar movimentações")
    print("3 - Exportar estoque por fornecedor")
    escolha = input("O que deseja exportar?")

    if escolha == "1":
        df = produtos
        nome_arquivo = "produtos"
    elif escolha == "2":
        df = movimentacoes
        nome_arquivo = "movimentacoes"
    elif escolha == "3":
        prod_fornec = produtos.merge(fornecedores, on="id_Fornecedor", how="left")
        df = prod_fornec.groupby("marca") ["quantidade_estoque_atual"].sum().reset_index()
        nome_arquivo = 'estoque_por_fornecedor'
    else:
        print("Opção Inválida!")
    
    tipo = input("1 - CSV, 2 - EXCEL")
    if tipo == "1":
        df.to_csv(f"{nome_arquivo}.csv", index=False)
        print(f"Relatório: {nome_arquivo}.csv")
    elif tipo == "2":
        df.to_excel(f"{nome_arquivo}.xlsx", index=False)
        print(f"Relatório: {nome_arquivo}.xlsx")
    else:
        print("Opção inválida")

# === Funções Estoque ===
def mostrar_estoque():
    print("\n Estoque atual:")
    print(produtos.head())
    print("\nQuantidade total em estoque:", produtos["quantidade_estoque_atual"].sum())
    print("Número de produtos diferentes:", produtos["id_produto"].nunique())

def produtos_baixo_estoque():
    baixo_estoque = produtos[produtos["quantidades-estoque_atual"] < 10]
    print("\n Produtos com baixo estoque:")
    print(baixo_estoque)

def valor_total_estoque():
    produtos["valor_total"] = produtos["quantidade_estoque_atual"] * produtos["preco_unitario"]
    total = produtos["valor_total"].sum()
    print(f"\n Valor total do estoque: R$ {total:,.2f}")

# === Funções Relatórios ===
def estoque_por_fornecedor():
    prod_fornec = produtos.merge(fornecedores, on="id_Fornecedor", how="left")
    estoque_fornecedor = prod_fornec.groupby("marca")["quantidade_estoque_atual"].sum()
    print("\n Estoque total por fornecedor:")
    print(estoque_fornecedor)

    estoque_fornecedor.plot(kind="bar", figsize=(8,4))
    plt.title("Estoque por fornecedor")
    plt.ylabel("Quantidade em estoque")
    plt.xlabel("Fornecedor")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def movimentacoes_mensais():
    movimentacoes["data_move"] = pd.to_datetime(movimentacoes["data_move"])
    vendas_mes = movimentacoes[movimentacoes["tipo"]=="saida"].groupby(
        movimentacoes["data_move"].dt.to_period("M")
    )["quantidade"].sum()

    print("\n Saídas (vendas) por mês:")
    print(vendas_mes)

    vendas_mes.plot(kind="line", marker="o", figsize=(8,4))
    plt.title("Saídas mensais (vendas)")
    plt.ylabel("Quantidade")
    plt.xlabel("Mês")
    plt.tight_layout()
    plt.show()

def top5_produtos_vendidos():
    saidas = movimentacoes[movimentacoes["tipo"]=="saida"]
    mais_vendidos = saidas.groupby("id_produto")["quantidade"].sum().nlargest(5)
    resultado = mais_vendidos.reset_index().merge(produtos, on="id_produto")
    print("\n Top 5 produtos mais vendidos:")
    print(resultado[["id_produto","nome","quantidade"]])

    resultado.plot(x="nome", y="quantidade", kind="bar", figsize=(8,4))
    plt.title("Top 5 produtos mais vendidos")
    plt.ylabel("Quantidade vendida")
    plt.xlabel("Produto")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def relatorio_fornecedores():
    prod_fornec = produtos.merge(fornecedores, on="id_Fornecedor", how="left")
    print("\n Fornecedores e seus produtos:")
    for marca, grupo in prod_fornec.groupby("marca"):
        print(f"\n {marca}")
        print(grupo[["id_produto","nome","quantidade_estoque_atual"]])

# === Funções Consultas ===
def buscar_produto():
    print("\nBuscar produto")
    escolha = input("(1) buscar por ID / (2) buscar por Nome ")

    if escolha == "1":
        try:
            pid = int(input("Informe o ID do produto: "))
            resultado = produtos[produtos["id_produto"] == pid]
        except ValueError:
            print("ID inválido.")
            return
    elif escolha == "2":
        nome = input("Informe o nome do produto: ").lower()
        resultado = produtos[produtos["nome"].str.lower().str.contains(nome)]
    else:
        print("Opção inválida.")
        return

    if resultado.empty:
        print("Nenhum produto encontrado.")
    else:
        print("\nResultado da busca:")
        print(resultado)

def historico_produto():
    try:
        pid = int(input("\nInforme o ID do produto: "))
        historico = movimentacoes[movimentacoes["id_produto"] == pid]
    except ValueError:
        print("ID inválido.")
        return

    if historico.empty:
        print("Nenhum histórico encontrado.")
        return

    historico = historico.merge(produtos[["id_produto","nome"]], on="id_produto")
    print("\nHistórico de movimentações do produto:")
    print(historico[["data_move","tipo","quantidade","nome"]])

    historico.groupby("tipo")["quantidade"].sum().plot(
        kind="bar", figsize=(6,4), title=f"Entradas x Saídas - Produto {pid}"
    )
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.show()
        

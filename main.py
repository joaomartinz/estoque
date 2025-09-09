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


        

        

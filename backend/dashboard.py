import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from mysql.connector import Error
from api import conectar_bd

def get_data_from_db():
    try:
        connection = conectar_bd()
        if connection is None or not connection.is_connected():
            raise Error("Falha ao conectar ao banco de dados")

        # 1. Carregar Pedidos
        query_orders = "SELECT * FROM orders"
        df_orders = pd.read_sql(query_orders, connection)

        # 2. Carregar Produtos e Categorias
        query_products = """
            SELECT p.*, c.name as category_name 
            FROM products p 
            JOIN categories c ON p.category_id = c.id
        """
        df_products = pd.read_sql(query_products, connection)

        # Converter preços de centavos para Reais (baseado no comentário do SQL)
        df_orders['total_price'] = df_orders['total_price'].astype(float)
        df_products['price'] = df_products['price'].astype(float) 

        return df_orders, df_products
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return pd.DataFrame(), pd.DataFrame()
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()




import os
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def conectar_bd():
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
    }
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Erro de conexão: {err}")
        return None

def verificar_login(email, password):
    """Esta função será usada pelo Flask para validar as credenciais"""
    conn = conectar_bd()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        # Consulta parametrizada para evitar SQL Injection
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Verifica se o usuário existe e se a senha coincide
        if result and result[0] == password:
            return True
        return False
    except mysql.connector.Error:
        return False
    
def cadastrar_produto(name, description, price, category_id, image, stock, slug, featured):
    """Função para cadastrar um produto no banco de dados"""
    conn = conectar_bd()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO products (name, description, price, category_id, image, stock, slug, featured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, description, price, category_id, image, stock, slug, featured))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error:
        return False
    
def listar_produtos():
    """Função para listar todos os produtos do banco de dados"""
    conn = conectar_bd()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        return produtos
    except mysql.connector.Error:
        return []

def listar_categorias():
    """Função para listar todas as categorias do banco de dados"""
    conn = conectar_bd()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        categorias = cursor.fetchall()
        cursor.close()
        conn.close()
        return categorias
    except mysql.connector.Error:
        return []

def consultar_produto(name):
    """Função para consultar um produto específico pelo nome"""
    conn = conectar_bd()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE name = %s", (name,))
        produto = cursor.fetchone()
        cursor.close()
        conn.close()
        return produto
    except mysql.connector.Error:
        return None

def atualizar_produto(product_id, name, description, price, category_id, image, stock, slug, featured): 
    """Função para atualizar um produto existente no banco de dados"""
    conn = conectar_bd()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        query = """
            UPDATE products
            SET name = %s, description = %s, price = %s, category_id = %s, image = %s, stock = %s, slug = %s, featured = %s
            WHERE id = %s
        """
        cursor.execute(query, (name, description, price, category_id, image, stock, slug, featured, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error:
        return False

if __name__ == "__main__":
    # Teste rápido via terminal
    u = input("Email: ")
    s = input("Senha: ")
    if verificar_login(u, s):
        print("Login OK!")
    else:
        print("Falha!")


import os
import mysql.connector
import uuid
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
        if result is not None and result[0] == password: # type: ignore
            return True
        return False
    except mysql.connector.Error:
        return False
    
def cadastrar_produto(code, name, description, price, category_id, image, stock, slug, featured):
    """Função para cadastrar um produto no banco de dados"""
    
    #cadatrar o produto no banco de dados com um codigo único gerado automaticamente
    code = str(uuid.uuid4())
    
    conn = conectar_bd()
    if not conn:
        return False
    
    try:        
        cursor = conn.cursor()
        query = """
            INSERT INTO products (code, name, description, price, category_id, image, stock, slug, featured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (code, name, description, price, category_id, image, stock, slug, featured))
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

def consultar_produto(code):
    """Função para consultar um produto específico pelo codigo"""
    conn = conectar_bd()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE code = %s", (code,))
        produto = cursor.fetchone()
        cursor.close()
        conn.close()
        return produto
    except mysql.connector.Error:
        return None

def atualizar_produto(code, product_id, name, description, price, category_id, image, stock, slug, featured): 
    """Função para atualizar um produto existente no banco de dados"""
    conn = conectar_bd()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            UPDATE products
            SET code = %s, name = %s, description = %s, price = %s, category_id = %s, image = %s, stock = %s, slug = %s, featured = %s
            WHERE id = %s
        """
        cursor.execute(query, (code, name, description, price, category_id, image, stock, slug, featured, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error:
        return False
    
def editar_status_produto(product_id, new_status):
    conn = conectar_bd()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # Atualiza diretamente com o valor que o JS enviou
        cursor.execute("UPDATE products SET status = %s WHERE id = %s", (new_status, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro no banco: {e}")
        return False

def detalhes_pedido(id_pedido):
    """Função para obter os detalhes de um pedido específico pelo ID"""
    conn = conectar_bd()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                o.id, 
                o.status, 
                o.created_at,
                u.name AS cliente, 
                u.email AS email,
                p.name AS produto
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN cart_items ci ON o.id = ci.order_id
            JOIN products p ON ci.product_id = p.id
            GROUP BY o.id
        """
        cursor.execute(query, (id_pedido,))
        pedido = cursor.fetchone()
        cursor.close()
        conn.close()
        return pedido
    except mysql.connector.Error:
        return None
    
def obter_nome_cliente(user_id):
    """Função para obter o nome do cliente pelo ID"""
    conn = conectar_bd()
    if not conn:
        return "N/A"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else "N/A"
    except mysql.connector.Error:
        return "N/A"

def obter_nome_categoria(category_id):
    """Função para obter o nome da categoria pelo ID"""
    conn = conectar_bd()
    if not conn:
        return "N/A"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else "N/A"
    except mysql.connector.Error:
        return "N/A"

def lista_pedidos():
    """Função para listar todos os pedidos do banco de dados"""
    conn = conectar_bd()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders")
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()
        return pedidos
    except mysql.connector.Error:
        return []
    
def obter_email(user_id):
    """Função para obter o email do cliente pelo ID"""
    conn = conectar_bd()
    if not conn:
        return "N/A"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else "N/A"
    except mysql.connector.Error:
        return "N/A"

if __name__ == "__main__":
    # Teste rápido via terminal
    u = input("Email: ")
    s = input("Senha: ")
    if verificar_login(u, s):
        print("Login OK!")
    else:
        print("Falha!")


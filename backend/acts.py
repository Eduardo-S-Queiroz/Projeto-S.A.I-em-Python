import os
import mysql.connector
import uuid
from dotenv import load_dotenv

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


def executar_escrita(query, params=()):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro de escrita no banco: {err}")
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return False


# --- USUÁRIOS ---
def verificar_login(email, password):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None and result[0] == password
    except Exception as err:
        print(f"Erro ao verificar login: {err}")
        return False


# --- PRODUTOS (Controle Geral: aparência, descrição, preço e imagem) ---
def listar_produtos():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY name")
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar produtos: {err}")
        return []


def cadastrar_produto(name, description, price, image_url=None, image_path=None, featured=0):
    code = str(uuid.uuid4())
    slug = (name or "produto").lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO products (code, name, description, price, image_url, image_path, slug, featured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (code, name, description, price or 0, image_url, image_path, slug, featured))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao cadastrar produto: {err}")
        return False


def atualizar_produto(id, name, description, price, image_url=None, image_path=None, featured=0):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        if image_path:
            query = """
                UPDATE products
                SET name=%s, description=%s, price=%s, image_url=%s, image_path=%s, featured=%s
                WHERE id=%s
            """
            params = (name, description, price or 0, image_url, image_path, featured, id)
        else:
            query = """
                UPDATE products
                SET name=%s, description=%s, price=%s, image_url=%s, featured=%s
                WHERE id=%s
            """
            params = (name, description, price or 0, image_url, featured, id)
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar produto: {err}")
        return False


# --- ESTOQUE (quantidade, categoria e fornecedor vinculados ao produto) ---
def listar_estoque():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                i.*,
                p.name AS product_name,
                p.price AS product_price,
                p.image_url,
                p.image_path,
                c.name AS category_name,
                s.name AS supplier_name
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            LEFT JOIN categories c ON i.category_id = c.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY p.name
        """
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar estoque: {err}")
        return []


def salvar_estoque(product_id, category_id, supplier_id, quantity, inventory_id=None):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        quantity = int(quantity or 0)
        cursor = conn.cursor()
        inventory_query = "SELECT id, quantity, product_id FROM inventory WHERE product_id = %s"
        inventory_params = (product_id,)
        if inventory_id:
            inventory_query = "SELECT id, quantity, product_id FROM inventory WHERE id = %s"
            inventory_params = (inventory_id,)
        cursor.execute(inventory_query, inventory_params)
        res = cursor.fetchone()
        if res:
            inventory_row_id = res[0]
            old_qty = int(res[1] or 0)
            current_product_id = res[2]
            cursor.execute(
                "UPDATE inventory SET category_id=%s, supplier_id=%s, quantity=%s WHERE id=%s",
                (category_id or None, supplier_id or None, quantity, inventory_row_id)
            )
            if quantity != old_qty:
                m_type = 'entry' if quantity > old_qty else 'exit'
                m_qty = abs(quantity - old_qty)
                cursor.execute(
                    "INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES (%s, %s, %s, %s)",
                    (current_product_id, m_type, m_qty, "Ajuste manual de estoque")
                )
        else:
            cursor.execute(
                "INSERT INTO inventory (product_id, category_id, supplier_id, quantity) VALUES (%s, %s, %s, %s)",
                (product_id, category_id or None, supplier_id or None, quantity)
            )
            if quantity > 0:
                cursor.execute(
                    "INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES (%s, %s, %s, %s)",
                    (product_id, 'entry', quantity, "Saldo inicial")
                )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao salvar estoque: {err}")
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return False


# --- MOVIMENTAÇÕES ---
def listar_movimentacoes():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT
                m.*,
                p.name AS product_name,
                c.name AS category_name,
                s.name AS supplier_name
            FROM stock_movements m
            JOIN products p ON m.product_id = p.id
            LEFT JOIN inventory i ON i.product_id = p.id
            LEFT JOIN categories c ON i.category_id = c.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY m.created_at DESC
        """
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar movimentações: {err}")
        return []


# --- CATEGORIAS ---
def listar_categorias():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories ORDER BY name")
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar categorias: {err}")
        return []


def cadastrar_categoria(name):
    return executar_escrita("INSERT INTO categories (name) VALUES (%s)", (name,))


def atualizar_categoria(id, name):
    return executar_escrita("UPDATE categories SET name=%s WHERE id=%s", (name, id))


def excluir_categoria(id):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET category_id=NULL WHERE category_id=%s", (id,))
        cursor.execute("DELETE FROM categories WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao excluir categoria: {err}")
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return False


# --- FORNECEDORES ---
def listar_fornecedores():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM suppliers ORDER BY name")
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar fornecedores: {err}")
        return []


def cadastrar_fornecedor(name):
    return executar_escrita("INSERT INTO suppliers (name) VALUES (%s)", (name,))


def atualizar_fornecedor(id, name):
    return executar_escrita("UPDATE suppliers SET name=%s WHERE id=%s", (name, id))


def excluir_fornecedor(id):
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET supplier_id=NULL WHERE supplier_id=%s", (id,))
        cursor.execute("DELETE FROM suppliers WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao excluir fornecedor: {err}")
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return False


# --- PEDIDOS ---
def lista_pedidos():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.*, u.name AS cliente, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
        """)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar pedidos: {err}")
        return []


def obter_detalhes_pedido(pedido_id):
    """Obtém detalhes completos de um pedido específico com seus itens."""
    conn = conectar_bd()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar dados do pedido
        cursor.execute("""
            SELECT o.*, u.name AS cliente, u.email, 
                   COALESCE(o.shipping_address, 'Não informado') AS shipping_address
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """, (pedido_id,))
        pedido = cursor.fetchone()
        
        if not pedido:
            cursor.close()
            conn.close()
            return None
        
        # Buscar itens do pedido
        cursor.execute("""
            SELECT ci.*, p.name AS product_name
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.order_id = %s
        """, (pedido_id,))
        itens = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            'pedido': pedido,
            'itens': itens if itens else []
        }
    except mysql.connector.Error as err:
        print(f"Erro ao obter detalhes do pedido: {err}")
        return None


def obter_nome_cliente(user_id):
    conn = conectar_bd()
    if not conn:
        return "N/A"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res[0] if res else "N/A"
    except Exception:
        return "N/A"


def obter_email(user_id):
    conn = conectar_bd()
    if not conn:
        return "N/A"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res[0] if res else "N/A"
    except Exception:
        return "N/A"


def obter_nome_categoria(id):
    conn = conectar_bd()
    if not conn:
        return "N/A"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE id = %s", (id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res[0] if res else "N/A"
    except Exception:
        return "N/A"


def obter_nome_fornecedor(id):
    conn = conectar_bd()
    if not conn:
        return "N/A"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM suppliers WHERE id = %s", (id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res[0] if res else "N/A"
    except Exception:
        return "N/A"


# --- HELPERS DE DASH/RELATÓRIO ---
def listar_anos_pedidos():
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT YEAR(created_at) FROM orders ORDER BY YEAR(created_at) DESC")
        anos = [r[0] for r in cursor.fetchall() if r[0]]
        cursor.close()
        conn.close()
        return anos
    except mysql.connector.Error as err:
        print(f"Erro ao listar anos: {err}")
        return []

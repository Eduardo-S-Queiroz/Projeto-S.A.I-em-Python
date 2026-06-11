import os
import mysql.connector
import uuid
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env.
load_dotenv()


def conectar_bd():
    """Abre a conexão com o banco de dados MySQL.

    Usa as variáveis de ambiente: DB_HOST, DB_USER, DB_PASSWORD e DB_NAME.
    Retorna None em caso de falha de conexão.
    """
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
    """Executa comandos SQL de escrita e trata commit/rollback.

    Usada por funções CRUD que não precisam retornar dados.
    """
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
    """Verifica se o email e senha existem no banco de dados.

    Atenção: senha é comparada em texto simples no schema atual.
    """
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
def listar_produtos(q=None):
    """Retorna a lista de produtos, opcionalmente filtrando por termo de busca."""
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        if q:
            q_like = f"%{q}%"
            cursor.execute(
                "SELECT * FROM products WHERE name LIKE %s OR description LIKE %s ORDER BY name",
                (q_like, q_like)
            )
        else:
            cursor.execute("SELECT * FROM products ORDER BY name")
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar produtos: {err}")
        return []


def cadastrar_produto(name, description, price, image_url=None, image_path=None, featured=0):
    """Insere um novo produto no banco com código único e slug gerado."""
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
    """Atualiza os dados do produto, preservando imagem se não houver upload novo."""
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
def listar_estoque(q=None):
    """Retorna o inventário com dados de produto, categoria e fornecedor."""
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
        """
        params = []
        if q:
            q_like = f"%{q}%"
            query += """
                WHERE p.name LIKE %s
                   OR c.name LIKE %s
                   OR s.name LIKE %s
                   OR CAST(i.quantity AS CHAR) LIKE %s
            """
            params = [q_like, q_like, q_like, q_like]
        query += " ORDER BY p.name"
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar estoque: {err}")
        return []


def salvar_estoque(product_id, category_id, supplier_id, quantity):
    """Cria ou atualiza o registro de estoque e registra movimentações relacionadas."""
    conn = conectar_bd()
    if not conn:
        return False
    try:
        quantity = int(quantity or 0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, quantity FROM inventory WHERE product_id = %s", (product_id,))
        res = cursor.fetchone()
        if res:
            # Atualiza estoque existente e registra ajuste se a quantidade mudou.
            old_qty = int(res[1] or 0)
            cursor.execute(
                "UPDATE inventory SET category_id=%s, supplier_id=%s, quantity=%s WHERE product_id=%s",
                (category_id or None, supplier_id or None, quantity, product_id)
            )
            if quantity != old_qty:
                m_type = 'entry' if quantity > old_qty else 'exit'
                m_qty = abs(quantity - old_qty)
                cursor.execute(
                    "INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES (%s, %s, %s, %s)",
                    (product_id, m_type, m_qty, "Ajuste manual de estoque")
                )
        else:
            # Insere novo inventário e registra entrada inicial se houver saldo.
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
def listar_movimentacoes(q=None):
    """Retorna o histórico de movimentações de estoque, com busca opcional."""
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
        """
        params = []
        if q:
            q_like = f"%{q}%"
            query += """
                WHERE p.name LIKE %s
                   OR c.name LIKE %s
                   OR s.name LIKE %s
                   OR m.type LIKE %s
                   OR m.reason LIKE %s
                   OR CAST(m.quantity AS CHAR) LIKE %s
            """
            params = [q_like, q_like, q_like, q_like, q_like, q_like]
        query += " ORDER BY m.created_at DESC"
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar movimentações: {err}")
        return []


# --- CATEGORIAS ---
def listar_categorias(q=None):
    """Retorna categorias cadastradas, com filtro opcional por nome."""
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        if q:
            q_like = f"%{q}%"
            cursor.execute("SELECT * FROM categories WHERE name LIKE %s ORDER BY name", (q_like,))
        else:
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
    """Exclui uma categoria e remove a referência no inventário."""
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
def listar_fornecedores(q=None):
    """Retorna fornecedores cadastrados, com filtro opcional por nome."""
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        if q:
            q_like = f"%{q}%"
            cursor.execute("SELECT * FROM suppliers WHERE name LIKE %s ORDER BY name", (q_like,))
        else:
            cursor.execute("SELECT * FROM suppliers ORDER BY name")
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar fornecedores: {err}")
        return []


def cadastrar_fornecedor(name):
    """Insere um novo fornecedor no banco de dados."""
    return executar_escrita("INSERT INTO suppliers (name) VALUES (%s)", (name,))


def atualizar_fornecedor(id, name):
    """Atualiza o nome de um fornecedor existente."""
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
def lista_pedidos(q=None):
    """Retorna pedidos com dados de cliente, permitindo busca por cliente, email ou status."""
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.*, u.name AS cliente, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.id
        """
        params = []
        if q:
            q_like = f"%{q}%"
            conditions = [
                "u.name LIKE %s",
                "u.email LIKE %s",
                "o.status LIKE %s"
            ]
            params = [q_like, q_like, q_like]
            if q.isdigit():
                conditions.append("o.id = %s")
                params.append(int(q))
            query += " WHERE " + " OR ".join(conditions)
        query += " ORDER BY o.created_at DESC"
        cursor.execute(query, params)
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res
    except mysql.connector.Error as err:
        print(f"Erro ao listar pedidos: {err}")
        return []


def obter_nome_cliente(user_id):
    """Retorna o nome do cliente pelo ID do usuário."""
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
    """Retorna o email do usuário pelo ID."""
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
    """Retorna o nome da categoria pelo seu ID."""
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
    """Retorna o nome do fornecedor pelo ID."""
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
    """Retorna os anos distintos dos pedidos registrados no sistema."""
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


def excluir_produto(id):
    """Remove um produto e seu registro de estoque associado."""
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE product_id=%s", (id,))
        cursor.execute("DELETE FROM products WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao excluir produto: {err}")
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return False
    
def excluir_estoque(id):
    """Remove um item do inventário pelo seu ID."""
    conn = conectar_bd()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao excluir estoque: {err}")
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return False


# --- ADICIONE ESTAS FUNÇÕES AO FINAL DO SEU ARQUIVO DE BANCO DE DADOS ---

def buscar_pedido_por_id(pedido_id):
    """Busca os dados principais de um pedido e do cliente associado pelo ID do pedido."""
    conn = conectar_bd()
    if not conn:
        return None
    try:
        # Usamos dictionary=True para retornar como um dicionário chave-valor
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.*, u.name AS cliente_nome, u.email AS cliente_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """
        cursor.execute(query, (pedido_id,))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return res  # Retorna o dicionário com os dados ou None se não achar
    except mysql.connector.Error as err:
        print(f"Erro ao buscar pedido por ID: {err}")
        return None


def buscar_itens_do_pedido(pedido_id):
    """Retorna a lista de itens/produtos que pertencem a um pedido específico."""
    conn = conectar_bd()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        # Query ajustada perfeitamente para a sua tabela 'cart_items'
        query = """
            SELECT ci.quantity AS quantidade, ci.price AS preco_unitario, p.name AS produto_nome
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.order_id = %s
        """
        cursor.execute(query, (pedido_id,))
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        return res  # Retorna a lista correta de itens
    except mysql.connector.Error as err:
        print(f"Erro ao buscar itens do pedido: {err}")
        return []
import os
import sys
import mysql.connector
from mysql.connector import errorcode

SQL = r"""
CREATE DATABASE IF NOT EXISTS sai_db;
USE sai_db;

-- 1. USUÁRIOS
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 2. CATEGORIAS
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);

-- 3. FORNECEDORES
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);

-- 4. PRODUTOS (Controle Geral: Aparência, Descrição, Preço)
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url TEXT,
    image_path VARCHAR(255),
    slug VARCHAR(255) UNIQUE,
    featured BOOLEAN DEFAULT FALSE,
    status BOOLEAN DEFAULT TRUE
);

-- 5. ESTOQUE (Quantidade, Fornecedor e Categoria vinculados ao Produto)
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    category_id INT,
    supplier_id INT,
    quantity INT DEFAULT 0,
    min_stock INT DEFAULT 5,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- 6. HISTÓRICO DE MOVIMENTAÇÃO (Entradas e Saídas)
CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    type ENUM('entry', 'exit') NOT NULL,
    quantity INT NOT NULL,
    reason VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 7. PEDIDOS (Vendas)
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    items JSON,
    total_price DECIMAL(10, 2),
    icms_rate DECIMAL(5,2) DEFAULT 0.00,
    pis_rate DECIMAL(5,2) DEFAULT 0.00,
    cofins_rate DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 8. ITENS DO CARRINHO/PEDIDOS
CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Dados iniciais (Opcional, mas ajuda no teste)
INSERT IGNORE INTO categories (name) VALUES ('Chá Verde'), ('Chá Preto'), ('Infusão'), ('Acessórios');
INSERT IGNORE INTO suppliers (name) VALUES ('Fazenda Chá Real'),( 'Importadora Oriente'),( 'Ervas do Brasil');
INSERT IGNORE INTO users (name, email, password) VALUES ('Admin', 'admin@example.com', 'admin');


-- 9. Ajustes: adicionar categoria e fornecedor diretamente em products (compatibilidade com código)
ALTER TABLE products ADD COLUMN IF NOT EXISTS category_id INT NULL;
ALTER TABLE products ADD COLUMN IF NOT EXISTS supplier_id INT NULL;
-- Adicionar chaves estrangeiras (podem falhar se já existirem; o script lida com erros)
ALTER TABLE products ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id);
ALTER TABLE products ADD CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id);

-- 10. Adicionar campo de endereço de entrega aos pedidos
ALTER TABLE orders ADD COLUMN IF NOT EXISTS shipping_address VARCHAR(500) NULL;

-- (O restante das inserções de dados e truncates foram omitidos nesta execução para evitar sobrescrita acidental.)
"""


def get_conn(host, port, user, password):
    return mysql.connector.connect(host=host, port=port, user=user, password=password)


def run_sql(conn, sql_text):
    cursor = conn.cursor()
    try:
        # Remove comentários iniciados por -- e separa por ';' para executar cada statement
        lines = []
        for line in sql_text.splitlines():
            if '--' in line:
                line = line.split('--', 1)[0]
            lines.append(line)
        cleaned = '\n'.join(lines)
        statements = [s.strip() for s in cleaned.split(';') if s.strip()]
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                # Loga aviso e continua (p.ex. quando ALTER/CONSTRAINT já existem)
                print('Aviso ao executar statement:', err)
        conn.commit()
    finally:
        cursor.close()


def main():
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', 3306))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')

    print('Conectando ao servidor MySQL em {}:{}...'.format(host, port))
    try:
        conn = get_conn(host, port, user, password)
    except mysql.connector.Error as err:
        print('Erro ao conectar:', err)
        sys.exit(1)

    try:
        run_sql(conn, SQL)
        print('Banco e esquema criados/atualizados com sucesso (sai_db).')
    except mysql.connector.Error as err:
        print('Erro ao executar SQL:', err)
    finally:
        conn.close()


if __name__ == '__main__':
    main()

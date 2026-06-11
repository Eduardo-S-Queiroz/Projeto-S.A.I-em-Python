import mysql.connector
import random
import json
from datetime import datetime, timedelta

# Configurações de conexão com o banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # Altere para a sua senha do MySQL
    'database': 'sai_db'
}

def conectar_bd():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco: {err}")
        exit(1)

def simular_vendas_ano():
    conn = conectar_bd()
    # CORREÇÃO: Adicionado buffered=True para evitar o erro "Unread result found"
    cursor = conn.cursor(dictionary=True, buffered=True)

    print("🚀 Iniciando simulação de vendas para 1 ano...")

    # 1. Garantir que existem alguns usuários compradores além do Admin
    usuarios_ficticios = [
        ('Lucas Silva', 'lucas@example.com', 'user123'),
        ('Maria Oliveira', 'maria@example.com', 'user123'),
        ('João Souza', 'joao@example.com', 'user123'),
        ('Ana Costa', 'ana@example.com', 'user123'),
        ('Pedro Rocha', 'pedro@example.com', 'user123')
    ]
    
    for nome, email, senha in usuarios_ficticios:
        cursor.execute("INSERT IGNORE INTO users (name, email, password) VALUES (%s, %s, %s)", (nome, email, senha))
    conn.commit()

    # Buscar IDs de usuários e produtos disponíveis
    cursor.execute("SELECT id FROM users")
    user_ids = [row['id'] for row in cursor.fetchall()]

    cursor.execute("SELECT id, name, price, category_id, supplier_id FROM products")
    produtos = cursor.fetchall()

    if not produtos:
        print("❌ Nenhum produto encontrado na tabela 'products'. Execute a carga inicial de produtos primeiro.")
        cursor.close()
        conn.close()
        return

    # 2. Configuração do período (Últimos 365 dias até hoje)
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=365)
    
    total_pedidos_gerados = 0

    # Iterar dia a dia no último ano
    data_atual = data_inicio
    while data_atual <= data_fim:
        vendas_no_dia = random.randint(0, 5)

        for _ in range(vendas_no_dia):
            user_id = random.choice(user_ids)
            
            hora_aleatoria = random.randint(8, 22)
            minuto_aleatorio = random.randint(0, 59)
            data_pedido = data_atual.replace(hour=hora_aleatoria, minute=minuto_aleatorio)

            qtd_itens_diferentes = random.randint(1, 4)
            produtos_carrinho = random.sample(produtos, min(qtd_itens_diferentes, len(produtos)))

            itens_pedido_detalhe = []
            itens_json = []
            preco_total_pedido = 0

            for prod in produtos_carrinho:
                qtd_comprada = random.randint(1, 3)
                
                # Verificar se há estoque suficiente antes de vender
                cursor.execute("SELECT quantity FROM inventory WHERE product_id = %s", (prod['id'],))
                estoque_atual = cursor.fetchone()

                if not estoque_atual or estoque_atual['quantity'] < qtd_comprada:
                    # Simula um reabastecimento automático rápido
                    cursor.execute("""
                        INSERT INTO inventory (product_id, category_id, supplier_id, quantity, min_stock) 
                        VALUES (%s, %s, %s, 50, 5)
                        ON DUPLICATE KEY UPDATE quantity = quantity + 50
                    """, (prod['id'], prod['category_id'], prod['supplier_id']))
                    
                    cursor.execute("""
                        INSERT INTO stock_movements (product_id, type, quantity, reason, created_at)
                        VALUES (%s, 'entry', 50, 'Reabastecimento automático simulado', %s)
                    """, (prod['id'], data_pedido))
                    
                    estoque_disponivel = 50
                else:
                    estoque_disponivel = estoque_atual['quantity']

                # Deduz do estoque
                novo_estoque = estoque_disponivel - qtd_comprada
                cursor.execute("UPDATE inventory SET quantity = %s WHERE product_id = %s", (novo_estoque, prod['id']))

                # Registra a movimentação de saída do estoque
                cursor.execute("""
                    INSERT INTO stock_movements (product_id, type, quantity, reason, created_at)
                    VALUES (%s, 'exit', %s, 'Venda - Pedido Simulado', %s)
                """, (prod['id'], qtd_comprada, data_pedido))

                subtotal_item = float(prod['price']) * qtd_comprada
                preco_total_pedido += subtotal_item

                itens_pedido_detalhe.append({
                    'product_id': prod['id'],
                    'quantity': qtd_comprada,
                    'price': float(prod['price'])
                })

                itens_json.append({
                    'product_name': prod['name'],
                    'quantity': qtd_comprada,
                    'price': float(prod['price']),
                    'subtotal': subtotal_item
                })

            if not itens_pedido_detalhe:
                continue

            icms = 18.00
            pis = 1.65
            cofins = 7.60
            endereco_simulado = f"Rua das Camélias, {random.randint(10, 999)} - São Paulo/SP"

            # 3. Inserir na tabela 'orders'
            query_order = """
                INSERT INTO orders (user_id, created_at, status, items, total_price, icms_rate, pis_rate, cofins_rate, shipping_address)
                VALUES (%s, %s, 'completed', %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_order, (
                user_id,
                data_pedido,
                json.dumps(itens_json, ensure_ascii=False),
                preco_total_pedido,
                icms,
                pis,
                cofins,
                endereco_simulado
            ))
            
            order_id = cursor.lastrowid

            # 4. Inserir na tabela 'cart_items'
            query_cart_item = """
                INSERT INTO cart_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """
            for item in itens_pedido_detalhe:
                cursor.execute(query_cart_item, (order_id, item['product_id'], item['quantity'], item['price']))

            total_pedidos_gerados += 1

        data_atual += timedelta(days=1)
        conn.commit()

    cursor.close()
    conn.close()
    print(f"✔️ Simulação concluída com sucesso! Total de {total_pedidos_gerados} pedidos inseridos.")

if __name__ == "__main__":
    simular_vendas_ano()
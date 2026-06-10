#!/usr/bin/env python3
"""Simula pedidos para um ano inteiro e escreve CSVs:

- orders.csv: order_id,user_id,created_at,total_price,status
- order_items.csv: order_id,product_id,quantity,unit_price,subtotal

Uso:
    python scripts/simulate_orders.py --year 2025 --avg-orders-per-day 20 --output-dir data

Opcional: --seed para reprodutibilidade.
"""
import argparse
import csv
import os
import random
import sys
import json
from datetime import datetime, timedelta, date

# permitir importar helper de conexão do backend
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from backend import acts
except Exception:
    acts = None


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def generate_product_pool(n=50):
    """Gera um pool de produtos sintéticos (id, price)."""
    pool = []
    for i in range(1, n + 1):
        price = round(random.uniform(5.0, 200.0), 2)
        pool.append({'id': i, 'price': price})
    return pool


def simulate_year(year, avg_orders_per_day=10, max_items=5, product_pool=None):
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    if product_pool is None:
        product_pool = generate_product_pool(200)

    orders = []
    items = []
    order_id = 1

    user_pool = list(range(1, 201))  # ids de usuário simulados

    for d in daterange(start, end):
        # número de pedidos no dia (Poisson-like via normal com floor)
        lam = avg_orders_per_day
        count = max(0, int(random.gauss(lam, max(1, lam * 0.4))))
        for _ in range(count):
            created_at = datetime.combine(d, datetime.min.time()) + timedelta(
                seconds=random.randint(0, 86399)
            )
            user_id = random.choice(user_pool)
            num_items = random.randint(1, max_items)
            order_total = 0.0
            for _ in range(num_items):
                p = random.choice(product_pool)
                qty = random.randint(1, 5)
                unit = p['price']
                subtotal = round(unit * qty, 2)
                order_total += subtotal
                items.append({
                    'order_id': order_id,
                    'product_id': p['id'],
                    'quantity': qty,
                    'unit_price': unit,
                    'subtotal': subtotal,
                })
            order_total = round(order_total, 2)
            status = random.choices(['completed', 'pending', 'canceled'], weights=[0.85, 0.1, 0.05])[0]
            orders.append({
                'order_id': order_id,
                'user_id': user_id,
                'created_at': created_at.isoformat(sep=' '),
                'total_price': order_total,
                'status': status,
            })
            order_id += 1

    return orders, items


def write_csvs(orders, items, outdir):
    os.makedirs(outdir, exist_ok=True)
    orders_path = os.path.join(outdir, 'orders.csv')
    items_path = os.path.join(outdir, 'order_items.csv')

    with open(orders_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['order_id', 'user_id', 'created_at', 'total_price', 'status'])
        w.writeheader()
        for o in orders:
            w.writerow(o)

    with open(items_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['order_id', 'product_id', 'quantity', 'unit_price', 'subtotal'])
        w.writeheader()
        for it in items:
            w.writerow(it)

    return orders_path, items_path


def insert_orders_to_db(orders, items):
    """Insere orders e cart_items no banco usando backend.acts.conectar_bd().

    Retorna (n_orders, n_items) ou lança exceção em erro.
    """
    if acts is None:
        raise RuntimeError('Módulo backend.acts não disponível — execute o script a partir da raiz do projeto')

    conn = acts.conectar_bd()
    if not conn:
        raise RuntimeError('Falha ao conectar ao banco de dados')

    cursor = conn.cursor()
    order_id_map = {}
    inserted_orders = 0
    inserted_items = 0
    try:
        # agrupa itens por pedido
        items_by_order = {}
        for it in items:
            items_by_order.setdefault(it['order_id'], []).append(it)

        # Inserir pedidos com campo JSON `items`
        for o in orders:
            order_items = items_by_order.get(o['order_id'], [])
            items_json = json.dumps([
                {
                    'product_id': it['product_id'],
                    'quantity': it['quantity'],
                    'unit_price': it['unit_price'],
                    'subtotal': it['subtotal'],
                } for it in order_items
            ], ensure_ascii=False)
            cursor.execute(
                "INSERT INTO orders (user_id, created_at, total_price, status, items, icms_rate, pis_rate, cofins_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (o['user_id'], o['created_at'], o['total_price'], o['status'], items_json, 0.00, 0.00, 0.00)
            )
            db_oid = cursor.lastrowid
            order_id_map[o['order_id']] = db_oid
            inserted_orders += 1

        # Inserir linhas em cart_items
        for src_oid, its in items_by_order.items():
            db_oid = order_id_map.get(src_oid)
            if not db_oid:
                continue
            for it in its:
                cursor.execute(
                    "INSERT INTO cart_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (db_oid, it['product_id'], it['quantity'], it['unit_price'])
                )
                inserted_items += 1

        conn.commit()
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        cursor.close()
        conn.close()
        raise
    cursor.close()
    conn.close()
    return inserted_orders, inserted_items


def main():
    p = argparse.ArgumentParser(description='Simula pedidos para um ano e gera CSVs.')
    p.add_argument('--year', type=int, default=datetime.now().year, help='Ano a simular')
    p.add_argument('--avg-orders-per-day', type=float, default=10.0, help='Média de pedidos por dia')
    p.add_argument('--max-items', type=int, default=5, help='Máximo de itens por pedido')
    p.add_argument('--output-dir', type=str, default='data', help='Pasta de saída dos CSVs')
    p.add_argument('--seed', type=int, default=None, help='Seed para RNG')
    p.add_argument('--insert-db', action='store_true', help='Inserir os pedidos gerados direto no banco de dados')
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print(f"Simulando pedidos para o ano {args.year} (média {args.avg_orders_per_day}/dia)...")
    orders, items = simulate_year(args.year, args.avg_orders_per_day, args.max_items)
    o_path, i_path = write_csvs(orders, items, args.output_dir)
    print(f"Gerado: {o_path} ({len(orders)} pedidos)")
    print(f"Gerado: {i_path} ({len(items)} itens)")

    if args.insert_db:
        try:
            n_o, n_i = insert_orders_to_db(orders, items)
            print(f"Inserido no DB: {n_o} pedidos e {n_i} itens de pedido")
        except Exception as e:
            print(f"Erro ao inserir no DB: {e}")


if __name__ == '__main__':
    main()

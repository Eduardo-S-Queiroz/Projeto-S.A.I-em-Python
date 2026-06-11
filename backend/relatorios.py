"""Relatórios e analytics do backend para a aplicação S.A.I.

Este módulo consulta o banco de dados, monta filtros SQL, calcula totais e gera
relatórios mensais e operacionais. Também exporta dados para CSV e converte os
gráficos Plotly em JSON para uso direto nas templates.
"""

import csv
import io
import json
from datetime import datetime
from math import ceil

import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

from acts import conectar_bd

# Tradução dos números dos meses para nomes em português.
MES_NOMES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# Cores usadas nos gráficos Plotly para manter o estilo consistente.
CORES = {
    'principal': '#6b8e6b',
    'secundaria': '#a3b18a',
    'alerta': '#eab308',
    'perigo': '#dc3545',
    'azul': '#4f7cac',
    'roxo': '#7b61ff',
    'texto': '#2d312d'
}


def _plotly_json(fig):
    """Prepara a figura Plotly com estilo e retorna JSON serializável."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, Arial, sans-serif', color=CORES['texto']),
        margin=dict(l=40, r=20, t=45, b=45),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return json.dumps(fig, cls=PlotlyJSONEncoder)


def _fetchall(query, params=None):
    """Executa a consulta SQL e retorna todas as linhas como dicionários."""
    conn = conectar_bd()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or [])
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as err:
        print(f'Erro relatório: {err}')
        try:
            conn.close()
        except Exception:
            pass
        return []


def _montar_where(filtros=None, ano=None, meses=None):
    """Monta a cláusula WHERE dinâmica para os filtros e retorna parâmetros."""
    filtros = filtros or {}
    where = []
    params = []

    if filtros.get('data_inicio'):
        where.append('DATE(o.created_at) >= %s')
        params.append(filtros['data_inicio'])
    if filtros.get('data_fim'):
        where.append('DATE(o.created_at) <= %s')
        params.append(filtros['data_fim'])
    if filtros.get('produto'):
        where.append('p.name LIKE %s')
        params.append(f"%{filtros['produto']}%")
    if filtros.get('fornecedor'):
        where.append('s.id = %s')
        params.append(filtros['fornecedor'])
    if filtros.get('categoria'):
        where.append('c.id = %s')
        params.append(filtros['categoria'])
    if filtros.get('busca'):
        busca = f"%{filtros['busca']}%"
        where.append('(' + ' OR '.join([
            'u.name LIKE %s',
            'u.email LIKE %s',
            'p.name LIKE %s',
            'c.name LIKE %s',
            's.name LIKE %s',
            'o.status LIKE %s'
        ]) + ')')
        params.extend([busca, busca, busca, busca, busca, busca])
    if ano:
        where.append('YEAR(o.created_at) = %s')
        params.append(ano)
    if meses:
        placeholders = ','.join(['%s'] * len(meses))
        where.append(f'MONTH(o.created_at) IN ({placeholders})')
        params.extend(meses)

    return (' WHERE ' + ' AND '.join(where)) if where else '', params


def _base_query(where_sql=''):
    """Retorna a query SQL base para os relatórios, com joins necessários."""
    return f"""
        SELECT o.id AS pedido_id, o.created_at AS data_pedido, o.status AS status_pedido,
               u.name AS cliente, u.email AS email, p.id AS product_id, p.name AS produto,
               p.price AS preco_produto, COALESCE(oi.quantity, 1) AS quantidade,
               COALESCE(oi.price, p.price, 0) AS preco_unitario,
               (COALESCE(oi.quantity, 1) * COALESCE(oi.price, p.price, 0)) AS valor_bruto,
               ((COALESCE(oi.quantity, 1) * COALESCE(oi.price, p.price, 0)) * 0.18) AS icms,
               ((COALESCE(oi.quantity, 1) * COALESCE(oi.price, p.price, 0)) * 0.0165) AS pis,
               ((COALESCE(oi.quantity, 1) * COALESCE(oi.price, p.price, 0)) * 0.076) AS cofins,
               ((COALESCE(oi.quantity, 1) * COALESCE(oi.price, p.price, 0)) * (1 - 0.18 - 0.0165 - 0.076)) AS valor_liquido,
               c.name AS categoria, s.name AS fornecedor
        FROM orders o
        JOIN users u ON u.id = o.user_id
        JOIN cart_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id
        LEFT JOIN inventory i ON i.product_id = p.id
        LEFT JOIN categories c ON c.id = i.category_id
        LEFT JOIN suppliers s ON s.id = i.supplier_id
        {where_sql}
    """


def _totalizadores(rows):
    """Calcula totais agregados usados em relatórios e no dashboard."""
    total_bruto = sum(float(r.get('valor_bruto') or 0) for r in rows)
    total_liquido = sum(float(r.get('valor_liquido') or 0) for r in rows)
    impostos = sum(
        float(r.get('icms') or 0)
        + float(r.get('pis') or 0)
        + float(r.get('cofins') or 0)
        for r in rows
    )
    pedidos = len(set(r.get('pedido_id') for r in rows))
    itens = sum(int(r.get('quantidade') or 0) for r in rows)
    ticket = total_bruto / pedidos if pedidos else 0
    return {
        'total_bruto': total_bruto,
        'total_liquido': total_liquido,
        'impostos': impostos,
        'pedidos': pedidos,
        'itens': itens,
        'ticket_medio': ticket
    }


def get_relatorio_operacional(filtros=None, pagina=1, por_pagina=10):
    """Retorna dados paginados do relatório operacional e totais gerais."""
    where_sql, params = _montar_where(filtros=filtros)
    rows = _fetchall(
        _base_query(where_sql) + ' ORDER BY o.created_at DESC, o.id DESC',
        params
    )

    total = len(rows)
    total_paginas = max(1, ceil(total / por_pagina))
    pagina = max(1, min(pagina, total_paginas))
    inicio_idx = (pagina - 1) * por_pagina
    fim_idx = inicio_idx + por_pagina

    return {
        'dados': rows[inicio_idx:fim_idx],
        'todos': rows,
        'totais': _totalizadores(rows),
        'pagina': pagina,
        'total_paginas': total_paginas,
        'inicio': inicio_idx + 1 if total else 0,
        'fim': min(fim_idx, total),
        'total_registros': total
    }


def get_relatorio_mensal(ano=None, meses=None):
    """Gera relatório mensais agregando por mês e calculando margens."""
    if not ano:
        ano = datetime.now().year

    where_sql, params = _montar_where(ano=ano, meses=meses)
    rows = _fetchall(_base_query(where_sql), params)
    agregados = {}

    for r in rows:
        data = r.get('data_pedido')
        mes = data.month if hasattr(data, 'month') else 0

        if mes not in agregados:
            agregados[mes] = {
                'mes_num': mes,
                'mes': MES_NOMES.get(mes, 'N/A'),
                'pedidos': set(),
                'itens': 0,
                'valor_bruto': 0,
                'icms': 0,
                'pis': 0,
                'cofins': 0,
                'valor_liquido': 0
            }

        agregados[mes]['pedidos'].add(r.get('pedido_id'))
        agregados[mes]['itens'] += int(r.get('quantidade') or 0)
        agregados[mes]['valor_bruto'] += float(r.get('valor_bruto') or 0)
        agregados[mes]['icms'] += float(r.get('icms') or 0)
        agregados[mes]['pis'] += float(r.get('pis') or 0)
        agregados[mes]['cofins'] += float(r.get('cofins') or 0)
        agregados[mes]['valor_liquido'] += float(r.get('valor_liquido') or 0)

    dados = []
    for item in sorted(agregados.values(), key=lambda x: x['mes_num']):
        item['qtd_pedidos'] = len(item.pop('pedidos'))
        item['impostos'] = item['icms'] + item['pis'] + item['cofins']
        item['margem_liquida'] = (
            item['valor_liquido'] / item['valor_bruto'] * 100
        ) if item['valor_bruto'] else 0
        dados.append(item)

    return {'dados': dados, 'totais': _totalizadores(rows), 'ano': ano}


def get_dashboard_analytics(ano=None, meses=None, filtros=None):
    """Gera os valores e gráficos necessários para o dashboard principal."""
    if not ano:
        ano = datetime.now().year

    where_sql, params = _montar_where(filtros=filtros, ano=ano, meses=meses)
    rows = _fetchall(_base_query(where_sql), params)
    totais = _totalizadores(rows)

    mensal = {m: 0 for m in range(1, 13)}
    fornecedores, categorias, produtos, status = {}, {}, {}, {}

    for r in rows:
        data = r.get('data_pedido')
        mes = data.month if hasattr(data, 'month') else 0

        if mes in mensal:
            mensal[mes] += float(r.get('valor_bruto') or 0)

        fornecedores[r.get('fornecedor') or 'Sem fornecedor'] = (
            fornecedores.get(r.get('fornecedor') or 'Sem fornecedor', 0)
            + float(r.get('valor_bruto') or 0)
        )
        categorias[r.get('categoria') or 'Sem categoria'] = (
            categorias.get(r.get('categoria') or 'Sem categoria', 0)
            + float(r.get('valor_bruto') or 0)
        )
        produtos[r.get('produto') or 'N/A'] = (
            produtos.get(r.get('produto') or 'N/A', 0)
            + int(r.get('quantidade') or 0)
        )
        status[r.get('status_pedido') or 'Indefinido'] = (
            status.get(r.get('status_pedido') or 'Indefinido', 0) + 1
        )

    fig_mensal = go.Figure(
        go.Scatter(
            x=[MES_NOMES[m] for m in mensal.keys()],
            y=list(mensal.values()),
            mode='lines+markers',
            fill='tozeroy',
            name='Faturamento',
            line=dict(color=CORES['principal'], width=3),
            marker=dict(size=8)
        )
    )

    top_fornecedores = sorted(fornecedores.items(), key=lambda x: x[1], reverse=True)[:8]
    fig_fornecedor = go.Figure(
        go.Bar(
            x=[x[1] for x in top_fornecedores],
            y=[x[0] for x in top_fornecedores],
            orientation='h',
            marker_color=CORES['secundaria'],
            name='Fornecedor'
        )
    )

    fig_categoria = go.Figure(
        go.Pie(
            labels=list(categorias.keys()),
            values=list(categorias.values()),
            hole=.48,
            marker=dict(colors=[
                CORES['principal'],
                CORES['secundaria'],
                CORES['alerta'],
                CORES['azul'],
                CORES['roxo']
            ])
        )
    )

    top_produtos = sorted(produtos.items(), key=lambda x: x[1], reverse=True)[:8]
    fig_produtos = go.Figure(
        go.Bar(
            x=[x[0] for x in top_produtos],
            y=[x[1] for x in top_produtos],
            marker_color=CORES['principal'],
            name='Unidades vendidas'
        )
    )

    return {
        'totais': totais,
        'ano': ano,
        'graficos': {
            'mensal': _plotly_json(fig_mensal),
            'fornecedores': _plotly_json(fig_fornecedor),
            'categorias': _plotly_json(fig_categoria),
            'produtos': _plotly_json(fig_produtos)
        },
        'status': status,
        'top_produtos': top_produtos,
        'top_fornecedores': top_fornecedores
    }


def exportar_operacional_csv(filtros=None):
    """Exporta o relatório operacional completo para CSV."""
    dados = get_relatorio_operacional(filtros=filtros, pagina=1, por_pagina=10**9)['todos']
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        'Pedido', 'Data', 'Cliente', 'Produto', 'Categoria', 'Fornecedor',
        'Qtd', 'Bruto', 'ICMS', 'PIS', 'COFINS', 'Líquido', 'Status'
    ])

    for r in dados:
        writer.writerow([
            r.get('pedido_id'),
            r.get('data_pedido'),
            r.get('cliente'),
            r.get('produto'),
            r.get('categoria'),
            r.get('fornecedor'),
            r.get('quantidade'),
            f"{float(r.get('valor_bruto') or 0):.2f}",
            f"{float(r.get('icms') or 0):.2f}",
            f"{float(r.get('pis') or 0):.2f}",
            f"{float(r.get('cofins') or 0):.2f}",
            f"{float(r.get('valor_liquido') or 0):.2f}",
            r.get('status_pedido')
        ])

    return output.getvalue()


def exportar_mensal_csv(ano=None, meses=None):
    """Exporta o relatório mensal para CSV."""
    dados = get_relatorio_mensal(ano=ano, meses=meses)['dados']
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        'Mês', 'Pedidos', 'Itens', 'Bruto', 'ICMS', 'PIS', 'COFINS',
        'Impostos', 'Líquido', 'Margem %'
    ])

    for r in dados:
        writer.writerow([
            r['mes'],
            r['qtd_pedidos'],
            r['itens'],
            f"{r['valor_bruto']:.2f}",
            f"{r['icms']:.2f}",
            f"{r['pis']:.2f}",
            f"{r['cofins']:.2f}",
            f"{r['impostos']:.2f}",
            f"{r['valor_liquido']:.2f}",
            f"{r['margem_liquida']:.2f}"
        ])

    return output.getvalue()

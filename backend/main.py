import os
import sys
from flask import Flask, render_template, request, redirect, url_for, Response
from werkzeug.utils import secure_filename

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

sys.path.insert(0, BASE_DIR)

from acts import (
    verificar_login,
    listar_produtos,
    cadastrar_produto,
    atualizar_produto,
    listar_estoque,
    salvar_estoque,
    listar_movimentacoes,
    listar_categorias,
    cadastrar_categoria,
    atualizar_categoria,
    excluir_categoria,
    listar_fornecedores,
    cadastrar_fornecedor,
    atualizar_fornecedor,
    excluir_fornecedor,
    lista_pedidos,
    obter_detalhes_pedido,
    listar_anos_pedidos,
)
from relatorios import (
    get_relatorio_operacional,
    get_relatorio_mensal,
    get_dashboard_analytics,
    exportar_operacional_csv,
    exportar_mensal_csv,
)

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def _filtrar_lista_por_q(items, campos, q):
    """Filtra uma lista de dicionários por termos em `q` (case-insensitive).

    - items: lista de dicts
    - campos: lista de chaves a checar no dict
    - q: string de busca
    Retorna a lista filtrada (se q vazio, retorna original).
    """
    if not q:
        return items
    ql = q.strip().lower()
    def matches(item):
        for c in campos:
            v = item.get(c) if isinstance(item, dict) else None
            if v is None:
                # tenta atributos de objetos (caso retornos não sejam dicts)
                try:
                    v = getattr(item, c)
                except Exception:
                    v = None
            if v is None:
                continue
            try:
                if ql in str(v).lower():
                    return True
            except Exception:
                continue
        return False
    return [it for it in items if matches(it)]


def salvar_upload_imagem(campo='image_file'):
    """Salva arquivo enviado e retorna caminho relativo dentro de static/."""
    if campo not in request.files:
        return None
    file = request.files[campo]
    if not file or file.filename == '':
        return None
    filename = secure_filename(file.filename)
    destino = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(destino)
    return 'uploads/' + filename


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if verificar_login(email, password):
            return redirect(url_for('index'))
        return render_template('login.html', error="Email ou senha inválidos!")
    return render_template('login.html')


@app.route('/index.html')
def index():
    q = request.args.get('q', default='')
    produtos = listar_produtos()
    categorias = listar_categorias()
    fornecedores = listar_fornecedores()

    if q:
        produtos = _filtrar_lista_por_q(produtos, ['name', 'description'], q)
        categorias = _filtrar_lista_por_q(categorias, ['name'], q)
        fornecedores = _filtrar_lista_por_q(fornecedores, ['name'], q)

    return render_template(
        'index.html',
        produtos=produtos,
        categorias=categorias,
        fornecedores=fornecedores
    )


@app.route('/produtos', methods=['POST'])
def produtos_actions():
    action = request.form.get('action')
    product_id = request.form.get('id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    image_url = request.form.get('image_url')
    featured = 1 if request.form.get('featured') else 0
    image_path = salvar_upload_imagem('image_file')

    if action == 'add':
        cadastrar_produto(name, description, price, image_url, image_path, featured)
    elif action == 'edit':
        atualizar_produto(product_id, name, description, price, image_url, image_path, featured)

    return redirect(url_for('index'))


@app.route('/estoque.html')
def estoque():
    q = request.args.get('q', default='')
    estoque_list = listar_estoque()
    produtos = listar_produtos()
    categorias = listar_categorias()
    fornecedores = listar_fornecedores()

    if q:
        estoque_list = _filtrar_lista_por_q(estoque_list, ['product_name', 'category_name', 'supplier_name'], q)

    return render_template(
        'estoque.html',
        estoque=estoque_list,
        produtos=produtos,
        categorias=categorias,
        fornecedores=fornecedores
    )


@app.route('/estoque/salvar', methods=['POST'])
def estoque_salvar():
    inventory_id = request.form.get('inventory_id')
    product_id = request.form.get('product_id') or request.form.get('original_product_id')
    category_id = request.form.get('category_id')
    supplier_id = request.form.get('supplier_id')
    quantity = request.form.get('quantity')
    salvar_estoque(product_id, category_id, supplier_id, quantity, inventory_id=inventory_id)
    return redirect(url_for('estoque'))


@app.route('/categorias.html', methods=['GET', 'POST'])
def categorias():
    if request.method == 'POST':
        action = request.form.get('action')
        category_id = request.form.get('id')
        name = request.form.get('name')
        if action == 'add' and name:
            cadastrar_categoria(name)
        elif action == 'edit' and category_id and name:
            atualizar_categoria(category_id, name)
        elif action == 'delete' and category_id:
            excluir_categoria(category_id)
        return redirect(url_for('categorias'))
    q = request.args.get('q', default='')
    categorias_list = listar_categorias()
    if q:
        categorias_list = _filtrar_lista_por_q(categorias_list, ['name'], q)
    return render_template('categorias.html', categorias=categorias_list)


@app.route('/fornecedores.html', methods=['GET', 'POST'])
def fornecedores():
    if request.method == 'POST':
        action = request.form.get('action')
        supplier_id = request.form.get('id')
        name = request.form.get('name')
        if action == 'add' and name:
            cadastrar_fornecedor(name)
        elif action == 'edit' and supplier_id and name:
            atualizar_fornecedor(supplier_id, name)
        elif action == 'delete' and supplier_id:
            excluir_fornecedor(supplier_id)
        return redirect(url_for('fornecedores'))
    q = request.args.get('q', default='')
    fornecedores_list = listar_fornecedores()
    if q:
        fornecedores_list = _filtrar_lista_por_q(fornecedores_list, ['name'], q)
    return render_template('fornecedores.html', fornecedores=fornecedores_list)


@app.route('/movimentacoes.html')
def movimentacoes():
    q = request.args.get('q', default='')
    movs = listar_movimentacoes()
    if q:
        movs = _filtrar_lista_por_q(movs, ['product_name', 'category_name', 'supplier_name', 'reason', 'type'], q)
    return render_template('movimentacoes.html', movs=movs)


@app.route('/pedidos.html')
def pedidos():
    q = request.args.get('q', default='')
    pedidos_list = lista_pedidos()
    if q:
        pedidos_list = _filtrar_lista_por_q(pedidos_list, ['cliente', 'id', 'status'], q)
    return render_template('pedidos.html', pedidos=pedidos_list)


@app.route('/pedido/<int:pedido_id>/detalhes')
def pedido_detalhes(pedido_id):
    from flask import jsonify
    
    resultado = obter_detalhes_pedido(pedido_id)
    
    if not resultado:
        return jsonify({'success': False, 'message': 'Pedido não encontrado'}), 404
    
    pedido = resultado['pedido']
    itens = resultado['itens']
    
    
    print("\n" + "="*40)
    print(f"DEBUG: Buscando itens para o pedido ID: {pedido_id}")
    print(f"DEBUG: Resultado do banco de dados: {itens}")
    print("="*40 + "\n")
    
    # Calcula o total somando (preço * quantidade) de cada item retornado do banco
    total = sum(float(item.get('price', 0)) * int(item.get('quantity', 0)) for item in itens)
    
    return jsonify({
        'success': True,
        'pedido': {
            'id': pedido.get('id'),
            'cliente': pedido.get('cliente', 'Não informado'),
            'email': pedido.get('email', 'Não informado'),
            'created_at': str(pedido.get('created_at', 'Não informado')),
            'status': pedido.get('status', 'Não informado'),
            'shipping_address': pedido.get('shipping_address', 'Não informado'),
        },
        'items': [
            {
                'product_name': item.get('product_name', 'Produto'),
                'quantity': item.get('quantity', 0),
                'unit_price': float(item.get('price', 0)), # Chave corrigida para o front-end
                'subtotal': float(item.get('price', 0)) * int(item.get('quantity', 0)),
            }
            for item in itens
        ],
        'total': total
    })


@app.route('/dashboard.html')
def dashboard():
    ano = request.args.get('ano', type=int)
    meses = request.args.getlist('mes', type=int)
    dados = get_dashboard_analytics(ano=ano, meses=meses)
    anos = listar_anos_pedidos()
    ano_selecionado = ano or dados.get('ano')
    return render_template('dashboard.html', dados=dados, anos=anos, ano_selecionado=ano_selecionado, meses_selecionados=meses)


@app.route('/relatorio_operacional.html')
def rel_operacional():
    filtros = {
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
        'produto': request.args.get('produto'),
        'fornecedor': request.args.get('fornecedor'),
        'categoria': request.args.get('categoria'),
    }
    pagina = request.args.get('pagina', default=1, type=int)
    resultado = get_relatorio_operacional(filtros=filtros, pagina=pagina, por_pagina=10)
    return render_template(
        'relatorio_operacional.html',
        dados=resultado['dados'],
        fornecedores=listar_fornecedores(),
        categorias=listar_categorias(),
        totais=resultado['totais'],
        pagina=resultado['pagina'],
        total_paginas=resultado['total_paginas'],
        inicio=resultado['inicio'],
        fim=resultado['fim'],
        total_registros=resultado['total_registros'],
    )


@app.route('/relatorio_mensal.html')
def rel_mensal():
    ano = request.args.get('ano', type=int)
    meses = request.args.getlist('mes', type=int)
    resultado = get_relatorio_mensal(ano=ano, meses=meses)
    return render_template(
        'relatorio_mensal.html',
        anos=listar_anos_pedidos(),
        dados=resultado['dados'],
        totais=resultado['totais'],
        ano_selecionado=ano or resultado['ano'],
        meses_selecionados=meses,
    )


@app.route('/exportar_operacional')
def exportar_operacional():
    filtros = {
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
        'produto': request.args.get('produto'),
        'fornecedor': request.args.get('fornecedor'),
        'categoria': request.args.get('categoria'),
    }
    csv_data = exportar_operacional_csv(filtros)
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=relatorio_operacional_sai.csv'}
    )


@app.route('/exportar_mensal')
def exportar_mensal():
    ano = request.args.get('ano', type=int)
    meses = request.args.getlist('mes', type=int)
    csv_data = exportar_mensal_csv(ano=ano, meses=meses)
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=relatorio_mensal_sai.csv'}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)

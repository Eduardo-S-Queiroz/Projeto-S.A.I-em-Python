import os
import sys
from flask import Flask, jsonify, render_template, request, redirect, url_for, Response
from werkzeug.utils import secure_filename

# Configuração de caminhos para templates, arquivos estáticos e uploads.
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
    listar_anos_pedidos,
    excluir_estoque,
    excluir_produto,
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

# Helper para salvar imagens de produto enviadas pelo formulário.
# Retorna o caminho relativo dentro de static/ para ser usado no campo image_path.
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
    """Rota de login principal.

    - GET: renderiza o formulário de login.
    - POST: valida as credenciais e redireciona para o dashboard de produtos.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if verificar_login(email, password):
            return redirect(url_for('index'))
        return render_template('login.html', error="Email ou senha inválidos!")
    return render_template('login.html')


@app.route('/index.html')
def index():
    """Mostra a lista de produtos e permite busca de produtos por nome/descrição."""
    q = request.args.get('q', '').strip() or None
    return render_template(
        'index.html',
        produtos=listar_produtos(q=q),
        categorias=listar_categorias(),
        fornecedores=listar_fornecedores()
    )


@app.route('/produtos', methods=['POST'])
def produtos_actions():
    """Processa ações de CRUD de produtos enviadas pelo formulário."""
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
    elif action == 'delete':
        excluir_produto(product_id)
    return redirect(url_for('index'))


@app.route('/estoque.html')
def estoque():
    """Rota para exibir o estoque com busca opcional."""
    q = request.args.get('q', '').strip() or None
    return render_template(
        'estoque.html',
        estoque=listar_estoque(q=q),
        produtos=listar_produtos(),
        categorias=listar_categorias(),
        fornecedores=listar_fornecedores()
    )


@app.route('/estoque/salvar', methods=['POST'])
def estoque_salvar():
    """Recebe o formulário de estoque e persiste a alteração no banco."""
    product_id = request.form.get('product_id')
    category_id = request.form.get('category_id')
    supplier_id = request.form.get('supplier_id')
    quantity = request.form.get('quantity')
    salvar_estoque(product_id, category_id, supplier_id, quantity)
    return redirect(url_for('estoque'))

@app.route('/estoque/excluir', methods=['POST'])
def excluir_estoque_route():
    """Recebe o pedido de exclusão de um registro de estoque."""
    stock_id = request.form.get('id')
    excluir_estoque(stock_id)
    return redirect(url_for('estoque'))


@app.route('/categorias.html', methods=['GET', 'POST'])
def categorias():
    """Mostra o cadastro de categorias e processa criação/edição/exclusão."""
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
    q = request.args.get('q', '').strip() or None
    return render_template('categorias.html', categorias=listar_categorias(q=q))


@app.route('/fornecedores.html', methods=['GET', 'POST'])
def fornecedores():
    """Mostra a página de fornecedores e processa criação/edição/exclusão."""
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
    q = request.args.get('q', '').strip() or None
    return render_template('fornecedores.html', fornecedores=listar_fornecedores(q=q))


@app.route('/movimentacoes.html')
def movimentacoes():
    """Exibe o histórico de movimentações de estoque, com busca opcional."""
    q = request.args.get('q', '').strip() or None
    return render_template('movimentacoes.html', movs=listar_movimentacoes(q=q))


@app.route('/pedidos.html')
def pedidos():
    """Exibe a lista de pedidos e aplica busca por cliente, email ou status."""
    q = request.args.get('q', '').strip() or None
    return render_template('pedidos.html', pedidos=lista_pedidos(q=q))

@app.route('/pedido/<int:id>/detalhes', methods=['GET'])
def detalhes_do_pedido(id):
    """Retorna dados de um pedido em JSON para o modal de detalhes."""
    return jsonify({
        "success": True,
        "total": 150.00, # Exemplo
        "pedido": {
            "cliente": "Nome do Cliente",
            "email": "cliente@email.com",
            "created_at": "10/06/2026",
            "status": "Pendente",
            "shipping_address": "Rua dos Chás, 123"
        },
        "items": [
            { "product_name": "Matcha Premium", "quantity": 2, "unit_price": 45.00, "subtotal": 90.00 },
            { "product_name": "Sencha Japonês", "quantity": 1, "unit_price": 32.00, "subtotal": 32.00 }
        ]
    })


@app.route('/dashboard.html')
def dashboard():
    """Renderiza a página de dashboard com gráficos e filtros por ano/mês."""
    ano = request.args.get('ano', type=int)
    meses = request.args.getlist('mes', type=int)
    q = request.args.get('q', '').strip() or None
    filtros = {'busca': q} if q else {}
    dados = get_dashboard_analytics(ano=ano, meses=meses, filtros=filtros)
    anos = listar_anos_pedidos()
    ano_selecionado = ano or dados.get('ano')
    return render_template(
        'dashboard.html',
        dados=dados,
        anos=anos,
        ano_selecionado=ano_selecionado,
        meses_selecionados=meses,
        q=q
    )


@app.route('/relatorio_operacional.html')
def rel_operacional():
    """Renderiza o relatório operacional com filtros, pesquisa e paginação."""
    q = request.args.get('q', '').strip() or None
    filtros = {
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
        'produto': request.args.get('produto'),
        'fornecedor': request.args.get('fornecedor'),
        'categoria': request.args.get('categoria'),
        'busca': q,
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
        q=q,
    )


@app.route('/relatorio_mensal.html')
def rel_mensal():
    """Renderiza o relatório mensal com filtros de ano e meses."""
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
    """Gera e envia o relatório operacional em formato CSV."""
    filtros = {
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
        'produto': request.args.get('produto'),
        'fornecedor': request.args.get('fornecedor'),
        'categoria': request.args.get('categoria'),
        'busca': request.args.get('q', '').strip() or None,
    }
    csv_data = exportar_operacional_csv(filtros)
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=relatorio_operacional_sai.csv'}
    )


@app.route('/exportar_mensal')
def exportar_mensal():
    """Gera e envia o relatório mensal em formato CSV."""
    ano = request.args.get('ano', type=int)
    meses = request.args.getlist('mes', type=int)
    csv_data = exportar_mensal_csv(ano=ano, meses=meses)
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=relatorio_mensal_sai.csv'}
    )


if __name__ == "__main__":
    # Inicia o servidor Flask em modo debug na porta 5000.
    app.run(debug=True, port=5000)

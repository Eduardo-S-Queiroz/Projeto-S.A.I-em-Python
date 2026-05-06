import os
import sys
import json
import plotly.graph_objects as go
import plotly.express as px
import calendar
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

# Adicionar o diretório atual ao sys.path para garantir que o módulo api seja encontrado
sys.path.insert(0, os.path.dirname(__file__))

from api import ( listar_produtos, verificar_login, listar_categorias, lista_pedidos, consultar_produto, 
cadastrar_produto, status_produto, atualizar_produto, obter_nome_cliente, obter_nome_categoria, obter_email )

from dashboard import get_data_from_db

# 1. Define o caminho base (onde o seu main.py está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define o caminho do projeto raiz (um nível acima de backend)
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# 3. Configura as pastas corretamente (elas estão na raiz do projeto)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

# 4. Inicializa o Flask usando essas variáveis
app = Flask(__name__, 
            template_folder=TEMPLATES_DIR,
            static_folder=STATIC_DIR) 

# Rota de Login (Única responsável pela raiz '/')
@app.route('/', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if verificar_login(email, password):
            
            return redirect(url_for('index')) 
        else:
            return render_template('login.html', error="Email ou senha inválidos!")
            
    return render_template('login.html')

# Rota de Produtos (Responsável por exibir a lista de produtos, tanto para GET quanto para POST)
@app.route("/index", methods=['GET', 'POST'])
def index():
    # Busca a lista de produtos e pedidos antes de renderizar
    lista_de_produtos = listar_produtos()
    lista_de_pedidos = lista_pedidos()
    lista_de_categorias = listar_categorias()
    
    

    # Converter status dos produtos 
    for produto in lista_de_produtos:
        # Converte o campo status para ativo/inativo
        status = produto.get('status')
        produto['status'] = 'ativo' if status else 'inativo'
        
        featured = produto.get('featured') or produto.get('destaque') or 0
        produto['featured'] = 'ativo' if featured else 'inativo'
        
        if 'category_id' in produto:
           produto['category'] = obter_nome_categoria(produto['category_id'])

    # Converter os itens dos pedidos para exibir o nome do produto e calcular o preço total
    for pedido in lista_de_pedidos:
        pedido['cliente'] = ''
        pedido['produto'] = ''
        pedido['price'] = ''

        if pedido.get('user_id') is not None:
            pedido['cliente'] = obter_nome_cliente(pedido['user_id'])
            pedido['email'] = obter_email(pedido['user_id'])

        itens_json = pedido.get('items') or pedido.get('itens')
        if itens_json:
            try:
                if isinstance(itens_json, (bytes, bytearray)):
                    itens_json = itens_json.decode('utf-8')

                if isinstance(itens_json, str):
                    itens = json.loads(itens_json)
                else:
                    itens = itens_json

                if isinstance(itens, dict):
                    itens = [itens]

                if isinstance(itens, list):
                    pedido['produto'] = ", ".join(
                        str(item.get('name') or item.get('nome') or '') for item in itens if isinstance(item, dict)
                    )
                    pedido['price'] = sum(
                        float(item.get('quantity') or item.get('quantidade') or 0) * float(item.get('price') or item.get('preco') or 0) for item in itens if isinstance(item, dict)
                    )
                else:
                    pedido['produto'] = str(itens)
                    pedido['price'] = ''
            except Exception:
                pedido['produto'] = str(itens_json)
                pedido['price'] = ''
                
    # Verificar se é uma requisição POST para atualizar um produto ou status
    if request.method == 'POST':
        # Verificar se é uma atualização de produto
        if 'product_id' in request.form:
            product_id = request.form['product_id']
            code = request.form['code']
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            category_id = request.form['category_id']
            image = request.form['image']
            stock = request.form['stock']
            slug = request.form['slug']
            featured = 1 if 'featured' in request.form else 0
            
            atualizar_produto(product_id, code, name, description, price, category_id, image, stock, slug, featured)
        
        # Verificar se é uma atualização de status
        elif 'status_product_id' in request.form:
            product_id = request.form['status_product_id']
            status_produto(product_id)

        return redirect(url_for('index'))
    
    #consultar categorias para exibir no dropdown de edição
    lista_de_categorias = listar_categorias()
    
    #ultilizando a função consultar_produto para obter os detalhes do produto para exibir no modal de edição
    for produto in lista_de_produtos:
        produto_id = produto.get('id') or produto.get('id')
        detalhes_produto = consultar_produto(produto_id)
        if detalhes_produto:
            produto['details'] = detalhes_produto
        else:
            produto['details'] = {}
            
    #ultilizando a função cadastrar_produto para cadastrar um novo produto caso os campos de cadastro sejam preenchidos
    if request.method == 'POST' and 'new_product' in request.form:
        code = request.form['new_code']
        name = request.form['new_name']
        description = request.form['new_description']
        price = request.form['new_price']
        category_id = request.form['new_category_id']
        image = request.form['new_image']
        stock = request.form['new_stock']
        slug = request.form['new_slug']
        featured = 1 if 'new_featured' in request.form else 0
        
        cadastrar_produto(code, name, description, price, category_id, image, stock, slug, featured)
        
        return redirect(url_for('index'))
    
    
    # Verificar se as listas estão vazias e renderizar a página com mensagens de erro apropriadas
    
    if not lista_de_produtos:
        return render_template('index.html', produtos=[], pedidos=lista_de_pedidos, error="Nenhum produto encontrado.")
    
    if not lista_de_pedidos:
        return render_template('index.html', produtos=lista_de_produtos, pedidos=[], error="Nenhum pedido encontrado.")
    if lista_de_categorias is None:
        return render_template('index.html', produtos=lista_de_produtos, pedidos=lista_de_pedidos, error="Erro ao carregar categorias.")

    
    return render_template('index.html', produtos=lista_de_produtos, pedidos=lista_de_pedidos, categorias=lista_de_categorias,)

@app.route("/dashboard", methods=['GET'])
@app.route("/dashboard.html", methods=['GET'])
def dashboard():
    df_orders, df_products = get_data_from_db()

    # Criar gráficos usando Plotly
    labels = {
        'created_at': 'Data do Pedido',
        'total_price': 'Total (R$)',
        'date_column': 'Data do Pedido',
        'category_name': 'Categoria'
    }

    # Faturamento Total
    total_faturado = df_orders['total_price'].sum()

    # Quantidade de Pedidos
    total_pedidos = len(df_orders)

    # Pega o ano e mês atuais automaticamente
    hoje = datetime.now()
    ano = hoje.year
    mes = hoje.month

    # Define o primeiro dia e o último dia dinamicamente
    data_inicio = f"{ano}-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_fim = f"{ano}-{mes:02d}-{ultimo_dia}"

    # Aplica a filtragem
    df_filtrado = df_orders[
        (df_orders['created_at'] >= data_inicio) & 
        (df_orders['created_at'] <= data_fim)
    ].copy()

    # Gráfico de Vendas por Data
    fig_sales = px.bar(
        df_filtrado,
        x = 'created_at',
        y = 'total_price',
        title = 'Vendas por Data',
        labels = labels,
        text_auto = '.2s',
        color_discrete_sequence = ['#1f77b4'],
        width = 555,
        
    )
    
    fig_sales.update_layout(bargap=0.7)  # Ajusta o espaçamento entre as barras
    
    fig_sales.update_layout(
        font=dict(family='Arial, sans-serif', size=13, color='#1e1e28'),
        xaxis_title="Período",
        yaxis_title="Faturamento (R$)",
        template="plotly_white", # Fundo limpo
        hovermode="x unified"    # Mostra os valores ao passar o mouse na linha
    )

    # Para formatar o R$ no eixo Y e nas barras
    fig_sales.update_traces(texttemplate='R$ %{y:.2f}', textposition='outside')
    
    
    fig_category = px.scatter(
        df_products, 
        x='stock',     # You need an X axis for a line chart
        y='price',    # You need a Y axis for a line chart
        color='category_name', 
        title='Relação Preço vs. Estoque por Categoria',
        labels={'stock': 'Estoque', 'price': 'Preço (R$)', 'category_name': 'Categoria'}
    )
    
    fig_category.update_layout(
        font=dict(family='Arial, sans-serif', size=13, color='#1e1e28'),
        xaxis_title="Estoque", 
        yaxis_title="Preço (R$)",
        template="plotly_white",    
        legend_title="Categoria",
        height=400,
        width=550,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    
    # Chart 2: Distribuição de Status (Pizza)
    if not df_orders.empty:
        status_chart = px.pie( 
                df_orders.groupby('status').size().reset_index(name='count'),
                names='status',
                values='count',
                title='Distribuição de Status dos Pedidos',
                hole=0.4,
                color='status',
                color_discrete_map={
                    'completed': "rgb(0, 204, 150)",
                    'pending': "rgb(255, 161, 90)",
                    'shipped': "rgb(59, 72, 246)",
                    'canceled': "rgb(239, 68, 68)"
                },
                template='plotly_white'
            )
    else:
            status_chart = go.Figure()
            status_chart.add_annotation(text="Sem dados de pedidos")
        
    status_chart.update_layout(
            font=dict(family='Arial, sans-serif', size=12, color='#1e1e28'),
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
           
    )
    
    
    
    if not df_products.empty:
        # 1. Agrupar, somar quantidades e pegar os 5 maiores
        top_5_df = df_products.groupby('name')['stock'].sum().nlargest(5).reset_index()
    
        # 2. Criar o gráfico de barras horizontais
        top_products_chart = px.line(
            top_5_df,
            x='stock',
            y='name',
            orientation='h', # Define como horizontal
            title='Top 5 Produtos Mais Vendidos',
            text='stock', # Exibe o valor sobre a barra
            labels={'stock': 'Estoque', 'name': 'Produto'},
            template='plotly_white',
            color_discrete_sequence=["rgb(59, 125, 246)"] # Azul similar ao dashboard
        )
        
        # Ajustar para que a maior barra fique no topo
        top_products_chart.update_layout(yaxis={'categoryorder': 'total ascending'})

    else:
        top_products_chart = go.Figure()
        top_products_chart.add_annotation(text="Sem dados de produtos")

    # Padronização de layout (conforme seu exemplo)
    top_products_chart.update_layout(
        font=dict(family='Arial, sans-serif, negrito', size=13, color='#1e1e28'),
        height=400,
        width=580,
        barmode='group',
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    # Renderizar o template do dashboard com os gráficos
    return render_template('dashboard.html', top_products_chart=top_products_chart.to_html(full_html=False), status_chart=status_chart.to_html(full_html=False), fig_sales=fig_sales.to_html(full_html=False), fig_category=fig_category.to_html(full_html=False, include_plotlyjs='cdn'), total_faturado=total_faturado, total_pedidos=total_pedidos )



if __name__ == '__main__':
    app.run(debug=True)

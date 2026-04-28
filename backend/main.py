import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for

# Adicionar o diretório atual ao sys.path para garantir que o módulo api seja encontrado
sys.path.insert(0, os.path.dirname(__file__))

from api import ( listar_produtos, verificar_login, listar_categorias, lista_pedidos, consultar_produto, 
cadastrar_produto, status_produto, atualizar_produto, obter_nome_cliente, obter_nome_categoria, obter_email )


# Configurar caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'templates', 'icon')

# Inicializar Flask com as pastas
app = Flask(__name__, 
            template_folder=TEMPLATES_DIR,
            static_folder=STATIC_DIR,
            static_url_path='/icon')

# Rota de Login (Única responsável pela raiz '/')
@app.route('/', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if verificar_login(email, password):
            
            return redirect(url_for('produtos')) 
        else:
            return render_template('login.html', error="Email ou senha inválidos!")
            
    return render_template('login.html')

# Rota de Produtos (Responsável por exibir a lista de produtos, tanto para GET quanto para POST)
@app.route("/produtos.html", methods=['GET', 'POST'])
def produtos():
    # Busca a lista de produtos e pedidos antes de renderizar
    lista_de_produtos = listar_produtos()
    lista_de_pedidos = lista_pedidos()
    lista_de_categorias = listar_categorias()

    # Converter status dos produtos 
    for produto in lista_de_produtos:
        # Converte o campo status para ativo/inativo
        status = produto.get('status') or produto.get('status') or 0
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

        return redirect(url_for('produtos'))
    
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
        
        return redirect(url_for('produtos'))
    
    # Verificar se as listas estão vazias e renderizar a página com mensagens de erro apropriadas
    
    if not lista_de_produtos:
        return render_template('produtos.html', produtos=[], pedidos=lista_de_pedidos, error="Nenhum produto encontrado.")
    
    if not lista_de_pedidos:
        return render_template('produtos.html', produtos=lista_de_produtos, pedidos=[], error="Nenhum pedido encontrado.")
    
    if lista_de_categorias is None:
        return render_template('produtos.html', produtos=lista_de_produtos, pedidos=lista_de_pedidos, error="Erro ao carregar categorias.")

    return render_template('produtos.html', produtos=lista_de_produtos, pedidos=lista_de_pedidos, categorias=lista_de_categorias)

if __name__ == '__main__':
    app.run(debug=True)

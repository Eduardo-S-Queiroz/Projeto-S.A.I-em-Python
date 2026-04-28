import os
import json
from flask import Flask, render_template, request, redirect, url_for
from api import listar_produtos, verificar_login, listar_categorias, lista_pedidos, consultar_produto, cadastrar_produto, status_produto, atualizar_produto, obter_nome_cliente, obeter_nome_categoria

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

    # Converter status dos produtos 
    for produto in lista_de_produtos:
        # Converte o campo status para ativo/inativo
        status = produto.get('status') or produto.get('status') or 0
        produto['status'] = 'ativo' if status else 'inativo'
        
        featured = produto.get('featured') or produto.get('destaque') or 0
        produto['featured'] = 'ativo' if featured else 'inativo'
        
        if 'category_id' in produto:
           produto['category'] = obeter_nome_categoria(produto['category_id'])

    for pedido in lista_de_pedidos:
        pedido['cliente'] = ''
        pedido['produto'] = ''
        pedido['price'] = ''

        if pedido.get('user_id') is not None:
            pedido['cliente'] = obter_nome_cliente(pedido['user_id'])

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

    return render_template('index.html', produtos=lista_de_produtos, pedidos=lista_de_pedidos)

if __name__ == '__main__':
    app.run(debug=True)

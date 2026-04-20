import os
import json
from flask import Flask, render_template, request, redirect, url_for
from api import listar_produtos, verificar_login, listar_categorias, lista_pedidos, consultar_produto, cadastrar_produto, status_produto, atualizar_produto, obter_nome_cliente

# Configurar caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'templates', 'icon')

# Inicializar Flask com as pastas
app = Flask(__name__, 
            template_folder=TEMPLATES_DIR,
            static_folder=STATIC_DIR,
            static_url_path='/icon')

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


@app.route("/produtos")
def produtos():
    # Busca a lista de produtos do banco de dados
    lista_de_produtos = listar_produtos()
    
    if not lista_de_produtos:
        return "<h1>Nenhum produto encontrado.</h1><p><a href='/cadastrar'>Cadastrar o primeiro produto</a></p>"
    
    html_lista = "<ul>"
    for p in lista_de_produtos:
        nome = p.get('name', 'Sem nome')
        preco = p.get('price', 0.0)
        estoque = p.get('stock', 0)
        preco_formatado = f"R$ {preco:2.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        html_lista += f"<div>{nome} - {preco_formatado} em estoque - {estoque} unidades</div>"
    html_lista += "</ul>"
    
    lista_de_pedidos = lista_pedidos()

    if not lista_de_pedidos:
        html_lista += "<p>Nenhum pedido encontrado.</p>"
    html_lista += "<h2>Pedidos</h2><ul>"
    for pedido in lista_de_pedidos:
        id_pedido = pedido.get('id', 'N/A')
        user_id = pedido.get('user_id', 'N/A')
        nome_cliente = obter_nome_cliente(user_id)
        status = pedido.get('status', 'N/A')
        
        # Parsear JSON do items
        items_str = pedido.get('items', '[]')
        if isinstance(items_str, bytes):
            items_str = items_str.decode('utf-8')
        try:
            items = json.loads(items_str)
            produtos_texto = ", ".join([f"{item.get('name', 'Produto')} (qty: {item.get('quantity', 1)})" for item in items])
        except:
            produtos_texto = "Produtos não disponíveis"
        
        preco_total = pedido.get('total_price')
        preco_total_formatado = f"R$ {preco_total:2.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        html_lista += f"<li>Pedido #{id_pedido} - Cliente: {nome_cliente} - Status: {status} - Produtos: {produtos_texto} - Total: {preco_total_formatado}</li>"
    html_lista += "</ul>"



    return f"<h1>Lista de Produtos</h1>{html_lista}<p><a href='/cadastrar'>Cadastrar Novo</a> | <a href='login.html'>Sair</a></p>"


if __name__ == '__main__':
    app.run(debug=True)

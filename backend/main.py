from flask import Flask, render_template, request, redirect, url_for
from api import listar_produtos, verificar_login 

app = Flask(__name__, template_folder='../template')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if verificar_login(email, password):
            return redirect(url_for('produtos'))
        else:
            return render_template('../template/login.html', error="Email ou senha inválidos!")
            
    return render_template('login.html')


@app.route("/produtos")
def produtos():
    # Busca a lista de produtos do banco de dados
    lista_de_produtos = listar_produtos()
    
    if not lista_de_produtos:
        return "<h1>Nenhum produto encontrado.</h1><p><a href='/cadastrar'>Cadastrar o primeiro produto</a></p>"
    
    # Gera uma lista simples em HTML para visualização rápida
    html_lista = "<ul>"
    for p in lista_de_produtos:
        #.get() para evitar erros se alguma coluna estiver vazia
        nome = p.get('name', 'Sem nome')
        preco = p.get('price', 0.0)
        estoque = p.get('stock', 0)
        html_lista += f"<li><strong>{nome}</strong> - R$ {preco:2.2f} em estoque - {estoque} unidades</li> "
    html_lista += "</ul>"

    return f"<h1>Lista de Produtos</h1>{html_lista}<p><a href='/cadastrar'>Cadastrar Novo</a> | <a href='/login'>Sair</a></p>"


if __name__ == '__main__':
    app.run(debug=True)

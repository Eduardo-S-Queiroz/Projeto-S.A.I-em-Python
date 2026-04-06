from flask import Flask, render_template, request, redirect, url_for
from api import verificar_login 

app = Flask(__name__, template_folder='../template')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Usamos a função correta aqui
        if verificar_login(email, password):
            return redirect(url_for('success'))
        else:
            return render_template('../template/login.html', error="Email ou senha inválidos!")
            
    return render_template('login.html')

@app.route("/success")
def success():
    return "<h1>Login realizado com sucesso! Bem-vindo!</h1>"

if __name__ == '__main__':
    app.run(debug=True)

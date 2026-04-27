# Projeto S.A.I. em Python 🐍

Bem-vindo ao Projeto S.A.I. (Sistema de Automação Inteligente) em Python! Este é um projeto web simples desenvolvido com Flask para gerenciar produtos, incluindo funcionalidades de login e listagem de itens. Ele demonstra a integração de um frontend básico com um backend Python que interage com um banco de dados MySQL. 🚀

## 🌟 Funcionalidades

Este projeto oferece as seguintes funcionalidades principais:

- **Autenticação de Usuário**: Sistema de login para acesso seguro à aplicação. 🔒
- **Listagem de Produtos**: Exibição de uma lista de produtos cadastrados no banco de dados. 📦
- **Gerenciamento de Produtos**: Funções para cadastrar, consultar, atualizar e excluir produtos (via API, não diretamente expostas no frontend atual). ➕➖
- **Gerenciamento de Categorias**: Função para listar categorias de produtos (via API). 🏷️

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando as seguintes tecnologias:

- **Backend**:
  - [Python 3.x](https://www.python.org/) 🐍
  - [Flask](https://flask.palletsprojects.com/) (Framework web) 🌐
  - [mysql-connector-python](https://pypi.org/project/mysql-connector-python/) (Conexão com MySQL) 📊
  - [python-dotenv](https://pypi.org/project/python-dotenv/) (Gerenciamento de variáveis de ambiente) 🔑
- **Frontend**:
  - HTML5 (Estrutura da página) 📄
  - CSS3 (Estilização) 🎨
  - JavaScript (Interatividade, embora mínima no exemplo fornecido) ✨
- **Banco de Dados**:
  - MySQL (Armazenamento de dados de usuários, produtos e categorias) 🗄️

## 📂 Estrutura do Projeto

A estrutura de diretórios do projeto é organizada da seguinte forma:

```
Projeto-S.A.I-em-Python/
├── backend/
│   ├── __pycache__/
│   ├── api.py
│   └── main.py
├── templates/
│   ├── frontend/
│   │   ├── img/
│   │   │   └── favicon.png
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   ├── icon/
│   │   ├── android-chrome-192x192.png
│   │   ├── android-chrome-512x512.png
│   │   ├── apple-touch-icon.png
│   │   ├── favicon-16x16.png
│   │   ├── favicon-32x32.png
│   │   ├── favicon.ico
│   │   └── site.webmanifest
│   └── login.html
├── .env.example
├── LICENSE
└── README.md
```

- **`backend/`**: Contém a lógica de backend da aplicação.
  - `api.py`: Módulo responsável pela interação com o banco de dados (conexão, login, CRUD de produtos e categorias).
  - `main.py`: Aplicação Flask principal, definindo as rotas e a lógica de negócio para as páginas web.
- **`templates/`**: Armazena os arquivos HTML que são renderizados pelo Flask.
  - `login.html`: Página de login da aplicação.
  - `frontend/`: Contém os arquivos do frontend (HTML, CSS, JS) para a interface de usuário.
  - `icon/`: Contém os ícones e favicons da aplicação.
- **`.env.example`**: Um arquivo de exemplo para as variáveis de ambiente necessárias para a conexão com o banco de dados.
- **`LICENSE`**: O arquivo de licença do projeto.
- **`README.md`**: Este arquivo, com informações sobre o projeto.

## ⚙️ Configuração do Ambiente

Para configurar e executar este projeto, siga os passos abaixo:

### 1. Pré-requisitos

Certifique-se de ter instalado:

- [Python 3.x](https://www.python.org/downloads/) 🐍
- [MySQL Server](https://dev.mysql.com/downloads/mysql/) 🗄️

### 2. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd Projeto-S.A.I-em-Python
```

### 3. Criar Ambiente Virtual e Instalar Dependências

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate
pip install Flask mysql-connector-python python-dotenv
```

### 4. Configurar o Banco de Dados

1.Crie um banco de dados MySQL para o projeto (ex: `sai_db`).
2.  Crie as tabelas `users`, `products` e `categories`. Um exemplo de esquema pode ser:

    ```sql
    CREATE DATABASE IF NOT EXISTS sai_db;
    USE sai_db;

    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        category_id INT,
        image VARCHAR(255),
        stock INT NOT NULL DEFAULT 0,
        slug VARCHAR(255) UNIQUE,
        featured BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );

    -- Inserir um usuário de exemplo para teste
    INSERT INTO users (email, password) VALUES (
        'teste@example.com', 'senha123'
    );

    -- Inserir categorias de exemplo
    INSERT INTO categories (name) VALUES ('Eletrônicos'), ('Roupas'), ('Alimentos');

    -- Inserir produtos de exemplo
    INSERT INTO products (name, description, price, category_id, image, stock, slug, featured) VALUES
    ('Smartphone X', 'Um smartphone poderoso.', 1500.00, 1, 'smartphone.jpg', 50, 'smartphone-x', TRUE),
    ('Camiseta Básica', 'Camiseta de algodão confortável.', 50.00, 2, 'camiseta.jpg', 200, 'camiseta-basica', FALSE),
    ('Arroz Integral 1kg', 'Arroz integral orgânico.', 10.00, 3, 'arroz.jpg', 100, 'arroz-integral-1kg', FALSE);
    ```

### 5. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (no mesmo nível de `backend/` e `templates/`) com as seguintes informações, substituindo os valores pelos seus dados de conexão com o MySQL:

```dotenv
DB_HOST=localhost
DB_USER=seu_usuario_mysql
DB_PASSWORD=sua_senha_mysql
DB_NAME=sai_db
```

## ▶️ Como Executar a Aplicação

Com o ambiente configurado e o banco de dados pronto, você pode iniciar a aplicação Flask:

```bash
# Certifique-se de que o ambiente virtual está ativado
python backend/main.py
```

A aplicação estará disponível em `http://127.0.0.1:5000/` ou `http://localhost:5000/`.

## 🌐 Rotas da Aplicação

- **`/` ou `/login` (GET/POST)**:
  - **GET**: Exibe a página de login.
  - **POST**: Processa as credenciais de login. Se o login for bem-sucedido, redireciona para `/produtos`; caso contrário, exibe uma mensagem de erro na página de login.
- **`/produtos` (GET)**:
  - Exibe a lista de produtos cadastrados. Se nenhum produto for encontrado, mostra uma mensagem e um link para cadastrar o primeiro produto.

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE). 📝

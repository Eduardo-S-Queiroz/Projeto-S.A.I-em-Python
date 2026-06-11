# Projeto S.A.I. em Python 🐍

Sistema de Automação Inteligente (S.A.I.) — uma aplicação web em Flask para gerenciar produtos, estoque, categorias, fornecedores, pedidos e relatórios.

## 🌟 Funcionalidades

- Login de usuário.
- Listagem e busca de produtos.
- Controle de estoque com categorias e fornecedores.
- Histórico de movimentações de estoque.
- Listagem de pedidos.
- Dashboard analítico com gráficos Plotly.
- Relatórios operacionais e mensais.
- Exportação de relatórios em CSV.

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Flask
- MySQL
- mysql-connector-python
- python-dotenv
- pandas
- plotly
- HTML, CSS e JavaScript

## 📂 Estrutura do Projeto

```
Projeto-S.A.I-em-Python/
├── backend/
│   ├── acts.py
│   ├── dashboard.py
│   ├── main.py
│   └── relatorios.py
├── scripts/
│   └── simulate_orders.py
├── static/
│   ├── acessibilidade.js
│   ├── script.js
│   ├── style.css
│   └── uploads/
├── templates/
│   ├── categorias.html
│   ├── dashboard.html
│   ├── estoque.html
│   ├── fornecedores.html
│   ├── index.html
│   ├── login.html
│   ├── movimentacoes.html
│   ├── pedidos.html
│   ├── relatorio_mensal.html
│   ├── relatorio_operacional.html
│   └── ...
├── requirements.txt
├── README.md
└── LICENSE
```

## ⚙️ Configuração do Ambiente

### 1. Pré-requisitos

- Python 3.x
- MySQL Server

### 2. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd Projeto-S.A.I-em-Python
```

### 3. Criar Ambiente Virtual e Instalar Dependências

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
pip install Flask python-dotenv pandas plotly
```

### 4. Configurar o Banco de Dados

Crie um banco de dados MySQL, por exemplo `sai_db`, e configure as tabelas necessárias.

Tabelas usadas pelo projeto:

- `users`
- `products`
- `inventory`
- `categories`
- `suppliers`
- `stock_movements`
- `orders`
- `cart_items`

### 5. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com:

```dotenv
DB_HOST=localhost
DB_USER=seu_usuario_mysql
DB_PASSWORD=sua_senha_mysql
DB_NAME=sai_db
```

## ▶️ Executar a Aplicação

```bash
python backend/main.py
```

Abra `http://127.0.0.1:5000/` no navegador.

## 🌐 Rotas Principais

- `/` — página de login.
- `/index.html` — lista de produtos.
- `/estoque.html` — controle de estoque.
- `/categorias.html` — gestão de categorias.
- `/fornecedores.html` — gestão de fornecedores.
- `/movimentacoes.html` — histórico de movimentações.
- `/pedidos.html` — lista de pedidos.
- `/dashboard.html` — dashboard com gráficos.
- `/relatorio_operacional.html` — relatório operacional.
- `/relatorio_mensal.html` — relatório mensal.
- `/exportar_operacional` — exporta relatório operacional para CSV.
- `/exportar_mensal` — exporta relatório mensal para CSV.

## 🧠 Arquivos Principais

- `backend/main.py`: aplicação Flask e rotas.
- `backend/acts.py`: conexão com banco e lógica CRUD.
- `backend/relatorios.py`: geração de relatórios, gráficos e exportação CSV.
- `backend/dashboard.py`: utilitário de dados com Pandas.
- `scripts/simulate_orders.py`: gera pedidos de exemplo.
- `templates/`: páginas HTML.
- `static/`: estilos, scripts e uploads.

## 💡 Observações

- A autenticação atual compara senha em texto simples; para produção, implemente hashing seguro.
- O dashboard usa Plotly para gráficos interativos.
- O `requirements.txt` lista `mysql-connector-python`, mas o projeto também depende de `Flask`, `python-dotenv`, `pandas` e `plotly`.
- As buscas no frontend funcionam via parâmetro `q` e são processadas pelo backend.

## 🧪 Gerar Dados de Teste

```bash
python scripts/simulate_orders.py
```

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

# Documentação do Projeto S.A.I em Python

Este documento descreve os principais componentes e o funcionamento do projeto S.A.I. em Python, incluindo backend, templates, relatórios e scripts auxiliares.

## 1. Visão geral

O projeto é uma aplicação web desenvolvida com Flask para gerenciar produtos, estoque, categorias, fornecedores, pedidos e relatórios operacionais/mensais. A aplicação usa MySQL como banco de dados e utiliza templates HTML para a interface.

## 2. Estrutura do projeto

- `backend/`
  - `main.py`: aplicação Flask principal, define rotas e integra com as funções de backend.
  - `acts.py`: funções de acesso ao banco de dados e lógica CRUD para produtos, estoque, categorias, fornecedores, movimentações e pedidos.
  - `relatorios.py`: funções de geração de relatórios, filtros, totais e gráficos Plotly.
  - `dashboard.py`: script auxiliar que lê dados do banco com Pandas para análises e importação.
- `templates/`: HTML renderizado pelo Flask.
- `static/`: arquivos estáticos como CSS, JavaScript e ícones.
- `scripts/`: scripts auxiliares, como `simulate_orders.py` para gerar dados de vendas de exemplo.
- `requirements.txt`: dependências do Python.

## 3. Backend

### 3.1 `backend/main.py`

Este arquivo inicializa o aplicativo Flask e define as rotas principais da aplicação.

- `app = Flask(...)`: configura os diretórios de templates e static.
- `salvar_upload_imagem()`: recebe upload de imagem e salva em `static/uploads/`.

Rotas principais:

- `/` (GET/POST): página de login.
  - POST valida email/senha com `verificar_login()` e redireciona para `/index.html` se bem-sucedido.
- `/index.html`: lista de produtos.
  - Passa `q` para `listar_produtos(q)` quando a pesquisa é usada.
- `/produtos` (POST): adiciona, edita ou exclui produto.
- `/estoque.html`: lista de itens de estoque.
  - Usa `listar_estoque(q)` para pesquisa.
- `/estoque/salvar` (POST): cria ou atualiza registro de estoque.
- `/estoque/excluir` (POST): remove item de estoque.
- `/categorias.html` (GET/POST): CRUD de categorias.
  - Pesquisa via `listar_categorias(q)`.
- `/fornecedores.html` (GET/POST): CRUD de fornecedores.
  - Pesquisa via `listar_fornecedores(q)`.
- `/movimentacoes.html`: histórico de movimentações de estoque.
  - Pesquisa via `listar_movimentacoes(q)`.
- `/pedidos.html`: lista de pedidos.
  - Pesquisa via `lista_pedidos(q)`.
- `/pedido/<int:id>/detalhes`: retorna JSON com os detalhes do pedido.
- `/dashboard.html`: mostra gráficos analíticos.
  - Usa `get_dashboard_analytics(ano, meses, filtros)`.
- `/relatorio_operacional.html`: mostra relatório operacional com filtros e paginação.
- `/relatorio_mensal.html`: mostra relatório mensal agregado.
- `/exportar_operacional`: exporta relatório operacional em CSV.
- `/exportar_mensal`: exporta relatório mensal em CSV.

### 3.2 `backend/acts.py`

Funções de acesso ao banco de dados e lógica de negócio.

#### Conexão e utilitários

- `conectar_bd()`: conecta ao MySQL usando variáveis de ambiente (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).
- `executar_escrita(query, params)`: executa comandos de escrita para INSERT/UPDATE/DELETE.

#### Usuários

- `verificar_login(email, password)`: verifica senha diretamente no banco de dados.

#### Produtos

- `listar_produtos(q=None)`: retorna produtos ordenados por nome.
  - Se `q` estiver presente, filtra por nome ou descrição.
- `cadastrar_produto(...)`: cria produto com código UUID e slug.
- `atualizar_produto(...)`: atualiza dados do produto.

#### Estoque

- `listar_estoque(q=None)`: retorna inventário com produto, categoria e fornecedor.
  - Suporta pesquisa por produto, categoria, fornecedor e quantidade.
- `salvar_estoque(...)`: cria ou atualiza registro de estoque.
  - Também registra movimentação de estoque em `stock_movements`.
- `excluir_estoque(id)`: remove registro do inventário.

#### Movimentações

- `listar_movimentacoes(q=None)`: retorna histórico de movimentação com produto, categoria e fornecedor.
  - Suporta pesquisa por produto, categoria, fornecedor, tipo, motivo e quantidade.

#### Categorias

- `listar_categorias(q=None)`: retorna categorias.
  - Filtra por nome quando `q` é usado.
- `cadastrar_categoria(name)`, `atualizar_categoria(id, name)`, `excluir_categoria(id)`.
  - Ao excluir categoria, atualiza registros de estoque para remover a referência.

#### Fornecedores

- `listar_fornecedores(q=None)`: retorna fornecedores.
  - Filtra por nome quando `q` é usado.
- `cadastrar_fornecedor(name)`, `atualizar_fornecedor(id, name)`, `excluir_fornecedor(id)`.
  - Ao excluir fornecedor, remove referência do estoque.

#### Pedidos

- `lista_pedidos(q=None)`: retorna pedidos com o cliente e email.
  - Filtra por nome do cliente, email, status e, se `q` for numérico, também por ID.

#### Helpers adicionais

- `listar_anos_pedidos()`: busca anos distintos de pedidos para filtros no dashboard/relatórios.

### 3.3 `backend/relatorios.py`

Funções de relatório, filtros SQL, totais e exportação.

#### Funções auxiliares

- `_fetchall(query, params)`: executa consulta e retorna lista de dicionários.
- `_montar_where(filtros=None, ano=None, meses=None)`: cria cláusula WHERE dinâmica para filtros.
  - Suporta filtros de data, produto, fornecedor, categoria e busca genérica.
- `_base_query(where_sql='')`: query base que junta `orders`, `users`, `cart_items`, `products`, `inventory`, `categories` e `suppliers`.
- `_totalizadores(rows)`: calcula totais operacionais, impostos, pedidos, itens e ticket médio.

#### Relatórios

- `get_relatorio_operacional(filtros=None, pagina=1, por_pagina=10)`: retorna dados de relatório com paginação.
- `get_relatorio_mensal(ano=None, meses=None)`: agrega dados por mês, calcula impostos e margem.
- `get_dashboard_analytics(ano=None, meses=None, filtros=None)`: gera totais e dados para gráficos.

#### Gráficos

- Gera JSON Plotly para:
  - faturamento mensal
  - top fornecedores
  - distribuição por categoria
  - produtos mais vendidos

#### Como os gráficos Plotly funcionam

- O módulo importa `plotly.graph_objects as go` para construir os objetos de gráfico.
- Cada gráfico é criado como uma instância de `go.Figure` contendo um ou mais traços (`go.Scatter`, `go.Bar`, `go.Pie`).
- `go.Scatter` é usado para o gráfico de faturamento mensal com linhas e marcadores (`mode='lines+markers'`), e `fill='tozeroy'` preenche a área sob a curva.
- `go.Bar` é usado para os gráficos de fornecedores e de produtos mais vendidos, com `orientation='h'` no gráfico de fornecedores para barras horizontais.
- `go.Pie` é usado para o gráfico de categorias, com `hole=.48` para gerar um gráfico de rosca.
- Em todas as figuras, o layout visual é padronizado por `_plotly_json(fig)`, que aplica:
  - fundo transparente (`paper_bgcolor='rgba(0,0,0,0)'`, `plot_bgcolor='rgba(0,0,0,0)'`)
  - tipografia e cores consistentes
  - margens customizadas e legenda horizontal.
- O método `_plotly_json(fig)` serializa a figura para JSON usando `json.dumps(..., cls=PlotlyJSONEncoder)`.
- O JSON resultante é enviado para o template e renderizado no frontend como gráfico interativo Plotly.
- Isso permite que o Flask gere o gráfico no backend e a interface exiba o gráfico sem precisar montar os dados diretamente em JavaScript.

#### Como os gráficos aparecem no frontend

- O template `templates/dashboard.html` inclui a biblioteca Plotly via CDN:
  - `<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>`
- Cada gráfico recebe um `div` com um `id` específico:
  - `graficoMensal`
  - `graficoFornecedores`
  - `graficoCategorias`
  - `graficoProdutos`
- O backend envia o JSON de cada gráfico como variáveis Jinja2:
  - `const gMensal = {{ dados.graficos.mensal | safe }};`
  - `const gFornecedores = {{ dados.graficos.fornecedores | safe }};`
  - `const gCategorias = {{ dados.graficos.categorias | safe }};`
  - `const gProdutos = {{ dados.graficos.produtos | safe }};`
- O template usa JavaScript para ajustar o layout dos gráficos antes de renderizar.
- `Plotly.newPlot('graficoMensal', gMensal.data, gMensal.layout, cfg)` monta o gráfico no `div` correspondente.
- Os gráficos aparecem dentro de cards responsivos, com títulos e espaçamento definidos pelo CSS.
- O template também define configurações de exibição:
  - `responsive: true`
  - `displaylogo: false`
  - `modeBarButtonsToRemove: ['lasso2d', 'select2d']`
- O resultado é um dashboard interativo onde o usuário pode passar o mouse sobre pontos, ampliar e arrastar os dados.

#### Gráficos do dashboard

- O dashboard é composto por quatro cards de visualização:
  - `Evolução Mensal de Vendas` (`graficoMensal`)
  - `Top Fornecedores` (`graficoFornecedores`)
  - `Vendas por Categoria` (`graficoCategorias`)
  - `Produtos Mais Vendidos` (`graficoProdutos`)
- Cada card usa a classe CSS `chart-card`, que aplica fundo, borda arredondada, padding e box-shadow.
- A grid `analytics-grid-projeto2` posiciona os quatro cards em duas colunas ou em layout responsivo.
- O título de cada card aparece acima do `div` do gráfico.
- `gMensal`, `gFornecedores`, `gCategorias` e `gProdutos` contêm objetos Plotly prontos para renderização:
  - `data`: lista de traços (`traces`) com valores, rótulos e cores.
  - `layout`: objeto de layout com margens, fontes e cores de fundo.
- A função `aplicarAjustesLayout(grafico)` garante que todos tenham altura (`360px`), largura (`700px`) e margens internas suficientes.
- O backend fornece valores numéricos agregados, e o frontend apenas consome esse JSON para desenhar os gráficos.
- O usuário vê o dashboard com interatividade imediata, porque Plotly adiciona tooltips e modo de zoom automaticamente.

- Em `templates/relatorio_mensal.html`, o gráfico é gerado diretamente no frontend a partir de arrays Jinja2 convertidas em JSON, usando `Plotly.newPlot('graficoComparativo', dataPlot, layoutPlot, configPlot)`.
- Esse gráfico mensal é montado a partir de dados de `meses`, `bruto`, `liquido` e `impostos` enviados pelo backend.

#### Exportação CSV

- `exportar_operacional_csv(filtros=None)`: exporta relatório operacional.
- `exportar_mensal_csv(ano=None, meses=None)`: exporta relatório mensal.

### 3.4 `backend/dashboard.py`

Script auxiliar de análise de dados usando Pandas.

- `get_data_from_db()`: conecta ao banco e carrega `orders` e `products`.
- Converte valores para `float` e retorna DataFrames.
- Este script é utilitário e pode ser usado fora do Flask para análises adicionais.

## 4. Templates

A aplicação utiliza templates Jinja2 para renderizar as páginas.

### 4.1 `templates/login.html`

Página de login com formulário de email e senha. Mostra mensagem de erro quando a autenticação falha.

### 4.2 `templates/index.html`

Página de produtos:
- busca por nomes e descrições
- lista produtos com imagem, nome, descrição, preço e destaque
- modal para adicionar/editar produtos
- exclusão de produto

### 4.3 `templates/estoque.html`

Página de estoque:
- mostra produto, categoria, fornecedor, quantidade, mínimo e status
- busca na lista de estoque
- modal para adicionar ou editar estoque

### 4.4 `templates/categorias.html`

Página de categorias:
- lista de categorias
- busca por nome
- modal para adicionar/editar categoria
- confirmação de exclusão

### 4.5 `templates/fornecedores.html`

Página de fornecedores:
- lista de fornecedores
- busca por nome
- modal para adicionar/editar fornecedor
- confirmação de exclusão

### 4.6 `templates/movimentacoes.html`

Página de movimentações:
- histórico de entradas e saídas do estoque
- busca por produto, categoria, fornecedor, tipo e motivo

### 4.7 `templates/pedidos.html`

Página de pedidos:
- lista de pedidos com ID, cliente, data, total e status
- botão para abrir modal com detalhes do pedido usando API JSON

### 4.8 `templates/dashboard.html`

Página analítica:
- filtros para ano e meses
- mostra KPIs e gráficos Plotly
- busca genérica aplicada ao dashboard

### 4.9 `templates/relatorio_operacional.html`

Relatório operacional:
- filtros por data, produto, categoria e fornecedor
- busca geral
- tabela paginada
- exportação em CSV

### 4.10 `templates/relatorio_mensal.html`

Relatório mensal:
- filtros por ano e meses
- gráfico de comparativo mensal com Plotly
- tabela com totais agregados, impostos e margem
- busca e ordenação na tabela

## 5. Arquivos estáticos

O diretório `static/` contém:
- `style.css`: estilos visuais da aplicação
- `acessibilidade.js`: possíveis melhorias de acessibilidade
- `uploads/`: imagens enviadas pelo usuário
- `icon/`: ícones e favicons

## 6. Script auxiliar

### `scripts/simulate_orders.py`

Este script gera vendas fictícias no banco de dados:
- cria usuários fictícios na tabela `users`
- lê produtos da tabela `products`
- simula vendas nos últimos 365 dias
- atualiza estoque e registra movimentações
- insere pedidos em `orders` e itens em `cart_items`

## 7. Dependências

O arquivo `requirements.txt` contém as bibliotecas necessárias:
- `mysql-connector-python>=8.0.33`

> Observação: o projeto também usa outras bibliotecas que não estão listadas em `requirements.txt`, como `Flask`, `python-dotenv`, `pandas` e `plotly`.

### 7.1 Bibliotecas de terceiros usadas no projeto
- `Flask`: microframework web para criar rotas, renderizar templates, processar formulários e construir a aplicação principal.
- `werkzeug`: biblioteca de utilitários do Flask; o projeto usa `secure_filename` para salvar uploads de arquivos com nomes seguros.
- `python-dotenv`: carrega variáveis de ambiente a partir de um arquivo `.env`, facilitando a configuração de acesso ao banco de dados.
- `mysql-connector-python`: driver oficial MySQL para Python; usado para conectar no banco, executar consultas SQL e manipular resultados.
- `pandas`: biblioteca de análise de dados usada em `backend/dashboard.py` para carregar tabelas SQL em DataFrames e converter valores numéricos.
- `plotly`: biblioteca de visualização que gera gráficos interativos no backend; o projeto usa `plotly.graph_objects` e `PlotlyJSONEncoder` para converter gráficos em JSON.

### 7.2 Módulos da biblioteca padrão do Python usados no projeto
- `os`: manipulação de caminhos, arquivos e diretórios.
- `sys`: ajuste de caminho de importação para carregar módulos locais.
- `uuid`: geração de identificadores únicos para códigos e slugs de produto.
- `csv`: escrita de arquivos CSV na exportação de relatórios.
- `io`: criação de buffers de texto em memória para gerar CSVs antes de enviar ao usuário.
- `json`: serialização de dados para JSON em APIs e no conteúdo armazenado.
- `datetime` e `timedelta`: manipulação de datas e períodos para relatórios e simulação de pedidos.
- `math.ceil`: cálculo do número de páginas no relatório operacional.
- `random`: geração de valores aleatórios na simulação de vendas.

## 8. Como executar

1. Configure o banco de dados MySQL e as variáveis de ambiente em `.env`:

```dotenv
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=seu_banco
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Execute a aplicação:

```bash
python backend/main.py
```

4. Acesse em `http://localhost:5000/`.

## 9. Observações importantes

- A autenticação atual compara a senha em texto simples. Para produção, recomenda-se usar hash seguro.
- A pesquisa nas páginas funciona via parâmetro `q` e é processada pelo backend.
- As rotas de relatório suportam exportação CSV e filtros dinâmicos.

## 10. Explicação detalhada por arquivo

### `backend/main.py`
- Inicializa o Flask com `template_folder` e `static_folder`, permitindo que o app use `templates/` e `static/`.
- Define a função `salvar_upload_imagem(campo='image_file')` que recebe um arquivo do formulário, valida o nome e salva em `static/uploads/`.
- A página de login (`/`) aceita GET para mostrar o formulário e POST para processar as credenciais.
  - No POST, `request.form['email']` e `request.form['password']` são lidos.
  - Se `verificar_login(email, password)` for verdadeiro, redireciona para `/index.html`.
  - Caso contrário, renderiza `login.html` com a variável `error` para exibir a mensagem na interface.
- A rota `/index.html` carrega produtos e dados auxiliares para exibir no dashboard de produtos.
  - Usa `request.args.get('q', '').strip() or None` para capturar o termo de busca.
  - Passa `produtos=listar_produtos(q=q)` para renderizar apenas os produtos filtrados.
- A rota `/produtos` trata operações de formulário do tipo adicionar, editar e excluir.
  - Usa `request.form.get('action')` para decidir a operação.
  - Para `add`, chama `cadastrar_produto()`.
  - Para `edit`, chama `atualizar_produto()`.
  - Para `delete`, chama `excluir_produto()`.
  - Ao final, redireciona para a lista de produtos.
- `/estoque.html` exibe o inventário e aceita busca via `q`.
  - Obtém `produtos`, `categorias` e `fornecedores` para popular os selects do formulário de estoque.
  - Reutiliza `listar_estoque(q=q)` para pesquisar nome de produto, categoria, fornecedor ou quantidade.
- `/estoque/salvar` processa o formulário de estoque.
  - Recebe `product_id`, `category_id`, `supplier_id` e `quantity`.
  - Sempre redireciona para `/estoque.html` após salvar.
- `/estoque/excluir` recebe `stock_id` e remove o registro correspondente.
- `/categorias.html` aceita GET e POST.
  - GET: mostra a lista de categorias filtrada por `q` quando presente.
  - POST: decide entre add/edit/delete com base em `action` e redireciona.
- `/fornecedores.html` funciona igual a `/categorias.html`, mas para fornecedores.
- `/movimentacoes.html` renderiza `movimentacoes.html` com `movs=listar_movimentacoes(q=q)`.
- `/pedidos.html` renderiza `pedidos.html` com `pedidos=lista_pedidos(q=q)`.
- `/pedido/<int:id>/detalhes` retorna JSON com detalhes estáticos de pedido.
  - Este endpoint é usado pelo JavaScript no template de pedidos para exibir um modal.
- `/dashboard.html` renderiza o dashboard analítico.
  - Captura `ano`, `mes` e `q`.
  - Passa filtros para `get_dashboard_analytics()`.
  - Retorna o JSON Plotly pré-formatado no template.
- `/relatorio_operacional.html` prepara filtros de busca e paginação.
  - Usa `get_relatorio_operacional(filtros=filtros, pagina=pagina, por_pagina=10)`.
  - Renderiza a tabela paginada e mantém os parâmetros de filtro entre páginas.
- `/relatorio_mensal.html` carrega os dados agrupados por mês.
  - Mostra apenas os meses selecionados e o ano escolhido.
- `/exportar_operacional` e `/exportar_mensal` usam funções de exportação CSV e retornam `Response` com `Content-Disposition` para download.
- `if __name__ == "__main__": app.run(debug=True, port=5000)` inicializa o servidor em modo debug na porta 5000.

## 11. Comandos Python e SQL usados no backend

### Comandos Python comuns
- `import ...`: importa módulos internos e externos.
- `from ... import ...`: importa funções ou classes específicas.
- `os.path.join()`, `os.path.exists()`, `os.makedirs()`: manipulam caminhos e criam diretórios.
- `sys.path.insert(0, BASE_DIR)`: adiciona o diretório local às importações Python.
- `Flask(__name__, template_folder=..., static_folder=...)`: cria a aplicação Flask com pastas customizadas.
- `@app.route('/rota', methods=['GET', 'POST'])`: registra uma função como manipulador de rota HTTP.
- `request.args.get('q', '').strip() or None`: lê parâmetro GET `q`, remove espaços e converte string vazia em `None`.
- `request.form.get('campo')` / `request.form['campo']`: lê valores de formulário enviados por POST.
- `request.files['campo']`: obtém arquivos enviados do formulário.
- `secure_filename(file.filename)`: sanitiza o nome do arquivo antes de gravar.
- `file.save(path)`: salva upload no disco.
- `redirect(url_for('endpoint'))`: redireciona para outra rota do Flask.
- `render_template('arquivo.html', chave=valor)`: renderiza um template Jinja2 com dados.
- `jsonify({...})`: cria resposta JSON para APIs internas.
- `Response(conteudo, mimetype='text/csv', headers=...)`: retorna um arquivo para download.
- `if __name__ == '__main__':`: executa código apenas quando o módulo é rodado diretamente.
- `try/except`: trata exceções e evita queda da aplicação.
- `finally`: garante fechamento de conexões ou liberação de recursos.
- `len(set(...))`, `sum(...)`, `sorted(..., key=lambda ...)`: operações de agregação e ordenação em coleções Python.
- `datetime.now().year`, `timedelta(days=365)`: obtém datas e intervalos de tempo.
- `json.dumps(obj, ensure_ascii=False)`: converte Python em JSON mantendo acentuação.
- `uuid.uuid4()`: gera identificador único para campos como `code` e `slug`.

### Comandos MySQL/SQL usados
- `mysql.connector.connect(**db_config)`: conecta ao banco MySQL.
- `cursor = conn.cursor(dictionary=True)`: cria um cursor que retorna resultados como dicionários.
- `cursor.execute(query, params)`: executa comando SQL parametrizado.
- `conn.commit()`: confirma alterações em INSERT/UPDATE/DELETE.
- `cursor.fetchall()`: obtém todas as linhas retornadas pela consulta.
- `cursor.fetchone()`: obtém apenas a primeira linha.
- `cursor.close()`, `conn.close()`: fecha cursor e conexão.
- `INSERT INTO tabela (...) VALUES (%s, %s, ...)`: insere novos registros.
- `UPDATE tabela SET campo=%s WHERE id=%s`: atualiza registros existentes.
- `DELETE FROM tabela WHERE id=%s`: remove registros.
- `SELECT * FROM tabela WHERE coluna LIKE %s`: pesquisa texto com curinga.
- `CAST(valor AS CHAR)`: converte valores numéricos em texto para permitir busca em string.
- `COALESCE(valor1, valor2, ...)`: retorna o primeiro valor não nulo.
- `JOIN`, `LEFT JOIN`: junta várias tabelas em uma consulta.
- `YEAR(created_at) = %s`, `MONTH(created_at) IN (...)`: filtra por ano e mês.
- `ON DUPLICATE KEY UPDATE`: insere ou atualiza quando chave duplicada existe.
- `ORDER BY coluna`: ordena resultados.
- `GROUP BY`: agrupa resultados para relatórios mensais.

### Comandos específicos de cada arquivo
- `backend/main.py`: usa Flask e `werkzeug.utils.secure_filename` para upload de imagens, `url_for` para rotas dinâmicas, e `Response` para exportação de CSV.
- `backend/acts.py`: usa `load_dotenv()` para carregar `.env`, cria conexão MySQL, executa queries parametrizadas e grava logs de erro com `print()`.
- `backend/relatorios.py`: usa `csv.writer()` e `io.StringIO()` para gerar CSV em memória; cria gráficos Plotly com `go.Figure(...)`, `go.Scatter(...)`, `go.Bar(...)` e `go.Pie(...)`; serializa gráficos com `PlotlyJSONEncoder`.
- `backend/dashboard.py`: carrega dados SQL diretamente em DataFrames com `pd.read_sql()` e converte colunas para número com `astype(float)`.
- `scripts/simulate_orders.py`: utiliza `random.randint`, `random.choice` e `random.sample` para gerar dados aleatórios; usa `cursor.lastrowid` para capturar o ID do pedido recém-inserido; insere JSON de itens com `json.dumps()`.

### Exemplo de fluxo de comando
1. Usuário envia formulário de busca em `/index.html`.
2. `main.py` lê `q` com `request.args.get(...)`.
3. Chama `acts.listar_produtos(q=q)`.
4. `acts.py` executa `SELECT * FROM products WHERE name LIKE %s OR description LIKE %s`.
5. O resultado retorna para `main.py`, que renderiza `index.html` com os produtos filtrados.

### Observação
O código atualmente usa comparações de senha em texto simples e não faz hashing, então a parte de autenticação deve ser melhorada para uso em produção.

### `backend/acts.py`
- `conectar_bd()` monta `db_config` a partir de variáveis de ambiente e tenta abrir conexão com MySQL.
  - Se falhar, imprime o erro e retorna `None`.
- `executar_escrita(query, params)` é um helper para operações que alteram dados.
  - Cria conexão, executa query, faz commit e fecha a conexão.
  - Em caso de erro, faz rollback e fecha a conexão.

#### `verificar_login(email, password)`
- Busca a senha armazenada em `users` por email.
- Compara a senha retornada com o valor enviado pelo formulário.
- Retorna `True` apenas quando as credenciais batem.
- Atenção: o esquema atual não usa hash de senha — isso é apenas para testes.

#### Produtos
- `listar_produtos(q=None)` usa `cursor(dictionary=True)` para retornar dicionários.
  - Se `q` for vazio, faz `SELECT * FROM products ORDER BY name`.
  - Caso contrário, busca por `name LIKE %q% OR description LIKE %q%`.
- `cadastrar_produto(name, description, price, image_url=None, image_path=None, featured=0)`
  - Gera um `code` UUID e um `slug` a partir do nome.
  - Insere o produto com todos os dados no banco.
- `atualizar_produto(id, ...)` atualiza os campos do produto.
  - Se `image_path` estiver presente, atualiza também o caminho da imagem.
  - Se não houver imagem nova, mantém a imagem atual.

#### Estoque
- `listar_estoque(q=None)` retorna dados de `inventory` com joins em `products`, `categories` e `suppliers`.
  - Usa `WHERE` dinâmico para buscar em `p.name`, `c.name`, `s.name` ou `CAST(i.quantity AS CHAR)`.
- `salvar_estoque(product_id, category_id, supplier_id, quantity)` faz:
  - se o produto já existe no inventário, atualiza categoria, fornecedor e quantidade.
  - se a quantidade mudou, registra uma movimentação de estoque de `entry` ou `exit`.
  - se o produto não existe no inventário, cria novo registro e, se `quantity > 0`, registra entrada inicial.
- `excluir_estoque(id)` remove o registro de inventário.

#### Movimentações
- `listar_movimentacoes(q=None)` retorna `stock_movements` com os nomes relacionados.
  - Quando há `q`, filtra em produto, categoria, fornecedor, tipo, motivo e quantidade.
  - Ordena por `created_at DESC`.

#### Categorias e fornecedores
- `listar_categorias(q=None)` e `listar_fornecedores(q=None)` usam query simples com `LIKE` para filtros.
- `cadastrar_*()`, `atualizar_*()`, `excluir_*()` realizam as operações correspondentes.
- Ao excluir categoria ou fornecedor, o código também remove a referência dessas entidades de `inventory`.

#### Pedidos
- `lista_pedidos(q=None)` retorna pedidos com cliente e email via join em `users`.
  - Se `q` for numérico, adiciona `o.id = %s` à condição.
  - Também permite busca por `u.name`, `u.email` e `o.status`.

#### Outros helpers
- `listar_anos_pedidos()` consulta `orders` e retorna anos distintos para permitir seleção no dashboard e relatórios.
- `excluir_produto(id)` remove entradas de estoque e o produto da tabela `products`.

### `backend/relatorios.py`
- Importa `plotly.graph_objects` e `PlotlyJSONEncoder` para converter gráficos em JSON.
- `MES_NOMES` e `CORES` definem os nomes dos meses e o estilo dos gráficos.

#### `_plotly_json(fig)`
- Ajusta layout do gráfico para fundo transparente, fonte e margens.
- Retorna JSON serializável via `json.dumps(..., cls=PlotlyJSONEncoder)`.

#### `_fetchall(query, params=None)`
- Executa uma query SQL e retorna resultado como lista de dicionários.
- Fecha conexão mesmo em caso de erro.

#### `_montar_where(filtros=None, ano=None, meses=None)`
- Recebe filtros e monta lista de condições `where`.
- Adiciona condições de datas (`data_inicio`, `data_fim`), produto, fornecedor, categoria.
- Quando há `busca`, adiciona cláusulas OR para buscar em usuário, email, produto, categoria, fornecedor e status do pedido.
- Quando há anos e meses, adiciona `YEAR(o.created_at) = %s` e `MONTH(o.created_at) IN (...)`.

#### `_base_query(where_sql='')`
- Monta a query principal para relatórios operacionais.
- Une `orders`, `users`, `cart_items`, `products`, `inventory`, `categories` e `suppliers`.
- Calcula valores brutos, impostos e líquido diretamente na query.

#### `_totalizadores(rows)`
- Soma `valor_bruto`, `valor_liquido` e impostos.
- Conta pedidos distintos, itens totais e calcula ticket médio.

#### `get_relatorio_operacional(filtros=None, pagina=1, por_pagina=10)`
- Consulta os dados completos do relatório.
- Faz paginação em memória após buscar todas as linhas filtradas.
- Retorna o subconjunto de linhas da página atual e totais agregados.

#### `get_relatorio_mensal(ano=None, meses=None)`
- Busca dados e agrupa por mês.
- Calcula quantidade de pedidos distintos, itens, bruto, ICMS, PIS, COFINS, líquido e margem.
- Retorna o ano usado e totais gerais.

#### `get_dashboard_analytics(ano=None, meses=None, filtros=None)`
- Usa os mesmos filtros do relatório e gera dados consolidados.
- Cria metricas por mês, fornecedores, categorias, produtos e status de pedidos.
- Gera 4 gráficos Plotly:
  - linha de faturamento mensal
  - barras horizontais de top fornecedores
  - pizza de categorias
  - barras de produtos mais vendidos

#### Exportação CSV
- `exportar_operacional_csv(filtros=None)` cria CSV com ponto e vírgula, exporta dados detalhados.
- `exportar_mensal_csv(ano=None, meses=None)` exporta dados agregados por mês.

### `backend/dashboard.py`
- Importa `pandas` e `mysql.connector.Error`.
- `get_data_from_db()` conecta e verifica `connection.is_connected()`.
- Lê `orders` e `products` com `pd.read_sql()`.
- Converte `total_price` e `price` para float.
- Fecha conexão no bloco `finally`.
- Retorna DataFrames vazios em caso de erro para evitar que o processo quebre.

### `scripts/simulate_orders.py`
- Define `db_config` local para conexão com o MySQL.
- `conectar_bd()` cria a conexão e encerra a execução em caso de falha.
- `simular_vendas_ano()` percorre os últimos 365 dias e cria entre 0 e 5 pedidos por dia.
- Insere usuários fictícios na tabela `users` com `INSERT IGNORE`.
- Para cada pedido:
  - seleciona usuário e produtos aleatórios
  - gera hora aleatória e itens do carrinho
  - verifica estoque e reabastece se necessário
  - registra movimentações de entrada e saída no estoque
  - insere pedido em `orders` com campo `items` JSON
  - insere itens em `cart_items`
- Usa `buffered=True` no cursor para evitar problemas de resultados não lidos.
- Fecha conexão ao final e imprime resumo de pedidos gerados.

### Templates principais
- `templates/login.html`: usa Bootstrap para layout simples de login.
  - Usa `request.form` para exibir erros via variável `error`.
- `templates/index.html`: lista produtos e usa modais Javascript para CRUD de produtos.
  - O formulário de busca envia GET para a mesma página.
  - Os botões de edição preenchem o modal com atributos `data-*`.
- `templates/estoque.html`: exibe inventário com botões de edição e exclusão.
  - Ao salvar estoque, faz POST para `/estoque/salvar`.
  - Os campos de categoria/fornecedor são preenchidos dinamicamente.
- `templates/categorias.html` e `templates/fornecedores.html`: cada uma possui modais para criar, editar e excluir.
  - JavaScript controla abertura/fechamento de modais e preenchimento de campos.
- `templates/movimentacoes.html`: mostra histórico de entradas e saídas com filtros de busca.
- `templates/pedidos.html`: exibe pedidos e carrega detalhes via `fetch()` em `/pedido/<id>/detalhes`.
  - Mostra modal com detalhes do pedido e itens.
- `templates/dashboard.html`: renderiza gráficos Plotly já gerados no backend.
  - Filtros de ano e mês recarregam a página com parâmetros GET.
- `templates/relatorio_operacional.html`: contém busca geral com `q`, filtros específicos e paginação.
  - O botão de exportar CSV preserva todos os filtros atuais.
- `templates/relatorio_mensal.html`: gera gráfico comparativo com Plotly e uma tabela filtrável/ordenável.

### `static/`
- `style.css` define aparência geral dos cards, tabelas, botões e grids.
- `acessibilidade.js` foi incluído no final dos templates para melhorias de interação.
- `uploads/` guarda imagens carregadas pelos usuários.
- `icon/` contém favicons e manifestos para o app.

## 11. Fluxo completo de uso

1. Usuário abre `/` e faz login.
2. Após o login, acessa `/index.html` para ver produtos.
3. Pode pesquisar produtos por nome/descrição ou criar/editar/excluir produtos.
4. Acessa `/estoque.html` para gerenciar níveis de estoque e vincular categorias/fornecedores.
5. Em `/categorias.html` e `/fornecedores.html`, cria ou edita dados auxiliares usados no estoque.
6. Em `/movimentacoes.html`, acompanha as entradas e saídas de estoque.
7. Em `/pedidos.html`, consulta pedidos e vê detalhes de cada pedido.
8. Em `/dashboard.html`, visualiza métricas gerais e gráficos.
9. Em `/relatorio_operacional.html` e `/relatorio_mensal.html`, gera relatórios filtrados e exporta CSV.

---

Esta documentação descreve o código principal do projeto. Para mudanças ou novos recursos, atualize este arquivo para refletir as alterações.

### `static/`
- Contém arquivos CSS e JavaScript de suporte.
- `style.css`: estilos gerais do layout.
- `acessibilidade.js`: scripts de acessibilidade e melhorias de interação.

## 11. Como usar este documento

Use esta documentação como referência para entender como o sistema está organizado. Se quiser alterar uma funcionalidade, identifique primeiro o arquivo relacionado:

- páginas e rotas: `backend/main.py`
- lógica de dados e consultas SQL: `backend/acts.py`
- relatórios e gráficos: `backend/relatorios.py`
- cargas de análise/extras: `backend/dashboard.py` e `scripts/simulate_orders.py`

---

Esta documentação descreve o código principal do projeto. Para mudanças ou novos recursos, atualize este arquivo para refletir as alterações.

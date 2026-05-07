/* =========================================
   1. VARIÁVEIS GERAIS (SELEÇÃO DO DOM)
   ========================================= */
const modal = document.querySelector('.janela-modal');
const modalTitulo = document.getElementById('modal-titulo');
const btnNovoCha = document.querySelector('.btn-adicionar');
const botaoCancelar = document.querySelector('.btn-cancelar');
const btnConfirmar = document.getElementById('btn-confirmar');
const corpoTabela = document.getElementById('corpo-tabela');
const inputBusca = document.querySelector('.input-busca');

// Variável para controle de edição (guarda a linha que está sendo editada)
let linhaSendoEditada = null;


/* =========================================
   2. NAVEGAÇÃO ENTRE TELAS (MENU LATERAL)
   ========================================= */
const itensMenu = document.querySelectorAll('.item-menu');
const todasTelas = document.querySelectorAll('.tela-secao');

itensMenu.forEach(item => {
    item.addEventListener('click', () => {
        // Remove a classe 'ativo' de todos os itens e adiciona no clicado
        itensMenu.forEach(i => i.classList.remove('ativo'));
        item.classList.add('ativo');

        // Esconde todas as telas
        todasTelas.forEach(t => t.style.display = 'none');
        
        // Pega o ID da tela correspondente e mostra ela
        const telaAlvo = item.getAttribute('data-tela');
        document.getElementById(telaAlvo).style.display = 'block';
    });
});


/* =========================================
   3. SISTEMA DE BUSCA (FILTRO NA TABELA)
   ========================================= */
inputBusca.addEventListener('keyup', () => {
    const termo = inputBusca.value.toLowerCase();
    const linhas = corpoTabela.querySelectorAll('tr');

    linhas.forEach(linha => {
        const nomeCha = linha.cells[0].innerText.toLowerCase();
        // Se o nome do chá contém o que foi digitado, mostra a linha. Senão, esconde.
        if (nomeCha.includes(termo)) {
            linha.style.display = "";
        } else {
            linha.style.display = "none";
        }
    });
});


/* =========================================
   4. CONTROLE DO MODAL (NOVO CHÁ / EDITAR)
   ========================================= */
// Abrir modal para NOVO chá
btnNovoCha.addEventListener('click', () => {
    linhaSendoEditada = null; // Garante que estamos criando um novo, não editando
    modalTitulo.innerText = "Cadastrar Novo Chá";
    document.getElementById('form-cha').reset(); // Limpa os campos do formulário
    modal.style.display = 'flex';
});

// Fechar modal no botão Cancelar
botaoCancelar.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Confirmar (Salvar Novo ou Salvar Edição)
btnConfirmar.addEventListener('click', (e) => {
    e.preventDefault(); // Evita que a página recarregue
    
    const nome = document.getElementById('input-nome').value;
    const qtd = document.getElementById('input-qtd').value;
    const preco = document.getElementById('input-preco').value;

    // VALIDAÇÃO COM TOAST
    if (!nome || !qtd || !preco) {
        mostrarToast("Preencha todos os campos do formulário!", "erro");
        return;
    }

    if (linhaSendoEditada) {
        // MODO EDIÇÃO: Atualiza os dados na linha existente
        linhaSendoEditada.cells[0].innerText = nome;
        linhaSendoEditada.cells[2].innerText = qtd;
        linhaSendoEditada.cells[3].innerText = `R$ ${parseFloat(preco).toFixed(2)}`;
    } else {
        // MODO NOVO: Cria uma nova linha na tabela
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${nome}</td>
            <td><span class="status ativo">Ativo</span></td>
            <td>${qtd}</td>
            <td>R$ ${parseFloat(preco).toFixed(2)}</td>
            <td>
                <button class="btn-acao btn-editar" title="Editar chá">
                    <i class="ph ph-pencil-simple"></i>
                </button>
                <button class="btn-acao btn-toggle-status" title="Desativar chá">
                    <i class="ph ph-power"></i>
                </button>
            </td>
        `;
        corpoTabela.appendChild(tr);
    }
    
    // SUCESSO COM TOAST
    mostrarToast("Chá salvo com sucesso!", "sucesso");

    // Fecha o modal após salvar
    modal.style.display = 'none';
});

// botão para alterar status do chá (Ativo/Inativo) utilizando a função editar_status_produto do backend funcionando via delegação de eventos (ver seção 5)
const btnstatus = document.querySelector('.btn-toggle-status');
btnstatus.addEventListener('click', () => {
    const badge = linhaSendoEditada.querySelector('.status');
});

/* =========================================
   5. AÇÕES NA TABELA (DELEGAÇÃO DE EVENTOS)
   ========================================= */
// Como usamos delegação, ouvimos os cliques no documento inteiro para as tabelas
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.querySelector('.janela-modal');
    let linhaSendoEditada = null;

    // 1. ESCUTAR CLIQUES NA TABELA (EDITAR E STATUS)
    document.addEventListener('click', function(event) {
        const btn = event.target.closest('button');
        if (!btn) return;

        const linha = btn.closest('tr');
        if (!linha) return;

        // Ação: EDITAR
        if (btn.classList.contains('btn-editar')) {
            linhaSendoEditada = linha;
            const d = linha.dataset; // Pega os atributos data- do HTML

            // Preenchendo os campos do modal com os dados "escondidos" na TR e da função listar_categorias do backend para preencher o select de categorias
            document.getElementById('input-id').value = d.productId || '';
            document.getElementById('input-code').value = d.code || '';
            document.getElementById('input-nome').value = linha.cells[0].innerText;
            document.getElementById('input-description').value = d.description || '';
            
            
            // Limpa o "R$" e converte vírgula em ponto para o input number
            const precoTexto = linha.cells[3].innerText.replace('R$ ', '').replace(',', '.');
            document.getElementById('input-preco').value = precoTexto;
            //trazer a lista de categorias do backend pra preencher o select e selecionar a categoria atual do produto
            const selectCategory = document.getElementById('input-category');
            const categorias = JSON.parse(document.getElementById('corpo-tabela').dataset.categorias || '[]');
            selectCategory.innerHTML = '<option value="">Selecione uma categoria</option>';
            categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.text = cat.name;
                if (cat.name === d.category) {
                    option.selected = true;
                }
                selectCategory.appendChild(option);
            });
        
            document.getElementById('input-image').value = d.image || '';
            document.getElementById('input-slug').value = d.slug || '';
            document.getElementById('input-featured').checked = d.featured === '1';

            modal.style.display = 'flex';
        }

        // Ação: ALTERNAR STATUS
        if (btn.classList.contains('btn-toggle-status')) {
            const productId = linha.dataset.productId;
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('action', 'toggle_status');

            fetch('/index.html', {
                method: 'POST',
                body: formData
            }).then(() => window.location.reload());
        }
    });

    // 2. BOTÃO CONFIRMAR (SALVAR EDIÇÃO)
    document.getElementById('btn-confirmar').addEventListener('click', function() {
        const formData = new FormData();
        
        formData.append('product_id', document.getElementById('input-id').value);
        formData.append('code', document.getElementById('input-code').value);
        formData.append('name', document.getElementById('input-nome').value);
        formData.append('description', document.getElementById('input-description').value);
        formData.append('price', document.getElementById('input-preco').value);
        formData.append('category_id', document.getElementById('input-category').value);
        formData.append('image', document.getElementById('input-image').value);
        formData.append('stock', document.getElementById('input-qtd').value);
        formData.append('slug', document.getElementById('input-slug').value);
        formData.append('featured', document.getElementById('input-featured').checked ? '1' : '0');

        fetch('/index.html', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert("Erro ao salvar alterações.");
            }
        });
    });

    // 3. BOTÃO CANCELAR/FECHAR MODAL
    document.querySelector('.btn-cancelar').addEventListener('click', () => {
        modal.style.display = 'none';
    });
});

// AÇÃO: VER DETALHES DO PEDIDO (FETCH PARA O BACKEND) utlizando as funções detalhes_pedido , intens_pedido e listar_categorias do backend para mostrar as informações do pedido e os itens do pedido no modal de detalhes, utilizando delegação de eventos
document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.getElementById('overlay-detalhes');

    // Escuta cliques na tabela
    document.addEventListener('click', function(event) {
        const btn = event.target.closest('.btn-detalhes');
        if (!btn) return;

        const linha = btn.closest('tr');
        if (!linha) return;

        // Pegando dados do dataset da linha
        const d = linha.dataset;

        // Preenchendo os campos do modal
        document.getElementById('detalhes-cliente').value = d.cliente || 'Não informado';
        document.getElementById('detalhes-email').value = d.email || 'Não informado';
        document.getElementById('detalhes-status').value = d.status || 'Não informado';
        document.getElementById('detalhes-data').value = d.data || 'Não informado';
        document.getElementById('detalhes-produto').value = d.produto || 'Não informado';

        // Mostra o modal
        if (overlay) overlay.style.display = 'flex';
    });

    // Fechar o modal
    const btnFechar = document.getElementById('btn-fechar-detalhes');
    if (btnFechar) {
        btnFechar.addEventListener('click', () => {
            overlay.style.display = 'none';
        });
    }
});

/* =========================================
   6. ACESSIBILIDADE E PREFERÊNCIAS
   ========================================= */
// Ativar/Desativar Modo Escuro
const toggleDarkMode = document.getElementById('toggle-dark-mode');

toggleDarkMode.addEventListener('change', (e) => {
    if (e.target.checked) {
        document.body.classList.add('dark-mode');
        mostrarToast("Modo escuro ativado!", "sucesso");
    } else {
        document.body.classList.remove('dark-mode');
        mostrarToast("Modo claro ativado!", "info");
    }
});

// Ativar VLibras
const btnLibras = document.getElementById('btn-libras');
btnLibras.addEventListener('click', () => {
    // Verifica se o widget já não foi carregado para não duplicar
    if (!document.querySelector('[vw]')) {
        const div = document.createElement('div');
        div.setAttribute('vw', '');
        div.classList.add('enabled');
        div.innerHTML = `
            <div vw-access-button class="active"></div>
            <div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>
        `;
        document.body.appendChild(div);

        const script = document.createElement('script');
        script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
        script.onload = () => new window.VLibras.Widget('https://vlibras.gov.br/app');
        document.head.appendChild(script);
        
        btnLibras.innerText = "VLibras Ativado";
        btnLibras.style.background = "#2ecc71";
    }
});

/* =========================================
   7. INTERAÇÕES DOS ÍCONES SUPERIORES
   ========================================= */
const btnNotificacao = document.getElementById('btn-notificacao');
const dropNotificacao = document.getElementById('drop-notificacao');
const btnPerfil = document.getElementById('btn-perfil');
const dropPerfil = document.getElementById('drop-perfil');

// Abrir aba de Notificações
btnNotificacao.addEventListener('click', (e) => {
    e.stopPropagation(); 
    dropNotificacao.style.display = dropNotificacao.style.display === 'block' ? 'none' : 'block';
    dropPerfil.style.display = 'none'; 
});

// Abrir aba de Log-off
btnPerfil.addEventListener('click', (e) => {
    e.stopPropagation();
    dropPerfil.style.display = dropPerfil.style.display === 'block' ? 'none' : 'block';
    dropNotificacao.style.display = 'none'; 
});

// Fechar menus se clicar fora deles
document.addEventListener('click', (e) => {
    if (!btnNotificacao.contains(e.target) && !dropNotificacao.contains(e.target)) {
        dropNotificacao.style.display = 'none';
    }
    if (!btnPerfil.contains(e.target) && !dropPerfil.contains(e.target)) {
        dropPerfil.style.display = 'none';
    }
});

// Piada do Ajuda (Question Mark) - COM TOAST
document.getElementById('btn-ajuda').addEventListener('click', () => {
    mostrarToast("Área restrita para administradores! Se você não é admin, é melhor 'dei-chá' essa página pra lá! ☕🏃‍♂️", "aviso");
});

// Botão Voltar para login - COM TOAST 
document.getElementById('btn-voltar-login').addEventListener('click', () => {
    mostrarToast("Fazendo log-off... Redirecionando.", "info");
    setTimeout(() => { 
        window.location.href = "login.html";
    }, 1500);
});

/* =========================================
   8. SISTEMA DE TOAST NOTIFICATIONS
   ========================================= */
function mostrarToast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.classList.add('toast', tipo);

    // Define o ícone baseado no tipo
    let icone = 'ph-info';
    if (tipo === 'erro') icone = 'ph-x-circle';
    if (tipo === 'sucesso') icone = 'ph-check-circle';
    if (tipo === 'aviso') icone = 'ph-warning';

    toast.innerHTML = `
        <i class="ph ${icone}"></i>
        <span>${mensagem}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('mostrar');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('mostrar');
        setTimeout(() => toast.remove(), 400); 
    }, 3000);
}
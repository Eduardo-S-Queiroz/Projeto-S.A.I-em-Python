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

// Controle de estado: armazena a referência da linha da tabela em edição
let linhaSendoEditada = null;

/* =========================================
   2. NAVEGAÇÃO ENTRE TELAS (MENU LATERAL)
   ========================================= */
const itensMenu = document.querySelectorAll('.item-menu');
const todasTelas = document.querySelectorAll('.tela-secao');

itensMenu.forEach(item => {
    item.addEventListener('click', () => {
        // Alterna a classe visual de seleção no menu lateral
        itensMenu.forEach(i => i.classList.remove('ativo'));
        item.classList.add('ativo');

        // Oculta todas as seções antes de exibir a selecionada
        todasTelas.forEach(t => t.style.display = 'none');
        
        // Exibe a tela correspondente via atributo data-tela
        const telaAlvo = item.getAttribute('data-tela');
        document.getElementById(telaAlvo).style.display = 'block';
    });
});

/* =========================================
   3. SISTEMA DE BUSCA (FILTRO DINÂMICO)
   ========================================= */
inputBusca.addEventListener('keyup', () => {
    const termo = inputBusca.value.toLowerCase();
    const linhas = corpoTabela.querySelectorAll('tr');

    linhas.forEach(linha => {
        const nomeCha = linha.cells[0].innerText.toLowerCase();
        // Exibe a linha se o nome do produto contiver o termo digitado
        if (nomeCha.includes(termo)) {
            linha.style.display = "";
        } else {
            linha.style.display = "none";
        }
    });
});

/* =========================================
   4. CONTROLE DO MODAL (UNIFICADO)
   ========================================= */

// Abre modal para NOVO produto
btnNovoCha.addEventListener('click', () => {
    linhaSendoEditada = null; 
    modalTitulo.innerText = "Cadastrar Novo Chá";
    document.getElementById('form-cha').reset();
    // Limpa o campo hidden de ID para garantir que o Flask entenda como novo
    document.getElementById('input-id').value = "";
    modal.style.display = 'flex';
});

botaoCancelar.addEventListener('click', () => {
    modal.style.display = 'none';
});

// FUNÇÃO ÚNICA PARA SALVAR (CADASTRO E EDIÇÃO)
btnConfirmar.addEventListener('click', async (e) => {
    e.preventDefault();
    
    // 1. Captura de todos os campos (IDs devem bater com seu HTML)
    const id = document.getElementById('input-id').value;
    const nome = document.getElementById('input-nome').value;
    const qtd = document.getElementById('input-qtd').value;
    const preco = document.getElementById('input-preco').value;
    const code = document.getElementById('input-code').value || "NOVO";
    const desc = document.getElementById('input-description').value;
    const catId = document.getElementById('input-category').value;
    const slug = document.getElementById('input-slug').value;
    const featured = document.getElementById('input-featured').checked ? '1' : '0';
    const imageInput = document.getElementById('input-image');
    formData.append('image', imageInput.files[0]); // Envia o arquivo ou vazio

    // 2. Validação básica
    if (!nome || !qtd || !preco) {
        mostrarToast("Preencha os campos obrigatórios!", "erro");
        return;
    }

    // 3. Montagem do FormData (Nomes das chaves devem ser iguais aos do seu Python)
    const formData = new FormData();
    formData.append('product_id', id);
    formData.append('code', code);
    formData.append('name', nome);         // Note: use 'name' se no Python for request.form.get('name')
    formData.append('description', desc);
    formData.append('price', preco);
    formData.append('stock', qtd);
    formData.append('category_id', catId);
    formData.append('image'),// Envia o arquivo ou vazio
    formData.append('slug', slug);
    formData.append('featured', featured);

    try {
        const response = await fetch('/index.html', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            mostrarToast("Dados sincronizados com o banco!", "sucesso");
            // Recarrega a página para mostrar os dados novos vindos do banco
            setTimeout(() => {
                window.location.reload();
            }, 800);
        } else {
            mostrarToast("Erro ao salvar no servidor", "erro");
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
        mostrarToast("Falha na conexão", "erro");
    }
});

/* =========================================
   5. AÇÕES NA TABELA (EDIÇÃO E STATUS)
   ========================================= */
document.addEventListener('click', function(event) {
    const btn = event.target.closest('button');
    if (!btn) return;

    const linha = btn.closest('tr');
    if (!linha) return;

    // AÇÃO: EDITAR (Preenche o modal)
    if (btn.classList.contains('btn-editar')) {
        linhaSendoEditada = linha;
        modalTitulo.innerText = "Editar Produto";
        const d = linha.dataset;

        // Preenchimento dos campos via dataset da linha
        document.getElementById('input-id').value = d.productId || '';
        document.getElementById('input-code').value = d.code || '';
        document.getElementById('input-nome').value = linha.cells[0].innerText;
        document.getElementById('input-description').value = d.description || '';
        
        const precoLimpo = linha.cells[3].innerText.replace('R$ ', '').replace(',', '.').trim();
        document.getElementById('input-preco').value = precoLimpo;
        document.getElementById('input-qtd').value = d.stock || '';
        
        // Categoria
        const selectCategory = document.getElementById('input-category');
        if (selectCategory) selectCategory.value = d.categoryId || '';
        
        document.getElementById('input-slug').value = d.slug || '';
        document.getElementById('input-featured').checked = d.featured === '1';

        modal.style.display = 'flex';
    }

    // AÇÃO: ALTERNAR STATUS
    if (btn.classList.contains('btn-toggle-status')) {
        const productId = btn.getAttribute('data-id'); 
        const statusAtual = parseInt(btn.getAttribute('data-status') || 0); 
        const novoStatus = statusAtual === 1 ? 0 : 1; 

        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('new_status', novoStatus);
        formData.append('action', 'toggle_status');

        fetch('/index.html', {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) window.location.reload();
        });
    }
});
/* =========================================
   DETALHES DO PEDIDO (INTEGRAÇÃO BACKEND)
   ========================================= */
// Gerencia o modal de detalhes e a exibição de informações específicas de pedidos
document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.getElementById('overlay-detalhes');

    document.addEventListener('click', function(event) {
        const btn = event.target.closest('.btn-detalhes');
        if (!btn) return;

        const linha = btn.closest('tr');
        if (!linha) return;

        // Recupera dados injetados via Jinja2 no dataset do HTML
        const d = linha.dataset;

        // Mapeamento de campos para preenchimento automático do modal
        const campos = {
            'detalhes-id': d.id,
            'detalhes-cliente': d.cliente,
            'detalhes-email': d.email,
            'detalhes-produto': d.produto,
            'detalhes-qtd': d.quantidade,
            'detalhes-preco': 'R$ ' + parseFloat(d.preco || 0).toFixed(2), 
            'detalhes-itens': d.itens, 
            'detalhes-status': d.status,
            'detalhes-data': d.data
        };

        for (const [id, valor] of Object.entries(campos)) {
            const el = document.getElementById(id);
            if (el) {
                // Diferencia o preenchimento entre inputs de formulário e elementos de texto
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.value = valor || 'Não informado';
                } else {
                    el.textContent = valor || 'Não informado';
                }
            }
        }

        if (overlay) overlay.style.display = 'flex';
    });

    // Lógica para fechamento do modal de detalhes
    const btnFechar = document.getElementById('btn-fechar-detalhes');
    if (btnFechar) {
        btnFechar.addEventListener('click', () => {
            if (overlay) overlay.style.display = 'none';
        });
    }

    // Fechamento ao clicar na área externa (overlay)
    if (overlay) {
        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) {
                overlay.style.display = 'none';
            }
        });
    }
});

/* =========================================
   6. ACESSIBILIDADE E PREFERÊNCIAS
   ========================================= */
// Gerencia a alternância entre temas Light e Dark
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

// Inicialização dinâmica do plugin de acessibilidade VLibras
const btnLibras = document.getElementById('btn-libras');
btnLibras.addEventListener('click', () => {
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
   7. INTERAÇÕES DO HEADER (NOTIFICAÇÕES E PERFIL)
   ========================================= */
const btnNotificacao = document.getElementById('btn-notificacao');
const dropNotificacao = document.getElementById('drop-notificacao');
const btnPerfil = document.getElementById('btn-perfil');
const dropPerfil = document.getElementById('drop-perfil');

// Exibe/Oculta painel de notificações
btnNotificacao.addEventListener('click', (e) => {
    e.stopPropagation(); 
    dropNotificacao.style.display = dropNotificacao.style.display === 'block' ? 'none' : 'block';
    dropPerfil.style.display = 'none'; 
});

// Exibe/Oculta menu de perfil (Log-off)
btnPerfil.addEventListener('click', (e) => {
    e.stopPropagation();
    dropPerfil.style.display = dropPerfil.style.display === 'block' ? 'none' : 'block';
    dropNotificacao.style.display = 'none'; 
});

// Listener global para fechar menus suspensos ao clicar fora
document.addEventListener('click', (e) => {
    if (!btnNotificacao.contains(e.target) && !dropNotificacao.contains(e.target)) {
        dropNotificacao.style.display = 'none';
    }
    if (!btnPerfil.contains(e.target) && !dropPerfil.contains(e.target)) {
        dropPerfil.style.display = 'none';
    }
});

// Feedback visual para o botão de ajuda
document.getElementById('btn-ajuda').addEventListener('click', () => {
    mostrarToast("Área restrita para administradores! ☕🏃‍♂️", "aviso");
});

// Redirecionamento para a tela de autenticação
btnVoltarLogin.addEventListener('click', () => {
    mostrarToast('Redirecionando...'); 
    window.location.href = '/login.html';
});

/* =========================================
   8. SISTEMA DE TOAST (NOTIFICAÇÕES FLUTUANTES)
   ========================================= */
function mostrarToast(mensagem, tipo = 'sucesso') {
    let container = document.getElementById('toast-container');
    
    // Cria o container caso não esteja presente no HTML
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = mensagem;

    container.appendChild(toast);

    // Remove automaticamente o elemento após 3 segundos
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
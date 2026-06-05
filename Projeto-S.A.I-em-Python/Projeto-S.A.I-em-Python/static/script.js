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
    // Ajusta os nomes dos campos para o padrão de "novo" esperado pelo backend
    const mapNewNames = {
        'input-id': 'new_product',
        'input-code': 'new_code',
        'input-nome': 'new_name',
        'input-description': 'new_description',
        'input-preco': 'new_price',
        'input-qtd': 'new_stock',
        'input-category': 'new_category_id',
        'input-image': 'new_image',
        'input-slug': 'new_slug',
        'input-featured': 'new_featured'
    };

    Object.keys(mapNewNames).forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        // Para o campo ID usamos um hidden flag; não enviamos um id numérico
        if (id === 'input-id') {
            el.value = '';
            // cria um campo hidden 'new_product' apenas quando for novo
            if (!document.querySelector('input[name="new_product"]')) {
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'new_product';
                hidden.value = '1';
                hidden.id = 'hidden-new-product-flag';
                document.getElementById('form-cha').appendChild(hidden);
            }
            return;
        }

        el.name = mapNewNames[id];
    });
    
    const selectCategory = document.getElementById('input-category');
    const corpoTabela = document.getElementById('corpo-tabela');
    
    // Tenta obter as categorias do dataset no HTML
    const dados = corpoTabela.dataset.categorias;
    if (dados) {
        const categorias = JSON.parse(dados);
        selectCategory.innerHTML = '<option value="">Selecione uma categoria</option>';
        
        categorias.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.text = cat.name;
            selectCategory.appendChild(option);
        });
    }

    modal.style.display = 'flex';
    
});

// Fechar modal no botão Cancelar
botaoCancelar.addEventListener('click', () => {
    modal.style.display = 'none';
});

// NOTE: O listener de confirmar é declarado dentro do DOMContentLoaded (seção 5)
// para unificar o fluxo de edição vs novo. Removido listener duplicado aqui.

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
            const d = linha.dataset;
            
            // Preencher inputs básicos
            document.getElementById('input-id').value = d.id || '';
            document.getElementById('input-code').value = d.code || '';
            document.getElementById('input-nome').value = linha.cells[0].innerText;
            document.getElementById('input-description').value = d.description || '';
            
            const precoTexto = linha.cells[3].innerText.replace('R$ ', '').replace(',', '.');
            document.getElementById('input-preco').value = precoTexto;

            // Preencher Select de Categorias com segurança
            const corpoTabela = document.getElementById('corpo-tabela');
            const categorias = JSON.parse(corpoTabela.dataset.categorias || '[]');

            const selectCategory = document.getElementById('input-category');
            selectCategory.innerHTML = '<option value="">Selecione uma categoria</option>';
            
            const catIdDoProduto = d.category; // Usamos o dataset que já temos

            categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.text = cat.name;
                
                // Compara IDs (convertendo para String para garantir igualdade)
                if (String(cat.id) === String(catIdDoProduto)) {
                    option.selected = true;
                }
                selectCategory.appendChild(option);
            });
            
            document.getElementById('input-qtd').value = d.stock || '';
            document.getElementById('input-image').value = d.image || '';
            document.getElementById('input-slug').value = d.slug || '';
            document.getElementById('input-featured').checked = d.featured === '1';

            // Garante que os names estão no formato de edição esperado pelo backend
            const mapEditNames = {
                'input-id': 'edit_product_id',
                'input-code': 'edit_code',
                'input-nome': 'edit_name',
                'input-description': 'edit_description',
                'input-preco': 'edit_price',
                'input-qtd': 'edit_stock',
                'input-category': 'edit_category_id',
                'input-image': 'edit_image',
                'input-slug': 'edit_slug',
                'input-featured': 'edit_featured'
            };

            Object.keys(mapEditNames).forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                el.name = mapEditNames[id];
            });

            // Remove flag de novo produto caso exista
            const hiddenFlag = document.getElementById('hidden-new-product-flag');
            if (hiddenFlag) hiddenFlag.remove();

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
            }).then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    mostrarToast("Erro ao alterar status.", "erro");
                }
            });
        }
    });

    // 2. BOTÃO CONFIRMAR (SALVAR EDIÇÃO OU NOVO)
    document.getElementById('btn-confirmar').addEventListener('click', function() {
        const form = document.getElementById('form-cha');
        const formData = new FormData(form);

        // Se temos uma linha sendo editada, é uma edição
        if (linhaSendoEditada) {
            formData.append('action', 'update_product');

            fetch('/index.html', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload(); // Recarrega para ver as mudanças
                } else {
                    alert('Erro ao atualizar produto.');
                }
            })
            .catch(error => console.error('Erro:', error));
        } else {
            // Novo produto: garante flag e envia como formulário padrão
            if (!formData.has('new_product')) formData.append('new_product', '1');

            fetch('/index.html', {
                method: 'POST',
                body: formData
            })
            .then(() => {
                // O backend redireciona para a página; recarregamos para refletir alteração
                window.location.reload();
            })
            .catch(error => console.error('Erro ao criar produto:', error));
        }
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

        const pedidoId = linha.dataset.pedidoId;
        const formData = new FormData();
        formData.append('pedido_id', pedidoId);

        fetch('/index.html', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(dados => {
            
            // Tenta pegar o primeiro item do array se vier como lista, senão usa o objeto
            const pedidoDoServidor = Array.isArray(dados) && dados.length > 0 ? dados[0] : (dados.id ? dados : null);

            // Função auxiliar para preencher campos com segurança
            const preencher = (id, valor) => {
                const campo = document.getElementById(id);
                if (campo) campo.value = valor || "Não informado";
            };

            if (pedidoDoServidor) {

                preencher('detalhes-cliente', pedidoDoServidor.cliente || pedidoDoServidor.user_id);
                preencher('detalhes-email', pedidoDoServidor.email);
                preencher('detalhes-status', pedidoDoServidor.status);
                preencher('detalhes-data', pedidoDoServidor.created_at);
                preencher('detalhes-endereco', pedidoDoServidor.shipping_address);
                preencher('detalhes-produto', pedidoDoServidor.produto);

                // TRATAMENTO DO PREÇO (Evita campo vazio)
                const precoBruto = pedidoDoServidor.total_price || 0;
                // Converte para número puro (ex: "261,00" -> 261.00)
                const precoNumerico = typeof precoBruto === 'string' 
                    ? parseFloat(precoBruto.replace(',', '.')) 
                    : parseFloat(precoBruto);
                
                const campoTotal = document.getElementById('detalhes-total_price');
                if (campoTotal) campoTotal.value = precoNumerico.toFixed(2);
                

               if (pedidoDoServidor.items) {
                try {
                    // Converte se for string, senão usa como objeto
                    const listaItens = typeof pedidoDoServidor.items === 'string' 
                        ? JSON.parse(pedidoDoServidor.items) 
                        : pedidoDoServidor.items;

                    // Se for uma lista, vamos juntar os nomes
                    if (Array.isArray(listaItens)) {
                        // Formata como: "Produto A (2), Produto B (1)"
                                    const textoFormatado = listaItens.map(item => {
                                        const nome = item.name || item.nome || "Produto";
                                        const qtd = item.quantity || item.quantidade || 1;
                                        return `${nome} (${qtd})`;
                                    }).join(', ');                        
                        preencher('detalhes-itens', textoFormatado);
                    } else {
                        // Se não for array, tenta mostrar o que houver
                        preencher('detalhes-itens', linha.dataset.itens);                    }
                } catch (e) {
                    console.error("Erro no JSON de itens:", e);
                    preencher('detalhes-itens', 'Erro ao processar lista');
                }
            } else {
                // Caso o backend não envie a chave 'items', tenta o fallback da linha
                preencher('detalhes-itens', linha.dataset.produto || 'Não informado');
                preencher('detalhes-itens', linha.dataset.quantity || 'Não informado');
            }
            } else {
                // FALLBACK: Se o banco retornar [], usamos os dados do HTML (data- attributes)
                // FALLBACK (Se o banco falhar, usa os atributos data- da linha)
                preencher('detalhes-cliente', linha.dataset.cliente);
                preencher('detalhes-email', linha.dataset.email);
                preencher('detalhes-status', linha.dataset.status);
                preencher('detalhes-data', linha.dataset.data);
                preencher('detalhes-produto', linha.dataset.produto);
                preencher('detalhes-itens', linha.dataset.itens);
                preencher('detalhes-endereco', linha.dataset.endereco);

                // Ajuste do preço no Fallback
                const precoLinha = linha.dataset.total_price || "0";
                const campoTotal = document.getElementById('detalhes-total_price');
                if (campoTotal) campoTotal.value = parseFloat(precoLinha.replace(',', '.')).toFixed(2);
            }

            if (overlay) overlay.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erro ao buscar detalhes:', error);
            mostrarToast("Erro ao carregar detalhes do pedido.", "erro");
        });
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
document.getElementById('btn-voltar').addEventListener('click', () => {
    mostrarToast("Fazendo log-off... Redirecionando.", "info");
    setTimeout(() => { 
        window.location.href = "login.html";
    }, 2000);
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
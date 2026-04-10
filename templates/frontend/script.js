const modal = document.querySelector('.janela-modal');
const modalTitulo = document.getElementById('modal-titulo');
const btnNovoCha = document.querySelector('.btn-adicionar');
const botaoCancelar = document.querySelector('.btn-cancelar');
const btnConfirmar = document.getElementById('btn-confirmar');
const corpoTabela = document.getElementById('corpo-tabela');

// Variável para controle de edição
let linhaSendoEditada = null;

// --- LÓGICA DE NAVEGAÇÃO ENTRE TELAS ---
const itensMenu = document.querySelectorAll('.item-menu');
const todasTelas = document.querySelectorAll('.tela-secao');

itensMenu.forEach(item => {
    item.addEventListener('click', () => {
        // Remove 'ativo' de todos e adiciona no clicado
        itensMenu.forEach(i => i.classList.remove('ativo'));
        item.classList.add('ativo');

        // Esconde todas as telas e mostra a selecionada
        todasTelas.forEach(t => t.style.display = 'none');
        const telaAlvo = item.getAttribute('data-tela');
        document.getElementById(telaAlvo).style.display = 'block';
    });
});

// --- CONTROLE DO MODAL ---
btnNovoCha.addEventListener('click', () => {
    linhaSendoEditada = null;
    modalTitulo.innerText = "Cadastrar Novo Chá";
    document.getElementById('form-cha').reset(); // Limpa todos os campos
    modal.style.display = 'flex';
});

botaoCancelar.addEventListener('click', () => modal.style.display = 'none');

btnConfirmar.addEventListener('click', (e) => {
    e.preventDefault();
    const nome = document.getElementById('input-nome').value;
    const qtd = document.getElementById('input-qtd').value;
    const preco = document.getElementById('input-preco').value;

    if (!nome || !qtd || !preco) return alert("Preencha todos os campos!");

    if (linhaSendoEditada) {
        // Modo Edição
        linhaSendoEditada.cells[0].innerText = nome;
        linhaSendoEditada.cells[2].innerText = qtd;
        linhaSendoEditada.cells[3].innerText = `R$ ${parseFloat(preco).toFixed(2)}`;
    } else {
        // Modo Novo
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${nome}</td>
            <td><span class="status ativo">Ativo</span></td>
            <td>${qtd}</td>
            <td>R$ ${parseFloat(preco).toFixed(2)}</td>
            <td>
                <button class="btn-editar">Editar</button>
                <button class="btn-toggle-status">Desativar</button>
            </td>
        `;
        corpoTabela.appendChild(tr);
    }
    modal.style.display = 'none';
});

// --- AÇÕES NA TABELA (EDITAR / STATUS) ---
corpoTabela.addEventListener('click', (e) => {
    const btn = e.target;
    const linha = btn.closest('tr');

    if (btn.classList.contains('btn-toggle-status')) {
        const badge = linha.querySelector('.status');
        if (btn.innerText === "Desativar") {
            badge.innerText = "Inativo";
            badge.classList.replace('ativo', 'inativo');
            linha.style.opacity = "0.4";
            btn.innerText = "Ativar";
        } else {
            badge.innerText = "Ativo";
            badge.classList.replace('inativo', 'ativo');
            linha.style.opacity = "1";
            btn.innerText = "Desativar";
        }
    }

    if (btn.classList.contains('btn-editar')) {
        linhaSendoEditada = linha;
        modalTitulo.innerText = "Editar Chá";
        document.getElementById('input-nome').value = linha.cells[0].innerText;
        document.getElementById('input-qtd').value = linha.cells[2].innerText;
        document.getElementById('input-preco').value = linha.cells[3].innerText.replace('R$ ', '').replace(',', '.');
        modal.style.display = 'flex';
    }
});

// --- ACESSIBILIDADE: TROCA DE COR ---
document.getElementById('seletor-cor').addEventListener('input', (e) => {
    const cor = e.target.value;
    document.documentElement.style.setProperty('--cor-principal', cor); // Se quiser usar variáveis CSS
    // Forma simples: mudar o que é roxo
    document.querySelectorAll('.item-menu.ativo, .btn-adicionar, .btn-salvar').forEach(el => {
        el.style.backgroundColor = cor;
    });
    document.querySelectorAll('h2, h1, th, .item-menu:hover').forEach(el => {
        el.style.color = cor;
    });
});

document.getElementById('seletor-cor').addEventListener('input', (e) => {
    const cor = e.target.value;
    document.documentElement.style.setProperty('--cor-principal', cor);
});

const inputBusca = document.querySelector('.input-busca');

inputBusca.addEventListener('keyup', () => {
    const termo = inputBusca.value.toLowerCase();
    const linhas = corpoTabela.querySelectorAll('tr');

    linhas.forEach(linha => {
        const nomeCha = linha.cells[0].innerText.toLowerCase();
        if (nomeCha.includes(termo)) {
            linha.style.display = "";
        } else {
            linha.style.display = "none";
        }
    });
});

const btnLibras = document.getElementById('btn-libras');
btnLibras.addEventListener('click', () => {
    if (!document.querySelector('[vw]')) {
        // Cria a estrutura do VLibras dinamicamente
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
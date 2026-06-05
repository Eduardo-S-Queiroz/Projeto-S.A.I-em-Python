document.addEventListener('DOMContentLoaded', () => {
    const existing = document.getElementById('painel-acessibilidade-flutuante');
    if (!existing) {
        const wrapper = document.createElement('div');
        wrapper.id = 'painel-acessibilidade-flutuante';
        wrapper.innerHTML = `
            <button type="button" id="btn-acessibilidade-flutuante" title="Abrir acessibilidade">
                <i class="fas fa-universal-access"></i>
            </button>
            <div id="caixa-acessibilidade-flutuante" class="caixa-acessibilidade-flutuante">
                <h3>Acessibilidade</h3>
                <p>Preferências visuais e recursos assistivos.</p>
                <label class="linha-acessibilidade"><input type="checkbox" id="toggle-dark-mode"> Modo escuro</label>
                <div class="linha-botoes-acessibilidade">
                    <button type="button" id="btn-fonte-menor">A-</button>
                    <button type="button" id="btn-fonte-padrao">A</button>
                    <button type="button" id="btn-fonte-maior">A+</button>
                </div>
                <button type="button" id="btn-libras" class="btn-libras">Ativar VLibras</button>
            </div>
        `;
        document.body.appendChild(wrapper);
    }

    const btnAbrir = document.getElementById('btn-acessibilidade-flutuante');
    const caixa = document.getElementById('caixa-acessibilidade-flutuante');
    const toggleDarkMode = document.getElementById('toggle-dark-mode');
    const btnFonteMenor = document.getElementById('btn-fonte-menor');
    const btnFontePadrao = document.getElementById('btn-fonte-padrao');
    const btnFonteMaior = document.getElementById('btn-fonte-maior');
    const btnLibras = document.getElementById('btn-libras');

    let escalaFonte = Number(localStorage.getItem('saiFonteEscala') || '100');

    function aplicarFonte() {
        document.documentElement.style.fontSize = escalaFonte + '%';
        localStorage.setItem('saiFonteEscala', String(escalaFonte));
    }

    function mostrarToastAcessivel(mensagem, tipo = 'info') {
        if (typeof mostrarToast === 'function') {
            mostrarToast(mensagem, tipo);
            return;
        }
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = `toast ${tipo}`;
        toast.textContent = mensagem;
        container.appendChild(toast);
        setTimeout(() => toast.classList.add('mostrar'), 10);
        setTimeout(() => {
            toast.classList.remove('mostrar');
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    aplicarFonte();

    if (localStorage.getItem('saiDarkMode') === '1') {
        document.body.classList.add('dark-mode');
        if (toggleDarkMode) toggleDarkMode.checked = true;
    }

    if (btnAbrir && caixa) {
        btnAbrir.addEventListener('click', (e) => {
            e.stopPropagation();
            caixa.classList.toggle('aberta');
        });
        document.addEventListener('click', (e) => {
            if (!caixa.contains(e.target) && !btnAbrir.contains(e.target)) {
                caixa.classList.remove('aberta');
            }
        });
    }

    if (toggleDarkMode) {
        toggleDarkMode.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('saiDarkMode', '1');
                mostrarToastAcessivel('Modo escuro ativado!', 'sucesso');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('saiDarkMode', '0');
                mostrarToastAcessivel('Modo claro ativado!', 'info');
            }
        });
    }

    if (btnFonteMenor) {
        btnFonteMenor.addEventListener('click', () => {
            escalaFonte = Math.max(85, escalaFonte - 10);
            aplicarFonte();
            mostrarToastAcessivel('Fonte reduzida.', 'info');
        });
    }

    if (btnFontePadrao) {
        btnFontePadrao.addEventListener('click', () => {
            escalaFonte = 100;
            aplicarFonte();
            mostrarToastAcessivel('Fonte restaurada ao padrão.', 'info');
        });
    }

    if (btnFonteMaior) {
        btnFonteMaior.addEventListener('click', () => {
            escalaFonte = Math.min(130, escalaFonte + 10);
            aplicarFonte();
            mostrarToastAcessivel('Fonte aumentada.', 'sucesso');
        });
    }

    if (btnLibras) {
        btnLibras.addEventListener('click', () => {
            if (!document.querySelector('[vw]')) {
                const div = document.createElement('div');
                div.setAttribute('vw', '');
                div.classList.add('enabled');
                div.innerHTML = '<div vw-access-button class="active"></div><div vw-plugin-wrapper><div class="vw-plugin-top-wrapper"></div></div>';
                document.body.appendChild(div);

                const script = document.createElement('script');
                script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
                script.onload = () => {
                    if (window.VLibras) new window.VLibras.Widget('https://vlibras.gov.br/app');
                };
                document.head.appendChild(script);
            }
            btnLibras.innerText = 'VLibras Ativado';
            btnLibras.style.background = '#2ecc71';
            mostrarToastAcessivel('VLibras ativado!', 'sucesso');
        });
    }
});

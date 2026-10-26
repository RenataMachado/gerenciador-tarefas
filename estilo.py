"""
estilo.py
---------
Visual do app, inspirado na identidade da FIAP: fundo preto, rosa como cor
de destaque e tipografia forte. Aqui ficam o CSS e os pedaços de HTML usados
pela interface. As cores básicas também estão em .streamlit/config.toml.
"""

import html

import streamlit as st

# Nome curto de cada status, usado nas classes CSS (sem espaço nem acento)
SLUG_STATUS = {"pendente": "pendente", "em andamento": "andamento", "concluída": "concluida", "atrasada": "atrasada"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;800&display=swap');

:root {
    --rosa: #ED145B;
    --preto: #000000;
    --grafite: #0E0E0E;
    --borda: #262626;
    --texto: #F5F5F5;
    --apagado: #9A9A9A;
}

/* Tipografia */
.stApp, .stApp p, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp li, .stApp h1, .stApp h2, .stApp h3 {
    font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif;
}
.stApp h3 { font-weight: 700; letter-spacing: -0.01em; }

header[data-testid="stHeader"] { background: transparent; }
.stApp .block-container { padding-top: 2.5rem; max-width: 1240px; margin: 0 auto; }

/* Cabeçalho */
.hero {
    border-left: 6px solid var(--rosa);
    padding: 0.25rem 0 0.25rem 1.25rem;
    margin-bottom: 2rem;
}
.hero-titulo {
    color: var(--texto);
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
}
.hero-sub { color: var(--apagado); font-size: 1.05rem; margin-top: 0.75rem; }

/* Painel de resumo */
.painel {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--borda);
    border: 1px solid var(--borda);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 2rem;
}
.indicador { background: var(--grafite); padding: 1rem 1.25rem; }
.indicador-num { color: var(--texto); font-size: 2.2rem; font-weight: 800; line-height: 1; }
.indicador-rotulo { color: var(--apagado); font-size: 0.85rem; margin-top: 0.4rem; }
.indicador-alerta .indicador-num { color: var(--rosa); }
@media (max-width: 700px) {
    .painel { grid-template-columns: repeat(2, 1fr); }
    .indicador:first-child { grid-column: span 2; }
}

/* Abas */
.stTabs [data-baseweb="tab"] p { font-weight: 600; font-size: 1rem; }

/* Cartões de tarefa (o status vem no nome da key do container) */
[class*="st-key-card-"] {
    background: var(--grafite);
    border: 1px solid var(--borda);
    border-left: 4px solid #5A5A5A;
    border-radius: 4px;
    padding: 1rem 1.25rem;
}
[class*="st-key-card-andamento"] { border-left-color: var(--rosa); }
[class*="st-key-card-concluida"] { border-left-color: #2E2E2E; }
[class*="st-key-card-atrasada"] { border-left-color: var(--rosa); background: #140409; }
[class*="st-key-card-concluida"] .tarefa-titulo { text-decoration: line-through; color: var(--apagado); }

.tarefa-data { color: var(--apagado); font-size: 0.85rem; }
.tarefa-titulo { color: var(--texto); font-size: 1.15rem; font-weight: 600; margin: 0.15rem 0 0.6rem; }
.tag {
    display: inline-block;
    padding: 0.1rem 0.6rem;
    margin: 0 0.35rem 0.35rem 0;
    border: 1px solid var(--borda);
    border-radius: 999px;
    color: #C8C8C8;
    font-size: 0.78rem;
    font-weight: 500;
}
.tag-andamento { background: var(--rosa); border-color: var(--rosa); color: #FFFFFF; }
.tag-alta { color: var(--rosa); border-color: rgba(237, 20, 91, 0.5); }
.tag-atrasada { background: rgba(237, 20, 91, 0.12); border-color: var(--rosa); color: var(--rosa); font-weight: 600; }

/* Botões e caixas */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
    border-radius: 4px;
    font-weight: 600;
}
[data-testid="stExpander"] details { border-color: var(--borda); border-radius: 4px; }
</style>
"""


# O quadro (streamlit-sortables) é desenhado dentro de um iframe,
# por isso recebe um CSS separado, passado no parâmetro custom_style.
CSS_QUADRO = """
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700&display=swap');
body { background: transparent; }
.sortable-component {
    background-color: transparent;
    border: none;
    padding: 0;
    font-family: 'Archivo', 'Helvetica Neue', Arial, sans-serif;
}
.sortable-container {
    background-color: #0E0E0E;
    border: 1px solid #262626;
    border-top: 3px solid #5A5A5A;
    border-radius: 4px;
}
.sortable-container:nth-child(2) { border-top-color: #ED145B; }
.sortable-container:nth-child(3) { border-top-color: #2E2E2E; }
.sortable-container:nth-child(4) { border-top-color: #ED145B; }
.sortable-container-header {
    background-color: transparent;
    color: #F5F5F5;
    font-weight: 700;
    padding: 0.6rem 0.9rem;
}
.sortable-container:nth-child(4) .sortable-container-header { color: #ED145B; }
.sortable-container-body { background-color: transparent; min-height: 140px; }
.sortable-item, .sortable-item:hover {
    background-color: #1A1A1A;
    color: #F5F5F5;
    border: 1px solid #2A2A2A;
    border-radius: 4px;
    font-weight: 500;
    cursor: grab;
}
.sortable-item:hover { border-color: #ED145B; }
.sortable-container:nth-child(3) .sortable-item { color: #8A8A8A; text-decoration: line-through; }
.sortable-container:nth-child(4) .sortable-item { border-left: 3px solid #ED145B; }
"""


def aplicar_estilo():
    """Injeta o CSS na página. Chamar logo no começo do app."""
    st.markdown(CSS, unsafe_allow_html=True)


def cabecalho():
    """HTML do topo da página."""
    return (
        '<div class="hero">'
        '<div class="hero-titulo">Gerenciador de Tarefas</div>'
        '<div class="hero-sub">Organize, acompanhe e conclua suas tarefas do dia a dia.</div>'
        '</div>'
    )


def painel_resumo(r):
    """HTML do painel com os números (r vem de tarefas.resumo)."""
    itens = [
        (r["total"], "Total", ""),
        (r["pendente"], "Pendentes", ""),
        (r["em andamento"], "Em andamento", ""),
        (r["concluída"], "Concluídas", ""),
        (r["atrasada"], "Atrasadas", "indicador-alerta" if r["atrasada"] else ""),
    ]
    blocos = "".join(
        f'<div class="indicador {classe}"><div class="indicador-num">{numero}</div>'
        f'<div class="indicador-rotulo">{rotulo}</div></div>'
        for numero, rotulo, classe in itens
    )
    return f'<div class="painel">{blocos}</div>'


def _tag(texto, classe=""):
    return f'<span class="tag {classe}">{html.escape(texto)}</span>'


def cartao_html(tarefa, vencimento_br, atrasada):
    """HTML com as informações de uma tarefa (data, descrição e etiquetas)."""
    tags = [
        _tag(tarefa["status"], f"tag-{SLUG_STATUS[tarefa['status']]}"),
        _tag(f"Prioridade {tarefa['prioridade']}", "tag-alta" if tarefa["prioridade"] == "alta" else ""),
        _tag(tarefa["categoria"].capitalize()),
    ]
    if tarefa["recorrencia"] != "nenhuma":
        tags.append(_tag(f"Repete: {tarefa['recorrencia']}"))
    if atrasada and tarefa["status"] != "atrasada":
        tags.append(_tag("Vencida", "tag-atrasada"))

    # html.escape evita que um texto digitado pelo usuário quebre o HTML
    return (
        f'<div class="tarefa-data">Vence em {vencimento_br}</div>'
        f'<div class="tarefa-titulo">{html.escape(tarefa["descricao"])}</div>'
        f'<div>{"".join(tags)}</div>'
    )

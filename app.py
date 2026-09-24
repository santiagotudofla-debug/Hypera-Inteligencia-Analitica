import streamlit as st
from utils import injetar_css

st.set_page_config(
    page_title="Hypera Analytics — HYPE3",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

injetar_css()

# Registra as páginas no sistema de navegação ocultando o menu padrão (forced to the top)
p1 = st.Page("pages/1_Visao_Corporativa.py", title="Visão Corporativa", icon="🌍")
p2 = st.Page("pages/2_Desempenho_Financeiro.py", title="Desempenho Financeiro", icon="💰")
p3 = st.Page("pages/3_Inteligencia_e_Risco.py", title="Inteligência & Risco", icon="🔎")
p4 = st.Page("pages/4_Hypera_AI_Analyst.py", title="Hypera AI Analyst", icon="🧠")
p6 = st.Page("pages/6_Exportacao_e_Relatorios.py", title="Exportação e Relatórios", icon="📥")

pg = st.navigation([p1, p2, p3, p4, p6], position="hidden")

# --- CONSTRUÇÃO MANUAL DA BARRA LATERAL (Para controlar a ordem) ---
st.sidebar.title("🌱 Hypera ESG & Analytics")
st.sidebar.markdown("**HYPE3** — Inteligência Financeira e Sustentabilidade Corporativa (Dados Reais CVM & B3)")
st.sidebar.markdown("---")

# Renderizamos os links de página na ordem que quisermos
st.sidebar.page_link(p1, label="Visão Corporativa", icon="🌍")
st.sidebar.page_link(p2, label="Desempenho Financeiro", icon="💰")
st.sidebar.page_link(p3, label="Inteligência & Risco", icon="🔎")
st.sidebar.page_link(p4, label="Hypera AI Analyst", icon="🧠")
st.sidebar.page_link(p6, label="Exportação e Relatórios", icon="📥")

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Atualizar Dados Agora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "**Aviso Legal:** Plataforma integrada com fontes públicas oficiais (CVM, B3 e Relatórios de Sustentabilidade) em tempo real."
)

# Executa a página selecionada
pg.run()

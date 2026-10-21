import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
from utils import (
    carregar_dados_mercado_real,
    carregar_demonstrativos_cvm_real,
    carregar_info_ticker,
    calcular_altman_z_score
)

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

st.title("🧠 Hypera AI Analyst — Assistente Inteligente (HYPE3)")
st.markdown("Converse com a inteligência analítica baseada nos dados contábeis, notas explicativas e relatórios da CVM.")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Chave da API não encontrada. Por favor, configure o arquivo .streamlit/secrets.toml com a variável GEMINI_API_KEY.")
    api_key = None

@st.cache_data(ttl=3600)
def consultar_gemini(query, contexto_texto, key):
    """Consulta segura ao Google Gemini com cache e retentativas em caso de instabilidade."""
    if not key:
        return False, "Chave da API Gemini não configurada."
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=key)
    system_instruction = (
        "Você é um analista sênior do mercado financeiro focado na Hypera Pharma (HYPE3). "
        "Use o contexto financeiro recente fornecido para embasar suas respostas. "
        "Responda em português de forma analítica, profissional, precisa e direta."
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=f"Contexto Oficial HYPE3:\n{contexto_texto}\n\nPergunta do Usuário:\n{query}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )
            return True, response.text
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg and attempt < max_retries - 1:
                time.sleep(2)
                continue
            elif "429" in error_msg and attempt < max_retries - 1:
                time.sleep(10)
                continue
            elif "429" in error_msg:
                return False, "⚠️ Limite de consultas gratuitas atingido temporariamente. Por favor, aguarde 1 minuto."
            else:
                return False, f"Ocorreu um erro ao consultar a API: {e}"
    
    return False, "A API do Gemini está com alta demanda no momento. Por favor, tente novamente em alguns instantes."

# Botões de sugestão
st.markdown("### 💡 Perguntas Sugeridas (Clique para testar)")
col_sug1, col_sug2, col_sug3 = st.columns(3)

pergunta_sugerida = None
with col_sug1:
    if st.button("📊 Qual o ROIC e Margens atuais?", use_container_width=True):
        pergunta_sugerida = "Qual a margem líquida, margem EBITDA e estimativa de rentabilidade atuais da Hypera?"
with col_sug2:
    if st.button("📈 Como está a saúde financeira?", use_container_width=True):
        pergunta_sugerida = "Como está a solvência e saúde financeira considerando o Z-Score e endividamento?"
with col_sug3:
    if st.button("📋 Perspectiva de Dividendos", use_container_width=True):
        pergunta_sugerida = "Considerando o yield e payout atuais, qual a sustentabilidade da distribuição de proventos?"

# Caixa de pergunta manual
pergunta_digitada = st.text_input(
    "💬 Faça uma pergunta sobre a Hypera Pharma (ou use uma das sugestões acima):",
    value=pergunta_sugerida if pergunta_sugerida else ""
)

query_ativa = pergunta_digitada if pergunta_digitada else pergunta_sugerida

if query_ativa:
    st.markdown("---")
    st.subheader("🤖 Resposta do Analista (Google Gemini):")
    
    if not api_key:
        st.warning("⚠️ Chave de API não localizada em `.streamlit/secrets.toml`.")
    else:
        with st.spinner("Consultando dados atualizados e gerando parecer analítico..."):
            info_ai = carregar_info_ticker("HYPE3.SA")
            z_info = calcular_altman_z_score(info_ai)
            
            dy_ai = float(info_ai.get('dividendYield', 0.0) or 0.0) * 100
            ml_ai = float(info_ai.get('profitMargins', 0.0) or 0.0) * 100
            me_ai = float(info_ai.get('ebitdaMargins', 0.0) or 0.0) * 100
            roe_ai = float(info_ai.get('returnOnEquity', 0.0) or 0.0) * 100
            div_ai = float(info_ai.get('totalDebt', 0.0) or 0.0)
            cx_ai = float(info_ai.get('totalCash', 0.0) or 0.0)
            
            contexto = f"""
            Dados Financeiros e de Risco Recentes da Hypera Pharma (HYPE3):
            - Preço/Lucro (P/L): {info_ai.get('trailingPE', 'N/A')}
            - Dividend Yield: {dy_ai:.2f}%
            - Margem Líquida: {ml_ai:.2f}%
            - Margem EBITDA: {me_ai:.2f}%
            - ROE: {roe_ai:.2f}%
            - Dívida Total: R$ {div_ai:,.2f}
            - Caixa e Equivalentes: R$ {cx_ai:,.2f}
            - Altman Z''-Score Calculado: {z_info['z_score']:.2f} ({z_info['zona']})
            """
            
            sucesso, texto_resposta = consultar_gemini(query_ativa, contexto, api_key)
            
            if sucesso:
                st.success(texto_resposta)
            else:
                st.error(texto_resposta)



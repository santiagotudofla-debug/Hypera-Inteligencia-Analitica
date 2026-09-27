import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from utils import carregar_dados_mercado_real, carregar_demonstrativos_cvm_real

df_mercado_real = carregar_dados_mercado_real()
ano_atual = datetime.now().year
df_cvm_real = carregar_demonstrativos_cvm_real(ano_atual)
if df_cvm_real.empty:
    df_cvm_real = carregar_demonstrativos_cvm_real(ano_atual - 1)

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
    st.error("Chave da API não encontrada. Por favor, configure o arquivo .streamlit/secrets.toml")
    api_key = None
    
pergunta = st.text_input("💬 Faça uma pergunta sobre a Hypera Pharma (ex: 'Resuma os principais desafios com base no endividamento?'):")

st.markdown("### 💡 Perguntas Sugeridas (Clique para testar)")
col_sug1, col_sug2, col_sug3 = st.columns(3)

pergunta_selecionada = None
with col_sug1:
    if st.button("📊 Qual o ROIC e Margem atuais?"):
        pergunta_selecionada = "Qual a margem líquida e ROE atuais?"
with col_sug2:
    if st.button("📈 Como está a saúde financeira?"):
        pergunta_selecionada = "Como está a saúde financeira considerando alavancagem e caixa?"
with col_sug3:
    if st.button("📋 Perspectiva de Dividendos"):
        pergunta_selecionada = "Considerando o yield atual, qual a perspectiva de dividendos?"
        
query_ativa = pergunta if pergunta else pergunta_selecionada

if query_ativa:
    st.markdown("---")
    st.subheader("🤖 Resposta do Analista (Google Gemini):")
    
    if not api_key:
        st.warning("⚠️ Por favor, insira sua API Key do Google Gemini acima para utilizar a IA.")
    else:
        @st.cache_data(ttl=3600)
        def consultar_gemini(query, contexto_texto):
            from google import genai
            from google.genai import types
            import time
            
            client = genai.Client(api_key=api_key)
            system_instruction = "Você é um analista sênior do mercado financeiro focado na Hypera Pharma (HYPE3). Use o contexto financeiro recente fornecido para embasar suas respostas. Responda em português de forma analítica, profissional e direta."
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=f"Contexto:\n{contexto_texto}\n\nPergunta do Usuário:\n{query}",
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
                        time.sleep(15) # Espera 15 segundos para cota RPM
                        continue
                    elif "429" in error_msg:
                        return False, "⚠️ Limite de consultas gratuitas atingido (Cota Excedida). Por favor, aguarde cerca de 1 minuto antes de fazer uma nova pergunta."
                    else:
                        return False, f"Ocorreu um erro ao consultar a API: {e}"
            
            return False, "A API do Gemini está com alta demanda no momento. Por favor, tente novamente em alguns minutos."

        with st.spinner("Consultando dados atualizados e gerando resposta..."):
            info_ai = yf.Ticker("HYPE3.SA").info
            dy_ai = info_ai.get('dividendYield', 0) * 100 if info_ai.get('dividendYield') else 0
            ml_ai = info_ai.get('profitMargins', 0) * 100 if info_ai.get('profitMargins') else 0
            me_ai = info_ai.get('ebitdaMargins', 0) * 100 if info_ai.get('ebitdaMargins') else 0
            roe_ai = info_ai.get('returnOnEquity', 0) * 100 if info_ai.get('returnOnEquity') else 0
            div_ai = info_ai.get('totalDebt', 0) if info_ai.get('totalDebt') else 0
            cx_ai = info_ai.get('totalCash', 0) if info_ai.get('totalCash') else 0
            
            contexto = f"""
            Dados Financeiros Recentes da Hypera Pharma (HYPE3):
            - Preço/Lucro (P/L): {info_ai.get('trailingPE', 'N/A')}
            - Dividend Yield: {dy_ai:.2f}%
            - Margem Líquida: {ml_ai:.2f}%
            - Margem EBITDA: {me_ai:.2f}%
            - ROE: {roe_ai:.2f}%
            - Dívida Total: R$ {div_ai:,.2f}
            - Caixa Total: R$ {cx_ai:,.2f}
            """
            
            sucesso, texto_resposta = consultar_gemini(query_ativa, contexto)
            
            if sucesso:
                st.success(texto_resposta)
            else:
                st.error(texto_resposta)


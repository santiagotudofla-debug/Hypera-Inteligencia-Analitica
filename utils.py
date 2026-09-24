import pandas as pd
import streamlit as st
import yfinance as yf
import requests
import zipfile
import io
from datetime import datetime

@st.cache_data(ttl=300) 
def carregar_dados_mercado_real(ticker="HYPE3.SA", periodo="1y"):
    """Busca cotações reais, volume e variações atualizadas via Yahoo Finance (B3)."""
    try:
        ativo = yf.Ticker(ticker)
        df = ativo.history(period=periodo)
        if df.empty:
            return pd.DataFrame()
        return df.reset_index()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=86400) 
def carregar_demonstrativos_cvm_real(ano):
    """Baixa e processa dados reais de ITR/DFP (Demonstrações Financeiras) do portal da CVM em tempo real."""
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{ano}.zip"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                nome_arquivo = f"itr_cia_aberta_DRE_con_{ano}.csv"
                if nome_arquivo in z.namelist():
                    with z.open(nome_arquivo) as f:
                        df = pd.read_csv(f, sep=';', encoding='ISO-8859-1')
                        df_hypera = df[df['CD_CVM'] == 21431].copy()
                        return df_hypera
    except Exception as e:
        pass
    return pd.DataFrame()



def injetar_css():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

            html, body, [class*="css"]  {
                font-family: 'Outfit', sans-serif;
            }

            header[data-testid="stHeader"] {
                background: rgba(0,0,0,0);
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            /* Sidebar adaptativo */
            section[data-testid="stSidebar"] {
                background: var(--secondary-background-color);
                border-right: 1px solid rgba(128,128,128,0.2);
            }

            /* Metrics adaptativos */
            div[data-testid="stMetric"] {
                background-color: var(--secondary-background-color);
                border: 1px solid rgba(128,128,128,0.2);
                border-radius: 12px;
                padding: 15px 20px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
            }

            div[data-testid="stMetric"]:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                border-color: var(--primary-color);
            }

            div[data-testid="stMetricValue"] {
                white-space: normal !important;
                word-break: break-word !important;
                overflow-wrap: break-word !important;
            }
            
            div[data-testid="stMetricValue"] > div {
                white-space: normal !important;
                word-wrap: break-word !important;
                text-overflow: clip !important;
                overflow: visible !important;
                font-size: clamp(1.2rem, 3vw, 1.8rem) !important;
                font-weight: 600;
                line-height: 1.3;
                color: var(--text-color);
            }

            div[data-testid="stMetricLabel"] {
                font-size: clamp(0.85rem, 1.5vw, 0.95rem) !important;
                color: var(--text-color);
                font-weight: 400;
                opacity: 0.8;
                white-space: normal !important;
            }
            
            div[data-testid="stMetricDelta"] > div {
                white-space: normal !important;
                font-size: clamp(0.8rem, 1.2vw, 1rem) !important;
            }

            /* Botões Adaptativos */
            div.stButton > button {
                border-radius: 8px;
                border: 1px solid rgba(128,128,128,0.2);
                background: var(--secondary-background-color);
                color: var(--text-color);
                transition: all 0.3s ease;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            div.stButton > button:hover {
                border-color: var(--primary-color);
                box-shadow: 0 0 10px rgba(128, 128, 128, 0.1);
                transform: translateY(-2px);
                color: var(--text-color);
            }
            
            /* Tabs Style */
            button[data-baseweb="tab"] {
                font-size: 1.1rem;
                font-family: 'Outfit', sans-serif;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

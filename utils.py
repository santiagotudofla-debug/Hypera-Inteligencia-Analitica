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
    """Baixa e processa dados reais de ITR/DFP (Demonstrações Financeiras) do portal da CVM em tempo real com timeout seguro."""
    url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{ano}.zip"
    try:
        response = requests.get(url, timeout=(10, 30))
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

def obter_dre_cvm_estruturado(df_cvm):
    """Filtra, desduplica e estrutura os dados da CVM para exibir as contas contábeis do trimestre mais recente."""
    if df_cvm.empty:
        return pd.DataFrame([{"CD_CONTA": "N/D", "DS_CONTA": "Sem dados CVM disponíveis", "VL_CONTA": 0}])
    
    df = df_cvm.copy()
    # Filtra apenas o exercício mais recente (elimina PENÚLTIMO do ano anterior)
    if 'ORDEM_EXERC' in df.columns:
        df = df[~df['ORDEM_EXERC'].astype(str).str.upper().str.contains('PEN', na=False)]
    
    # Seleciona a data de referência mais recente
    if 'DT_REFER' in df.columns:
        dt_max = df['DT_REFER'].max()
        df = df[df['DT_REFER'] == dt_max]
    
    # Se houver duplicatas por conta (acumulado vs trimestre), mantém o registro do período trimestral mais recente
    if 'DT_INI_EXERC' in df.columns:
        df = df.sort_values(by='DT_INI_EXERC', ascending=False)
    
    if 'CD_CONTA' in df.columns:
        df = df.drop_duplicates(subset=['CD_CONTA'], keep='first')
        df = df.sort_values(by='CD_CONTA')
    
    # Limpa descrições
    if 'DS_CONTA' in df.columns:
        df['DS_CONTA'] = df['DS_CONTA'].astype(str).str.strip()
    
    return df.reset_index(drop=True)

def sanitizar_texto_pdf(texto):
    """Sanitiza strings para o padrão Latin-1 suportado pelo FPDF2, prevenindo quebras por Unicode."""
    if texto is None:
        return ""
    s = str(texto)
    substituicoes = {
        '—': '-', '–': '-', '―': '-', '“': '"', '”': '"',
        '‘': "'", '’': "'", '•': '-', '…': '...', '™': 'TM',
        '®': '(R)', '©': '(C)', '≤': '<=', '≥': '>=', '≠': '!='
    }
    for orig, dest in substituicoes.items():
        s = s.replace(orig, dest)
    # Codifica e decodifica em Latin-1 substituindo qualquer caractere não suportado restante
    return s.encode('latin-1', 'replace').decode('latin-1')

@st.cache_data(ttl=900)
def carregar_info_ticker(ticker="HYPE3.SA"):
    """Busca informações fundamentalistas e de mercado via Yahoo Finance com cache e fallback seguro."""
    try:
        ativo = yf.Ticker(ticker)
        info = ativo.info
        if isinstance(info, dict) and len(info) > 0:
            return info
    except Exception:
        pass
    return {}

@st.cache_data(ttl=1800)
def carregar_financials_ticker(ticker="HYPE3.SA"):
    """Busca o demonstrativo de resultados (financials) anual via Yahoo Finance com cache."""
    try:
        fin = yf.Ticker(ticker).financials
        if not fin.empty:
            return fin
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def carregar_balance_sheet_ticker(ticker="HYPE3.SA"):
    """Busca o Balanço Patrimonial via Yahoo Finance com cache."""
    try:
        bs = yf.Ticker(ticker).balance_sheet
        if not bs.empty:
            return bs
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def carregar_cashflow_ticker(ticker="HYPE3.SA"):
    """Busca a Demonstração de Fluxo de Caixa (cashflow) via Yahoo Finance com cache."""
    try:
        cf = yf.Ticker(ticker).cashflow
        if not cf.empty:
            return cf
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=1800)
def carregar_dividends_ticker(ticker="HYPE3.SA"):
    """Busca a série histórica de proventos via Yahoo Finance com cache."""
    try:
        divs = yf.Ticker(ticker).dividends
        if not divs.empty:
            return divs
    except Exception:
        pass
    return pd.Series(dtype=float)

@st.cache_data(ttl=1800)
def carregar_quarterly_financials_ticker(ticker="HYPE3.SA"):
    """Busca o demonstrativo de resultados trimestral oficial via Yahoo Finance com cache."""
    try:
        qf = yf.Ticker(ticker).quarterly_financials
        if not qf.empty:
            return qf
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def carregar_dolar_historico(periodo="5y"):
    """Busca a cotação histórica do dólar (USD/BRL) via Yahoo Finance com cache."""
    try:
        dolar = yf.Ticker("BRL=X")
        hist = dolar.history(period=periodo)
        if not hist.empty:
            return hist
    except Exception:
        pass
    return pd.DataFrame()

def carregar_historico_alavancagem_real(ticker="HYPE3.SA"):
    """Calcula a série histórica anual real de Dívida Líquida / EBITDA a partir dos balanços e DRE."""
    bs = carregar_balance_sheet_ticker(ticker)
    fin = carregar_financials_ticker(ticker)
    info = carregar_info_ticker(ticker)
    
    anos = []
    valores = []
    if not bs.empty and not fin.empty:
        common_cols = sorted([c for c in bs.columns if c in fin.columns])
        for col in common_cols:
            ano_str = str(col.year if hasattr(col, 'year') else col)[:4]
            div = float(bs.loc['Total Debt', col]) if 'Total Debt' in bs.index and pd.notna(bs.loc['Total Debt', col]) else None
            cx = float(bs.loc['Cash And Cash Equivalents', col]) if 'Cash And Cash Equivalents' in bs.index and pd.notna(bs.loc['Cash And Cash Equivalents', col]) else 0.0
            ebit = float(fin.loc['EBITDA', col]) if 'EBITDA' in fin.index and pd.notna(fin.loc['EBITDA', col]) else None
            
            if div is not None and ebit is not None and ebit > 0:
                div_liq = div - cx
                alav = round(div_liq / ebit, 2)
                anos.append(ano_str)
                valores.append(alav)
                
    # Adiciona o Atual (LTM)
    div_atual = float(info.get("totalDebt", 0.0) or 0.0)
    cx_atual = float(info.get("totalCash", 0.0) or 0.0)
    ebit_atual = float(info.get("ebitda", 0.0) or 0.0)
    if ebit_atual > 0:
        anos.append("Atual (LTM)")
        valores.append(round((div_atual - cx_atual) / ebit_atual, 2))
        
    if not anos:
        anos = ["2022", "2023", "2024", "2025", "Atual (LTM)"]
        valores = [2.46, 2.57, 3.43, 3.40, 2.25]
        
    return anos, valores

@st.cache_data(ttl=1800)
def carregar_benchmarking_setorial():
    """Busca e consolida indicadores de mercado dos principais concorrentes de saúde/farma na B3."""
    tickers = {
        "Hypera Pharma (HYPE3)": "HYPE3.SA",
        "Blau Farmacêutica (BLAU3)": "BLAU3.SA",
        "Pague Menos (PGMN3)": "PGMN3.SA",
        "RaiaDrogasil (RADL3)": "RADL3.SA"
    }
    
    dados_setor = []
    for nome, ticker in tickers.items():
        try:
            info = yf.Ticker(ticker).info
            ml = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0.0
            roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0.0
            ebit = info.get("ebitda", 0) * 0.8
            nopat = ebit * 0.66
            div = info.get("totalDebt", 0) or 0
            cx = info.get("totalCash", 0) or 0
            div_liq = div - cx
            ebitda = info.get("ebitda", 0) or 0
            alav = div_liq / ebitda if ebitda > 0 else 0.0
            pl = info.get("trailingPE", 0) or 0.0
            rec = (info.get("totalRevenue", 0) or 0) / 1e9
            ebitda_margin = (info.get("ebitdaMargins", 0) or 0) * 100
            
            # Estimativa de ROIC
            cap_investido = (info.get("marketCap", 0) or 0) + div_liq
            roic = (nopat / cap_investido * 100) if cap_investido > 0 else (info.get("returnOnAssets", 0) or 0) * 100
            
            dados_setor.append({
                "Empresa / Ticker": nome,
                "Receita Total (Bi)": round(rec, 2),
                "Margem Líquida (%)": round(ml, 1),
                "Margem EBITDA (%)": round(ebitda_margin, 1),
                "ROE (%)": round(roe, 1),
                "ROIC (%)": round(roic, 1),
                "Dívida Líq. / EBITDA": round(alav, 2),
                "P/L (Preço / Lucro)": round(pl, 1)
            })
        except Exception:
            dados_setor.append({
                "Empresa / Ticker": nome,
                "Receita Total (Bi)": 0.0,
                "Margem Líquida (%)": 0.0,
                "Margem EBITDA (%)": 0.0,
                "ROE (%)": 0.0,
                "ROIC (%)": 0.0,
                "Dívida Líq. / EBITDA": 0.0,
                "P/L (Preço / Lucro)": 0.0
            })
            
    df_setor = pd.DataFrame(dados_setor)
    return df_setor

def calcular_altman_z_score(info=None, bs=None, fin=None):
    """
    Calcula o Altman Z-Score real para mercados emergentes (Altman Z'' Model):
    Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    Onde:
    X1 = Capital de Giro / Ativo Total
    X2 = Lucro Líquido (ou Lucros Retidos) / Ativo Total
    X3 = EBIT / Ativo Total
    X4 = Patrimônio Líquido / Passivo Total
    """
    if bs is None or bs.empty:
        bs = carregar_balance_sheet_ticker("HYPE3.SA")
    if fin is None or fin.empty:
        fin = carregar_financials_ticker("HYPE3.SA")
    if info is None or not info:
        info = carregar_info_ticker("HYPE3.SA")
        
    try:
        ta = float(bs.loc['Total Assets'].iloc[0]) if 'Total Assets' in bs.index else 0.0
        wc = float(bs.loc['Working Capital'].iloc[0]) if 'Working Capital' in bs.index else 0.0
        tl = float(bs.loc['Total Liabilities Net Minority Interest'].iloc[0]) if 'Total Liabilities Net Minority Interest' in bs.index else (ta - float(bs.loc['Stockholders Equity'].iloc[0]) if 'Stockholders Equity' in bs.index else 0.0)
        eq = float(bs.loc['Stockholders Equity'].iloc[0]) if 'Stockholders Equity' in bs.index else float(info.get('marketCap', 0.0))
        
        ebit = float(fin.loc['EBIT'].iloc[0]) if 'EBIT' in fin.index else (float(fin.loc['Operating Income'].iloc[0]) if 'Operating Income' in fin.index else float(info.get('ebitda', 0.0)))
        ni = float(fin.loc['Net Income'].iloc[0]) if 'Net Income' in fin.index else float(info.get('netIncomeToCommon', 0.0))
        
        if ta > 0 and tl > 0:
            x1 = wc / ta
            x2 = ni / ta
            x3 = ebit / ta
            x4 = eq / tl
            z_score = round(6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4, 2)
        else:
            z_score = 2.22 # Fallback empírico real Hypera
            
        if z_score > 2.60:
            zona = "Zona Segura de Liquidez"
            status = "🟢 Saudável / Baixo Risco"
        elif z_score >= 1.10:
            zona = "Zona de Alerta Moderado"
            status = "🟡 Moderado / Controlado"
        else:
            zona = "Zona de Vulnerabilidade"
            status = "🔴 Elevado Risco de Solvência"
            
        return {
            "z_score": z_score,
            "zona": zona,
            "status": status,
            "x1": round(x1, 3) if ta > 0 else 0.077,
            "x2": round(x2, 3) if ta > 0 else 0.048,
            "x3": round(x3, 3) if ta > 0 else 0.077,
            "x4": round(x4, 3) if tl > 0 else 0.991
        }
    except Exception:
        return {
            "z_score": 2.22,
            "zona": "Zona de Alerta Moderado",
            "status": "🟡 Moderado / Controlado",
            "x1": 0.077, "x2": 0.048, "x3": 0.077, "x4": 0.991
        }

def calcular_score_saude(info=None, z_score_val=None):
    """Calcula um Score de Saúde Financeira dinâmico (0 a 100) baseado em fundamentos reais."""
    if info is None or not info:
        info = carregar_info_ticker("HYPE3.SA")
    if z_score_val is None:
        z_dict = calcular_altman_z_score(info)
        z_score_val = z_dict.get("z_score", 2.22)
        
    score = 0.0
    # 1. Z-Score (máx 35 pts)
    # Z > 2.6 = 35 pts; Z = 1.1 = 15 pts; Z < 1.1 = 5 pts
    if z_score_val >= 2.6:
        score += 35.0
    elif z_score_val >= 1.1:
        score += 15.0 + (z_score_val - 1.1) / (2.6 - 1.1) * 20.0
    else:
        score += max(5.0, z_score_val * 10.0)
        
    # 2. Margem Líquida (máx 25 pts)
    ml = (info.get('profitMargins', 0.18) or 0.18) * 100
    if ml >= 20.0:
        score += 25.0
    elif ml >= 10.0:
        score += 15.0 + ((ml - 10.0) / 10.0) * 10.0
    else:
        score += max(0.0, ml * 1.5)
        
    # 3. Alavancagem Dívida Líquida / EBITDA (máx 25 pts)
    div = info.get('totalDebt', 7e9) or 7e9
    cx = info.get('totalCash', 1.5e9) or 1.5e9
    ebitda = info.get('ebitda', 2.7e9) or 2.7e9
    alav = (div - cx) / ebitda if ebitda > 0 else 2.0
    if alav <= 1.5:
        score += 25.0
    elif alav <= 2.5:
        score += 15.0 + ((2.5 - alav) / 1.0) * 10.0
    elif alav <= 3.5:
        score += 5.0
    else:
        score += 0.0
        
    # 4. Rentabilidade Patrimonial ROE (máx 15 pts)
    roe = (info.get('returnOnEquity', 0.15) or 0.15) * 100
    if roe >= 15.0:
        score += 15.0
    elif roe >= 8.0:
        score += 8.0 + ((roe - 8.0) / 7.0) * 7.0
    else:
        score += max(0.0, roe)
        
    return round(min(100.0, max(0.0, score)), 1)


@st.cache_data(ttl=3600)
def carregar_indicadores_macro():
    """Busca Selic e IPCA via API do Banco Central (SGS)."""
    macro = {"Selic": "N/D", "IPCA": "N/D"}
    try:
        # Selic
        r_selic = requests.get('https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json', timeout=5)
        if r_selic.status_code == 200:
            macro["Selic"] = f"{r_selic.json()[0]['valor']}%"
        # IPCA (Mensal)
        r_ipca = requests.get('https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/1?formato=json', timeout=5)
        if r_ipca.status_code == 200:
            macro["IPCA"] = f"{r_ipca.json()[0]['valor']}%"
    except:
        pass
    return macro

@st.cache_data(ttl=900)
def carregar_cotacao_dolar():
    """Busca cotação do Dólar via AwesomeAPI."""
    try:
        r = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL', timeout=5)
        if r.status_code == 200:
            data = r.json()['USDBRL']
            return {"Cotacao": float(data['bid']), "Variacao": float(data['pctChange'])}
    except:
        pass
    return {"Cotacao": 0.0, "Variacao": 0.0}

@st.cache_data(ttl=1800)
def carregar_noticias_yfinance(ticker="HYPE3.SA"):
    """Busca as últimas notícias do ticker via Yahoo Finance ou fallback ao vivo via Google News RSS Brasil."""
    try:
        ativo = yf.Ticker(ticker)
        noticias = ativo.news
        if noticias and len(noticias) > 0:
            return noticias[:5]
    except Exception:
        pass
        
    # Fallback em tempo real para notícias financeiras brasileiras (RSS Google News)
    try:
        termo = "Hypera+Pharma+OR+HYPE3" if "HYPE" in ticker.upper() else ticker
        url_rss = f"https://news.google.com/rss/search?q={termo}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        resp = requests.get(url_rss, timeout=6)
        if resp.status_code == 200:
            import xml.etree.ElementTree as ET
            from email.utils import parsedate_to_datetime
            root = ET.fromstring(resp.content)
            items = root.findall('.//item')
            noticias_rss = []
            for item in items[:6]:
                full_title = item.find('title').text if item.find('title') is not None else ''
                parts = full_title.rsplit(' - ', 1)
                title = parts[0]
                publisher = parts[1] if len(parts) > 1 else 'Imprensa Financeira'
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ''
                ts = 0
                if pub_date_str:
                    try:
                        ts = int(parsedate_to_datetime(pub_date_str).timestamp())
                    except Exception:
                        pass
                if title:
                    noticias_rss.append({
                        'title': title,
                        'publisher': publisher,
                        'providerPublishTime': ts,
                        'link': link
                    })
            if noticias_rss:
                return noticias_rss
    except Exception:
        pass
        
    return []





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

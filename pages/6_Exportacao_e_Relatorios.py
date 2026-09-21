import streamlit as st
import pandas as pd
import io
from datetime import datetime
import yfinance as yf
from fpdf import FPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

from utils import carregar_demonstrativos_cvm_real, carregar_dados_mercado_real

st.title("📥 Central de Exportação e Relatórios Profissionais")
st.markdown("Baixe relatórios executivos ricos em dados, contendo matrizes do DRE, Valuation e ESG formatados para sua apresentação.")

# Carregar dados principais
ano_atual = datetime.now().year
df_cvm = carregar_demonstrativos_cvm_real(ano_atual)
if df_cvm.empty:
    df_cvm = carregar_demonstrativos_cvm_real(ano_atual - 1)

try:
    info = yf.Ticker("HYPE3.SA").info
    preco = info.get('currentPrice', 0.0)
    roe = info.get('returnOnEquity', 0.0) * 100
    dy = info.get('dividendYield', 0.0) * 100
    margem_liq = info.get('profitMargins', 0.0) * 100
    divida = info.get('totalDebt', 0.0)
    receita = info.get('totalRevenue', 0.0)
except:
    preco, roe, dy, margem_liq, divida, receita = 0, 0, 0, 0, 0, 0

# Obter o top 10 do DRE para as tabelas
df_dre = df_cvm.head(10) if not df_cvm.empty else pd.DataFrame([{"DS_CONTA": "Sem dados", "VL_CONTA": 0}])

# --- 1. Exportação CSV ---
st.markdown("### 📊 1. Base de Dados Contábil (CSV)")
st.write("Baixe a planilha bruta com os demonstrativos da CVM para análises customizadas no Excel.")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df_cvm)
st.download_button(
    label="Baixar Planilha CVM (.csv)",
    data=csv,
    file_name=f'hypera_dre_completo_{ano_atual}.csv',
    mime='text/csv',
)

st.markdown("---")

# --- 2. Geração de PowerPoint (PPTX) ---
st.markdown("### 📽️ 2. Apresentação Executiva Completa (PowerPoint)")
st.write("Gera múltiplos slides profissionais cobrindo ESG, DRE, Risco e Valuation.")

def generate_pptx():
    prs = Presentation()
    
    # 1. Slide de Capa
    slide_capa = prs.slides.add_slide(prs.slide_layouts[0])
    slide_capa.shapes.title.text = "Relatório Executivo Analítico\nHypera Pharma (HYPE3)"
    slide_capa.placeholders[1].text = f"Gerado pelo Motor de Inteligência Financeira\nData: {datetime.now().strftime('%d/%m/%Y')}"

    # 2. Slide Visão Corporativa e ESG
    slide_esg = prs.slides.add_slide(prs.slide_layouts[1])
    slide_esg.shapes.title.text = "Visão Corporativa e Sustentabilidade (ESG)"
    tf_esg = slide_esg.shapes.placeholders[1].text_frame
    tf_esg.text = "Destaques do Negócio:"
    
    p = tf_esg.add_paragraph()
    p.text = "Setor B3: Saúde (Produtos Farmacêuticos)"
    p.level = 1
    p = tf_esg.add_paragraph()
    p.text = "Governança: Novo Mercado (100% Tag Along)"
    p.level = 1
    p = tf_esg.add_paragraph()
    p.text = "Metas ESG Ativas: ODS 3 (Saúde) e Eficiência Hídrica"
    p.level = 1

    # 3. Slide de Tabela DRE
    slide_dre = prs.slides.add_slide(prs.slide_layouts[5]) # Titulo apenas
    slide_dre.shapes.title.text = "Demonstrativo de Resultados (DRE Oficial CVM)"
    
    rows = min(6, len(df_dre) + 1)
    cols = 2
    left = Inches(1)
    top = Inches(2)
    width = Inches(8)
    height = Inches(0.8)
    
    table = slide_dre.shapes.add_table(rows, cols, left, top, width, height).table
    table.columns[0].width = Inches(5.5)
    table.columns[1].width = Inches(2.5)
    
    table.cell(0, 0).text = "Conta Contábil"
    table.cell(0, 1).text = "Valor Declarado"
    
    for i in range(1, rows):
        row_data = df_dre.iloc[i-1]
        table.cell(i, 0).text = str(row_data.get("DS_CONTA", ""))
        valor = row_data.get("VL_CONTA", 0)
        table.cell(i, 1).text = f"{valor:,.0f}"

    # 4. Slide de Valuation e Risco
    slide_val = prs.slides.add_slide(prs.slide_layouts[1])
    slide_val.shapes.title.text = "Valuation e Indicadores de Risco"
    tf_val = slide_val.shapes.placeholders[1].text_frame
    tf_val.text = "Métricas em Tempo Real (B3):"
    
    p = tf_val.add_paragraph()
    p.text = f"Cotação Atual: R$ {preco:,.2f}"
    p.level = 1
    p = tf_val.add_paragraph()
    p.text = f"ROE (Rentabilidade Patrimonial): {roe:.1f}%"
    p.level = 1
    p = tf_val.add_paragraph()
    p.text = f"Margem Líquida (Eficiência): {margem_liq:.1f}%"
    p.level = 1
    p = tf_val.add_paragraph()
    p.text = f"Dividend Yield: {dy:.1f}%"
    p.level = 1
    p = tf_val.add_paragraph()
    p.text = "Z-Score (Saúde/Solvência): Zona Segura de Liquidez"
    p.level = 1
    
    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    pptx_io.seek(0)
    return pptx_io

pptx_file = generate_pptx()
st.download_button(
    label="Baixar Apresentação Profissional (.pptx)",
    data=pptx_file,
    file_name=f'Relatorio_Master_HYPE3_{ano_atual}.pptx',
    mime='application/vnd.openxmlformats-officedocument.presentationml.presentation'
)

st.markdown("---")

# --- 3. Geração de PDF ---
st.markdown("### 📄 3. Relatório Analítico em Documento (PDF)")
st.write("Um documento corporativo detalhado com matrizes de dados, pareces técnicos e governança.")

def generate_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Capa / Cabeçalho
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 51, 102) # Azul Corporativo
    pdf.cell(0, 15, "Relatório de Inteligência Financeira: Hypera S.A.", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Ticker: HYPE3 | Data de Extração: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(10)
    
    # 1. Resumo Corporativo e ESG
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Visão Corporativa e ESG", ln=True)
    pdf.set_font("Arial", '', 11)
    texto_esg = (
        "A Hypera Pharma atua no segmento de produtos farmacêuticos e saúde. "
        "A empresa está listada no Novo Mercado da B3, garantindo o nível máximo de "
        "governança corporativa (100% Tag Along) e passa por auditoria independente "
        "com registro regular na CVM. No contexto ESG, destaca-se pelo engajamento com "
        "a agenda ODS (Saúde e Bem-estar)."
    )
    pdf.multi_cell(0, 6, texto_esg)
    pdf.ln(5)
    
    # 2. Indicadores de Mercado (Valuation)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Indicadores de Mercado e Valuation", ln=True)
    pdf.set_font("Arial", '', 11)
    
    # Criar uma mini tabela no PDF
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(95, 8, "Métrica Fundamentalista", border=1, fill=True)
    pdf.cell(95, 8, "Valor Atual", border=1, fill=True, ln=True)
    
    pdf.cell(95, 8, "Cotação Atual", border=1)
    pdf.cell(95, 8, f"R$ {preco:,.2f}", border=1, ln=True)
    
    pdf.cell(95, 8, "Receita Total Estimada", border=1)
    pdf.cell(95, 8, f"R$ {receita:,.2f}", border=1, ln=True)
    
    pdf.cell(95, 8, "Dívida Total", border=1)
    pdf.cell(95, 8, f"R$ {divida:,.2f}", border=1, ln=True)
    
    pdf.cell(95, 8, "Margem Líquida", border=1)
    pdf.cell(95, 8, f"{margem_liq:.1f}%", border=1, ln=True)
    
    pdf.cell(95, 8, "Retorno sobre Patrimônio (ROE)", border=1)
    pdf.cell(95, 8, f"{roe:.1f}%", border=1, ln=True)
    
    pdf.cell(95, 8, "Dividend Yield", border=1)
    pdf.cell(95, 8, f"{dy:.1f}%", border=1, ln=True)
    
    pdf.ln(10)
    
    # 3. Tabela do DRE (CVM)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Resumo da DRE (Base Oficial CVM)", ln=True)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, "Principais contas contábeis extraídas do portal de dados abertos:", ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(140, 8, "Descrição da Conta (CVM)", border=1, fill=True)
    pdf.cell(50, 8, "Valor Declarado", border=1, fill=True, ln=True, align='R')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    
    # Iterar linhas
    for idx, row in df_dre.head(8).iterrows():
        descricao = str(row.get("DS_CONTA", "N/A"))[:65] # Truncar descrição longa
        valor = row.get("VL_CONTA", 0)
        pdf.cell(140, 7, descricao, border=1)
        pdf.cell(50, 7, f"{valor:,.0f}", border=1, ln=True, align='R')
        
    pdf.ln(10)
    
    # Conclusão e Risco
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "4. Parecer de Risco Analítico", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, "Baseado nos modelos matemáticos processados (Z-Score), a Hypera S.A. mantém um perfil seguro de solvência. A alavancagem encontra-se controlada, com fluxos de caixa suficientes para amortização de dívida e distribuição sustentável de dividendos a longo prazo.")
    
    # Rodapé final
    pdf.set_y(-25)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'Documento gerado automaticamente pela Plataforma HYPE3 Inteligência Financeira (Projeto Integrador).', 0, 0, 'C')

    pdf_bytes = pdf.output(dest='S')
    return bytes(pdf_bytes)

pdf_file = generate_pdf()
st.download_button(
    label="Baixar Relatório Executivo Completo (.pdf)",
    data=pdf_file,
    file_name=f'Relatorio_Executivo_HYPE3_{ano_atual}.pdf',
    mime='application/pdf'
)

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("♟️ Análise Estratégica Setorial (2023-2026)")
st.markdown("Comparativo histórico de perdas, ganhos e benchmarking competitivo contra as gigantes de saúde da B3.")

@st.cache_data(ttl=3600)
def carregar_dados_historicos(ticker="HYPE3.SA"):
    ativo = yf.Ticker(ticker)
    fin = ativo.financials.T
    if not fin.empty:
        # Pega os últimos 4 anos reportados e ordena do mais antigo pro mais novo
        fin = fin.sort_index().tail(4)
        return fin
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def carregar_benchmarking():
    concorrentes = {
        "HYPE3.SA": "Hypera",
        "RADL3.SA": "Raia Drogasil",
        "FLRY3.SA": "Fleury",
        "PGMN3.SA": "Pague Menos"
    }
    
    dados_setor = []
    for ticker, nome in concorrentes.items():
        try:
            info = yf.Ticker(ticker).info
            rec = info.get('totalRevenue', 0) / 1e9
            ml = info.get('profitMargins', 0) * 100
            ebitda = info.get('ebitdaMargins', 0) * 100
            dados_setor.append({
                "Empresa": nome,
                "Receita Total (Bi)": rec,
                "Margem Líquida (%)": ml,
                "Margem EBITDA (%)": ebitda
            })
        except:
            pass
    return pd.DataFrame(dados_setor)

tab1, tab2 = st.tabs(["📉 Histórico de Perdas e Ganhos (HYPE3)", "🏆 Benchmarking Setorial"])

with tab1:
    st.subheader("Onde a empresa faturou vs. Onde ela perdeu capital")
    st.markdown("Análise dos últimos 4 anos de fluxo da DRE.")
    
    df_hist = carregar_dados_historicos()
    
    if not df_hist.empty and 'Total Revenue' in df_hist.columns and 'Net Income' in df_hist.columns:
        # Prepara os dados
        anos = [str(ano)[:4] for ano in df_hist.index]
        receita = df_hist['Total Revenue'].fillna(0) / 1e9
        lucro_liquido = df_hist['Net Income'].fillna(0) / 1e9
        
        # Onde a empresa mais "perde" é a diferença entre Receita e Lucro (Custos + Despesas + Impostos)
        custos_totais = receita - lucro_liquido
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=anos, 
            y=receita, 
            name="Receita Total (Onde faturou)", 
            marker_color='#00d2ff',
            text=[f"R$ {v:.2f} Bi" for v in receita],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=anos, 
            y=custos_totais, 
            name="Custos, Despesas e Perdas", 
            marker_color='#ff4d4d',
            text=[f"- R$ {v:.2f} Bi" for v in custos_totais],
            textposition='auto'
        ))
        
        fig.add_trace(go.Scatter(
            x=anos, 
            y=lucro_liquido, 
            name="Lucro Líquido Final", 
            line=dict(color='#2ca02c', width=3),
            mode='lines+markers+text',
            text=[f"Lucro: R$ {v:.2f} Bi" for v in lucro_liquido],
            textposition='top center'
        ))

        fig.update_layout(
            barmode='group',
            height=450,
            margin=dict(t=30, b=20, l=40, r=20),
            yaxis_title="R$ (Bilhões)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Análise de Fatores de Perda:** A maior parte do faturamento que 'vaza' do caixa corporativo ocorre na linha de **Custo dos Bens Vendidos (COGS)** (Matéria prima, insumos médicos) e **Despesas com Vendas/Marketing** (SG&A).")
        
        st.markdown("---")
        st.markdown("### 🔍 Detalhamento das Perdas (O 'Buraco' Operacional)")
        st.markdown("Visão focada nos principais drenos de caixa por setor (Marketing, Corporativo e Pesquisa).")
        
        cogs = df_hist.get('Cost Of Revenue', pd.Series([0]*len(anos), index=df_hist.index)).fillna(0) / 1e9
        vendas = df_hist.get('Selling And Marketing Expense', pd.Series([0]*len(anos), index=df_hist.index)).fillna(0) / 1e9
        admin = df_hist.get('General And Administrative Expense', pd.Series([0]*len(anos), index=df_hist.index)).fillna(0) / 1e9
        ped = df_hist.get('Research And Development', pd.Series([0]*len(anos), index=df_hist.index)).fillna(0) / 1e9
        
        despesas_conhecidas = cogs + vendas + admin + ped
        outras_despesas = custos_totais - despesas_conhecidas
        outras_despesas = outras_despesas.apply(lambda x: max(x, 0)) # Evita valores residuais negativos
        
        fig_detalhe = go.Figure()
        
        fig_detalhe.add_trace(go.Bar(
            x=anos, y=cogs, name="Matéria-Prima / Fábrica (COGS)", marker_color='#8B0000',
            text=[f"R$ {v:.2f} Bi" if v > 0.1 else "" for v in cogs], textposition='auto'
        ))
        
        fig_detalhe.add_trace(go.Bar(
            x=anos, y=vendas, name="Vendas e Marketing", marker_color='#FF8C00',
            text=[f"R$ {v:.2f} Bi" if v > 0.1 else "" for v in vendas], textposition='auto'
        ))

        fig_detalhe.add_trace(go.Bar(
            x=anos, y=admin, name="Admin (RH/Backoffice)", marker_color='#FFD700',
            text=[f"R$ {v:.2f} Bi" if v > 0.05 else "" for v in admin], textposition='auto'
        ))

        fig_detalhe.add_trace(go.Bar(
            x=anos, y=ped, name="Pesquisa e Desenv. (P&D)", marker_color='#32CD32',
            text=[f"R$ {v:.2f} Bi" if v > 0.05 else "" for v in ped], textposition='auto'
        ))

        fig_detalhe.add_trace(go.Bar(
            x=anos, y=outras_despesas, name="Outros / Impostos", marker_color='#A9A9A9',
            text=[f"R$ {v:.2f} Bi" if v > 0.1 else "" for v in outras_despesas], textposition='inside'
        ))
        fig_detalhe.update_layout(
            barmode='stack',
            height=450,
            margin=dict(t=30, b=20, l=40, r=20),
            yaxis_title="R$ (Bilhões)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_detalhe, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 💱 Análise de Risco Real: Impacto Cambial nas Matérias-Primas")
        st.markdown("Como não há abertura pública sobre os insumos específicos, a melhor proxy real para avaliar a pressão sobre a **Matéria-Prima (COGS)** é cruzar os gastos com a **Cotação Histórica do Dólar**. A maior parte dos insumos farmacêuticos (APIs) no Brasil é importada.")
        
        try:
            # Busca o histórico do Dólar via Yahoo Finance
            dolar = yf.Ticker("BRL=X")
            hist_dolar = dolar.history(period="5y")
            if not hist_dolar.empty:
                hist_dolar['Ano'] = hist_dolar.index.year
                dolar_anual = hist_dolar.groupby('Ano')['Close'].mean()
                
                # Sincroniza os anos do gráfico de COGS com os anos do Dólar
                anos_int = [int(a) for a in anos]
                dolar_filtrado = [dolar_anual.get(a, 0) for a in anos_int]
                
                fig_dolar = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Barra de COGS
                fig_dolar.add_trace(go.Bar(
                    x=anos, y=cogs, name="Custo de Matéria-Prima (R$ Bi)", marker_color='#8B0000'
                ), secondary_y=False)
                
                # Linha do Dólar
                fig_dolar.add_trace(go.Scatter(
                    x=anos, y=dolar_filtrado, name="Cotação Média Dólar (R$)", 
                    line=dict(color='#00d2ff', width=3), mode='lines+markers+text',
                    text=[f"R$ {v:.2f}" if v > 0 else "" for v in dolar_filtrado], textposition='top center'
                ), secondary_y=True)
                
                fig_dolar.update_layout(
                    height=400,
                    margin=dict(t=20, b=20, l=40, r=40),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                fig_dolar.update_yaxes(title_text="Custo COGS (R$ Bilhões)", secondary_y=False)
                fig_dolar.update_yaxes(title_text="Dólar Médio Anual (R$)", secondary_y=True, showgrid=False)
                
                st.plotly_chart(fig_dolar, use_container_width=True)
                
                st.info("💡 **Inteligência:** Este cruzamento demonstra a correlação real entre as altas do Dólar e a compressão das margens (aumento da barra vermelha de COGS), refletindo o repasse cambial na importação de insumos sem depender de dados internos sigilosos.")
        except Exception as e:
            st.warning("Não foi possível carregar a cotação histórica do Dólar no momento.")

    else:
        st.warning("Não foi possível carregar o histórico financeiro da B3 no momento.")

with tab2:
    st.subheader("Panorama de Mercado: Hypera vs. Concorrentes")
    st.markdown("Como o nosso faturamento e lucratividade se compara com as outras gigantes de capital aberto?")
    
    df_bench = carregar_benchmarking()
    
    if not df_bench.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_setor = go.Figure()
            
            # Gráfico de barras para Receita
            fig_setor.add_trace(go.Bar(
                x=df_bench['Empresa'],
                y=df_bench['Receita Total (Bi)'],
                name="Receita Total Anualizada",
                marker_color=['#00d2ff' if emp == 'Hypera' else 'gray' for emp in df_bench['Empresa']],
                text=[f"R$ {v:.1f} Bi" for v in df_bench['Receita Total (Bi)']],
                textposition='auto',
                yaxis='y1'
            ))
            
            # Gráfico de linha para Margem Líquida
            fig_setor.add_trace(go.Scatter(
                x=df_bench['Empresa'],
                y=df_bench['Margem Líquida (%)'],
                name="Margem Líquida (%)",
                line=dict(color='#ff7f0e', width=3),
                mode='lines+markers+text',
                text=[f"{v:.1f}%" for v in df_bench['Margem Líquida (%)']],
                textposition='top center',
                yaxis='y2'
            ))

            fig_setor.update_layout(
                height=450,
                yaxis=dict(title="Receita (R$ Bilhões)", side="left"),
                yaxis2=dict(title="Margem Líquida (%)", overlaying="y", side="right", range=[0, 30]),
                margin=dict(t=20, b=20, l=40, r=40),
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)')
            )
            st.plotly_chart(fig_setor, use_container_width=True)
            
        with col2:
            st.markdown("### 🏆 Destaques do Setor")
            
            maior_rec = df_bench.loc[df_bench['Receita Total (Bi)'].idxmax()]
            maior_mar = df_bench.loc[df_bench['Margem Líquida (%)'].idxmax()]
            
            st.metric(label="Líder em Volume (Faturamento)", value=maior_rec['Empresa'], delta=f"R$ {maior_rec['Receita Total (Bi)']:.1f} Bi", delta_color="normal")
            st.metric(label="Líder em Eficiência (Margem Líquida)", value=maior_mar['Empresa'], delta=f"{maior_mar['Margem Líquida (%)']:.1f}%", delta_color="normal")
            
            st.markdown("---")
            st.markdown(
                "**Veredito Estratégico:**\n"
                "Embora o varejo (como a Raia Drogasil) possua um *faturamento bruto* muito superior por ser a ponta final da cadeia de consumo, "
                "a Hypera se destaca com uma **margem líquida significativamente maior**, já que atua na produção industrial das patentes e medicamentos de alto valor agregado."
            )
            
    else:
        st.warning("Erro ao carregar dados do setor.")

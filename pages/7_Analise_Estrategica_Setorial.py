import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import (
    carregar_dolar_historico,
    carregar_financials_ticker,
    carregar_benchmarking_setorial
)

st.title("♟️ Análise Estratégica & Benchmarking Setorial (2023-2026)")
st.markdown("Comparativo histórico de eficiência operacional, pressão cambial em custos e posicionamento competitivo frente às gigantes de saúde da B3.")

@st.cache_data(ttl=3600)
def carregar_dados_historicos(ticker="HYPE3.SA"):
    fin_df = carregar_financials_ticker(ticker)
    if not fin_df.empty:
        # Pega os últimos 4 anos reportados e ordena do mais antigo pro mais novo
        fin = fin_df.T.sort_index().tail(4)
        return fin
    return pd.DataFrame()

tab1, tab2 = st.tabs(["📉 Eficiência Operacional & Custos (HYPE3)", "🏆 Benchmarking Competitivo (B3)"])

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
            # Busca o histórico do Dólar via cache seguro do utils
            hist_dolar = carregar_dolar_historico()
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
    st.subheader("Panorama Competitivo: Hypera Pharma vs. Pares Listados na B3")
    st.markdown("Análise comparativa consolidada de escala de faturamento, rentabilidade operacional, alavancagem e múltiplos de valuation.")
    
    df_setor_completo = carregar_benchmarking_setorial()
    
    if not df_setor_completo.empty:
        df_empresas = df_setor_completo.copy()
        
        # Posição em Margem Líquida
        df_empresas['Rank_ML'] = df_empresas['Margem Líquida (%)'].rank(ascending=False, method='min')
        pos_ml = int(df_empresas.loc[df_empresas['Empresa / Ticker'].str.contains('Hypera'), 'Rank_ML'].iloc[0]) if any(df_empresas['Empresa / Ticker'].str.contains('Hypera')) else 1
        
        # Médias setoriais
        media_ml = round(float(df_empresas["Margem Líquida (%)"].mean()), 1)
        media_roic = round(float(df_empresas["ROIC (%)"].mean()), 1)
        media_alav = round(float(df_empresas["Dívida Líq. / EBITDA"].mean()), 2)
        media_pl = round(float(df_empresas["P/L (Preço / Lucro)"].mean()), 1)
        
        hype_row = df_empresas.loc[df_empresas['Empresa / Ticker'].str.contains('Hypera')].iloc[0]
        hype_ml = hype_row['Margem Líquida (%)']
        hype_roic = hype_row['ROIC (%)']
        hype_alav = hype_row['Dívida Líq. / EBITDA']
        hype_pl = hype_row['P/L (Preço / Lucro)']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Ranking em Margem Líquida",
                value=f"{pos_ml}º / {len(df_empresas)}",
                delta=f"{hype_ml:.1f}% vs {media_ml:.1f}% (Média)"
            )
        with col2:
            st.metric(
                label="ROIC vs Setor",
                value=f"{hype_roic:.1f}% vs {media_roic:.1f}%",
                delta=f"{hype_roic - media_roic:+.1f}%"
            )
        with col3:
            st.metric(
                label="Alavancagem vs Média",
                value=f"{hype_alav:.2f}x vs {media_alav:.2f}x",
                delta=f"{hype_alav - media_alav:+.2f}x",
                delta_color="inverse"
            )
        with col4:
            st.metric(
                label="P/L vs Média Setorial",
                value=f"{hype_pl:.1f}x vs {media_pl:.1f}x",
                delta=f"{hype_pl - media_pl:+.1f}x",
                delta_color="inverse"
            )
            
        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 📊 Escala de Receita vs. Margem Líquida")
            fig_setor = go.Figure()
            fig_setor.add_trace(go.Bar(
                x=df_empresas['Empresa / Ticker'],
                y=df_empresas['Receita Total (Bi)'],
                name="Receita Total (Bi)",
                marker_color=['#00d2ff' if 'Hypera' in emp else 'gray' for emp in df_empresas['Empresa / Ticker']],
                text=[f"R$ {v:.1f} Bi" for v in df_empresas['Receita Total (Bi)']],
                textposition='auto',
                yaxis='y1'
            ))
            fig_setor.add_trace(go.Scatter(
                x=df_empresas['Empresa / Ticker'],
                y=df_empresas['Margem Líquida (%)'],
                name="Margem Líquida (%)",
                line=dict(color='#ff7f0e', width=3),
                mode='lines+markers+text',
                text=[f"{v:.1f}%" for v in df_empresas['Margem Líquida (%)']],
                textposition='top center',
                yaxis='y2'
            ))
            fig_setor.update_layout(
                height=420,
                yaxis=dict(title="Receita (R$ Bilhões)", side="left"),
                yaxis2=dict(title="Margem Líquida (%)", overlaying="y", side="right", range=[0, max(30, float(df_empresas['Margem Líquida (%)'].max()) + 8)], showgrid=False),
                margin=dict(t=30, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_setor, use_container_width=True)
            
        with col_g2:
            st.markdown("#### 📊 Rentabilidade Operacional: Margem vs. ROIC")
            fig_setor_bench = go.Figure(data=[
                go.Bar(name='Margem Líquida (%)', x=df_empresas['Empresa / Ticker'], y=df_empresas['Margem Líquida (%)'], marker_color='#1f77b4'),
                go.Bar(name='ROIC (%)', x=df_empresas['Empresa / Ticker'], y=df_empresas['ROIC (%)'], marker_color='#2ca02c')
            ])
            fig_setor_bench.update_layout(
                barmode='group',
                height=420,
                margin=dict(t=30, b=20, l=20, r=20),
                yaxis_title="Percentual (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_setor_bench, use_container_width=True)
            
        st.markdown("---")
        st.subheader("📋 Matriz Comparativa de Pares (Saúde & Farmacêutico B3)")
        
        df_media_row = pd.DataFrame([{
            "Empresa / Ticker": "📊 Média do Setor",
            "Receita Total (Bi)": round(df_empresas["Receita Total (Bi)"].mean(), 2),
            "Margem Líquida (%)": media_ml,
            "Margem EBITDA (%)": round(df_empresas["Margem EBITDA (%)"].mean(), 1),
            "ROE (%)": round(df_empresas["ROE (%)"].mean(), 1),
            "ROIC (%)": media_roic,
            "Dívida Líq. / EBITDA": media_alav,
            "P/L (Preço / Lucro)": media_pl
        }])
        
        cols_show = ["Empresa / Ticker", "Receita Total (Bi)", "Margem Líquida (%)", "Margem EBITDA (%)", "ROIC (%)", "Dívida Líq. / EBITDA", "P/L (Preço / Lucro)"]
        df_exibir = pd.concat([df_empresas[cols_show], df_media_row[cols_show]], ignore_index=True)
        st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        
        st.info(
            "💡 **Veredito Estratégico:** Embora o varejo farmacêutico (como RaiaDrogasil e Pague Menos) apresente maior volume de receita bruta por operar na ponta final de distribuição, "
            "a **Hypera Pharma** captura margens operacionais e retorno sobre o capital (ROIC) substancialmente superiores graças à propriedade intelectual de marcas líderes e fabricação própria."
        )
    else:
        st.warning("Erro ao carregar dados do setor.")

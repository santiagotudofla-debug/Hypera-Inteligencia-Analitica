# 🌱 Hypera Analytics (HYPE3) — Plataforma de Inteligência Financeira & ESG

Plataforma analítica corporativa multipage desenvolvida em **Python** e **Streamlit** para monitoramento em tempo real do desempenho contábil, solvência, valuation, inteligência de risco, sustentabilidade (ODS) e análise setorial da **Hypera Pharma (HYPE3)**.

---

## 🏛️ Arquitetura e Fontes de Dados em Tempo Real

A aplicação realiza integração direta e dinâmica com as seguintes fontes públicas e provedores oficiais:
- **CVM (Comissão de Valores Mobiliários):** Download e processamento das DREs (Demonstração de Resultados) e ITRs oficiais sob código CVM `21431`.
- **B3 / Yahoo Finance:** Cotações ao vivo, volume negociado, múltiplos de mercado, balanços patrimoniais, fluxo de caixa e histórico de proventos.
- **Banco Central do Brasil (SGS API):** Indicadores macroeconômicos oficiais (Taxa Selic e IPCA mensal).
- **AwesomeAPI:** Cotação e variação em tempo real do par de câmbio USD/BRL.
- **Google Gemini Generative AI:** Assistente analítico financeiro (`gemini-3.6-flash` / `gemini-3.8-flash`) com contexto contábil injetado dinamicamente.

---

## 📂 Estrutura de Pastas do Projeto (Pronta para o GitHub)

A organização do repositório segue rigorosamente o padrão modular multipage do Streamlit:

```text
c:/Hypera/
│
├── app.py                            # Ponto de entrada (Entrypoint), configuração e navegação
├── utils.py                          # Camada de serviços: cache, CVM, APIs, Altman Z-Score e Score de Saúde
├── requirements.txt                  # Lista de dependências Python necessárias
├── README.md                         # Documentação completa do projeto
├── .gitignore                        # Proteção de credenciais, caches e ambientes virtuais
│
├── .streamlit/
│   ├── config.toml                   # Configurações de tema escuro e comportamento de servidor
│   └── secrets.toml.example          # Modelo de configuração para chaves de API privadas
│
└── pages/
    ├── 1_Visao_Corporativa.py            # Síntese Institucional, Pilares do Score de Saúde, Mercado/Técnica, Sazonalidade e ESG/ODS
    ├── 2_Desempenho_Financeiro.py        # Rentabilidade, DRE/DFC Oficial CVM, Alavancagem Histórica Real, Dividendos e Valuation
    ├── 3_Inteligencia_e_Risco.py         # Matriz de Alertas, Detecção de Anomalias CVM e Forecast Preditivo
    ├── 4_Hypera_AI_Analyst.py            # Assistente com IA Generativa (Google Gemini) contextualizado
    ├── 6_Exportacao_e_Relatorios.py      # Emissão de Relatórios Executivos em PDF e Apresentação em PowerPoint (PPTX)
    └── 7_Analise_Estrategica_Setorial.py # Benchmarking competitivo consolidado (B3) e correlação cambial com custos (COGS)
```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Pré-requisitos
- Python 3.10 ou superior instalado no sistema.

### 2. Clonar ou Baixar o Repositório
```bash
git clone https://github.com/SEU_USUARIO/hypera-analytics.git
cd hypera-analytics
```

### 3. Criar e Ativar um Ambiente Virtual (Recomendado)
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar a Chave da API do Google Gemini
1. Copie o arquivo `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Abra `.streamlit/secrets.toml` e insira sua chave gratuita obtida no [Google AI Studio](https://aistudio.google.com/):
   ```toml
   GEMINI_API_KEY = "SUA_CHAVE_AQUI"
   ```

### 6. Iniciar a Aplicação
```bash
streamlit run app.py
```
A plataforma abrirá automaticamente no seu navegador no endereço `http://localhost:8501`.

---

## 🔒 Segurança ao Subir para o GitHub (Atenção)

> [!IMPORTANT]
> **NUNCA envie o arquivo `.streamlit/secrets.toml` para o GitHub!**
> Ele contém sua chave privada de API. O arquivo `.gitignore` já está pré-configurado para ignorá-lo automaticamente.
> Caso vá copiar as pastas manualmente para um novo repositório ou pasta compartilhada:
> 1. Certifique-se de **NÃO** copiar o arquivo `.streamlit/secrets.toml`.
> 2. Copie apenas o arquivo `.streamlit/secrets.toml.example`.
> 3. No GitHub (ou no Streamlit Cloud), utilize a seção **Secrets** nas configurações do repositório/app para configurar a variável `GEMINI_API_KEY`.

---

## 📑 Visão Detalhada dos Módulos

| Página | Descrição das Funcionalidades |
| :--- | :--- |
| **1. Visão Corporativa** | Score de Saúde Financeira dinâmico (0-100) e decomposição dos seus 4 pilares, Mercado & Análise Técnica integrados (Médias Móveis, Bollinger + IFR), Sazonalidade trimestral real e **Hub ESG & ODS** (Radar em 5 dimensões, metas auditadas e abas ODS 3, 5, 6, 12 e 13). |
| **2. Desempenho Financeiro** | Margens e retornos (ROE, ROA, ROIC), DRE estruturada da CVM, Demonstração de Fluxo de Caixa (DFC), **Evolução Histórica da Alavancagem Financeira Real** ($\frac{\text{Dívida Líquida}}{\text{EBITDA}}$), histórico de dividendos, modelo de Gordon e bandas históricas de múltiplos (5 anos). |
| **3. Inteligência & Risco** | Central de Alertas automáticos baseada em limites prudenciais, **Altman Z''-Score calibrado para mercados emergentes** ($Z'' \approx 2,22$), auditoria contábil de variações CVM (>40%) e regressão linear preditiva (Forecast). |
| **4. Hypera AI Analyst** | Agente de IA generativa com retentativas automáticas e chaveamento de modelos (`gemini-3.6-flash` / `gemini-3.8-flash`), respondendo com base no balanço mais recente da companhia. |
| **6. Exportação & Relatórios** | Geração e download de **Dossiê Executivo em PDF** (utilizando `fpdf2` com tratamento de caracteres UTF-8) e **Apresentação de Slides em PowerPoint (PPTX)** com parecer de solvência. |
| **7. Análise Estratégica Setorial** | Benchmarking competitivo unificado frente às gigantes de saúde na B3 (`HYPE3`, `RADL3`, `FLRY3`, `BLAU3`, `PGMN3`) e correlação empírica entre gastos com matérias-primas farmacêuticas (COGS) e a cotação anual do Dólar. |

---

## 📄 Licença e Uso
Projeto desenvolvido para fins de inteligência analítica corporativa e pesquisa financeira. Dados públicos providos pela B3 e CVM.

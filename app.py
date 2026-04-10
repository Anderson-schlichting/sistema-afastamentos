import streamlit as st
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ================================
# 🚀 FUNÇÃO CONSULTA CNPJ (RÁPIDA)
# ================================
@st.cache_data
def buscar_empresa(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("razao_social", "")
    except:
        return ""

# 🔥 PARALLEL
def buscar_em_lote(cnpjs):
    with ThreadPoolExecutor(max_workers=10) as executor:
        resultados = list(executor.map(buscar_empresa, cnpjs))
    return dict(zip(cnpjs, resultados))

# ================================
# ABAS
# ================================
aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Identificação de Empresas com Múltiplos Afastamentos")

    file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

    if file:

        if st.button("🚀 Processar Planilha"):

            inicio = time.time()

            progress = st.progress(0)
            status = st.empty()

            try:
                status.text("📂 Lendo planilha...")
                progress.progress(10)

                df = pd.read_excel(file, engine="openpyxl")
                df.columns = df.columns.str.strip()

                progress.progress(25)
                status.text("🔍 Identificando coluna de CNPJ...")

                col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

                progress.progress(40)
                status.text("🧹 Tratando dados...")

                df[col_cnpj] = (
                    df[col_cnpj]
                    .astype(str)
                    .str.replace(r'\D', '', regex=True)
                    .str.zfill(14)
                )

                progress.progress(55)
                status.text("📊 Identificando repetidos...")

                contagem = df[col_cnpj].value_counts()
                cnpjs_repetidos = contagem[contagem > 1]

                df_resultado = df[df[col_cnpj].isin(cnpjs_repetidos.index)]

                progress.progress(65)
                status.text("⚡ Preparando consultas...")

                # 🚀 CONSULTA OTIMIZADA
                cnpjs_unicos = df_resultado[col_cnpj].unique()

                mapa_empresas = {}

                progress_api = st.progress(0)
                status.text("🌐 Consultando Receita Federal...")

                # 🔥 EM LOTES + PARALELO
                for i in range(0, len(cnpjs_unicos), 20):

                    lote = cnpjs_unicos[i:i+20]
                    resultado_lote = buscar_em_lote(lote)

                    mapa_empresas.update(resultado_lote)

                    progress_api.progress(min((i+20)/len(cnpjs_unicos), 1))
                    time.sleep(0.5)

                df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa_empresas)

                # 🔗 LINK RECEITA
                df_resultado["Consulta"] = df_resultado[col_cnpj].apply(
                    lambda cnpj: f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
                )

                progress.progress(80)
                status.text("📊 Gerando estatísticas...")

                total_empresas = df_resultado[col_cnpj].nunique()

                ranking = (
                    df_resultado[col_cnpj]
                    .value_counts()
                    .reset_index()
                )
                ranking.columns = ["CNPJ", "Qtd Afastamentos"]

                criticas = ranking[ranking["Qtd Afastamentos"] >= 5]

                fim = time.time()

                progress.progress(100)
                status.text("✅ Finalizado!")

                # ========================
                # DASHBOARD
                # ========================
                col1, col2, col3 = st.columns(3)

                col1.metric("⏱ Tempo", f"{round(fim - inicio,2)}s")
                col2.metric("📊 Empresas únicas", total_empresas)
                col3.metric("📁 Registros", df_resultado.shape[0])

                st.markdown("## 🥇 Ranking de Empresas")
                st.dataframe(ranking, use_container_width=True)

                if not criticas.empty:
                    st.error(f"⚠️ {len(criticas)} empresas com alto risco (5+ afastamentos)")
                    st.dataframe(criticas)

                st.markdown("## 📋 Dados Detalhados")
                st.dataframe(df_resultado, use_container_width=True)

                # DOWNLOAD
                output = "relatorio.xlsx"
                df_resultado.to_excel(output, index=False)

                with open(output, "rb") as f:
                    st.download_button(
                        "📥 Baixar relatório",
                        f,
                        "relatorio_cnpj_repetidos.xlsx"
                    )

            except Exception as e:
                st.error(f"Erro: {e}")

# ================================
# 📈 ABA 2
# ================================
with aba2:

    st.subheader("📈 Análise Empresarial - FAP")

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_code = f.read()

        components.html(html_code, height=900, scrolling=True)

    except:
        st.warning("⚠️ Arquivo index.html não encontrado.")

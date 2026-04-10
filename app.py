import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ================================
# 🔎 CONSULTA CNPJ
# ================================
@st.cache_data
def buscar_empresa(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json().get("razao_social", "")
    except:
        return "Não encontrado"

# ================================
# ABAS
# ================================
aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Análise Inteligente de Empresas")

    file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

    if file:

        if st.button("🚀 Processar Planilha"):

            inicio = time.time()

            progress = st.progress(0)
            status = st.empty()

            try:
                progress.progress(10)
                df = pd.read_excel(file, engine="openpyxl")
                df.columns = df.columns.str.strip()

                col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

                df[col_cnpj] = (
                    df[col_cnpj]
                    .astype(str)
                    .str.replace(r'\D', '', regex=True)
                    .str.zfill(14)
                )

                # ====================
                # 🔍 FILTROS
                # ====================
                st.sidebar.header("🔍 Filtros")

                if "Cidade" in df.columns:
                    cidade = st.sidebar.selectbox("Cidade", ["Todas"] + list(df["Cidade"].dropna().unique()))
                    if cidade != "Todas":
                        df = df[df["Cidade"] == cidade]

                if "Data" in df.columns:
                    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
                    data_ini = st.sidebar.date_input("Data inicial", df["Data"].min())
                    data_fim = st.sidebar.date_input("Data final", df["Data"].max())
                    df = df[(df["Data"] >= pd.to_datetime(data_ini)) & (df["Data"] <= pd.to_datetime(data_fim))]

                progress.progress(40)

                contagem = df[col_cnpj].value_counts()
                repetidos = contagem[contagem > 1]

                df_resultado = df[df[col_cnpj].isin(repetidos.index)]

                # Consulta otimizada
                cnpjs_unicos = df_resultado[col_cnpj].unique()[:100]

                mapa = {}
                for cnpj in cnpjs_unicos:
                    mapa[cnpj] = buscar_empresa(cnpj)

                df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa)

                progress.progress(70)

                fim = time.time()

                progress.progress(100)

                # ====================
                # 📊 DASHBOARD
                # ====================
                col1, col2, col3 = st.columns(3)
                col1.metric("⏱ Tempo", f"{round(fim-inicio,2)}s")
                col2.metric("📊 Empresas únicas", df_resultado[col_cnpj].nunique())
                col3.metric("📁 Registros", df_resultado.shape[0])

                # ====================
                # 🥇 RANKING
                # ====================
                ranking = (
                    df_resultado.groupby([col_cnpj, "Empresa"])
                    .size()
                    .reset_index(name="Qtd Afastamentos")
                    .sort_values(by="Qtd Afastamentos", ascending=False)
                )

                st.markdown("## 🥇 Ranking de Empresas")
                st.dataframe(ranking, use_container_width=True, hide_index=True)

                # ====================
                # 📊 GRÁFICO
                # ====================
                st.markdown("## 📊 Top 10 Empresas")

                top10 = ranking.head(10).set_index("Empresa")

                st.bar_chart(top10["Qtd Afastamentos"])

                # ====================
                # ⚠️ RISCO
                # ====================
                criticas = ranking[ranking["Qtd Afastamentos"] >= 5]

                if not criticas.empty:
                    st.markdown("## ⚠️ Alto Risco")

                    for _, row in criticas.iterrows():
                        st.markdown(f"""
                        <div style="background:#7f1d1d;padding:15px;border-radius:10px;margin-bottom:10px;">
                        <b>{row['Empresa']}</b><br>
                        CNPJ: {row[col_cnpj]}<br>
                        Afastamentos: {row['Qtd Afastamentos']}
                        </div>
                        """, unsafe_allow_html=True)

                # ====================
                # 📋 DETALHADO
                # ====================
                st.markdown("## 📋 Dados Detalhados")
                st.dataframe(df_resultado, use_container_width=True)

                # ====================
                # 📥 DOWNLOAD
                # ====================
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_resultado.to_excel(writer, index=False)
                    ranking.to_excel(writer, index=False, sheet_name='Ranking')

                output.seek(0)

                st.download_button(
                    "📥 Baixar relatório",
                    output,
                    "relatorio.xlsx"
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
            html = f.read()

        components.html(html, height=900, scrolling=True)

    except:
        st.error("❌ Arquivo index.html não encontrado.")

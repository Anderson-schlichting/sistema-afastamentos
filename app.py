import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ================================
# 🔎 CONSULTA COMPLETA (ReceitaWS)
# ================================
@st.cache_data
def buscar_empresa(cnpj):
    try:
        url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        r = requests.get(url, timeout=5)
        data = r.json()

        nome = data.get("nome", "")
        telefone = data.get("telefone", "")

        socios = ""
        if "qsa" in data:
            socios = ", ".join([s["nome"] for s in data["qsa"][:3]])

        return nome, telefone, socios

    except:
        return "Não encontrado", "", ""

# ================================
# 📂 LEITURA AUTOMÁTICA
# ================================
def carregar_arquivo(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file, sep=None, engine="python")
    else:
        return pd.read_excel(file, engine="openpyxl")

# ================================
# ABAS
# ================================
aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Análise Inteligente de Empresas")

    file = st.file_uploader("Envie Excel ou CSV", type=["xlsx","csv"])

    if file:

        if st.button("🚀 Processar"):

            inicio = time.time()

            df = carregar_arquivo(file)
            df.columns = df.columns.str.strip()

            # Detecta CNPJ
            col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

            # Corrige CNPJ
            df[col_cnpj] = (
                df[col_cnpj]
                .astype(str)
                .str.replace(r'\D', '', regex=True)
                .str.zfill(14)
            )

            # Repetidos
            contagem = df[col_cnpj].value_counts()
            repetidos = contagem[contagem > 1]

            df_resultado = df[df[col_cnpj].isin(repetidos.index)]

            # ====================
            # 🔍 FILTROS
            # ====================
            st.sidebar.header("Filtros")

            if "Cidade" in df.columns:
                cidade = st.sidebar.selectbox("Cidade", ["Todas"] + list(df["Cidade"].dropna().unique()))
                if cidade != "Todas":
                    df_resultado = df_resultado[df_resultado["Cidade"] == cidade]

            # ====================
            # 🚀 CONSULTA OTIMIZADA
            # ====================
            cnpjs_unicos = df_resultado[col_cnpj].unique()[:30]

            mapa_nome = {}
            mapa_tel = {}
            mapa_socios = {}

            for cnpj in cnpjs_unicos:
                nome, tel, socios = buscar_empresa(cnpj)

                mapa_nome[cnpj] = nome
                mapa_tel[cnpj] = tel
                mapa_socios[cnpj] = socios

                time.sleep(0.3)

            df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa_nome)
            df_resultado["Telefone"] = df_resultado[col_cnpj].map(mapa_tel)
            df_resultado["Sócios"] = df_resultado[col_cnpj].map(mapa_socios)

            fim = time.time()

            # ====================
            # DASHBOARD
            # ====================
            col1, col2, col3 = st.columns(3)
            col1.metric("Tempo", f"{round(fim-inicio,2)}s")
            col2.metric("Empresas", df_resultado[col_cnpj].nunique())
            col3.metric("Registros", df_resultado.shape[0])

            # ====================
            # RANKING
            # ====================
            ranking = (
                df_resultado.groupby([col_cnpj,"Empresa","Telefone","Sócios"])
                .size()
                .reset_index(name="Afastamentos")
                .sort_values(by="Afastamentos", ascending=False)
            )

            st.markdown("## Ranking")
            st.dataframe(ranking, use_container_width=True)

            # ====================
            # GRÁFICO
            # ====================
            st.markdown("## Top 10 Empresas")
            top10 = ranking.head(10).set_index("Empresa")
            st.bar_chart(top10["Afastamentos"])

            # ====================
            # ALTO RISCO
            # ====================
            criticas = ranking[ranking["Afastamentos"] >= 5]

            if not criticas.empty:
                st.markdown("## ⚠️ Alto Risco")

                for _, row in criticas.iterrows():
                    st.markdown(f"""
                    <div style="background:#7f1d1d;padding:15px;border-radius:10px;margin-bottom:10px;">
                    <b>{row['Empresa']}</b><br>
                    CNPJ: {row[col_cnpj]}<br>
                    Telefone: {row['Telefone']}<br>
                    Sócios: {row['Sócios']}<br>
                    Afastamentos: {row['Afastamentos']}
                    </div>
                    """, unsafe_allow_html=True)

            # ====================
            # DADOS
            # ====================
            st.markdown("## Dados Detalhados")
            st.dataframe(df_resultado, use_container_width=True)

            # ====================
            # DOWNLOAD
            # ====================
            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_resultado.to_excel(writer, index=False)
                ranking.to_excel(writer, index=False, sheet_name="Ranking")

            output.seek(0)

            st.download_button(
                "📥 Baixar relatório",
                output,
                "relatorio.xlsx"
            )

# ================================
# 📈 ABA 2 (FAP)
# ================================
with aba2:

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=900, scrolling=True)

    except:
        st.error("index.html não encontrado")

import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ================================
# 📂 LEITURA
# ================================
def carregar_arquivo(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file, sep=None, engine="python")
    else:
        return pd.read_excel(file, engine="openpyxl")

# ================================
# 🔎 CONSULTA CNPJ
# ================================
@st.cache_data(ttl=3600)
def buscar_empresa(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)
        nome = r.json().get("razao_social", "")

        url2 = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        r2 = requests.get(url2, timeout=5)
        data = r2.json()

        telefone = data.get("telefone", "")
        socios = ", ".join([s.get("nome","") for s in data.get("qsa", [])[:3]])

        if not nome:
            nome = data.get("nome") or data.get("fantasia") or "Não encontrado"

        return nome, telefone, socios

    except:
        return "Não encontrado", "", ""

# ================================
# ABAS
# ================================
aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Análise de Empresas")

    file = st.file_uploader("Envie Excel ou CSV", type=["xlsx","csv"])

    if file:

        if st.button("🚀 Processar"):

            df = carregar_arquivo(file)
            df.columns = df.columns.str.strip()

            st.write("📋 Colunas detectadas:", list(df.columns))

            # ====================
            # 🔎 DETECTA CNPJ (INTELIGENTE)
            # ====================
            col_cnpj = next(
                (c for c in df.columns if any(x in c.upper() for x in ["CNPJ","CEI","EMPREGADOR"])),
                None
            )

            if not col_cnpj:
                st.error("❌ Não encontrei coluna de CNPJ")
                st.stop()

            # ====================
            # 🏙️ DETECTA CIDADE
            # ====================
            col_cidade = next(
                (c for c in df.columns if "MUNIC" in c.upper()),
                None
            )

            # ====================
            # LIMPA CNPJ
            # ====================
            df[col_cnpj] = (
                df[col_cnpj]
                .astype(str)
                .str.replace(r'\D', '', regex=True)
                .str.zfill(14)
            )

            # ====================
            # REPETIDOS
            # ====================
            contagem = df[col_cnpj].value_counts()
            repetidos = contagem[contagem > 1]

            df_resultado = df[df[col_cnpj].isin(repetidos.index)]

            # ====================
            # CONSULTA EMPRESAS
            # ====================
            cnpjs = df_resultado[col_cnpj].dropna().unique()[:20]

            mapa_nome = {}
            mapa_tel = {}
            mapa_socios = {}

            progress = st.progress(0)

            for i, cnpj in enumerate(cnpjs):
                nome, tel, socios = buscar_empresa(cnpj)

                mapa_nome[cnpj] = nome
                mapa_tel[cnpj] = tel
                mapa_socios[cnpj] = socios

                progress.progress((i+1)/len(cnpjs))

                time.sleep(0.2)

            df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa_nome)
            df_resultado["Telefone"] = df_resultado[col_cnpj].map(mapa_tel)
            df_resultado["Sócios"] = df_resultado[col_cnpj].map(mapa_socios)

            # ====================
            # DASHBOARD
            # ====================
            st.markdown("## 🥇 Ranking de Empresas")

            ranking = (
                df_resultado.groupby(["Empresa","Telefone","Sócios"])
                .size()
                .reset_index(name="Afastamentos")
                .sort_values(by="Afastamentos", ascending=False)
            )

            st.dataframe(ranking, use_container_width=True)

            # ====================
            # GRÁFICO
            # ====================
            st.markdown("## 📊 Top 10 Empresas")
            st.bar_chart(ranking.head(10).set_index("Empresa")["Afastamentos"])

            # ====================
            # RANKING POR CIDADE
            # ====================
            if col_cidade:
                st.markdown("## 🏙️ Ranking por Cidade")
                ranking_cidade = df_resultado.groupby(col_cidade).size().reset_index(name="Afastamentos")
                st.bar_chart(ranking_cidade.set_index(col_cidade))

            # ====================
            # DADOS
            # ====================
            st.markdown("## 📋 Dados Detalhados")
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

    st.subheader("📈 Análise Empresarial - FAP")

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=900, scrolling=True)

    except:
        st.warning("⚠️ Arquivo index.html não encontrado")

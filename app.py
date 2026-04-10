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
# 🔎 CONSULTA EMPRESA
# ================================
@st.cache_data(ttl=3600)
def buscar_empresa(cnpj):
    try:
        # Nome
        url1 = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r1 = requests.get(url1, timeout=3)
        nome = r1.json().get("razao_social", "")

        # Telefone + sócios
        url2 = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        r2 = requests.get(url2, timeout=5)
        data = r2.json()

        telefone = data.get("telefone", "")
        socios = ", ".join([s.get("nome", "") for s in data.get("qsa", [])[:3]])

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

    st.subheader("📊 Análise de Empresas (Santa Catarina)")

    file = st.file_uploader("Envie Excel ou CSV", type=["xlsx", "csv"])

    if file:

        if st.button("🚀 Processar"):

            df = carregar_arquivo(file)
            df.columns = df.columns.str.strip()

            # ====================
            # IDENTIFICA COLUNAS
            # ====================
            col_cnpj = next((c for c in df.columns if "CNPJ" in c.upper()), None)
            col_uf = next((c for c in df.columns if "UF" in c.upper()), None)
            col_cidade = next((c for c in df.columns if "MUNIC" in c.upper()), None)

            if not col_cnpj:
                st.error("❌ Coluna de CNPJ não encontrada")
                st.stop()

            # ====================
            # LIMPA CNPJ
            # ====================
            df[col_cnpj] = (
                df[col_cnpj]
                .astype(str)
                .str.replace(r"\D", "", regex=True)
                .str.zfill(14)
            )

            # ====================
            # FILTRO SC (ROBUSTO)
            # ====================
            if col_uf:

                df[col_uf] = (
                    df[col_uf]
                    .astype(str)
                    .str.upper()
                    .str.strip()
                )

                df = df[
                    df[col_uf].isin(["SC", "SANTA CATARINA"]) |
                    df[col_uf].str.contains("SC", na=False) |
                    df[col_uf].str.contains("CATARINA", na=False)
                ]

                if df.empty:
                    st.warning("⚠️ Nenhum dado encontrado para SC — exibindo todos os dados")
                    df = carregar_arquivo(file)

            # ====================
            # FILTRA REPETIDOS
            # ====================
            contagem = df[col_cnpj].value_counts()
            df = df[df[col_cnpj].isin(contagem[contagem > 1].index)]

            if df.empty:
                st.warning("⚠️ Nenhum CNPJ repetido encontrado")
                st.stop()

            # ====================
            # CONSULTA EMPRESAS
            # ====================
            cnpjs = df[col_cnpj].dropna().unique()[:20]

            mapa_nome = {}
            mapa_tel = {}
            mapa_socios = {}

            progress = st.progress(0)

            for i, cnpj in enumerate(cnpjs):
                nome, tel, socios = buscar_empresa(cnpj)

                mapa_nome[cnpj] = nome
                mapa_tel[cnpj] = tel
                mapa_socios[cnpj] = socios

                progress.progress((i + 1) / len(cnpjs))
                time.sleep(0.2)

            df["Empresa"] = df[col_cnpj].map(mapa_nome)
            df["Telefone"] = df[col_cnpj].map(mapa_tel)
            df["Sócios"] = df[col_cnpj].map(mapa_socios)

            # ====================
            # RANKING EMPRESAS
            # ====================
            st.markdown("## 🥇 Ranking de Empresas")

            ranking = (
                df.groupby(["Empresa", "Telefone", "Sócios"])
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
                ranking_cidade = df.groupby(col_cidade).size().reset_index(name="Afastamentos")
                st.bar_chart(ranking_cidade.set_index(col_cidade))

            # ====================
            # DADOS
            # ====================
            st.markdown("## 📋 Dados Detalhados")
            st.dataframe(df, use_container_width=True)

            # ====================
            # DOWNLOAD
            # ====================
            output = BytesIO()

            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Dados")
                ranking.to_excel(writer, index=False, sheet_name="Ranking")

            output.seek(0)

            st.download_button(
                "📥 Baixar relatório completo",
                output,
                "relatorio_sc.xlsx"
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

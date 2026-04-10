import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ================================
# 🔎 CONSULTA CNPJ
# ================================
@st.cache_data(ttl=3600)
def buscar_empresa(cnpj):
    try:
        url1 = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r1 = requests.get(url1, timeout=3)
        nome = ""
        if r1.status_code == 200:
            nome = r1.json().get("razao_social", "")

        url2 = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        r2 = requests.get(url2, timeout=5)
        data = r2.json()

        if not nome:
            nome = data.get("nome") or data.get("fantasia") or "Não encontrado"

        telefone = data.get("telefone", "")

        socios = ""
        if "qsa" in data:
            socios = ", ".join([s.get("nome", "") for s in data["qsa"][:3]])

        return nome, telefone, socios

    except:
        return "Não encontrado", "", ""

# ================================
# 📂 LEITURA INTELIGENTE
# ================================
def carregar_arquivo(file):

    if file.name.endswith(".csv"):
        try:
            return pd.read_csv(file, sep=";", encoding="utf-8")
        except:
            try:
                return pd.read_csv(file, sep=",", encoding="latin1")
            except:
                return pd.read_csv(file, engine="python")

    else:
        return pd.read_excel(file, engine="openpyxl")

# ================================
# 🔍 DETECTAR COLUNA
# ================================
def detectar_coluna(df, palavras):
    for col in df.columns:
        for p in palavras:
            if p in col.upper():
                return col
    return None

# ================================
# APP
# ================================
file = st.file_uploader("Envie Excel ou CSV", type=["xlsx", "csv"])

if file:

    if st.button("🚀 Processar"):

        df = carregar_arquivo(file)
        df.columns = df.columns.str.strip()

        st.write("📋 Colunas detectadas:", list(df.columns))

        # ====================
        # 🔵 FILTRO SC
        # ====================
        col_uf = detectar_coluna(df, ["UF", "ESTADO"])

        if col_uf:
            df[col_uf] = df[col_uf].astype(str).str.upper()
            df = df[df[col_uf].str.contains("SC", na=False)]
            st.success(f"Filtro aplicado: {col_uf}")
        else:
            st.warning("⚠️ Não encontrou coluna de UF/Estado")

        # ====================
        # 🔎 CNPJ
        # ====================
        col_cnpj = detectar_coluna(df, ["CNPJ"])

        if not col_cnpj:
            st.error("❌ Não encontrou coluna de CNPJ")
            st.stop()

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
        df = df[df[col_cnpj].isin(contagem[contagem > 1].index)]

        # ====================
        # CONSULTA API
        # ====================
        cnpjs = df[col_cnpj].unique()[:20]

        mapa_nome = {}
        mapa_tel = {}
        mapa_socios = {}

        for cnpj in cnpjs:
            nome, tel, socios = buscar_empresa(cnpj)

            mapa_nome[cnpj] = nome
            mapa_tel[cnpj] = tel
            mapa_socios[cnpj] = socios

            time.sleep(0.2)

        df["Empresa"] = df[col_cnpj].map(mapa_nome)
        df["Telefone"] = df[col_cnpj].map(mapa_tel)
        df["Sócios"] = df[col_cnpj].map(mapa_socios)

        # ====================
        # DASHBOARD
        # ====================
        col1, col2, col3 = st.columns(3)

        col1.metric("Empresas", df[col_cnpj].nunique())
        col2.metric("Registros", df.shape[0])
        col3.metric("CNPJs repetidos", len(cnpjs))

        # ====================
        # RANKING
        # ====================
        ranking = (
            df.groupby(["Empresa","Telefone","Sócios"])
            .size()
            .reset_index(name="Afastamentos")
            .sort_values(by="Afastamentos", ascending=False)
        )

        st.markdown("## 🥇 Ranking")
        st.dataframe(ranking, use_container_width=True)

        # ====================
        # GRÁFICO
        # ====================
        st.markdown("## 📊 Top 10")
        top10 = ranking.head(10).set_index("Empresa")
        st.bar_chart(top10["Afastamentos"])

        # ====================
        # DADOS
        # ====================
        st.markdown("## 📋 Dados Detalhados")
        st.dataframe(df, use_container_width=True)

        # ====================
        # DOWNLOAD
        # ====================
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        st.download_button("📥 Baixar Excel", output, "relatorio.xlsx")

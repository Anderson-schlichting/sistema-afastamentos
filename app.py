import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente Empresarial")

# ================================
# 📂 LEITURA
# ================================
def carregar_arquivo(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, sep=';', encoding='latin1')
        else:
            return pd.read_excel(file)
    except:
        return None

# ================================
# 🧠 LIMPAR CIDADE
# ================================
def limpar_cidade(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor)
    if "-" in valor:
        valor = valor.split("-", 1)[1]
    return valor.strip().upper()

# ================================
# 🔎 API
# ================================
@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

# ================================
# 📊 SCORE
# ================================
def score_empresa(qtd):
    return min(qtd * 10, 200)

def classificar(score):
    if score >= 30:
        return "🔴 Alto"
    elif score >= 15:
        return "🟠 Médio"
    else:
        return "🟢 Baixo"

# ================================
# 💰 CÁLCULO FINANCEIRO
# ================================
def calcular_valores(afastamentos, anos=5):
    valor_base = afastamentos * 1200
    total = valor_base * anos
    mensal = valor_base / 12
    projecao = mensal * 12
    return total, mensal, projecao

# ================================
# ABAS
# ================================
aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    file = st.file_uploader("Envie Excel ou CSV")

    if file and st.button("🚀 Processar"):

        progress = st.progress(0)
        df = carregar_arquivo(file)

        if df is None:
            st.error("Erro ao ler arquivo")
            st.stop()

        df.columns = df.columns.str.strip()

        col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]
        col_cidade = [c for c in df.columns if "MUNIC" in c.upper()][0]

        df[col_cnpj] = df[col_cnpj].astype(str).str.replace(r'\D','',regex=True).str.zfill(14)
        df["CIDADE_LIMPA"] = df[col_cidade].apply(limpar_cidade)

        df_resultado = df[df[col_cnpj].duplicated(keep=False)]

        lista = []
        total = len(df_resultado[col_cnpj].unique())

        for i, cnpj in enumerate(df_resultado[col_cnpj].unique()):
            dados = consultar_cnpj(cnpj)

            lista.append({
                "CNPJ": cnpj,
                "Empresa": dados.get("razao_social",""),
                "Telefone": dados.get("ddd_telefone_1",""),
                "Cidade": dados.get("municipio",""),
                "Socios": ", ".join([s.get("nome","") for s in dados.get("qsa",[])[:2]])
            })

            progress.progress((i+1)/total)

        df_api = pd.DataFrame(lista)

        df_resultado = df_resultado.merge(df_api, left_on=col_cnpj, right_on="CNPJ")

        ranking = df_resultado.groupby(["CNPJ","Empresa","Telefone","Cidade","Socios"]).size().reset_index(name="Afastamentos")

        ranking["Score"] = ranking["Afastamentos"].apply(score_empresa)
        ranking["Classificação"] = ranking["Score"].apply(classificar)

        # DASHBOARD
        st.success("Processado com sucesso")

        c1,c2,c3 = st.columns(3)
        c1.metric("Empresas", ranking.shape[0])
        c2.metric("Registros", df_resultado.shape[0])
        c3.metric("Oportunidades", (ranking["Score"]>=15).sum())

        st.markdown("## 📊 Ranking Comercial")
        st.dataframe(ranking.sort_values("Score", ascending=False))

        st.markdown("## 📈 Top Empresas")
        st.bar_chart(ranking.set_index("Empresa")["Score"].head(10))

        st.markdown("## 🎯 Classificação")
        st.write(ranking["Classificação"].value_counts())

# ================================
# 🔎 ABA 2
# ================================
with aba2:

    cnpj_input = st.text_input("Digite o CNPJ")

    if cnpj_input:

        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)
        dados = consultar_cnpj(cnpj)

        if dados:

            st.success("Empresa encontrada")

            afastamentos = st.number_input("Quantidade de afastamentos", 0, 100, 5)
            anos = st.number_input("Anos para cálculo", 1, 10, 5)

            total, mensal, projecao = calcular_valores(afastamentos, anos)

            col1,col2 = st.columns(2)

            col1.write(f"Empresa: {dados.get('razao_social')}")
            col1.write(f"Telefone: {dados.get('ddd_telefone_1')}")

            col2.write(f"Cidade: {dados.get('municipio')}")
            col2.write(f"UF: {dados.get('uf')}")

            st.markdown("## 💰 Simulação Financeira")
            st.metric("Valor Recuperável", f"R$ {total:,.2f}")
            st.metric("Economia Mensal", f"R$ {mensal:,.2f}")
            st.metric("Projeção 12 meses", f"R$ {projecao:,.2f}")

            obs = st.text_area("📝 Anotações")

            if "historico" not in st.session_state:
                st.session_state["historico"] = []

            if st.button("Salvar Consulta"):
                st.session_state["historico"].append({
                    "CNPJ": cnpj,
                    "Empresa": dados.get("razao_social"),
                    "Valor": total
                })

        st.markdown("## 📜 Histórico")
        if "historico" in st.session_state:
            st.dataframe(pd.DataFrame(st.session_state["historico"]))

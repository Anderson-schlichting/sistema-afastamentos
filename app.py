import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Empresas + FAP")

# ================================
# 📍 CIDADES SC (RESUMIDA)
# ================================
CIDADES_SC = ["BLUMENAU","JOINVILLE","FLORIANÓPOLIS","CHAPECÓ","ITAJAÍ","LAGES","CRICIÚMA"]

# ================================
# 📂 LEITURA INTELIGENTE
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
# 🔎 DETECTAR COLUNA CNPJ
# ================================
def detectar_cnpj(df):
    for col in df.columns:
        if "CNPJ" in col.upper():
            return col
    return None

# ================================
# 🚀 API RECEITA
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
# 📊 CALCULO FAP
# ================================
def calcular_fap(qtd):
    if qtd <= 2:
        return 0.5
    elif qtd <= 5:
        return 1.0
    elif qtd <= 10:
        return 1.5
    else:
        return 2.0

# ================================
# 📊 ABAS
# ================================
aba1, aba2 = st.tabs(["📊 Processamento", "🔎 Consulta CNPJ"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    file = st.file_uploader("Envie sua planilha (CSV ou Excel)")

    if file:

        if st.button("🚀 Processar Dados"):

            with st.spinner("Processando dados..."):

                df = carregar_arquivo(file)

                if df is None:
                    st.error("Erro ao ler arquivo")
                    st.stop()

                df.columns = df.columns.astype(str).str.strip()

                col_cnpj = detectar_cnpj(df)

                if not col_cnpj:
                    st.error("Coluna CNPJ não encontrada")
                    st.stop()

                # normalizar CNPJ
                df[col_cnpj] = (
                    df[col_cnpj]
                    .astype(str)
                    .str.replace(r'\D','',regex=True)
                    .str.zfill(14)
                )

                # duplicados
                df_resultado = df[df[col_cnpj].duplicated(keep=False)]

                # ====================
                # CONSULTA API
                # ====================
                mapa = []

                for cnpj in df_resultado[col_cnpj].unique()[:50]:

                    dados = consultar_cnpj(cnpj)

                    mapa.append({
                        "CNPJ": cnpj,
                        "Empresa": dados.get("razao_social",""),
                        "Fantasia": dados.get("nome_fantasia",""),
                        "Telefone": dados.get("ddd_telefone_1",""),
                        "Cidade": dados.get("municipio",""),
                        "UF": dados.get("uf","")
                    })

                df_api = pd.DataFrame(mapa)

                df_resultado = df_resultado.merge(
                    df_api, left_on=col_cnpj, right_on="CNPJ", how="left"
                )

                # ====================
                # FILTRO SC
                # ====================
                df_resultado["SC"] = df_resultado["UF"] == "SC"

                # ====================
                # RANKING + FAP
                # ====================
                ranking = (
                    df_resultado.groupby(["CNPJ","Empresa"])
                    .size()
                    .reset_index(name="Afastamentos")
                )

                ranking["FAP"] = ranking["Afastamentos"].apply(calcular_fap)

                # ====================
                # DASHBOARD
                # ====================
                st.success("Processamento concluído")

                c1, c2, c3 = st.columns(3)
                c1.metric("Empresas", ranking.shape[0])
                c2.metric("Registros", df_resultado.shape[0])
                c3.metric("SC", df_resultado["SC"].sum())

                st.markdown("## 📊 Ranking + FAP")
                st.dataframe(ranking, use_container_width=True)

                st.markdown("## 📋 Dados Completos")
                st.dataframe(df_resultado, use_container_width=True)

# ================================
# 🔎 ABA 2
# ================================
with aba2:

    st.subheader("Consulta individual de CNPJ")

    cnpj_input = st.text_input("Digite o CNPJ")

    if cnpj_input:

        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)

        dados = consultar_cnpj(cnpj)

        if dados:

            st.success("Empresa encontrada")

            col1, col2 = st.columns(2)

            col1.write(f"Empresa: {dados.get('razao_social','')}")
            col1.write(f"Fantasia: {dados.get('nome_fantasia','')}")
            col1.write(f"Telefone: {dados.get('ddd_telefone_1','')}")

            col2.write(f"Cidade: {dados.get('municipio','')}")
            col2.write(f"UF: {dados.get('uf','')}")

            # FAP simulado
            st.markdown("### 📊 FAP Estimado")
            st.success("FAP base: 1.0 (simulado)")

        else:
            st.error("CNPJ não encontrado")

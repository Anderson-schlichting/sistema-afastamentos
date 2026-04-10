import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ===== FUNÇÃO CONSULTA CNPJ =====
@st.cache_data
def buscar_empresa(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("razao_social", "")
    except:
        return ""

# ===== ABAS =====
aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1 - CNPJ REPETIDO
# ================================
with aba1:

    st.subheader("📊 Identificação de Empresas com Múltiplos Afastamentos")

    file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

    if file:
        try:
            df = pd.read_excel(file, engine="openpyxl")

            # Limpa nomes das colunas
            df.columns = df.columns.str.strip()

            # Detecta coluna de CNPJ automaticamente
            col_cnpj = None
            for col in df.columns:
                if "CNPJ" in col.upper():
                    col_cnpj = col
                    break

            if not col_cnpj:
                st.error("❌ Coluna de CNPJ não encontrada.")
            else:
                # Padroniza CNPJ (14 dígitos)
                df[col_cnpj] = (
                    df[col_cnpj]
                    .astype(str)
                    .str.replace(r'\D', '', regex=True)
                    .str.zfill(14)
                )

                # Conta repetições
                contagem = df[col_cnpj].value_counts()
                cnpjs_repetidos = contagem[contagem > 1].index

                # Filtra dados
                df_resultado = df[df[col_cnpj].isin(cnpjs_repetidos)]

                # Busca nome da empresa
                df_resultado["Empresa"] = df_resultado[col_cnpj].apply(buscar_empresa)

                st.success(f"✅ {df_resultado.shape[0]} registros encontrados")

                st.dataframe(df_resultado, use_container_width=True)

                # Download Excel
                output = "relatorio.xlsx"
                df_resultado.to_excel(output, index=False)

                with open(output, "rb") as f:
                    st.download_button(
                        "📥 Baixar relatório",
                        f,
                        "relatorio_cnpj_repetidos.xlsx"
                    )

        except Exception as e:
            st.error(f"Erro ao processar: {e}")

# ================================
# 📈 ABA 2 - SISTEMA FAP
# ================================
with aba2:

    st.subheader("📈 Análise Empresarial - FAP")

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_code = f.read()

        components.html(html_code, height=900, scrolling=True)

    except:
        st.warning("⚠️ Arquivo index.html não encontrado.")

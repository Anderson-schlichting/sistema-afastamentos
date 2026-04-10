import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

def carregar_arquivo(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file, sep=None, engine="python")
    else:
        return pd.read_excel(file, engine="openpyxl")

@st.cache_data(ttl=86400)
def buscar_empresa(cnpj):
    try:
        url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        r = requests.get(url, timeout=5)
        data = r.json()

        if data.get("status") == "ERROR":
            return None

        return {
            "cnpj": cnpj,
            "nome": data.get("nome") or data.get("fantasia"),
            "uf": data.get("uf"),
            "telefone": data.get("telefone"),
            "socios": ", ".join([s.get("nome") for s in data.get("qsa", [])[:3]])
        }

    except:
        return None

def consultar_lote(cnpjs):
    resultados = []

    def task(cnpj):
        info = buscar_empresa(cnpj)
        if not info:
            return None
        uf = str(info.get("uf", "")).upper().strip()
        if "SC" in uf:
            return info

    with ThreadPoolExecutor(max_workers=10) as executor:
        for r in executor.map(task, cnpjs):
            if r:
                resultados.append(r)

    return resultados

aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

with aba1:
    st.subheader("📊 Análise de Empresas (Santa Catarina)")
    file = st.file_uploader("Envie Excel ou CSV", type=["xlsx", "csv"])

    if file:
        if st.button("🚀 Processar"):
            df = carregar_arquivo(file)
            df.columns = df.columns.str.strip()

            col_cnpj = next((c for c in df.columns if "CNPJ" in c.upper()), None)

            if not col_cnpj:
                st.error("❌ Coluna CNPJ não encontrada")
                st.stop()

            df[col_cnpj] = (
                df[col_cnpj]
                .astype(str)
                .str.replace(r"\D", "", regex=True)
                .str.zfill(14)
            )

            contagem = df[col_cnpj].value_counts()
            cnpjs_relevantes = contagem[contagem > 1].index

            df = df[df[col_cnpj].isin(cnpjs_relevantes)]
            cnpjs = df[col_cnpj].dropna().unique()

            st.info(f"⚡ Consultando {len(cnpjs)} empresas relevantes...")

            dados = consultar_lote(cnpjs)
            df_empresas = pd.DataFrame(dados)

            if df_empresas.empty:
                st.warning("⚠️ Nenhuma empresa de SC encontrada")
                st.stop()

            ranking = (
                df.groupby(col_cnpj)
                .size()
                .reset_index(name="Afastamentos")
            )

            ranking = ranking.merge(
                df_empresas,
                left_on=col_cnpj,
                right_on="cnpj"
            )

            ranking = ranking.sort_values(by="Afastamentos", ascending=False)

            st.success("✅ Processamento concluído")

            st.markdown("## 🥇 Ranking de Empresas (SC)")
            st.dataframe(
                ranking[["cnpj", "nome", "telefone", "socios", "Afastamentos"]],
                use_container_width=True
            )

            st.markdown("## 📊 Top 10 Empresas")
            st.bar_chart(
                ranking.head(10).set_index("nome")["Afastamentos"]
            )

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                ranking.to_excel(writer, index=False)

            output.seek(0)

            st.download_button(
                "📥 Baixar Excel",
                output,
                "ranking_sc.xlsx"
            )

with aba2:
    st.subheader("📈 Análise Empresarial - FAP")
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        components.html(html, height=900, scrolling=True)
    except:
        st.warning("⚠️ Arquivo index.html não encontrado")

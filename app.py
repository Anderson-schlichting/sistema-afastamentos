import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos (SC via Receita)")

# ================================
# 📂 LEITURA
# ================================
def carregar_arquivo(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file, sep=None, engine="python")
    else:
        return pd.read_excel(file, engine="openpyxl")

# ================================
# 🔎 CONSULTA RECEITA
# ================================
@st.cache_data(ttl=3600)
def buscar_empresa(cnpj):
    try:
        url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"
        r = requests.get(url, timeout=5)
        data = r.json()

        if data.get("status") == "ERROR":
            return {}

        return {
            "nome": data.get("nome") or data.get("fantasia"),
            "uf": data.get("uf"),
            "telefone": data.get("telefone"),
            "socios": ", ".join([s.get("nome") for s in data.get("qsa", [])[:3]])
        }

    except:
        return {}

# ================================
# 📤 UPLOAD
# ================================
file = st.file_uploader("Envie Excel ou CSV", type=["xlsx", "csv"])

if file:

    if st.button("🚀 Processar"):

        df = carregar_arquivo(file)
        df.columns = df.columns.str.strip()

        # ====================
        # 🔍 IDENTIFICA CNPJ
        # ====================
        col_cnpj = next((c for c in df.columns if "CNPJ" in c.upper()), None)

        if not col_cnpj:
            st.error("❌ Coluna CNPJ não encontrada")
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
        # LISTA CNPJs
        # ====================
        cnpjs = df[col_cnpj].dropna().unique()

        st.info(f"🔍 Consultando {len(cnpjs)} empresas na Receita...")

        progress = st.progress(0)
        status = st.empty()

        dados = []

        # ====================
        # 🔄 CONSULTA COM FILTRO SC
        # ====================
        for i, cnpj in enumerate(cnpjs):

            status.text(f"Consultando {i+1}/{len(cnpjs)}")

            info = buscar_empresa(cnpj)

            uf = str(info.get("uf", "")).upper().strip()

            if "SC" in uf:  # 👈 FILTRO REAL
                dados.append({
                    "CNPJ": cnpj,
                    "Empresa": info.get("nome", "Não encontrado"),
                    "Telefone": info.get("telefone"),
                    "Sócios": info.get("socios")
                })

            progress.progress((i + 1) / len(cnpjs))
            time.sleep(0.15)

        df_empresas = pd.DataFrame(dados)

        if df_empresas.empty:
            st.warning("⚠️ Nenhuma empresa de SC encontrada na Receita")
            st.stop()

        # ====================
        # 📊 CONTAGEM
        # ====================
        ranking = (
            df[df[col_cnpj].isin(df_empresas["CNPJ"])]
            .groupby(col_cnpj)
            .size()
            .reset_index(name="Afastamentos")
        )

        ranking = ranking.merge(df_empresas, left_on=col_cnpj, right_on="CNPJ")

        ranking = ranking.sort_values(by="Afastamentos", ascending=False)

        # ====================
        # 📈 RESULTADO
        # ====================
        st.success("✅ Processamento concluído")

        st.markdown("## 🥇 Ranking de Empresas (SC)")
        st.dataframe(ranking, use_container_width=True)

        # ====================
        # 📊 GRÁFICO
        # ====================
        st.markdown("## 📊 Top 10 Empresas")
        st.bar_chart(ranking.head(10).set_index("Empresa")["Afastamentos"])

        # ====================
        # 📥 DOWNLOAD
        # ====================
        output = BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            ranking.to_excel(writer, index=False)

        output.seek(0)

        st.download_button(
            "📥 Baixar Excel",
            output,
            "ranking_sc.xlsx"
        )

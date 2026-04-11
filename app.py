import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente Empresas + FAP PRO")

# ================================
# 🚀 API COM CACHE
# ================================
@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)

        if r.status_code == 200:
            data = r.json()

            return {
                "empresa": data.get("razao_social"),
                "fantasia": data.get("nome_fantasia"),
                "telefone": data.get("ddd_telefone_1"),
                "cidade": data.get("municipio"),
                "uf": data.get("uf"),
                "socios": ", ".join([q.get("nome_socio","") for q in data.get("qsa",[])])
            }
    except:
        pass

    return None

# ================================
# 📂 LEITURA INTELIGENTE
# ================================
def carregar_arquivo(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, sep=';', encoding='latin1')
        return pd.read_excel(file)
    except:
        return None

# ================================
# 🔎 DETECTAR CNPJ
# ================================
def detectar_cnpj(df):
    for c in df.columns:
        if "CNPJ" in c.upper():
            return c
    return None

# ================================
# 📊 FAP REAL
# ================================
def calcular_fap_valores(folha, rat, fap_atual, fap_ideal):

    atual = folha * rat * fap_atual
    correto = folha * rat * fap_ideal

    economia = max(atual - correto, 0)

    return {
        "atual": atual,
        "correto": correto,
        "mensal": economia,
        "anual": economia * 12,
        "recuperavel": economia * 60
    }

# ================================
# 📊 RANKING + SCORE (CORRIGIDO)
# ================================

ranking = (
    df.groupby(["CNPJ","empresa","telefone","socios","cidade"])
    .size()
    .reset_index(name="Afastamentos")
)

# função score
def score_empresa(qtd):
    score = min(qtd * 5, 200)

    if score >= 30:
        nivel = "🔴"
    elif score >= 15:
        nivel = "🟠"
    else:
        nivel = "🟢"

    return pd.Series([score, nivel])

# aplica score (SOMENTE DEPOIS DO RANKING EXISTIR)
if not ranking.empty:
    ranking[["Score", "Nivel"]] = ranking["Afastamentos"].apply(score_empresa)
else:
    ranking["Score"] = []
    ranking["Nivel"] = []

# ================================
# 📊 ABAS
# ================================
aba1, aba2 = st.tabs(["📊 Análise Inteligente", "🔎 Consulta + FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    file = st.file_uploader("Envie CSV ou Excel")

    if file and st.button("🚀 Processar"):

        df = carregar_arquivo(file)

        if df is None:
            st.error("Erro ao ler arquivo")
            st.stop()

        df.columns = df.columns.astype(str).str.strip()

        col_cnpj = detectar_cnpj(df)

        if not col_cnpj:
            st.error("Coluna CNPJ não encontrada")
            st.stop()

        df[col_cnpj] = (
            df[col_cnpj].astype(str)
            .str.replace(r"\D","",regex=True)
            .str.zfill(14)
        )

        # duplicados
        df = df[df[col_cnpj].duplicated(keep=False)]

        progress = st.progress(0)

        dados_api = []
        total = len(df[col_cnpj].unique())
        lote = 10

        for i, cnpj in enumerate(df[col_cnpj].unique()):

            dados = consultar_cnpj(cnpj)

            if dados and dados["empresa"]:  # 🔥 garante empresa válida

                dados_api.append({
                    "CNPJ": cnpj,
                    **dados
                })

            if i % lote == 0:
                progress.progress(i / total)

        progress.progress(1.0)

        df_api = pd.DataFrame(dados_api)

        df = df.merge(df_api, left_on=col_cnpj, right_on="CNPJ", how="inner")

        # somente SC
        df = df[df["uf"] == "SC"]

        # ranking
        ranking = (
            df.groupby(["CNPJ","empresa","telefone","socios","cidade"])
            .size()
            .reset_index(name="Afastamentos")
        )

        ranking["Score"], ranking["Nivel"] = zip(*ranking["Afastamentos"].apply(score_empresa))

        # ====================
        # DASHBOARD
        # ====================
        st.success("Processamento concluído")

        c1, c2, c3 = st.columns(3)
        c1.metric("Empresas", ranking.shape[0])
        c2.metric("Registros", df.shape[0])
        c3.metric("SC", ranking.shape[0])

        st.markdown("## 📊 Ranking Inteligente")

        st.dataframe(ranking, use_container_width=True)

        st.bar_chart(ranking.set_index("empresa")["Afastamentos"])

        st.markdown("## 📋 Base Completa")
        st.dataframe(df, use_container_width=True)

# ================================
# 🔎 ABA 2 (FAP COMPLETO)
# ================================
with aba2:

    st.subheader("Consulta + Cálculo FAP")

    cnpj = st.text_input("Digite o CNPJ")

    if cnpj:

        cnpj = ''.join(filter(str.isdigit, cnpj)).zfill(14)

        dados = consultar_cnpj(cnpj)

        if dados:

            st.success("Empresa encontrada")

            st.write("Empresa:", dados["empresa"])
            st.write("Sócios:", dados["socios"])
            st.write("Telefone:", dados["telefone"])
            st.write("Cidade:", dados["cidade"])

            st.markdown("### 📊 Simulação FAP")

            folha = st.number_input("Folha salarial mensal")
            rat = st.number_input("RAT (ex: 0.02)")
            fap_atual = st.number_input("FAP atual", 0.5, 2.0)
            fap_ideal = st.number_input("FAP ideal", 0.5, 2.0)

            if st.button("Calcular"):

                res = calcular_fap_valores(folha, rat, fap_atual, fap_ideal)

                st.success(f"Economia mensal: R$ {res['mensal']:.2f}")
                st.info(f"Economia anual: R$ {res['anual']:.2f}")
                st.warning(f"Recuperável 5 anos: R$ {res['recuperavel']:.2f}")

                # PDF
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()

                story = [
                    Paragraph(f"Empresa: {dados['empresa']}", styles["Normal"]),
                    Paragraph(f"Economia mensal: R$ {res['mensal']:.2f}", styles["Normal"]),
                    Paragraph(f"Recuperável: R$ {res['recuperavel']:.2f}", styles["Normal"]),
                ]

                doc.build(story)

                st.download_button(
                    "📄 Baixar PDF",
                    buffer.getvalue(),
                    "relatorio.pdf"
                )
        else:
            st.error("CNPJ não encontrado")

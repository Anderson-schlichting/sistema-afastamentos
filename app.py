import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente Empresas + FAP")

# ================================
# 📂 LEITURA SEGURA
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
# 🔎 DETECTAR CNPJ
# ================================
def detectar_cnpj(df):
    for c in df.columns:
        if "CNPJ" in c.upper():
            return c
    return None

# ================================
# 🚀 API SEGURA
# ================================
@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)

        if r.status_code == 200:
            data = r.json()

            return {
                "empresa": data.get("razao_social",""),
                "fantasia": data.get("nome_fantasia",""),
                "telefone": data.get("ddd_telefone_1",""),
                "cidade": data.get("municipio",""),
                "uf": data.get("uf",""),
                "socios": ", ".join([q.get("nome_socio","") for q in data.get("qsa",[])])
            }
    except:
        pass

    return None

# ================================
# 🎯 SCORE
# ================================
def score_empresa(qtd):
    score = min(qtd * 5, 200)

    if score >= 30:
        nivel = "🔴"
    elif score >= 15:
        nivel = "🟠"
    else:
        nivel = "🟢"

    return pd.Series([score, nivel])

# ================================
# 📊 FAP
# ================================
def calcular_fap(folha, rat, fap_atual, fap_ideal):
    atual = folha * rat * fap_atual
    correto = folha * rat * fap_ideal

    economia = max(atual - correto, 0)

    return atual, correto, economia, economia*12, economia*60

# ================================
# 📊 ABAS
# ================================
aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta FAP"])

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

        # normalizar CNPJ
        df[col_cnpj] = (
            df[col_cnpj].astype(str)
            .str.replace(r"\D","",regex=True)
            .str.zfill(14)
        )

        # duplicados
        df = df[df[col_cnpj].duplicated(keep=False)]

        st.info("🔄 Consultando Receita...")

        progress = st.progress(0)

        dados_lista = []
        cnpjs = df[col_cnpj].unique()
        total = len(cnpjs)

        for i, cnpj in enumerate(cnpjs):

            dados = consultar_cnpj(cnpj)

            if dados and dados["empresa"]:
                dados_lista.append({
                    "CNPJ": cnpj,
                    **dados
                })

            progress.progress((i+1)/total)

        df_api = pd.DataFrame(dados_lista)

        if df_api.empty:
            st.error("Nenhuma empresa válida encontrada na Receita")
            st.stop()

        df = df.merge(df_api, left_on=col_cnpj, right_on="CNPJ", how="inner")

        # filtrar SC
        df = df[df["uf"] == "SC"]

        if df.empty:
            st.warning("Nenhuma empresa de SC encontrada")
            st.stop()

        # ========================
        # RANKING
        # ========================
        ranking = (
            df.groupby(["CNPJ","empresa","telefone","socios","cidade"])
            .size()
            .reset_index(name="Afastamentos")
        )

        if not ranking.empty:
            ranking[["Score","Nivel"]] = ranking["Afastamentos"].apply(score_empresa)

        # ========================
        # DASHBOARD
        # ========================
        st.success("Processamento concluído")

        c1, c2, c3 = st.columns(3)
        c1.metric("Empresas", ranking.shape[0])
        c2.metric("Registros", df.shape[0])
        c3.metric("SC", ranking.shape[0])

        st.markdown("## 📊 Ranking")
        st.dataframe(ranking, use_container_width=True)

        st.bar_chart(ranking.set_index("empresa")["Afastamentos"])

        st.markdown("## 📋 Dados")
        st.dataframe(df, use_container_width=True)

# ================================
# 🔎 ABA 2 - CONSULTA + FAP
# ================================
with aba2:

    st.subheader("🔎 Consulta Completa + FAP")

    # ================================
    # 🔧 API
    # ================================
    @st.cache_data(ttl=86400)
    def consultar_cnpj_seguro(cnpj):
        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
            r = requests.get(url, timeout=5)

            if r.status_code == 200:
                data = r.json()

                if isinstance(data, dict):
                    return {
                        "empresa": data.get("razao_social",""),
                        "fantasia": data.get("nome_fantasia",""),
                        "telefone": data.get("ddd_telefone_1",""),
                        "cidade": data.get("municipio",""),
                        "uf": data.get("uf",""),
                        "cnae": data.get("cnae_fiscal_descricao",""),
                        "socios": ", ".join([q.get("nome_socio","") for q in data.get("qsa",[])])
                    }

        except:
            pass

        return {}

    # ================================
    # 🧠 CNPJ
    # ================================
    cnpj_input = st.text_input("Digite o CNPJ")

    dados = {}

    if cnpj_input:
        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)

        if len(cnpj) == 14:

            with st.spinner("Consultando Receita..."):
                dados = consultar_cnpj_seguro(cnpj)

            if dados and dados.get("empresa"):

                st.success("Empresa encontrada")

                col1, col2 = st.columns(2)

                col1.write(f"🏢 Empresa: {dados['empresa']}")
                col1.write(f"🏷 Fantasia: {dados['fantasia']}")
                col1.write(f"📞 Telefone: {dados['telefone']}")

                col2.write(f"📍 Cidade: {dados['cidade']}")
                col2.write(f"🌎 UF: {dados['uf']}")
                col2.write(f"🏭 CNAE: {dados['cnae']}")

                st.write(f"👥 Sócios: {dados['socios']}")

            else:
                st.error("❌ CNPJ não encontrado ou API instável")

    # ================================
    # 📊 DADOS
    # ================================
    st.markdown("## 📊 Dados da Empresa")

    colA, colB, colC = st.columns(3)

    funcionarios = colA.number_input("👷 Nº Funcionários", 0)
    ano_inicio = colB.number_input("📅 Ano início problema", 2000, 2035)
    folha = colC.number_input("💰 Folha salarial mensal (R$)", 0.0)

    # ================================
    # 📊 BENEFÍCIOS
    # ================================
    st.markdown("## ⚠️ Benefícios INSS")

    c1, c2, c3, c4 = st.columns(4)

    b91 = c1.number_input("B91", 0)
    b31 = c2.number_input("B31", 0)
    b94 = c3.number_input("B94", 0)
    outros = c4.number_input("Outros", 0)

    total_afast = b91 + b31 + b94 + outros
    st.info(f"Total de afastamentos: {total_afast}")

    # ================================
    # 📊 FAP
    # ================================
    st.markdown("## 📊 Parâmetros FAP")

    c1, c2 = st.columns(2)

    rat = c1.number_input("RAT (ex: 0.02)", 0.0)
    fap_atual = c2.number_input("FAP atual", 0.5, 2.0)

    fap_ideal = st.slider("FAP ideal", 0.5, 2.0, 1.0)

    # ================================
    # 💰 CÁLCULO
    # ================================
    if st.button("💰 Calcular Impacto Financeiro"):

        if folha > 0 and rat > 0:

            valor_atual = folha * rat * fap_atual
            valor_correto = folha * rat * fap_ideal

            economia = max(valor_atual - valor_correto, 0)

            economia_anual = economia * 12
            recuperavel = economia * 60

            st.markdown("## 💰 Resultado")

            c1, c2, c3 = st.columns(3)

            c1.metric("💸 Valor Atual", f"R$ {valor_atual:,.2f}")
            c2.metric("✅ Valor Correto", f"R$ {valor_correto:,.2f}")
            c3.metric("📉 Economia Mensal", f"R$ {economia:,.2f}")

            c4, c5 = st.columns(2)

            c4.metric("📊 Economia Anual", f"R$ {economia_anual:,.2f}")
            c5.metric("🏦 Recuperável (5 anos)", f"R$ {recuperavel:,.2f}")

        else:
            st.warning("Preencha folha e RAT")

    # ================================
    # 📝 OBS
    # ================================
    st.markdown("## 📝 Observações")

    obs = st.text_area("Anotações")

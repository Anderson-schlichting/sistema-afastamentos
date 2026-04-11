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
# 🔎 ABA 2 FINAL COMPLETA (PRO)
# ================================
with aba2:

    import datetime
    from io import BytesIO
    import pandas as pd

    try:
        import plotly.graph_objects as go
        PLOTLY_OK = True
    except:
        PLOTLY_OK = False

    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        PDF_OK = True
    except:
        PDF_OK = False

    def br(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

    st.subheader("🔎 Diagnóstico Comercial FAP")

    # ================================
    # 📡 API
    # ================================
    @st.cache_data(ttl=86400)
    def consultar_cnpj(cnpj):
        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return {
                    "empresa": data.get("razao_social",""),
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
    cnpj = ""

    if cnpj_input:
        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)
        dados = consultar_cnpj(cnpj)

        if dados.get("empresa"):
            st.success("Empresa encontrada")
            st.write(f"🏢 {dados['empresa']}")
            st.write(f"📞 {dados['telefone']}")
            st.write(f"👥 {dados['socios']}")
            st.write(f"📍 {dados['cidade']} - {dados['uf']}")
            st.write(f"🏭 CNAE: {dados['cnae']}")

    # ================================
    # 💰 ENTRADA
    # ================================
    st.markdown("## 💰 Dados Financeiros")

    folha_input = st.text_input("Folha salarial mensal (R$)", "500000")

    def parse(valor):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".")
        try:
            return float(valor)
        except:
            return 0

    folha = parse(folha_input)
    st.write(f"💰 Interpretado: {br(folha)}")

    col1, col2 = st.columns(2)
    rat = col1.number_input("RAT (%)", 1.0, 3.0, 2.0) / 100
    fap_atual = col2.number_input("FAP atual", 0.5, 2.0, 1.5)

    fap_ideal = max(fap_atual - 0.5, 0.5)
    st.info(f"FAP ideal estimado: {fap_ideal:.2f}")

    ano_inicio = st.number_input("Ano início problema", 2000, 2035, 2023)

    # ================================
    # 📝 ANOTAÇÕES
    # ================================
    obs = st.text_area("📝 Anotações sobre o cliente")

    # ================================
    # 🚀 CÁLCULO
    # ================================
    if st.button("🚀 Gerar Diagnóstico"):

        hoje = datetime.datetime.now()
        meses = (hoje.year - ano_inicio) * 12 + hoje.month

        atual = folha * rat * fap_atual
        correto = folha * rat * fap_ideal
        economia = max(atual - correto, 0)

        recuperavel = economia * meses
        honorarios = recuperavel * 0.20
        mensalidade = 5000
        total = honorarios + (mensalidade * 12)

        st.markdown("## 💰 Resultado")

        st.metric("Pago Atual", br(atual))
        st.metric("Valor Correto", br(correto))
        st.metric("Economia Mensal", br(economia))

        st.metric("Recuperável", br(recuperavel))
        st.metric("Honorários", br(honorarios))
        st.metric("Projeto Total", br(total))

        # ================================
        # 📊 GRÁFICOS
        # ================================
        if PLOTLY_OK:

            meses_lista = list(range(1,13))

            fig = go.Figure()
            fig.add_bar(x=meses_lista, y=[atual]*12, name="Atual", marker_color="red")
            fig.add_bar(x=meses_lista, y=[correto]*12, name="Correto", marker_color="green")
            fig.add_bar(x=meses_lista, y=[correto+mensalidade]*12, name="Correto + Serviço", marker_color="blue")

            st.plotly_chart(fig)

            # gráfico recuperação
            acumulado = [economia * i for i in meses_lista]
            fig2 = go.Figure()
            fig2.add_scatter(x=meses_lista, y=acumulado, mode="lines+markers")

            st.plotly_chart(fig2)

        # ================================
        # 📄 PDF COM GRÁFICO
        # ================================
        if PDF_OK and PLOTLY_OK:

            img_bytes = fig.to_image(format="png")

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            styles = getSampleStyleSheet()

            story = [
                Paragraph(f"Empresa: {dados.get('empresa','')}", styles["Normal"]),
                Paragraph(f"Recuperável: {br(recuperavel)}", styles["Normal"]),
                Paragraph(f"Honorários: {br(honorarios)}", styles["Normal"]),
                Paragraph(f"Observações: {obs}", styles["Normal"]),
                Image(BytesIO(img_bytes), width=400, height=200)
            ]

            doc.build(story)

            st.download_button("📄 Baixar PDF", buffer.getvalue(), "proposta.pdf")

        # ================================
        # 📚 HISTÓRICO
        # ================================
        if "historico" not in st.session_state:
            st.session_state["historico"] = []

        st.session_state["historico"].append({
            "data": str(datetime.datetime.now()),
            "empresa": dados.get("empresa",""),
            "cnpj": cnpj,
            "recuperavel": br(recuperavel)
        })

    # ================================
    # 📚 VISUAL HISTÓRICO
    # ================================
    st.markdown("## 📚 Histórico")

    if "historico" in st.session_state:
        st.dataframe(st.session_state["historico"])

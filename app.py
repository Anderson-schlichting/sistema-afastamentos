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
# 📊 ABA 1 - PROSPECÇÃO COMPLETA SC
# ================================
import pandas as pd
import time
import requests

st.subheader("📊 Prospecção Inteligente - Santa Catarina")

CIDADES_SC = [
    "BLUMENAU","JOINVILLE","FLORIANÓPOLIS","CHAPECÓ","ITAJAÍ","LAGES",
    "CRICIÚMA","RIO DO SUL","JARAGUÁ DO SUL","PALHOÇA"
]

file = st.file_uploader("Envie CSV ou Excel")

def carregar_arquivo(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, sep=';', encoding='latin1')
        return pd.read_excel(file)
    except:
        return None

def detectar_cnpj(df):
    for c in df.columns:
        if "CNPJ" in c.upper():
            return c
    return None

def limpar_cidade(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor)
    if "-" in valor:
        valor = valor.split("-", 1)[1]
    return valor.strip().upper()

@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=3)
        if r.status_code == 200:
            data = r.json()
            return {
                "empresa": data.get("razao_social",""),
                "telefone": data.get("ddd_telefone_1",""),
                "cidade_api": data.get("municipio",""),
                "uf": data.get("uf",""),
                "socios": ", ".join([q.get("nome_socio","") for q in data.get("qsa",[])])
            }
    except:
        pass
    return {}

if file is not None and st.button("🚀 Processar"):

    df = carregar_arquivo(file)

    if df is None:
        st.error("Erro ao ler arquivo")
        st.stop()

    df.columns = df.columns.astype(str).str.strip()

    col_cnpj = detectar_cnpj(df)

    if col_cnpj is None:
        st.error("Coluna CNPJ não encontrada")
        st.stop()

    df[col_cnpj] = (
        df[col_cnpj].astype(str)
        .str.replace(r"\D","",regex=True)
        .str.zfill(14)
    )

    df = df[df[col_cnpj].duplicated(keep=False)]

    col_cidade = None
    for c in df.columns:
        if "MUNIC" in c.upper() or "CIDADE" in c.upper():
            col_cidade = c
            break

    if col_cidade:
        df["cidade"] = df[col_cidade].apply(limpar_cidade)
    else:
        df["cidade"] = ""

    st.markdown("## 🔄 Processando...")

    progress_bar = st.progress(0)
    status = st.empty()

    dados_lista = []
    cnpjs = df[col_cnpj].unique()
    total = len(cnpjs)

    with st.spinner("Consultando Receita..."):

        for i, cnpj in enumerate(cnpjs):

            pct = int(((i + 1) / total) * 100)

            status.markdown(f"### 🔄 {pct}% concluído")
            progress_bar.progress(pct)

            dados = consultar_cnpj(cnpj)

            if dados.get("empresa"):
                dados_lista.append({"CNPJ": cnpj, **dados})

            time.sleep(0.02)

    df_api = pd.DataFrame(dados_lista)

    if df_api.empty:
        st.error("Nenhuma empresa encontrada na Receita")
        st.stop()

    df = df.merge(df_api, left_on=col_cnpj, right_on="CNPJ", how="inner")

    df["cidade_api"] = df["cidade_api"].astype(str).str.upper()
    df["cidade"] = df["cidade"].astype(str).str.upper()

    df = df[
        (df["uf"] == "SC") |
        (df["cidade_api"].isin(CIDADES_SC)) |
        (df["cidade"].isin(CIDADES_SC))
    ]

    if df.empty:
        st.warning("Nenhuma empresa de SC encontrada")
        st.stop()

    ranking = df["cidade_api"].value_counts().reset_index()
    ranking.columns = ["Cidade", "Empresas"]

    st.dataframe(ranking)

    import pandas as pd
    import streamlit as st
    import time
    import requests

    st.subheader("📊 Prospecção Inteligente - Santa Catarina")

CIDADES_SC = [
"ABELARDO LUZ","AGROLÂNDIA","AGRONÔMICA","ÁGUA DOCE","ÁGUAS DE CHAPECÓ",
"ÁGUAS FRIAS","ÁGUAS MORNAS","ALFREDO WAGNER","ALTO BELA VISTA",
"ANCHIETA","ANGELINA","ANITA GARIBALDI","ANITÁPOLIS","ANTÔNIO CARLOS",
"APIÚNA","ARABUTÃ","ARAQUARI","ARARANGUÁ","ARMAZÉM","ARROIO TRINTA",
"ARVOREDO","ASCURRA","ATALANTA","AURORA","BALNEÁRIO ARROIO DO SILVA",
"BALNEÁRIO CAMBORIÚ","BALNEÁRIO BARRA DO SUL","BALNEÁRIO GAIVOTA",
"BARRA BONITA","BARRA VELHA","BELMONTE","BENEDITO NOVO","BIGUAÇU",
"BLUMENAU","BOCAINA DO SUL","BOMBINHAS","BOM JARDIM DA SERRA",
"BOM JESUS","BOM JESUS DO OESTE","BOM RETIRO","BOTUVERÁ","BRAÇO DO NORTE",
"BRAÇO DO TROMBUDO","BRUNÓPOLIS","BRUSQUE","CAÇADOR","CAIBI","CALMON",
"CAMBORIÚ","CAMPO ALEGRE","CAMPO BELO DO SUL","CAMPO ERÊ",
"CAMPOS NOVOS","CANELINHA","CANOINHAS","CAPÃO ALTO","CAPINZAL",
"CAPIVARI DE BAIXO","CATANDUVAS","CAXAMBU DO SUL","CELSO RAMOS",
"CHAPADÃO DO LAGEADO","CHAPECÓ","COCAL DO SUL","CONCÓRDIA",
"CORDILHEIRA ALTA","CORONEL FREITAS","CORONEL MARTINS","CORUPÁ",
"CRICIÚMA","CUNHA PORÃ","CUNHATAÍ","CURITIBANOS","DESCANSO",
"DIONÍSIO CERQUEIRA","DONA EMMA","DOUTOR PEDRINHO","ENTRE RIOS",
"ERMO","ERVAL VELHO","FAXINAL DOS GUEDES","FLOR DO SERTÃO",
"FLORIANÓPOLIS","FORMOSA DO SUL","FORQUILHINHA","FRAIBURGO",
"FREI ROGÉRIO","GALVÃO","GAROPABA","GARUVA","GASPAR",
"GOIO-EN","GOVERNADOR CELSO RAMOS","GRÃO-PARÁ","GRAVATAL",
"GUABIRUBA","GUARACIABA","GUARAMIRIM","GUARUJÁ DO SUL",
"GUATAMBÚ","HERVAL D’OESTE","IBIAM","IBICARÉ","IBIRAMA",
"IÇARA","ILHOTA","IMARUÍ","IMBITUBA","IMBUIA","INDAIAL",
"IOMERÊ","IPIRA","IPORÃ DO OESTE","IPUAÇU","IPUMIRIM",
"IRACEMINHA","IRANI","IRATI","IRINEÓPOLIS","ITÁ","ITAÍÓPOLIS",
"ITAJÁ","ITAPEMA","ITAPIRANGA","ITAPOÁ","ITUPORANGA",
"JABORÁ","JACINTO MACHADO","JAGUARUNA","JARAGUÁ DO SUL",
"JARDINÓPOLIS","JOAÇABA","JOINVILLE","JOSÉ BOITEUX",
"JUPIÁ","LACERDÓPOLIS","LAGES","LAGUNA","LAJEADO GRANDE",
"LAURENTINO","LAURO MÜLLER","LEBON RÉGIS","LEOBERTO LEAL",
"LINDÓIA DO SUL","LONTRAS","LUIZ ALVES","LUZERNA","MACIEIRA",
"MAFRA","MAJOR GERCINO","MAJOR VIEIRA","MARACAJÁ","MARAVILHA",
"MAREMA","MASSARANDUBA","MATOS COSTA","MELEIRO","MIRIM DOCE",
"MODELO","MONDAÍ","MONTE CARLO","MONTE CASTELO","MORRO DA FUMAÇA",
"MORRO GRANDE","NAVEGANTES","NOVA ERECHIM","NOVA ITABERABA",
"NOVA TRENTO","NOVA VENEZA","NOVO HORIZONTE","ORLEANS","OTACÍLIO COSTA",
"OURO","OURO VERDE","PAIAL","PAINEL","PALHOÇA","PALMA SOLA",
"PALMEIRA","PALMITOS","PAPANDUVA","PARAÍSO","PASSO DE TORRES",
"PASSOS MAIA","PAULO LOPES","PEDRAS GRANDES","PENHA","PERITIBA",
"PESCARIA BRAVA","PETROLÂNDIA","PIÇARRAS","PINHALZINHO","PINHEIRO PRETO",
"PIRATUBA","PLANALTO ALEGRE","POMERODE","PONTE ALTA",
"PONTE ALTA DO NORTE","PONTE SERRADA","PORTO BELO","PORTO UNIÃO",
"POUSO REDONDO","PRAIA GRANDE","PRESIDENTE CASTELLO BRANCO",
"PRESIDENTE GETÚLIO","PRESIDENTE NEREU","PRINCESA","QUILOMBO",
"RANCHO QUEIMADO","RIO DAS ANTAS","RIO DO CAMPO","RIO DO OESTE",
"RIO DOS CEDROS","RIO DO SUL","RIO FORTUNA","RIO NEGRINHO",
"RIO RUFINO","RIQUEZA","RODEIO","ROMELÂNDIA","SALETE",
"SALTINHO","SALTO VELOSO","SANGÃO","SANTA CECÍLIA",
"SANTA HELENA","SANTA ROSA DE LIMA","SANTA ROSA DO SUL",
"SANTA TEREZINHA","SANTA TEREZINHA DO PROGRESSO",
"SANTIAGO DO SUL","SANTO AMARO DA IMPERATRIZ","SÃO BENTO DO SUL",
"SÃO BERNARDINO","SÃO BONIFÁCIO","SÃO CARLOS","SÃO CRISTÓVÃO DO SUL",
"SÃO DOMINGOS","SÃO FRANCISCO DO SUL","SÃO JOÃO BATISTA",
"SÃO JOÃO DO ITAPERIÚ","SÃO JOÃO DO OESTE","SÃO JOÃO DO SUL",
"SÃO JOAQUIM","SÃO JOSÉ","SÃO JOSÉ DO CEDRO","SÃO JOSÉ DO CERRITO",
"SÃO LOURENÇO DO OESTE","SÃO LUDGERO","SÃO MARTINHO",
"SÃO MIGUEL DA BOA VISTA","SÃO MIGUEL DO OESTE","SÃO PEDRO DE ALCÂNTARA",
"SAUDADES","SCHROEDER","SEARA","SERRA ALTA","SIDERÓPOLIS",
"SOMBRIO","SUL BRASIL","TAIÓ","TANGARÁ","TIGRINHOS","TIJUCAS",
"TIMBÉ DO SUL","TIMBÓ","TIMBÓ GRANDE","TRÊS BARRAS","TREVISO",
"TREZE DE MAIO","TREZE TÍLIAS","TROMBUDO CENTRAL","TUBARÃO",
"TUNÁPOLIS","TURVO","UNIÃO DO OESTE","URUBICI","URUPEMA",
"URUPEMA","URUSSANGA","VARGEÃO","VARGEM","VARGEM BONITA",
"VIDAL RAMOS","VIDEIRA","VITOR MEIRELES","WITMARSUM","XANXERÊ",
"XAVANTINA","XAXIM","ZORTÉA"
]
    # ================================
    # 📂 UPLOAD
    # ================================
    file = st.file_uploader("Envie CSV ou Excel")

    # ================================
    # 📂 LEITURA
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
    # 📡 API
    # ================================
    @st.cache_data(ttl=86400)
    def consultar_cnpj(cnpj):
        try:
            r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}", timeout=3)
            if r.status_code == 200:
                data = r.json()
                return {
                    "empresa": data.get("razao_social",""),
                    "telefone": data.get("ddd_telefone_1",""),
                    "cidade_api": data.get("municipio",""),
                    "uf": data.get("uf",""),
                    "socios": ", ".join([q.get("nome_socio","") for q in data.get("qsa",[])])
                }
        except:
            pass
        return {}

    # ================================
    # 🚀 PROCESSAMENTO
    # ================================
    if file is not None and st.button("🚀 Processar"):

        df = carregar_arquivo(file)

        if df is None:
            st.error("Erro ao ler arquivo")
            st.stop()

        df.columns = df.columns.astype(str).str.strip()

        col_cnpj = detectar_cnpj(df)

        if col_cnpj is None:
            st.error("Coluna CNPJ não encontrada")
            st.stop()

        # normalizar CNPJ
        df[col_cnpj] = (
            df[col_cnpj]
            .astype(str)
            .str.replace(r"\D","",regex=True)
            .str.zfill(14)
        )

        # pegar duplicados
        df = df[df[col_cnpj].duplicated(keep=False)]

        # ================================
        # 📍 CIDADE CSV
        # ================================
        col_cidade = None
        for c in df.columns:
            if "MUNIC" in c.upper() or "CIDADE" in c.upper():
                col_cidade = c
                break

        if col_cidade is not None:
            df["cidade"] = df[col_cidade].apply(limpar_cidade)
        else:
            df["cidade"] = ""

        # ================================
        # 🔄 CONSULTA API COM %
        # ================================
        st.markdown("## 🔄 Processando...")

        progress_bar = st.progress(0)
        status = st.empty()

        dados_lista = []
        cnpjs = df[col_cnpj].unique()
        total = len(cnpjs)

        with st.spinner("Consultando Receita..."):

            for i, cnpj in enumerate(cnpjs):

                pct = int(((i + 1) / total) * 100)

                status.markdown(f"### 🔄 {pct}% concluído")
                progress_bar.progress(pct)

                dados = consultar_cnpj(cnpj)

                if dados.get("empresa"):
                    dados_lista.append({"CNPJ": cnpj, **dados})

                time.sleep(0.02)

        df_api = pd.DataFrame(dados_lista)

        if df_api.empty:
            st.error("Nenhuma empresa encontrada na Receita")
            st.stop()

        # ================================
        # 🔗 MERGE
        # ================================
        df = df.merge(df_api, left_on=col_cnpj, right_on="CNPJ", how="inner")

        # ================================
        # 📍 FILTRO SC
        # ================================
        df["cidade_api"] = df["cidade_api"].astype(str).str.upper()
        df["cidade"] = df["cidade"].astype(str).str.upper()

        df = df[
            (df["uf"] == "SC") |
            (df["cidade_api"].isin(CIDADES_SC)) |
            (df["cidade"].isin(CIDADES_SC))
        ]

        if df.empty:
            st.warning("Nenhuma empresa de SC encontrada")
            st.stop()

        # ================================
        # 📊 RANKING
        # ================================
        ranking = df["cidade_api"].value_counts().reset_index()
        ranking.columns = ["Cidade", "Empresas"]

        st.markdown("## 📊 Ranking por Cidade")
        st.dataframe(ranking, use_container_width=True)

        st.bar_chart(ranking.set_index("Cidade"))

        # ================================
        # 🗺️ MAPA
        # ================================
        st.markdown("## 🗺️ Mapa")

        mapa = ranking.copy()
        mapa["lat"] = -27
        mapa["lon"] = -50

        st.map(mapa)

        # ================================
        # 📋 LEADS
        # ================================
        st.markdown("## 📋 Leads")

        leads = df[["empresa","telefone","socios","cidade_api"]]

        st.dataframe(leads, use_container_width=True)

        # ================================
        # 📲 WHATSAPP
        # ================================
        st.markdown("## 📲 Contato Rápido")

        for _, row in leads.head(10).iterrows():

            tel = str(row["telefone"])
            tel = tel.replace("(","").replace(")","").replace("-","").replace(" ","")

            if tel and tel != "nan":

                link = f"https://wa.me/55{tel}?text=Olá, analisamos sua empresa e identificamos oportunidades de redução no FAP."

                st.markdown(f"👉 {row['empresa']} - [WhatsApp]({link})")
# ================================
# 🔎 ABA 2 FINAL ESTÁVEL
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
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        PDF_OK = True
    except:
        PDF_OK = False

    # ================================
    # 💰 FORMATAÇÃO BR
    # ================================
    def br(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

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

    st.subheader("🔎 Diagnóstico Comercial FAP")

    # ================================
    # 🧠 CNPJ
    # ================================
    cnpj_input = st.text_input("Digite o CNPJ")
    dados = {}
    cnpj = ""

    if cnpj_input:
        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)

        with st.spinner("Consultando Receita..."):
            dados = consultar_cnpj(cnpj)

        if dados.get("empresa"):
            st.success("Empresa encontrada")

            col1, col2 = st.columns(2)

            col1.write(f"🏢 {dados['empresa']}")
            col1.write(f"📞 {dados['telefone']}")
            col1.write(f"👥 {dados['socios']}")

            col2.write(f"📍 {dados['cidade']} - {dados['uf']}")
            col2.write(f"🏭 CNAE: {dados['cnae']}")
        else:
            st.warning("CNPJ não localizado")

    # ================================
    # 💰 ENTRADA EM R$
    # ================================
    st.markdown("## 💰 Dados Financeiros")

    folha_input = st.text_input("Folha salarial mensal (R$)", "50000")

    def parse(valor):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(valor)
        except:
            return 0.0

    folha = parse(folha_input)

    if folha > 0:
        st.write(f"💰 Interpretado: {br(folha)}")

    # ================================
    # 📊 PARÂMETROS
    # ================================
    col1, col2 = st.columns(2)

    rat = col1.number_input("RAT (%)", min_value=1.0, max_value=3.0, value=2.0) / 100
    fap_atual = col2.number_input("FAP atual", min_value=0.5, max_value=2.0, value=1.5)

    fap_ideal = max(fap_atual - 0.5, 0.5)

    st.info(f"FAP ideal estimado: {fap_ideal:.2f}")

    rat_ajustado = rat * fap_atual
    st.warning(f"RAT ajustado: {(rat_ajustado*100):.2f}%")

    ano_inicio = st.number_input("Ano início problema", 2000, 2035, 2023)

    # ================================
    # 📝 ANOTAÇÕES
    # ================================
    obs = st.text_area("📝 Anotações")

    # ================================
    # 🚀 CÁLCULO
    # ================================
    if st.button("🚀 Gerar Diagnóstico"):

        if folha > 0:

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
            # 📊 GRÁFICO
            # ================================
            if PLOTLY_OK:

                meses_lista = list(range(1, 13))

                fig = go.Figure()

                fig.add_bar(x=meses_lista, y=[atual]*12, name="Atual", marker_color="red")
                fig.add_bar(x=meses_lista, y=[correto]*12, name="Correto", marker_color="green")
                fig.add_bar(x=meses_lista, y=[correto+mensalidade]*12, name="Correto + Serviço", marker_color="blue")

                fig.update_layout(title="Comparativo Mensal", barmode="group")

                st.plotly_chart(fig, use_container_width=True)

            # ================================
            # 📄 PROPOSTA
            # ================================
            proposta = f"""
Empresa: {dados.get('empresa','')}

Valor atual: {br(atual)}
Valor correto: {br(correto)}

Economia mensal: {br(economia)}
Recuperação: {br(recuperavel)}

Honorários: {br(honorarios)}
Mensalidade: R$ 5.000,00

Projeto total: {br(total)}

Observações:
{obs}
"""

            st.markdown("## 📄 Proposta")
            st.text_area("Copiar proposta", proposta, height=250)

            # ================================
            # 📄 PDF (SEM ERRO)
            # ================================
            if PDF_OK:

                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()

                story = [
                    Paragraph(f"Empresa: {dados.get('empresa','')}", styles["Normal"]),
                    Paragraph(f"Recuperável: {br(recuperavel)}", styles["Normal"]),
                    Paragraph(f"Honorários: {br(honorarios)}", styles["Normal"]),
                    Paragraph(f"Observações: {obs}", styles["Normal"]),
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
    # 📚 HISTÓRICO
    # ================================
    st.markdown("## 📚 Histórico")

    if "historico" in st.session_state:
        st.dataframe(st.session_state["historico"])

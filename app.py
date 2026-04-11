import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente Empresas + FAP")

# ================================
# 📊 ABAS
# ================================
aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Prospecção Inteligente - SC")

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

    # ================================
    # 🧾 NORMALIZAR CNPJ
    # ================================
    df[col_cnpj] = (
        df[col_cnpj].astype(str)
        .str.replace(r"\D","",regex=True)
        .str.zfill(14)
    )

    # ================================
    # 📍 IDENTIFICAR CIDADE (CSV)
    # ================================
    col_cidade = None
    for c in df.columns:
        if "MUNIC" in c.upper() or "CIDADE" in c.upper():
            col_cidade = c
            break

    if col_cidade:
        df["cidade"] = df[col_cidade].apply(limpar_cidade)
    else:
        df["cidade"] = ""

    df["cidade"] = df["cidade"].astype(str).str.upper()

    # ================================
    # 📍 FILTRAR SC (ANTES DA API)
    # ================================
    df = df[df["cidade"].isin(CIDADES_SC)]

    if df.empty:
        st.warning("Nenhuma empresa de SC encontrada na base")
        st.stop()

    st.success(f"{len(df)} registros em SC encontrados")

    # ================================
    # 📊 AGRUPAR AFASTAMENTOS
    # ================================
    agrupado = df.groupby(col_cnpj).size().reset_index(name="Afastamentos")

    # ================================
    # 🔄 CONSULTA COM RETRY (3x)
    # ================================
    st.markdown("## 🔄 Consultando Receita...")

    progress = st.progress(0)
    status = st.empty()

    dados_lista = []
    falhas = []

    cnpjs = agrupado[col_cnpj].tolist()
    total = len(cnpjs)

    def consultar_com_retry(cnpj, tentativas=3):
        for i in range(tentativas):
            dados = consultar_cnpj(cnpj)
            if dados.get("empresa"):
                return dados
            time.sleep(1)
        return None

    # 🔎 PRIMEIRA PASSADA
    for i, cnpj in enumerate(cnpjs):

        pct = int(((i+1)/total)*100)
        progress.progress(pct)
        status.markdown(f"### 🔄 {pct}%")

        dados = consultar_com_retry(cnpj)

        if dados:
            dados_lista.append({"CNPJ": cnpj, **dados})
        else:
            falhas.append(cnpj)

    # 🔁 SEGUNDA PASSADA (FALHAS)
    if falhas:
        st.warning(f"Tentando novamente {len(falhas)} CNPJs...")

        for cnpj in falhas:
            dados = consultar_com_retry(cnpj)

            if dados:
                dados_lista.append({"CNPJ": cnpj, **dados})

    df_api = pd.DataFrame(dados_lista)

    if df_api.empty:
        st.error("Nenhuma empresa validada na Receita")
        st.stop()

    # ================================
    # 🔗 MERGE FINAL
    # ================================
    final = agrupado.merge(df_api, left_on=col_cnpj, right_on="CNPJ", how="inner")

    # ================================
    # 📊 RANKING FINAL
    # ================================
    ranking = final.sort_values("Afastamentos", ascending=False)

    st.markdown("## 📊 Ranking Final")

    st.dataframe(
        ranking[[
            col_cnpj,
            "empresa",
            "telefone",
            "socios",
            "cidade_api",
            "Afastamentos"
        ]],
        use_container_width=True
    )

    # ================================
    # 📋 LEADS
    # ================================
    st.markdown("## 📋 Leads Prioritários")

    top = ranking.head(20)

    for _, row in top.iterrows():

        tel = str(row["telefone"]).replace("(","").replace(")","").replace("-","").replace(" ","")

        st.write(f"🏢 {row['empresa']}")
        st.write(f"📍 {row['cidade_api']}")
        st.write(f"👥 {row['socios']}")
        st.write(f"📊 Afastamentos: {row['Afastamentos']}")

        if tel and tel != "nan":
            link = f"https://wa.me/55{tel}?text=Olá, identificamos oportunidades de redução no FAP da sua empresa."
            st.markdown(f"[📲 WhatsApp]({link})")

        st.divider()

# ================================
# 🔄 CONSULTA EM BLOCOS + RETRY
# ================================
st.markdown("## 🔄 Consultando Receita (modo otimizado)...")

progress = st.progress(0)
status = st.empty()

dados_lista = []
falhas = []

cnpjs = agrupado[col_cnpj].tolist()
total = len(cnpjs)

BLOCO = 20  # você pode mudar para 30 ou 50

def consultar_com_retry(cnpj, tentativas=2):
    for _ in range(tentativas):
        dados = consultar_cnpj(cnpj)
        if dados.get("empresa"):
            return dados
        time.sleep(0.5)
    return None

# ================================
# 🚀 PROCESSAMENTO EM BLOCOS
# ================================
for i in range(0, total, BLOCO):

    bloco = cnpjs[i:i+BLOCO]

    status.markdown(f"### 🔄 Processando lote {int(i/BLOCO)+1}")

    for cnpj in bloco:

        dados = consultar_com_retry(cnpj)

        if dados:
            dados_lista.append({"CNPJ": cnpj, **dados})
        else:
            falhas.append(cnpj)

    progresso = int((min(i+BLOCO, total) / total) * 100)
    progress.progress(progresso)

# ================================
# 🔁 REPROCESSAR FALHAS
# ================================
if falhas:
    st.warning(f"🔁 Reprocessando {len(falhas)} falhas...")

    for cnpj in falhas:

        dados = consultar_com_retry(cnpj, tentativas=3)

        if dados:
            dados_lista.append({"CNPJ": cnpj, **dados})

# ================================
# 📊 FINAL
# ================================
df_api = pd.DataFrame(dados_lista)

        if df_api.empty:
            st.error("Nenhuma empresa encontrada")
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

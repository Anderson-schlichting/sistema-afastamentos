import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# ================================
# 📍 LISTA DE CIDADES SC
# ================================
CIDADES_SC = [ "ABDON BATISTA","ABELARDO LUZ","AGROLÂNDIA","AGRONÔMICA","ÁGUA DOCE","ÁGUAS DE CHAPECÓ",
"ÁGUAS FRIAS","ÁGUAS MORNAS","ALFREDO WAGNER","ALTO BELA VISTA","ANCHIETA","ANGELINA",
"ANITA GARIBALDI","ANITÁPOLIS","ANTÔNIO CARLOS","APIÚNA","ARABUTÃ","ARAQUARI","ARARANGUÁ",
"ARMAZÉM","ARROIO TRINTA","ARVOREDO","ASCURRA","ATALANTA","AURORA","BALNEÁRIO ARROIO DO SILVA",
"BALNEÁRIO BARRA DO SUL","BALNEÁRIO CAMBORIÚ","BALNEÁRIO GAIVOTA","BANDEIRANTE","BARRA BONITA",
"BARRA VELHA","BELA VISTA DO TOLDO","BELMONTE","BENEDITO NOVO","BIGUAÇU","BLUMENAU","BOCAINA DO SUL",
"BOMBINHAS","BOM JARDIM DA SERRA","BOM JESUS","BOM JESUS DO OESTE","BOM RETIRO","BOMBINHAS",
"BOTUVERÁ","BRAÇO DO NORTE","BRAÇO DO TROMBUDO","BRUNÓPOLIS","BRUSQUE","CAÇADOR","CAIBI",
"CALMON","CAMBORIÚ","CAMPO ALEGRE","CAMPO BELO DO SUL","CAMPO ERÊ","CAMPOS NOVOS",
"CANELINHA","CANOINHAS","CAPÃO ALTO","CAPINZAL","CAPIVARI DE BAIXO","CATANDUVAS",
"CAXAMBU DO SUL","CELSO RAMOS","CERRO NEGRO","CHAPADÃO DO LAGEADO","CHAPECÓ",
"COCAL DO SUL","CONCÓRDIA","CORDILHEIRA ALTA","CORONEL FREITAS","CORONEL MARTINS",
"CORREIA PINTO","CORUPÁ","CRICIÚMA","CUNHA PORÃ","CUNHATAÍ","CURITIBANOS",
"DESCANSO","DIONÍSIO CERQUEIRA","DONA EMMA","DOUTOR PEDRINHO","ENTRE RIOS",
"ERMO","ERVAL VELHO","FAXINAL DOS GUEDES","FLOR DO SERTÃO","FLORIANÓPOLIS",
"FORMOSA DO SUL","FORQUILHINHA","FRAIBURGO","FREI ROGÉRIO","GALVÃO",
"GAROPABA","GARUVA","GASPAR","GOVERNADOR CELSO RAMOS","GRÃO PARÁ",
"GRAVATAL","GUABIRUBA","GUARACIABA","GUARAMIRIM","GUARUJÁ DO SUL",
"GUATAMBÚ","HERVAL D'OESTE","IBIAM","IBICARÉ","IBIRAMA","IÇARA",
"ILHOTA","IMARUÍ","IMBITUBA","IMBUIA","INDAIAL","IOMERÊ","IPIRA",
"IPORÃ DO OESTE","IPUAÇU","IPUMIRIM","IRACEMINHA","IRANI","IRATI",
"IRINEÓPOLIS","ITÁ","ITAIAL","ITAJAÍ","ITAPEMA","ITAPIRANGA","ITAPOÁ",
"ITUPORANGA","JABORÁ","JACINTO MACHADO","JAGUARUNA","JARAGUÁ DO SUL",
"JARDINÓPOLIS","JOAÇABA","JOINVILLE","JOSÉ BOITEUX","JUPIÁ",
"LACERDÓPOLIS","LAGES","LAGUNA","LAURENTINO","LAURO MÜLLER",
"LEBON RÉGIS","LEOBERTO LEAL","LINDÓIA DO SUL","LONTRAS","LUIZ ALVES",
"LUZERNA","MACIEIRA","MAFRA","MAJOR GERCINO","MAJOR VIEIRA",
"MARACAJÁ","MARAVILHA","MAREMA","MASSARANDUBA","MATOS COSTA",
"MELEIRO","MIRIM DOCE","MODELO","MONDAÍ","MONTE CARLO",
"MONTE CASTELO","MORRO DA FUMAÇA","MORRO GRANDE","NAVEGANTES",
"NOVA ERECHIM","NOVA ITABERABA","NOVA TRENTO","NOVA VENEZA",
"NOVO HORIZONTE","ORLEANS","OTACÍLIO COSTA","OURO","OURO VERDE",
"PAIAL","PAINEL","PALHOÇA","PALMA SOLA","PALMEIRA","PALMITOS",
"PAPANDUVA","PARAÍSO","PASSO DE TORRES","PASSOS MAIA","PAULO LOPES",
"PEDRAS GRANDES","PENHA","PERITIBA","PESCARIA BRAVA","PETROLÂNDIA",
"PINHALZINHO","PINHEIRO PRETO","PIRATUBA","PLANALTO ALEGRE","POMERODE",
"PONTE ALTA","PONTE ALTA DO NORTE","PONTE SERRADA","PORTO BELO",
"PORTO UNIÃO","POUSO REDONDO","PRAIA GRANDE","PRESIDENTE CASTELLO BRANCO",
"PRESIDENTE GETÚLIO","PRESIDENTE NEREU","PRINCESA","QUILOMBO",
"RANCHO QUEIMADO","RIO DAS ANTAS","RIO DO CAMPO","RIO DO OESTE",
"RIO DO SUL","RIO DOS CEDROS","RIO FORTUNA","RIO NEGRINHO",
"RIO RUFINO","RIQUEZA","RODEIO","ROMELÂNDIA","SALETE",
"SALTINHO","SALTO VELOSO","SANGÃO","SANTA CECÍLIA","SANTA HELENA",
"SANTA ROSA DE LIMA","SANTA ROSA DO SUL","SANTA TEREZINHA",
"SANTA TEREZINHA DO PROGRESSO","SANTIAGO DO SUL","SANTO AMARO DA IMPERATRIZ",
"SÃO BENTO DO SUL","SÃO BERNARDINO","SÃO BONIFÁCIO","SÃO CARLOS",
"SÃO CRISTÓVÃO DO SUL","SÃO DOMINGOS","SÃO FRANCISCO DO SUL",
"SÃO JOÃO BATISTA","SÃO JOÃO DO ITAPERIÚ","SÃO JOÃO DO OESTE",
"SÃO JOÃO DO SUL","SÃO JOAQUIM","SÃO JOSÉ","SÃO JOSÉ DO CEDRO",
"SÃO JOSÉ DO CERRITO","SÃO LOURENÇO DO OESTE","SÃO LUDGERO",
"SÃO MARTINHO","SÃO MIGUEL DA BOA VISTA","SÃO MIGUEL DO OESTE",
"SÃO PEDRO DE ALCÂNTARA","SAUDADES","SCHROEDER","SEARA",
"SERRA ALTA","SIDERÓPOLIS","SOMBRIO","SUL BRASIL","TAIÓ",
"TANGARÁ","TIGRINHOS","TIJUCAS","TIMBÉ DO SUL","TIMBÓ",
"TIMBÓ GRANDE","TRÊS BARRAS","TREVISO","TREZE DE MAIO",
"TREZE TÍLIAS","TROMBUDO CENTRAL","TUBARÃO","TUNÁPOLIS",
"TURVO","UNIÃO DO OESTE","URUBICI","URUPEMA","URUSSANGA",
"VARGEÃO","VARGEM","VARGEM BONITA","VIDAL RAMOS","VIDEIRA",
"VITOR MEIRELES","WITMARSUM","XANXERÊ","XAVANTINA","XAXIM",
"ZORTÉA"]

# ================================
# 📂 LEITURA CSV (CORRIGIDA)
# ================================
def carregar_arquivo(file):
    if file.name.endswith(".csv"):
        for enc in ["utf-8", "latin1", "ISO-8859-1"]:
            try:
                return pd.read_csv(file, sep=None, engine="python", encoding=enc)
            except:
                continue
        st.error("Erro ao ler CSV")
        return None
    else:
        return pd.read_excel(file, engine="openpyxl")

# ================================
# 🚀 API CONSULTA CNPJ
# ================================
@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)

        if r.status_code == 200:
            d = r.json()
            return {
                "Empresa": d.get("razao_social",""),
                "Fantasia": d.get("nome_fantasia",""),
                "Telefone": d.get("ddd_telefone_1",""),
                "Email": d.get("email",""),
                "Cidade": d.get("municipio",""),
                "UF": d.get("uf",""),
                "CNAE": d.get("cnae_fiscal_descricao",""),
            }
    except:
        pass

    return {}

# ================================
# 🔍 FILTROS
# ================================
def aplicar_filtros(df, usar_sc=False, cidade=None):
    df = df.copy()

    if usar_sc:
        if "Estado" in df.columns:
            df = df[df["Estado"].str.upper().str.contains("SANTA CATARINA|SC", na=False)]

    if cidade and cidade != "Todas" and "Cidade" in df.columns:
        df["Cidade"] = df["Cidade"].str.upper()
        df = df[df["Cidade"] == cidade]

    return df

# ================================
# 🖥️ APP
# ================================
st.title("📊 Sistema Inteligente de Empresas")

aba1, aba2 = st.tabs(["📊 Análise de Empresas", "🔎 Consulta CNPJ"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    file = st.file_uploader("Envie Excel ou CSV")

    if file and st.button("🚀 Processar"):

        inicio = time.time()

        df = carregar_arquivo(file)
        df.columns = df.columns.str.strip()

        col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

        df[col_cnpj] = df[col_cnpj].astype(str).str.replace(r'\D','',regex=True).str.zfill(14)

        contagem = df[col_cnpj].value_counts()
        df_resultado = df[df[col_cnpj].isin(contagem[contagem > 1].index)]

        # filtros
        usar_sc = st.sidebar.checkbox("Apenas SC")
        cidade = st.sidebar.selectbox("Cidade", ["Todas"] + sorted(CIDADES_SC))

        df_resultado = aplicar_filtros(df_resultado, usar_sc, cidade)

        # API rápida
        mapa = {}
        for cnpj in df_resultado[col_cnpj].unique()[:50]:
            dados = consultar_cnpj(cnpj)
            mapa[cnpj] = dados.get("Empresa","")

        df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa)

        fim = time.time()

        # ============================
        # DASHBOARD
        # ============================
        st.markdown("## 📊 Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.metric("Empresas", df_resultado[col_cnpj].nunique())
        c2.metric("Registros", df_resultado.shape[0])
        c3.metric("Tempo", f"{round(fim-inicio,2)}s")

        ranking = df_resultado.groupby(col_cnpj).size().reset_index(name="Qtd")

        st.bar_chart(ranking.set_index(col_cnpj)["Qtd"].head(10))

        st.dataframe(df_resultado, use_container_width=True)

# ================================
# 🔎 ABA 2 (CONSULTA REAL)
# ================================
with aba2:

    st.subheader("🔎 Consulta automática por CNPJ")

    cnpj_input = st.text_input("Digite o CNPJ (somente números)")

    if cnpj_input:

        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)

        if len(cnpj) == 14:

            with st.spinner("Buscando dados..."):
                dados = consultar_cnpj(cnpj)

            if dados:

                st.success("Empresa encontrada!")

                col1, col2 = st.columns(2)

                col1.write("🏢 Empresa:", dados["Empresa"])
                col1.write("🏷 Fantasia:", dados["Fantasia"])
                col1.write("📞 Telefone:", dados["Telefone"])

                col2.write("📍 Cidade:", dados["Cidade"])
                col2.write("🌎 UF:", dados["UF"])
                col2.write("📧 Email:", dados["Email"])

                st.write("🏭 CNAE:", dados["CNAE"])

            else:
                st.error("CNPJ não encontrado ou API indisponível")

        else:
            st.warning("Digite um CNPJ válido com 14 números")

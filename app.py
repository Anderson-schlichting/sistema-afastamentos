import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(layout="wide")

# ================================
# 📍 CIDADES SC (COMPLETO)
# ================================
CIDADES_SC = [
"ABDON BATISTA","ABELARDO LUZ","AGROLÂNDIA","AGRONÔMICA","ÁGUA DOCE","ÁGUAS DE CHAPECÓ",
"ÁGUAS FRIAS","ÁGUAS MORNAS","ALFREDO WAGNER","ALTO BELA VISTA","ANCHIETA","ANGELINA",
"ANITA GARIBALDI","ANITÁPOLIS","ANTÔNIO CARLOS","APIÚNA","ARABUTÃ","ARAQUARI","ARARANGUÁ",
"ARMAZÉM","ARROIO TRINTA","ARVOREDO","ASCURRA","ATALANTA","AURORA","BALNEÁRIO ARROIO DO SILVA",
"BALNEÁRIO BARRA DO SUL","BALNEÁRIO CAMBORIÚ","BALNEÁRIO GAIVOTA","BANDEIRANTE","BARRA BONITA",
"BARRA VELHA","BELA VISTA DO TOLDO","BELMONTE","BENEDITO NOVO","BIGUAÇU","BLUMENAU","BOCAINA DO SUL",
"BOMBINHAS","BOM JARDIM DA SERRA","BOM JESUS","BOM JESUS DO OESTE","BOM RETIRO",
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
"IRINEÓPOLIS","ITÁ","ITAJAÍ","ITAPEMA","ITAPIRANGA","ITAPOÁ",
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
"VITOR MEIRELES","WITMARSUM","XANXERÊ","XAVANTINA","XAXIM","ZORTÉA"
]

# ================================
# 📂 LEITURA CSV
# ================================
def carregar_arquivo(file):
    try:
        return pd.read_csv(file, sep=';', encoding='latin1')
    except:
        return pd.read_excel(file)

# ================================
# 🚀 API
# ================================
@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json()
    except:
        return {}

# ================================
# 🔍 FILTRO
# ================================
def aplicar_filtros(df, usar_sc=False, cidade=None):
    df = df.copy()

    col_cidade = None
    col_estado = None

    for c in df.columns:
        if "CIDADE" in c.upper() or "MUNICIP" in c.upper():
            col_cidade = c
        if "ESTADO" in c.upper() or "UF" in c.upper():
            col_estado = c

    if usar_sc and col_estado:
        df = df[df[col_estado].astype(str).str.upper().str.contains("SC|SANTA CATARINA", na=False)]

    if cidade != "Todas" and col_cidade:
        df[col_cidade] = df[col_cidade].astype(str).str.upper().str.strip()
        df = df[df[col_cidade] == cidade]

    return df

# ================================
# APP
# ================================
st.title("📊 Sistema Inteligente + FAP")

aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta"])

# ================================
# ABA 1
# ================================
with aba1:

    file = st.file_uploader("Envie CSV ou Excel")

    if file and st.button("Processar"):

        df = carregar_arquivo(file)

        if df is None:
            st.error("Erro ao ler arquivo")
            st.stop()

        df.columns = df.columns.str.strip()

        col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

        df[col_cnpj] = df[col_cnpj].astype(str).str.replace(r'\D','',regex=True)

        df_resultado = df[df[col_cnpj].duplicated(keep=False)]

        usar_sc = st.checkbox("Apenas SC")
        cidade = st.selectbox("Cidade", ["Todas"] + CIDADES_SC)

        df_resultado = aplicar_filtros(df_resultado, usar_sc, cidade)

        # API
        nomes = []
        for cnpj in df_resultado[col_cnpj].unique()[:30]:
            dados = consultar_cnpj(cnpj)
            nomes.append((cnpj, dados.get("razao_social","")))

        mapa = dict(nomes)
        df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa)

        st.dataframe(df_resultado)

# ================================
# ABA 2
# ================================
with aba2:

    cnpj = st.text_input("Digite o CNPJ")

    if cnpj:

        cnpj = ''.join(filter(str.isdigit, cnpj)).zfill(14)

        dados = consultar_cnpj(cnpj)

        if dados:
            st.write("Empresa:", dados.get("razao_social"))
            st.write("Cidade:", dados.get("municipio"))
            st.write("UF:", dados.get("uf"))
        else:
            st.error("CNPJ não encontrado")

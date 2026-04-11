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
# 📂 LEITURA FORTE CSV
# ================================
def carregar_arquivo(file):
   df.columns = df.columns.astype(str).str.strip()

# 🔍 detectar coluna de cidade automaticamente
col_cidade = None
for c in df.columns:
    if "CIDADE" in c.upper() or "MUNICIP" in c.upper():
        col_cidade = c
        break

# DEBUG (APARECE NA TELA)
st.write("📌 Colunas:", df.columns.tolist())
st.write("📌 Coluna cidade detectada:", col_cidade)

# ================================
# 🚀 API CNPJ
# ================================
@st.cache_data(ttl=86400)
def consultar_cnpj(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)

        if r.status_code == 200:
            d = r.json()
            return {
                "Empresa": d.get("razao_social","Não encontrado"),
                "Fantasia": d.get("nome_fantasia",""),
                "Telefone": d.get("ddd_telefone_1",""),
                "Cidade": d.get("municipio",""),
                "UF": d.get("uf",""),
                "Email": d.get("email","")
            }
    except:
        pass

    return None

# ================================
# 🔍 FILTROS
# ================================
def aplicar_filtros(df, usar_sc=False, cidade=None):
    df = df.copy()

    # 🔍 detectar coluna de cidade automaticamente
    col_cidade = None
    for c in df.columns:
        if "CIDADE" in c.upper() or "MUNICIP" in c.upper():
            col_cidade = c
            break

    # 🔍 detectar coluna de estado
    col_estado = None
    for c in df.columns:
        if "ESTADO" in c.upper() or "UF" in c.upper():
            col_estado = c
            break

    # filtro SC
    if usar_sc and col_estado:
        df = df[df[col_estado].astype(str).str.upper().str.contains("SC|SANTA CATARINA", na=False)]

    # filtro cidade
    if cidade != "Todas" and col_cidade:
        df[col_cidade] = df[col_cidade].astype(str).str.upper().str.strip()
        df = df[df[col_cidade] == cidade]

    return df

# ================================
# 📊 CÁLCULO FAP
# ================================
def calcular_fap(df, col_cnpj):
    ranking = (
        df.groupby(col_cnpj)
        .size()
        .reset_index(name="Afastamentos")
    )

    ranking["FAP"] = ranking["Afastamentos"].apply(lambda x:
        0.5 if x <= 2 else
        1.0 if x <= 5 else
        1.5 if x <= 10 else
        2.0
    )

    return ranking

# ================================
# 🖥️ APP
# ================================
st.title("📊 Sistema Inteligente de Empresas + FAP")

aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta CNPJ"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    file = st.file_uploader("Envie Excel ou CSV")

    if file and st.button("🚀 Processar"):

        df = carregar_arquivo(file)

        if df is None:
            st.error("❌ Erro ao ler arquivo CSV")
            st.stop()

        df.columns = df.columns.astype(str).str.strip()

        col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()]

        if not col_cnpj:
            st.error("❌ Coluna CNPJ não encontrada")
            st.stop()

        col_cnpj = col_cnpj[0]

        df[col_cnpj] = df[col_cnpj].astype(str).str.replace(r'\D','',regex=True).str.zfill(14)

        contagem = df[col_cnpj].value_counts()
        df_resultado = df[df[col_cnpj].isin(contagem[contagem > 1].index)]

        # salva global para aba 2
        st.session_state["df_resultado"] = df_resultado
        st.session_state["col_cnpj"] = col_cnpj

        # filtros
        usar_sc = st.checkbox("Apenas SC")
        cidade = st.selectbox("Cidade", ["Todas"] + CIDADES_SC)

        df_resultado = aplicar_filtros(df_resultado, usar_sc, cidade)

        # dashboard
        st.subheader("📊 Indicadores")

        c1, c2 = st.columns(2)
        c1.metric("Empresas", df_resultado[col_cnpj].nunique())
        c2.metric("Registros", df_resultado.shape[0])

        # ranking
        ranking = calcular_fap(df_resultado, col_cnpj)

        st.markdown("## 📈 FAP por Empresa")
        st.dataframe(ranking, use_container_width=True)

        st.bar_chart(ranking.set_index(col_cnpj)["Afastamentos"].head(10))

        st.markdown("## 📋 Dados")
        st.dataframe(df_resultado, use_container_width=True)

# ================================
# 🔎 ABA 2
# ================================
with aba2:

    st.subheader("🔎 Consulta CNPJ + FAP")

    cnpj_input = st.text_input("Digite o CNPJ")

    if cnpj_input:

        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)

        if len(cnpj) == 14:

            dados = consultar_cnpj(cnpj)

            if dados:

                st.success("Empresa encontrada")

                col1, col2 = st.columns(2)

                col1.write(f"🏢 Empresa: {dados.get('Empresa','')}")
                col1.write(f"🏷 Fantasia: {dados.get('Fantasia','')}")
                col1.write(f"📞 Telefone: {dados.get('Telefone','')}")

                col2.write(f"📍 Cidade: {dados.get('Cidade','')}")
                col2.write(f"🌎 UF: {dados.get('UF','')}")
                col2.write(f"📧 Email: {dados.get('Email','')}")

                # =====================
                # 🔥 FAP AUTOMÁTICO
                # =====================
                if "df_resultado" in st.session_state:

                    df_resultado = st.session_state["df_resultado"]
                    col_cnpj = st.session_state["col_cnpj"]

                    dados_empresa = df_resultado[df_resultado[col_cnpj] == cnpj]

                    if not dados_empresa.empty:

                        total = len(dados_empresa)

                        if total <= 2:
                            fap = 0.5
                        elif total <= 5:
                            fap = 1.0
                        elif total <= 10:
                            fap = 1.5
                        else:
                            fap = 2.0

                        st.markdown("### 📊 FAP Estimado")
                        st.success(f"Afastamentos: {total} | FAP: {fap}")

                    else:
                        st.info("Empresa não encontrada na base carregada")

            else:
                st.error("❌ CNPJ não encontrado")

        else:
            st.warning("Digite um CNPJ válido com 14 números")

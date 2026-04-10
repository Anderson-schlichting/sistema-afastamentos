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
"ZORTÉA"
]

# ================================
# 🚀 API OTIMIZADA (CACHE)
# ================================
@st.cache_data(ttl=86400)
def buscar_empresa(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)

        if r.status_code == 200:
            data = r.json()
            return (
                data.get("razao_social", "Não encontrado"),
                data.get("ddd_telefone_1", ""),
                data.get("municipio", ""),
                data.get("uf", "")
            )
    except:
        pass

    return "Não encontrado", "", "", ""

# ================================
# 📂 LEITURA
# ================================
def carregar_arquivo(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file, sep=None, engine="python")
    else:
        return pd.read_excel(file, engine="openpyxl")

# ================================
# 🔍 FILTROS
# ================================
def filtrar_sc(df):
    for col in ["Estado", "UF", "uf"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper()
            return df[df[col].isin(["SC", "SANTA CATARINA"])]
    return df


def aplicar_filtros(df, usar_sc=False, cidade=None):
    df_filtrado = df.copy()

    if usar_sc:
        df_filtrado = filtrar_sc(df_filtrado)

    if cidade and cidade != "Todas":
        if "Cidade" in df_filtrado.columns:
            df_filtrado["Cidade"] = df_filtrado["Cidade"].astype(str).str.upper()
            df_filtrado = df_filtrado[df_filtrado["Cidade"] == cidade]

    return df_filtrado

# ================================
# 🖥️ UI
# ================================
st.title("📊 Sistema Inteligente de Afastamentos + FAP")

aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Análise Inteligente de Empresas")

    file = st.file_uploader("Envie Excel ou CSV", type=["xlsx","csv"])

    if file:

        if st.button("🚀 Processar"):

            inicio = time.time()

            df = carregar_arquivo(file)
            df.columns = df.columns.str.strip()

            col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

            df[col_cnpj] = (
                df[col_cnpj]
                .astype(str)
                .str.replace(r'\D', '', regex=True)
                .str.zfill(14)
            )

            contagem = df[col_cnpj].value_counts()
            repetidos = contagem[contagem > 1]

            df_resultado = df[df[col_cnpj].isin(repetidos.index)]

            # ====================
            # 🔍 FILTROS UI
            # ====================
            st.sidebar.header("🔍 Filtros Inteligentes")

            usar_sc = st.sidebar.checkbox("Apenas Santa Catarina")

            cidade = st.sidebar.selectbox(
                "Filtrar por cidade",
                ["Todas"] + sorted(CIDADES_SC)
            )

            # aplica filtros
            df_resultado = aplicar_filtros(df_resultado, usar_sc, cidade)

            # ====================
            # 🚀 CONSULTA RÁPIDA
            # ====================
            cnpjs_unicos = df_resultado[col_cnpj].unique()[:50]

            mapa_nome = {}
            mapa_tel = {}

            for cnpj in cnpjs_unicos:
                nome, tel, cidade_api, uf_api = buscar_empresa(cnpj)

                mapa_nome[cnpj] = nome
                mapa_tel[cnpj] = tel

                # preenche cidade se não tiver
                if "Cidade" not in df_resultado.columns and cidade_api:
                    df_resultado.loc[df_resultado[col_cnpj] == cnpj, "Cidade"] = cidade_api

            df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa_nome)
            df_resultado["Telefone"] = df_resultado[col_cnpj].map(mapa_tel)

            fim = time.time()

            # ====================
            # 📊 DASHBOARD
            # ====================
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("⏱ Tempo", f"{round(fim-inicio,2)}s")
            col2.metric("🏢 Empresas únicas", df_resultado[col_cnpj].nunique())
            col3.metric("📄 Registros", df_resultado.shape[0])
            col4.metric(
                "📍 Cidades",
                df_resultado["Cidade"].nunique() if "Cidade" in df_resultado else 0
            )

            # ====================
            # 🥇 RANKING
            # ====================
            ranking = (
                df_resultado.groupby([col_cnpj,"Empresa","Telefone"])
                .size()
                .reset_index(name="Afastamentos")
                .sort_values(by="Afastamentos", ascending=False)
            )

            st.markdown("## 🥇 Ranking de Empresas")
            st.dataframe(ranking, use_container_width=True)

            # ====================
            # 📊 GRÁFICO
            # ====================
            st.markdown("## 📊 Top 10 Empresas")
            top10 = ranking.head(10).set_index("Empresa")
            st.bar_chart(top10["Afastamentos"])

            # ====================
            # ⚠️ ALERTAS
            # ====================
            criticas = ranking[ranking["Afastamentos"] >= 5]

            if not criticas.empty:
                st.markdown("## ⚠️ Empresas com Alto Risco")

                for _, row in criticas.iterrows():
                    st.warning(
                        f"{row['Empresa']} | CNPJ: {row[col_cnpj]} | "
                        f"Afastamentos: {row['Afastamentos']}"
                    )

            # ====================
            # 📋 DADOS
            # ====================
            st.markdown("## 📋 Dados Detalhados")
            st.dataframe(df_resultado, use_container_width=True)

            # ====================
            # 📥 DOWNLOAD
            # ====================
            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_resultado.to_excel(writer, index=False, sheet_name="Dados")
                ranking.to_excel(writer, index=False, sheet_name="Ranking")

            output.seek(0)

            st.download_button(
                "📥 Baixar relatório completo",
                output,
                "relatorio_completo.xlsx"
            )

# ================================
# 📈 ABA 2
# ================================
with aba2:

    st.subheader("📈 Análise Empresarial - FAP")

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=900, scrolling=True)

    except:
        st.error("❌ index.html não encontrado")

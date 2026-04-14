import streamlit as st
import pandas as pd
import requests
import time
import re
import pdfplumber

# cria abas
aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta FAP"])

with aba1:

    st.subheader("🚀 Prospecção Inteligente + FAP")

    # ================================
    # 📂 BASE EDITAIS (ONLINE)
    # ================================
    @st.cache_data(show_spinner="Buscando editais online...")
    def carregar_editais():

        import requests
        import re
        import pdfplumber
        from io import BytesIO

        urls = [
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITAL02FAPDOU30042021.pdf",
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/fap04.pdf",
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/Edital.FAP.pdf",
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITAISFAP06A102021_05_24_dou.pdf",
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/FAPEDITAIS11A162021.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITAIS1A5FAPDOU19012022.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITAL062022_DOU.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITAL72022_01_31_ASSINADO_FAPDOU.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALFAPN82022_02_01_dou.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN9CRPS_SEPRT_MTPDE12DEMAIODE2022EDITALN9CRPS_SEPRT_MTPDE12DEMAIODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN10CRPS_SPREV_MTPDE12DEMAIODE2022EDITALN10CRPS_SPREV_MTPDE12DEMAIODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN11_2022CRPS_SPREV_MTPDE12DEMAIODE2022EDITALN11_2022CRPS_SPREV_MTPDE12DEMAIODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN12_2022CRPS_SPREV_MTPDE13DEMAIODE2022EDITALN12_2022CRPS_SPREV_MTPDE13DEMAIODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN13_2022CRPS_SPREV_MTPDE13DEMAIODE2022EDITALN13_2022CRPS_SPREV_MTPDE13DEMAIODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy_of_1523.08.2022.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy_of_1623.08.2022.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy_of_1723.08.2022.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy_of_1823.08.2022.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy_of_1923.08.2022.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN20_2022CRPS_SPREV_MTPDE30DEAGOSTODE2022EDITALN20_2022CRPS_SPREV_MTPDE30DEAGOSTODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy_of_EDITALN21_2022CRPS_SPREV_MTPDE30DEAGOSTODE2022EDITALN21_2022CRPS_SPREV_MTPDE30DEAGOSTODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN22CRPS_SPREV_MTPDE31DEAGOSTODE2022EDITALN22CRPS_SPREV_MTPDE31DEAGOSTODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/copy3_of_EDITALN23_2022CRPS_SPREV_MTPDE9DESETEMBRODE2022EDITALN23_2022CRPS_SPREV_MTPDE9DESETEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN24CRPS_SPREV_MTPDE17DEOUTUBRODE2022EDITALN24CRPS_SPREV_MTPDE17DEOUTUBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN25CRPS_SPREV_MTPDE17DENOVEMBRODE2022EDITALN25CRPS_SPREV_MTPDE17DENOVEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN26CRPS_SEPREV_MTPDE17DENOVEMBRODE2022EDITALN26CRPS_SEPREV_MTPDE17DENOVEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN27CRPS_SEPREV_MTPDE17DENOVEMBRODE2022EDITALN27CRPS_SEPREV_MTPDE17DENOVEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN28CRPS_SEPREV_MTPDE17DENOVEMBRODE2022EDITALN28CRPS_SEPREV_MTPDE17DENOVEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN29CRPS_SPREV_MTPDE23DENOVEMBRODE2022EDITALN29CRPS_SPREV_MTPDE23DENOVEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN30CRPS_SPREV_MTPDE17DENOVEMBRODE2022EDITALN30CRPS_SPREV_MTPDE17DENOVEMBRODE2022DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN1CRPS_SPREV_MPSDE23DEJANEIRODE2023EDITALN1CRPS_SPREV_MPSDE23DEJANEIRODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/fap.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN3_CRPS_SPREV_MPSDE24DEMARODE2023EDITALN3_CRPS_SPREV_MPSDE24DEMARODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN4_CRPS_SPREV_MPSDE24DEMARODE2023EDITALN4_CRPS_SPREV_MPSDE24DEMARODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN5_CRPS_SPREV_MPSDE24DEMARODE2023EDITALN5_CRPS_SPREV_MPSDE24DEMARODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN6_CRPS_SPREV_MPSDE24DEMARODE2023EDITALN6_CRPS_SPREV_MPSDE24DEMARODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN7_CRPS_SPREV_MPSDE24DEMARODE2023EDITALN7_CRPS_SPREV_MPSDE24DEMARODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/arquivos-editais/EDITALN8_CRPS_SPREV_MPSDE24DEMARODE2023EDITALN8_CRPS_SPREV_MPSDE24DEMARODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/copy_of_EDITALN11CRPS_SPREV_MPSDE6DEJUNHODE2023EDITALN11CRPS_SPREV_MPSDE6DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/copy_of_EDITALN12CRPS_SPREV_MPSDE6DEJUNHODE2023EDITALN12CRPS_SPREV_MPSDE6DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN13CRPS_SPREV_MPSDE6DEJUNHODE2023EDITALN13CRPS_SPREV_MPSDE6DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN14CRPS_SPREV_MPSDE6DEJUNHODE2023EDITALN14CRPS_SPREV_MPSDE6DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/copy_of_EDITALN15CRPS_SPREV_MPSDE6DEJUNHODE2023EDITALN15CRPS_SPREV_MPSDE6DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN16CRPS_SPREV_MPSDE6DEJUNHODE2023EDITALN16CRPS_SPREV_MPSDE6DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN17_2023CRPS_SPREV_MPSDE7DEJUNHODE2023EDITALN17_2023CRPS_SPREV_MPSDE7DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN18CRPS_SPREV_MPSDE7DEJUNHODE2023EDITALN18CRPS_SPREV_MPSDE7DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN19CRPS_SPREV_MPSDE7DEJUNHODE2023EDITALN19CRPS_SPREV_MPSDE7DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN20CRPS_SPREV_MPSDE7DEJUNHODE2023EDITALN20CRPS_SPREV_MPSDE7DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN21CRPS_SPREV_MPSDE7DEJUNHODE2023EDITALN21CRPS_SPREV_MPSDE7DEJUNHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN22CRPS_SPREV_MPSDE26DEJULHODE2023EDITALN22CRPS_SPREV_MPSDE26DEJULHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN23CRPS_SPREV_MPSDE26DEJULHODE2023EDITALN23CRPS_SPREV_MPSDE26DEJULHODE2023DOUImprensaNacional.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALFAP242023.pdf"
            "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/editais/EDITALN25CRPS_SPREV_MPSDE26DEJULHODE2023EDITALN25CRPS_SPREV_MPSDE26DEJULHODE2023DOUImprensaNacional.pdf"
            
            
            
        ]

        cnpjs = set()

        for url in urls:
            try:
                response = requests.get(url, timeout=15)

                if response.status_code == 200:

                    pdf = pdfplumber.open(BytesIO(response.content))

                    for p in pdf.pages:

                        # 🔥 TABELAS
                        tabelas = p.extract_tables()

                        if tabelas:
                            for tabela in tabelas:
                                for linha in tabela:
                                    for celula in linha:
                                        if celula:
                                            encontrados = re.findall(r"\d{14}", str(celula))
                                            cnpjs.update(encontrados)

                        # 🔥 TEXTO (fallback)
                        txt = p.extract_text()

                        if txt:
                            encontrados = re.findall(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}", txt)
                            encontrados = [re.sub(r"\D", "", cnpj) for cnpj in encontrados]
                            cnpjs.update(encontrados)

            except Exception:
                continue

        return cnpjs

    base_editais = carregar_editais()

    st.success(f"📊 {len(base_editais)} empresas com recurso FAP identificadas")

    # ================================
    # 🌐 API CNPJ
    # ================================
    @st.cache_data(ttl=86400)
    def consultar_cnpj(cnpj):

        urls = [
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
            f"https://receitaws.com.br/v1/cnpj/{cnpj}",
            f"https://api.cnpj.ws/cnpj/{cnpj}"
        ]

        for url in urls:
            try:
                r = requests.get(url, timeout=5)

                if r.status_code == 200:
                    data = r.json()

                    return {
                        "razao_social": data.get("razao_social") or data.get("nome") or "",
                        "nome_fantasia": data.get("nome_fantasia") or data.get("fantasia") or "",
                        "municipio": data.get("municipio") or "",
                        "uf": data.get("uf") or "",
                        "cnae": data.get("cnae_fiscal_descricao") or "",
                        "telefone": data.get("ddd_telefone_1") or data.get("telefone") or ""
                    }
            except:
                continue

        return {}

    # ================================
    # 🧠 FUNÇÕES
    # ================================
    def extrair_uf_ibge(valor):
        try:
            codigo = str(valor).split("-")[0][:2]

            mapa = {
                "11":"RO","12":"AC","13":"AM","14":"RR","15":"PA","16":"AP","17":"TO",
                "21":"MA","22":"PI","23":"CE","24":"RN","25":"PB","26":"PE","27":"AL","28":"SE","29":"BA",
                "31":"MG","32":"ES","33":"RJ","35":"SP",
                "41":"PR","42":"SC","43":"RS",
                "50":"MS","51":"MT","52":"GO","53":"DF"
            }

            return mapa.get(codigo, "")
        except:
            return ""

    def extrair_cidade(valor):
        try:
            return str(valor).split("-")[1].strip().upper()
        except:
            return ""

    def is_b91(valor):
        return "B91" in str(valor).upper()

    def potencial(af):
        if af >= 50: return "🔥 ALTA"
        elif af >= 20: return "🟠 BOA"
        elif af >= 10: return "🟡 MÉDIA"
        return "🟢 BAIXA"

    def gerar_whatsapp(t):
        t = ''.join(filter(str.isdigit, str(t)))
        return f"https://wa.me/55{t}" if t else ""

    # ================================
    # 📥 UPLOAD
    # ================================
    files = st.file_uploader("Envie até 5 planilhas", accept_multiple_files=True, key="upload_aba1")

    if files:

        dfs = []

        for file in files:
            if file.name.endswith(".csv"):
                df_temp = pd.read_csv(file, sep=';', encoding='latin1')
            else:
                df_temp = pd.read_excel(file)

            dfs.append(df_temp)

        df = pd.concat(dfs, ignore_index=True)
        df.columns = df.columns.astype(str)

        col_cnpj_list = [c for c in df.columns if "CNPJ" in c.upper()]

        if not col_cnpj_list:
            st.error("❌ Coluna CNPJ não encontrada")
            st.stop()

        col_cnpj = col_cnpj_list[0]

        df[col_cnpj] = df[col_cnpj].astype(str).str.replace(r"\D","",regex=True).str.zfill(14)

        col_beneficio = None
        for c in df.columns:
            if "BENEF" in c.upper() or "ESPÉCIE" in c.upper():
                col_beneficio = c
                break

        df["B91"] = df[col_beneficio].apply(is_b91) if col_beneficio else False

        col_municipio = [c for c in df.columns if "MUNIC" in c.upper()]

        if col_municipio:
            col_municipio = col_municipio[0]
            df["cidade"] = df[col_municipio].apply(extrair_cidade)
            df["uf"] = df[col_municipio].apply(extrair_uf_ibge)
        else:
            df["cidade"] = ""
            df["uf"] = ""

        agrupado = df.groupby(col_cnpj).agg(
            AFASTAMENTOS=(col_cnpj, "count"),
            B91=("B91", "sum"),
            cidade=("cidade", "first"),
            uf=("uf", "first")
        ).reset_index()

        agrupado["TEVE_ACIDENTE"] = agrupado["B91"].apply(lambda x: "SIM" if x > 0 else "NÃO")
        agrupado["RECURSO_FAP"] = agrupado[col_cnpj].apply(lambda x: "SIM" if x in base_editais else "NÃO")
        agrupado["POTENCIAL"] = agrupado["AFASTAMENTOS"].apply(potencial)

        agrupado["grupo"] = agrupado["uf"].apply(lambda x: x if x else "AVULSOS")

        grupos = agrupado["grupo"].unique()

        st.markdown("## 📂 Grupos encontrados")

        for g in grupos:

            df_g = agrupado[agrupado["grupo"] == g]

            st.markdown(f"### 📍 {g} ({len(df_g)} empresas)")

            if st.button(f"🚀 Processar {g}", key=f"btn_{g}"):

                resultados = []

                status_text = st.empty()
                progress_bar = st.progress(0)
                tabela = st.empty()

                total = len(df_g)

                for i, (_, row) in enumerate(df_g.iterrows()):

                    cnpj = row[col_cnpj]
                    dados = consultar_cnpj(cnpj)

                    percent = int((i + 1) / total * 100)

                    status_text.text(f"Processando: {percent}% ({i+1}/{total})")
                    progress_bar.progress((i + 1) / total)

                    linha = {
                        "Empresa": dados.get("razao_social",""),
                        "Fantasia": dados.get("nome_fantasia",""),
                        "CNPJ": cnpj,
                        "Município": dados.get("municipio") or row["cidade"],
                        "UF": dados.get("uf") or row["uf"],
                        "Telefone": dados.get("telefone",""),
                        "WhatsApp": gerar_whatsapp(dados.get("telefone")),
                        "CNAE": dados.get("cnae",""),
                        "Afastamentos": row["AFASTAMENTOS"],
                        "B91": row["B91"],
                        "Acidente": row["TEVE_ACIDENTE"],
                        "Recorreu FAP": row["RECURSO_FAP"],
                        "Potencial": row["POTENCIAL"]
                    }

                    resultados.append(linha)

                    tabela.dataframe(pd.DataFrame(resultados), use_container_width=True)

                    time.sleep(0.3)

                final = pd.DataFrame(resultados)

                st.success(f"{len(final)} empresas processadas")

                csv = final.to_csv(index=False).encode('utf-8')

                st.download_button(
                    "📤 Baixar Leads",
                    csv,
                    f"leads_{g}.csv",
                    key=f"download_{g}"
                )
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

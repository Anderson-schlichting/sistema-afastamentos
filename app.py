import streamlit as st

# ================================
# 🔁 SESSION STATE (INTEGRAÇÃO)
# ================================
if "cnpj_selecionado" not in st.session_state:
    st.session_state["cnpj_selecionado"] = ""

# 🔹 ABAS
aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    import pandas as pd
    import requests
    import time

    st.subheader("🚀 Prospecção Inteligente")

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

    def consultar_cnpj(cnpj):
        urls = [
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
            f"https://receitaws.com.br/v1/cnpj/{cnpj}",
            f"https://api.cnpj.ws/cnpj/{cnpj}"
        ]

        for url in urls:
            try:
                r = requests.get(url, timeout=10)
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

    def potencial(af):
        if af >= 50: return "🔥 ALTA"
        elif af >= 20: return "🟠 BOA"
        elif af >= 10: return "🟡 MÉDIA"
        return "🟢 BAIXA"

    def gerar_whatsapp(t):
        t = ''.join(filter(str.isdigit, str(t)))
        return f"https://wa.me/55{t}" if t else ""

    files = st.file_uploader("Envie até 5 planilhas", accept_multiple_files=True)

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

        col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

        df[col_cnpj] = df[col_cnpj].astype(str).str.replace(r"\D","",regex=True).str.zfill(14)
        df = df.drop_duplicates(subset=[col_cnpj])

        col_municipio = [c for c in df.columns if "MUNIC" in c.upper()]

        if col_municipio:
            col_municipio = col_municipio[0]
            df["cidade"] = df[col_municipio].apply(extrair_cidade)
            df["uf"] = df[col_municipio].apply(extrair_uf_ibge)
        else:
            df["cidade"] = ""
            df["uf"] = ""

        df["Afastamentos"] = 1
        df["grupo"] = df["uf"].apply(lambda x: x if x else "AVULSOS")

        grupos = df["grupo"].unique()

        st.markdown("## 📂 Grupos encontrados")

        for g in grupos:

            df_g = df[df["grupo"] == g]

            st.markdown(f"### 📍 {g} ({len(df_g)} empresas)")

            if st.button(f"🚀 Processar {g}"):

                resultados = []
                progress = st.progress(0)
                tabela = st.empty()

                total = len(df_g)
                lote = 10

                for i in range(0, total, lote):

                    bloco = df_g.iloc[i:i+lote]

                    for _, row in bloco.iterrows():

                        cnpj = row[col_cnpj]

                        dados = {}
                        for tentativa in range(3):
                            dados = consultar_cnpj(cnpj)
                            if dados.get("razao_social"):
                                break
                            time.sleep(1)

                        linha = {
                            "Empresa": dados.get("razao_social","NÃO ENCONTRADO"),
                            "Fantasia": dados.get("nome_fantasia",""),
                            "CNPJ": cnpj,
                            "Município": dados.get("municipio") or row["cidade"],
                            "UF": dados.get("uf") or row["uf"],
                            "Telefone": dados.get("telefone",""),
                            "WhatsApp": gerar_whatsapp(dados.get("telefone")),
                            "CNAE": dados.get("cnae",""),
                            "Afastamentos": row["Afastamentos"],
                            "Potencial": potencial(row["Afastamentos"])
                        }

                        resultados.append(linha)
                        time.sleep(0.4)

                    progress.progress(min((i+lote)/total,1.0))

                    df_view = pd.DataFrame(resultados)

                    st.data_editor(
                        df_view,
                        use_container_width=True,
                        column_config={
                            "WhatsApp": st.column_config.LinkColumn(
                                "WhatsApp",
                                display_text="💬 Abrir"
                            )
                        }
                    )

                    # BOTÃO CONSULTAR
                    st.markdown("### 🔎 Consultar empresa")

                    for _, row in df_view.iterrows():

                        col1, col2, col3 = st.columns([3,2,2])

                        col1.write(row["Empresa"])
                        col2.write(row["CNPJ"])

                        if col3.button("🔎 Consultar", key=row["CNPJ"]):
                            st.session_state["cnpj_selecionado"] = row["CNPJ"]
                            st.success("CNPJ enviado para aba Consulta FAP 👇")

                    time.sleep(1.5)

# ================================
# 🔎 ABA 2
# ================================
with aba2:

    import datetime
    import requests

    st.subheader("🔎 Diagnóstico Comercial FAP")

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

    cnpj_input = st.text_input(
        "Digite o CNPJ",
        value=st.session_state.get("cnpj_selecionado", "")
    )

    if cnpj_input:
        cnpj = ''.join(filter(str.isdigit, cnpj_input)).zfill(14)

        dados = consultar_cnpj(cnpj)

        if dados.get("empresa"):
            st.success("Empresa encontrada")

            col1, col2 = st.columns(2)

            col1.write(f"🏢 {dados['empresa']}")
            col1.write(f"📞 {dados['telefone']}")
            col1.write(f"👥 {dados['socios']}")

            col2.write(f"📍 {dados['cidade']} - {dados['uf']}")
            col2.write(f"🏭 CNAE: {dados['cnae']}")

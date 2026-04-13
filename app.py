import streamlit as st

# 🔹 1. CRIA AS ABAS
aba1, aba2 = st.tabs(["📊 Análise", "🔎 Consulta FAP"])
# ================================
# 📊 ABA 1 - FINAL COM ESTADOS + AVULSOS
# ================================
with aba1:

    import pandas as pd
    import requests
    import time
    import streamlit as st

    st.subheader("🚀 Prospecção Inteligente")

    # ================================
    # 🧠 IBGE → UF
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

    # ================================
    # 🔄 API
    # ================================
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

    # ================================
    # 💰 POTENCIAL
    # ================================
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

        # ================================
        # 📍 DETECTA MUNICÍPIO
        # ================================
        col_municipio = [c for c in df.columns if "MUNIC" in c.upper()]

        if col_municipio:
            col_municipio = col_municipio[0]

            df["cidade"] = df[col_municipio].apply(extrair_cidade)
            df["uf"] = df[col_municipio].apply(extrair_uf_ibge)
        else:
            df["cidade"] = ""
            df["uf"] = ""

        df["Afastamentos"] = 1

        # ================================
        # 📂 ORGANIZA GRUPOS
        # ================================
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

tabela.data_editor(
    df_view,
    use_container_width=True,
    column_config={
        "WhatsApp": st.column_config.LinkColumn(
            "WhatsApp",
            display_text="💬 Abrir"
        )
    }
)

                    time.sleep(1.5)

                final = pd.DataFrame(resultados)

                st.success(f"{len(final)} empresas processadas")

                csv = final.to_csv(index=False).encode('utf-8')
                st.download_button("📤 Baixar Leads", csv, f"leads_{g}.csv")
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

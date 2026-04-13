# ================================
# 📊 ABA 1 NOVA (OTIMIZADA)
# ================================
with aba1:

    import pandas as pd
    import requests
    import time
    import os
    import streamlit as st

    st.subheader("📊 Prospecção Inteligente")

    CACHE_FILE = "cache_cnpj.csv"

    # ================================
    # 🔄 CONSULTA MULTI API
    # ================================
    def consultar_cnpj(cnpj):

        apis = [
            f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}",
            f"https://receitaws.com.br/v1/cnpj/{cnpj}",
            f"https://api.cnpj.ws/cnpj/{cnpj}"
        ]

        for url in apis:
            try:
                r = requests.get(url, timeout=5)

                if r.status_code == 200:
                    data = r.json()

                    return {
                        "empresa": data.get("razao_social") or data.get("nome") or "",
                        "telefone": data.get("ddd_telefone_1") or data.get("telefone") or "",
                        "cidade": data.get("municipio") or data.get("cidade") or "",
                        "uf": data.get("uf") or "",
                    }
            except:
                continue

        return {}

    # ================================
    # 🎯 SCORE
    # ================================
    def calcular_score(qtd):
        if qtd >= 30:
            return "🔴 QUENTE"
        elif qtd >= 15:
            return "🟠 MÉDIO"
        return "🟢 FRIO"

    # ================================
    # 📥 UPLOAD
    # ================================
    file = st.file_uploader("Envie CSV ou Excel")

    if file:

        if file.name.endswith(".csv"):
            df = pd.read_csv(file, sep=';', encoding='latin1')
        else:
            df = pd.read_excel(file)

        df.columns = df.columns.astype(str)

        # ================================
        # 🔍 IDENTIFICAR CNPJ
        # ================================
        col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()]

        if not col_cnpj:
            st.error("Coluna CNPJ não encontrada")
            st.stop()

        col_cnpj = col_cnpj[0]

        df[col_cnpj] = (
            df[col_cnpj]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(14)
        )

        # ================================
        # 📊 AGRUPAR (AFASTAMENTOS)
        # ================================
        agrupado = df.groupby(col_cnpj).size().reset_index(name="Afastamentos")
        agrupado["Score"] = agrupado["Afastamentos"].apply(calcular_score)

        # ================================
        # 📂 CACHE
        # ================================
        if os.path.exists(CACHE_FILE):
            cache = pd.read_csv(CACHE_FILE)
        else:
            cache = pd.DataFrame(columns=["CNPJ","empresa","telefone","cidade","uf"])

        # ================================
        # 📦 DIVIDIR POR ESTADO
        # ================================
        st.markdown("## 📂 Blocos por Estado")

        # inicialmente sem UF → será preenchido pela API
        agrupado["uf"] = ""

        estados = ["SC","PR","RS","SP","MG"]

        for uf in estados:

            st.markdown(f"### 📍 Estado: {uf}")

            if st.button(f"Consultar {uf}"):

                df_uf = agrupado.copy()

                resultados = []
                consultar = []

                # ================================
                # 🔍 CACHE
                # ================================
                for cnpj in df_uf[col_cnpj]:

                    encontrado = cache[cache["CNPJ"] == cnpj]

                    if not encontrado.empty:
                        resultados.append(encontrado.iloc[0].to_dict())
                    else:
                        consultar.append(cnpj)

                st.info(f"Cache: {len(resultados)} | Consultar: {len(consultar)}")

                progress = st.progress(0)

                # ================================
                # ⚡ PROCESSAMENTO EM LOTE (10)
                # ================================
                lote = 10

                for i in range(0, len(consultar), lote):

                    bloco = consultar[i:i+lote]

                    for cnpj in bloco:

                        dados = consultar_cnpj(cnpj)

                        if dados.get("empresa"):
                            registro = {"CNPJ": cnpj, **dados}
                            resultados.append(registro)

                            cache = pd.concat([cache, pd.DataFrame([registro])], ignore_index=True)

                    progress.progress(min((i+len(bloco))/len(consultar), 1.0))
                    time.sleep(0.3)

                cache.drop_duplicates(subset=["CNPJ"], inplace=True)
                cache.to_csv(CACHE_FILE, index=False)

                df_api = pd.DataFrame(resultados)

                final = agrupado.merge(
                    df_api,
                    left_on=col_cnpj,
                    right_on="CNPJ",
                    how="left"
                )

                # ================================
                # 📍 FILTRAR ESTADO
                # ================================
                final = final[final["uf"] == uf]

                # ================================
                # 📊 RANKING FINAL
                # ================================
                final = final.sort_values("Afastamentos", ascending=False)

                st.success(f"{len(final)} empresas encontradas em {uf}")

                st.dataframe(final, use_container_width=True)
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

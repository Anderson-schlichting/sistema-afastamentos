with aba1:

    st.subheader("📊 Identificação de Empresas com Múltiplos Afastamentos")

    file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

    if file:

        if st.button("🚀 Processar Planilha"):

            progress = st.progress(0)
            status = st.empty()

            try:
                status.text("📂 Lendo planilha...")
                progress.progress(20)

                df = pd.read_excel(file, engine="openpyxl")

                df.columns = df.columns.str.strip()

                progress.progress(40)
                status.text("🔍 Identificando coluna de CNPJ...")

                col_cnpj = None
                for col in df.columns:
                    if "CNPJ" in col.upper():
                        col_cnpj = col
                        break

                if not col_cnpj:
                    st.error("❌ Coluna de CNPJ não encontrada.")
                else:

                    progress.progress(60)
                    status.text("🧹 Tratando dados...")

                    df[col_cnpj] = (
                        df[col_cnpj]
                        .astype(str)
                        .str.replace(r'\D', '', regex=True)
                        .str.zfill(14)
                    )

                    progress.progress(75)
                    status.text("📊 Identificando CNPJs repetidos...")

                    contagem = df[col_cnpj].value_counts()
                    cnpjs_repetidos = contagem[contagem > 1].index

                    df_resultado = df[df[col_cnpj].isin(cnpjs_repetidos)]

                    progress.progress(85)
                    status.text("🌐 Consultando empresas na Receita...")

                    df_resultado["Empresa"] = df_resultado[col_cnpj].apply(buscar_empresa)

                    progress.progress(100)
                    status.text("✅ Finalizado!")

                    st.success(f"✅ {df_resultado.shape[0]} registros encontrados")

                    st.dataframe(df_resultado, use_container_width=True)

                    # Download Excel
                    output = "relatorio.xlsx"
                    df_resultado.to_excel(output, index=False)

                    with open(output, "rb") as f:
                        st.download_button(
                            "📥 Baixar relatório",
                            f,
                            "relatorio_cnpj_repetidos.xlsx"
                        )

            except Exception as e:
                st.error(f"Erro ao processar: {e}")

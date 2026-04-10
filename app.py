import streamlit as st
import pandas as pd

st.title("📊 Analisador de CNPJ Repetido")

file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

if file:
    try:
        # Lê automaticamente a primeira aba
        df = pd.read_excel(file, engine="openpyxl")

        # Limpa nomes das colunas
        df.columns = df.columns.str.strip()

        # Encontrar coluna de CNPJ automaticamente
        col_cnpj = None
        for col in df.columns:
            if "CNPJ" in col.upper():
                col_cnpj = col
                break

        if not col_cnpj:
            st.error("❌ Coluna de CNPJ não encontrada na planilha.")
        else:
            # Padroniza CNPJ
            df[col_cnpj] = df[col_cnpj].astype(str).str.strip()

            # Identifica repetidos
            repetidos = df[col_cnpj][df[col_cnpj].duplicated(keep=False)]

            # Filtra todas as linhas desses CNPJs
            df_resultado = df[df[col_cnpj].isin(repetidos)]

            # Ordena
            df_resultado = df_resultado.sort_values(by=col_cnpj)

            st.success(f"✅ {df_resultado.shape[0]} registros encontrados")

            st.dataframe(df_resultado, use_container_width=True)

            # Download Excel (melhor que CSV)
            output = pd.ExcelWriter("relatorio.xlsx", engine="xlsxwriter")
            df_resultado.to_excel(output, index=False)
            output.close()

            with open("relatorio.xlsx", "rb") as f:
                st.download_button(
                    "📥 Baixar relatório em Excel",
                    f,
                    "relatorio_cnpj_repetidos.xlsx"
                )

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")

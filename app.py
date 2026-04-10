import streamlit as st
import pandas as pd

st.title("📊 Analisador de CNPJ Repetido")

file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

if file:
    # Lê a primeira aba automaticamente
    df = pd.read_excel(file, engine="openpyxl")

    # Nome da coluna de CNPJ (ajuste se necessário)
    col_cnpj = "CNPJ/CEI Empregador"

    # Garantir string
    df[col_cnpj] = df[col_cnpj].astype(str)

    # Encontrar CNPJs repetidos
    repetidos = df[col_cnpj][df[col_cnpj].duplicated(keep=False)]

    # Filtrar todas as linhas desses CNPJs
    df_resultado = df[df[col_cnpj].isin(repetidos)]

    # Ordenar por CNPJ
    df_resultado = df_resultado.sort_values(by=col_cnpj)

    st.write("### Empresas com mais de um afastamento:")
    st.dataframe(df_resultado)

    # Download Excel
    output = df_resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar relatório",
        output,
        "relatorio_cnpj_repetidos.csv",
        "text/csv"
    )

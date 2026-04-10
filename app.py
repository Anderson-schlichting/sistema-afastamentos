import streamlit as st
import pandas as pd

st.title("📊 Analisador de Afastamentos - Litoral SC")

file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file, sheet_name="LITORAL SC")

    col_cnpj = "CNPJ/CEI Empregador"
    col_motivo = "Natureza da Lesão"

    df[col_cnpj] = df[col_cnpj].astype(str)

    grouped = df.groupby(col_cnpj)

    resultado = []

    for cnpj, group in grouped:
        if len(group) > 1:
            motivos = group[col_motivo].dropna().unique()

            resultado.append({
                "CNPJ": cnpj,
                "Quantidade Afastamentos": len(group),
                "Motivos": ", ".join(map(str, motivos))
            })

    result_df = pd.DataFrame(resultado).sort_values(by="Quantidade Afastamentos", ascending=False)

    st.write("### Resultado:")
    st.dataframe(result_df)

    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar relatório", csv, "relatorio.csv", "text/csv")

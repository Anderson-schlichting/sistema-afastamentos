import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("📊 Sistema Inteligente de Afastamentos + FAP")

# ================================
# 🚀 CONSULTA CNPJ
# ================================
@st.cache_data
def buscar_empresa(cnpj):
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json().get("razao_social", "")
    except:
        return "Não encontrado"

# ================================
# ABAS
# ================================
aba1, aba2 = st.tabs(["📊 CNPJ Repetido", "📈 Análise FAP"])

# ================================
# 📊 ABA 1
# ================================
with aba1:

    st.subheader("📊 Identificação de Empresas com Múltiplos Afastamentos")

    file = st.file_uploader("Envie a planilha Excel", type=["xlsx"])

    if file:

        if st.button("🚀 Processar Planilha"):

            inicio = time.time()

            progress = st.progress(0)
            status = st.empty()
            porcentagem = st.empty()

            try:
                status.text("📂 Lendo planilha...")
                progress.progress(10)
                porcentagem.text("10%")

                df = pd.read_excel(file, engine="openpyxl")
                df.columns = df.columns.str.strip()

                progress.progress(25)
                porcentagem.text("25%")

                col_cnpj = [c for c in df.columns if "CNPJ" in c.upper()][0]

                status.text("🧹 Tratando dados...")
                progress.progress(40)
                porcentagem.text("40%")

                df[col_cnpj] = (
                    df[col_cnpj]
                    .astype(str)
                    .str.replace(r'\D', '', regex=True)
                    .str.zfill(14)
                )

                status.text("📊 Identificando repetidos...")
                progress.progress(55)
                porcentagem.text("55%")

                contagem = df[col_cnpj].value_counts()
                cnpjs_repetidos = contagem[contagem > 1]

                df_resultado = df[df[col_cnpj].isin(cnpjs_repetidos.index)]

                # 🔥 Consulta otimizada
                cnpjs_unicos = df_resultado[col_cnpj].unique()[:100]

                status.text("🌐 Consultando Receita...")
                progress.progress(70)
                porcentagem.text("70%")

                mapa_empresas = {}

                for i, cnpj in enumerate(cnpjs_unicos):
                    mapa_empresas[cnpj] = buscar_empresa(cnpj)

                    perc = int(70 + (i / len(cnpjs_unicos)) * 20)
                    progress.progress(perc)
                    porcentagem.text(f"{perc}%")

                    if i % 10 == 0:
                        time.sleep(0.2)

                df_resultado["Empresa"] = df_resultado[col_cnpj].map(mapa_empresas)

                status.text("📊 Finalizando...")
                progress.progress(90)
                porcentagem.text("90%")

                fim = time.time()

                progress.progress(100)
                porcentagem.text("100%")

                st.success("✅ Concluído!")

                # ========================
                # DASHBOARD
                # ========================
                col1, col2, col3 = st.columns(3)

                col1.metric("⏱ Tempo", f"{round(fim - inicio,2)}s")
                col2.metric("📊 Empresas únicas", df_resultado[col_cnpj].nunique())
                col3.metric("📁 Registros", df_resultado.shape[0])

                # ========================
                # 🥇 RANKING
                # ========================
                ranking = (
                    df_resultado.groupby([col_cnpj, "Empresa"])
                    .size()
                    .reset_index(name="Qtd Afastamentos")
                    .sort_values(by="Qtd Afastamentos", ascending=False)
                )

                st.markdown("## 🥇 Ranking de Empresas")
                st.dataframe(ranking, use_container_width=True, hide_index=True)

                # ========================
                # ⚠️ ALTO RISCO
                # ========================
                criticas = ranking[ranking["Qtd Afastamentos"] >= 5]

                if not criticas.empty:
                    st.markdown("## ⚠️ Empresas com Alto Risco")

                    for _, row in criticas.iterrows():
                        st.markdown(f"""
                        <div style="
                            background:#7f1d1d;
                            padding:15px;
                            border-radius:10px;
                            margin-bottom:10px;
                        ">
                            <b>🏢 Empresa:</b> {row['Empresa']}<br>
                            <b>📄 CNPJ:</b> {row[col_cnpj]}<br>
                            <b>📊 Afastamentos:</b> {row['Qtd Afastamentos']}<br>
                            <b>⚠️ Risco:</b> ALTO
                        </div>
                        """, unsafe_allow_html=True)

                # ========================
                # 📋 DADOS DETALHADOS
                # ========================
                st.markdown("## 📋 Dados Detalhados")

                st.dataframe(
                    df_resultado.style.highlight_max(axis=0),
                    use_container_width=True
                )

                # ========================
                # 📥 DOWNLOAD
                # ========================
                output = BytesIO()

                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name='Dados')
                    ranking.to_excel(writer, index=False, sheet_name='Ranking')

                output.seek(0)

                st.download_button(
                    "📥 Baixar relatório completo",
                    output,
                    "relatorio_completo.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Erro: {e}")

# ================================
# 📈 ABA 2 (FAP)
# ================================
with aba2:

    st.subheader("📈 Análise Empresarial - FAP")

    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=900, scrolling=True)

    except:
        st.error("❌ Arquivo index.html não encontrado.")

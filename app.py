df = carregar_arquivo(file)
df.columns = df.columns.str.strip()

st.write("📋 Colunas detectadas:", list(df.columns))

# ====================
# 🔎 IDENTIFICA CNPJ (INTELIGENTE)
# ====================
col_cnpj = next(
    (c for c in df.columns if "CNPJ" in c.upper() or "CEI" in c.upper()),
    None
)

if not col_cnpj:
    st.error("❌ Coluna de CNPJ não encontrada")
    st.stop()

# ====================
# 🏙️ IDENTIFICA CIDADE
# ====================
col_cidade = next(
    (c for c in df.columns if "MUNIC" in c.upper() or "CIDADE" in c.upper()),
    None
)

# ====================
# LIMPA CNPJ
# ====================
df[col_cnpj] = (
    df[col_cnpj]
    .astype(str)
    .str.replace(r'\D', '', regex=True)
    .str.zfill(14)
)

# ====================
# FILTRO SC (POR SEGURANÇA)
# ====================
if col_cidade:
    df = df[df[col_cidade].notna()]
else:
    st.warning("⚠️ Cidade não encontrada — seguindo sem filtro")

# ====================
# REPETIDOS
# ====================
contagem = df[col_cnpj].value_counts()
repetidos = contagem[contagem > 1]

df_resultado = df[df[col_cnpj].isin(repetidos.index)]

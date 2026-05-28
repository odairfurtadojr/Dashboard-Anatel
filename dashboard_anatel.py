import streamlit as st
import pandas as pd

# =========================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================

st.set_page_config(
    page_title="Dashboard ANATEL",
    layout="wide"
)

st.title("📡 Dashboard de Homologações ANATEL")

# =========================================
# UPLOAD
# =========================================

arquivo = st.file_uploader(
    "Selecione a planilha XLSX",
    type=["xlsx"]
)

# =========================================
# PROCESSAMENTO
# =========================================

if arquivo is not None:

    # Ler planilha
    df = pd.read_excel(arquivo)

    # Renomear colunas
    df = df.rename(columns={
        df.columns[1]: "MODELO",
        df.columns[4]: "HOMOLOGACAO",
        df.columns[7]: "VALIDADE"
    })

    # Converter data
    df["VALIDADE"] = pd.to_datetime(
        df["VALIDADE"],
        errors="coerce"
    )

    hoje = pd.Timestamp.today().normalize()

    # Status
    df["STATUS"] = df["VALIDADE"].apply(
        lambda x: "SUSPENSO"
        if pd.isna(x) or x < hoje
        else "ATIVO"
    )

    # Dias restantes
    df["DIAS_RESTANTES"] = (
        df["VALIDADE"] - hoje
    ).dt.days

    # =========================================
    # INDICADORES
    # =========================================

    ativos = len(df[df["STATUS"] == "ATIVO"])

    suspensos = len(df[df["STATUS"] == "SUSPENSO"])

    venc_3 = len(df[
        (df["VALIDADE"] >= hoje) &
        (df["VALIDADE"] <= hoje + pd.DateOffset(months=3))
    ])

    venc_6 = len(df[
        (df["VALIDADE"] >= hoje) &
        (df["VALIDADE"] <= hoje + pd.DateOffset(months=6))
    ])

    venc_9 = len(df[
        (df["VALIDADE"] >= hoje) &
        (df["VALIDADE"] <= hoje + pd.DateOffset(months=9))
    ])

    venc_12 = len(df[
        (df["VALIDADE"] >= hoje) &
        (df["VALIDADE"] <= hoje + pd.DateOffset(months=12))
    ])

    # =========================================
    # CARDS
    # =========================================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("ATIVOS", ativos)
    col2.metric("SUSPENSOS", suspensos)
    col3.metric("3 MESES", venc_3)
    col4.metric("6 MESES", venc_6)
    col5.metric("9 MESES", venc_9)
    col6.metric("12 MESES", venc_12)

    st.divider()

    # =========================================
    # FILTROS
    # =========================================

    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        filtro_status = st.selectbox(
            "Status",
            ["TODOS", "ATIVO", "SUSPENSO"]
        )

    with colf2:
        filtro_vencimento = st.selectbox(
            "Vencimento",
            [
                "TODOS",
                "3 MESES",
                "6 MESES",
                "9 MESES",
                "12 MESES"
            ]
        )

    with colf3:
        filtro_modelo = st.text_input(
            "Buscar Modelo",
            placeholder="Digite parte do nome..."
        )

    # =========================================
    # APLICAR FILTROS
    # =========================================

    df_filtrado = df.copy()

    # Filtro Modelo
    if filtro_modelo:
        df_filtrado = df_filtrado[
            df_filtrado["MODELO"].astype(str).str.contains(
                filtro_modelo, case=False, na=False
            )
        ]

    # Filtro Status
    if filtro_status != "TODOS":
        df_filtrado = df_filtrado[
            df_filtrado["STATUS"] == filtro_status
        ]

    # Filtro vencimento
    if filtro_vencimento == "3 MESES":

        df_filtrado = df_filtrado[
            (df_filtrado["VALIDADE"] >= hoje) &
            (df_filtrado["VALIDADE"] <= hoje + pd.DateOffset(months=3))
        ]

    elif filtro_vencimento == "6 MESES":

        df_filtrado = df_filtrado[
            (df_filtrado["VALIDADE"] >= hoje) &
            (df_filtrado["VALIDADE"] <= hoje + pd.DateOffset(months=6))
        ]

    elif filtro_vencimento == "9 MESES":

        df_filtrado = df_filtrado[
            (df_filtrado["VALIDADE"] >= hoje) &
            (df_filtrado["VALIDADE"] <= hoje + pd.DateOffset(months=9))
        ]

    elif filtro_vencimento == "12 MESES":

        df_filtrado = df_filtrado[
            (df_filtrado["VALIDADE"] >= hoje) &
            (df_filtrado["VALIDADE"] <= hoje + pd.DateOffset(months=12))
        ]

    # =========================================
    # ORDENAÇÃO
    # =========================================

    df_filtrado = df_filtrado.sort_values(
        by="VALIDADE",
        ascending=True
    )

    # =========================================
    # TABELA
    # =========================================

    st.subheader("Tabela de Homologações")

    st.dataframe(
        df_filtrado[
            [
                "MODELO",
                "HOMOLOGACAO",
                "VALIDADE",
                "STATUS",
                "DIAS_RESTANTES"
            ]
        ],
        column_config={
            "VALIDADE": st.column_config.DateColumn(
                "VALIDADE",
                format="DD/MM/YYYY"
            )
        },
        use_container_width=True,
        height=600
    )

else:
    st.info("Faça upload da planilha para iniciar.")
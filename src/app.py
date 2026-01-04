import streamlit as st
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode
from pathlib import Path

try:
    from filters import (
        load_data,
        apply_filters,
        get_cronobiological_sorter,
        get_unique_values
    )
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from filters import (
        load_data,
        apply_filters,
        get_cronobiological_sorter,
        get_unique_values
    )

# =========================
# CAMINHO ABSOLUTO DA IMAGEM (GARANTIDO)
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
IMG_PATH = BASE_DIR / "assets" / "Gabriel.jpeg"

st.set_page_config(
    page_title=" Painel de Inteligência Nutricional",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }
        h1 {
            font-family: Arial, Helvetica, sans-serif;
            font-weight: 700;
            color: #1E293B;
        }
        h2, h3 {
            font-family: Arial, Helvetica, sans-serif;
            font-weight: 600;
            color: #334155;
        }
        .stMetric {
            background-color: #F8FAFC;
            padding: 14px;
            border-radius: 6px;
            border: 1px solid #E2E8F0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 46px;
            background-color: #F1F5F9;
            border-radius: 4px 4px 0 0;
            padding-top: 8px;
            padding-bottom: 8px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF;
            border-top: 2px solid #2563EB;
        }
    </style>
    """,
    unsafe_allow_html=True
)

df = load_data()

if df.empty:
    st.error(
        "A base de dados não foi carregada corretamente. "
        "Verifique o arquivo CSV na pasta /data."
    )
    st.stop()

with st.sidebar:
    st.title("Protocolo")
    st.caption("Nutrição & Saúde Cognitiva")
    st.markdown("---")

    objetivos = get_unique_values(df, "Objetivo_Primario")
    periodos = get_unique_values(df, "Cronobiologia_Periodo")
    momentos_refeicao = get_unique_values(df, "Momento_Refeicao")
    categorias = get_unique_values(df, "Categoria")

    selected_objetivos = st.multiselect(
        "Objetivo Primário",
        options=objetivos,
        placeholder="Selecione um ou mais objetivos"
    )

    selected_periodos = st.multiselect(
        "Período do Dia",
        options=periodos,
        placeholder="Manhã, Tarde ou Noite"
    )

    selected_moments = st.multiselect(
        "Momento da Refeição",
        options=momentos_refeicao,
        placeholder="Antes, Durante, Depois ou Independente"
    )

    selected_categorias = st.multiselect(
        "Categoria",
        options=categorias,
        placeholder="Alimento, Suplemento, Nootrópico"
    )

    st.markdown("---")
    st.markdown(
        """
        **Notas de uso**
        - Período do dia refere-se ao ritmo circadiano
        - Momento da refeição é independente do período
        - Um item pode aparecer em mais de um período
        """
    )

df_filtered = apply_filters(
    df=df,
    selected_goals=selected_objetivos,
    selected_periods=selected_periodos,
    selected_moments=selected_moments,
    selected_cats=selected_categorias
)

if df_filtered.empty:
    st.warning(
        "Nenhum item encontrado com os filtros atuais. "
        "Ajuste os critérios na barra lateral."
    )

# =========================
# HEADER COM FOTO (CORRIGIDO)
# =========================
st.title("Manual Avançado de Nutrição e Otimização Cognitiva")

col_img, col_txt = st.columns([1, 5])

col_img, col_txt = st.columns([1, 8], gap="small")

with col_img:
    st.image(str(IMG_PATH), width=120)

with col_txt:
    st.markdown(
        """
        <div style="line-height:1.3; margin-top:6px;">
            <strong>Gabriel Guerra</strong><br>
            Analytics Engineer | Data & Analytics<br>
            <span style="color:#64748B;">Data Analytics, BI & Applied Intelligence</span><br>
            <span style="color:#2563EB;">
                <a href="https://www.linkedin.com/in/gabgsp/" target="_blank">LinkedIn</a> ·
                <a href="https://github.com/GabriGuerra" target="_blank">GitHub</a> ·
                <a href="mailto:gb.guerra@icloud.com">Email</a>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


k1, k2, k3, k4 = st.columns(4)

k1.metric("Itens Ativos", len(df_filtered))
k2.metric("Categorias", df_filtered["Categoria"].nunique())
k3.metric("Subcategorias", df_filtered["Subcategoria"].nunique())
k4.metric("Objetivos", df_filtered["Objetivo_Primario"].nunique())

tab1, tab2, tab3 = st.tabs(
    [
        "Protocolo Cronobiológico",
        "Base de Dados",
        "Visão Analítica"
    ]
)

with tab1:
    st.subheader("Planejamento Cronobiológico Diário")

    df_chrono = get_cronobiological_sorter(df_filtered)

    current_period = None

    for _, row in df_chrono.iterrows():
        period = row["Cronobiologia_Periodo"]

        if period != current_period:
            st.markdown(f"### {period}")
            current_period = period

        c1, c2, c3 = st.columns([2, 4, 2])

        with c1:
            st.markdown(f"**{row['Nome_Item']}**")
            st.caption(row["Categoria"])

        with c2:
            st.markdown(row["Uso_Pratico"])
            st.caption(f"Fonte alimentar: {row['Fonte_Alimentar']}")

        with c3:
            st.markdown(row["Tipo_Obtencao"])

        st.divider()

with tab2:
    st.subheader("Explorador de Dados")

    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    gb.configure_pagination(paginationPageSize=15)
    gb.configure_side_bar()
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True
    )

    gb.configure_column(
        "Nome_Item",
        header_name="Item",
        pinned="left",
        minWidth=200
    )

    gb.configure_column(
        "Objetivo_Primario",
        header_name="Objetivo",
        minWidth=200
    )

    gb.configure_column(
        "Cronobiologia_Periodo",
        header_name="Período"
    )

    gb.configure_column(
        "Momento_Refeicao",
        header_name="Refeição"
    )

    AgGrid(
        df_filtered,
        gridOptions=gb.build(),
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        height=600,
        fit_columns_on_grid_load=False
    )

with tab3:
    st.subheader("Distribuição Estratégica")

    c1, c2 = st.columns(2)

    with c1:
        fig_obj = px.bar(
            df_filtered["Objetivo_Primario"].value_counts().reset_index(name="count"),
            x="count",
            y="Objetivo_Primario",
            orientation="h",
            labels={"count": "Quantidade", "Objetivo_Primario": "Objetivo"}
        )
        st.plotly_chart(fig_obj, width="stretch")

    with c2:
        fig_cat = px.pie(
            df_filtered,
            names="Categoria",
            hole=0.45
        )
        st.plotly_chart(fig_cat, width="stretch")

    st.divider()

    fig_hier = px.sunburst(
        df_filtered,
        path=["Categoria", "Subcategoria", "Nome_Item"],
        color="Objetivo_Primario"
    )
    st.plotly_chart(fig_hier, width="stretch")

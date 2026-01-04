import pandas as pd
import streamlit as st
import os

# ==============================================================================
# CARREGAMENTO DE DADOS
# ==============================================================================
@st.cache_data
def load_data():
    """
    Carrega o CSV da pasta /data de forma robusta e padronizada.
    """
    possible_paths = [
        "data/database_nutri_otimizada.csv",
        "../data/database_nutri_otimizada.csv",
        "database_nutri_otimizada.csv"
    ]

    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if file_path is None:
        st.error(
            "Erro crítico: arquivo 'database_nutri_otimizada.csv' não encontrado. "
            "Verifique a pasta /data."
        )
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)

        required_columns = [
            "Nome_Item",
            "Categoria",
            "Objetivo_Primario",
            "Cronobiologia_Periodo",
            "Momento_Refeicao"
        ]

        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            st.error(f"Colunas obrigatórias ausentes no CSV: {missing}")
            return pd.DataFrame()

        return df

    except Exception as e:
        st.error(f"Erro ao ler o CSV: {e}")
        return pd.DataFrame()


# ==============================================================================
# LÓGICA DE FILTRAGEM (ALINHADA COM app.py)
# ==============================================================================
def apply_filters(
    df,
    selected_goals=None,
    selected_periods=None,
    selected_moments=None,
    selected_cats=None
):
    """
    Aplica filtros combinados ao DataFrame.
    Todos os filtros são opcionais.
    """
    if df.empty:
        return df

    df_filtered = df.copy()

    if selected_goals:
        df_filtered = df_filtered[
            df_filtered["Objetivo_Primario"].isin(selected_goals)
        ]

    if selected_periods:
        df_filtered = df_filtered[
            df_filtered["Cronobiologia_Periodo"].isin(selected_periods)
        ]

    if selected_moments:
        df_filtered = df_filtered[
            df_filtered["Momento_Refeicao"].isin(selected_moments)
        ]

    if selected_cats:
        df_filtered = df_filtered[
            df_filtered["Categoria"].isin(selected_cats)
        ]

    return df_filtered


# ==============================================================================
# ORDENAÇÃO CRONOBIOLÓGICA (MANHÃ → TARDE → NOITE)
# ==============================================================================
def get_cronobiological_sorter(df):
    """
    Ordena o DataFrame exclusivamente por:
    Manhã -> Tarde -> Noite

    Momento de refeição é tratado separadamente.
    """
    if df.empty:
        return df

    period_order = {
        "Manhã": 1,
        "Tarde": 2,
        "Noite": 3
    }

    df_sorted = df.copy()
    df_sorted["_order"] = df_sorted["Cronobiologia_Periodo"].map(
        lambda x: period_order.get(x, 99)
    )

    df_sorted = df_sorted.sort_values("_order")
    df_sorted = df_sorted.drop(columns="_order")

    return df_sorted


# ==============================================================================
# UTILITÁRIOS
# ==============================================================================
def get_unique_values(df, column):
    """
    Retorna lista única, ordenada e sem NaN para dropdowns.
    """
    if df.empty or column not in df.columns:
        return []

    return sorted(df[column].dropna().unique())

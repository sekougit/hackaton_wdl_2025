import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------- Chargement des données traitées ----------
@st.cache_data
def load_data():
    path = "processed_data/"
    data = {}
    for file in os.listdir(path):
        if file.endswith(".csv"):
            name = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(path, file))
            data[name] = df
    return data

# ---------- Filtrage des jeunes ----------
def filter_youth(df, age_col='age'):
    if age_col in df.columns:
        return df[(df[age_col] >= 15) & (df[age_col] <= 35)].copy()
    else:
        return df

# ---------- Streamlit App ----------
st.set_page_config(page_title="Emploi des jeunes dans l'UEMOA", layout="wide")

st.title("📊 Analyse de l'emploi des jeunes (15–35 ans) dans l'UEMOA")
st.markdown("Cette application permet d'explorer les données d'emploi, d'éducation et de secteur d'activité pour les jeunes dans les pays de l'UEMOA.")

data = load_data()

# --------- Sélection des données à explorer ----------
section = st.sidebar.selectbox("🔍 Choisir une base de données :", list(data.keys()))

df = data[section]
df = filter_youth(df)

# --------- Filtres dynamiques ----------
with st.sidebar.expander("🎛️ Filtres"):
    country = st.sidebar.selectbox("Pays :", df['country'].dropna().unique(), default=df['country'].dropna().unique())
    year = st.sidebar.slider("Année :", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))

    analyse = st.sidebar.radio("Analyses & modélisation", ["🏠 Analyses", "📊 Modeles", "📝 Performances"])

# --------- Application des filtres ----------
filtered_df = df[
    df['country'].isin(country) &
    df['year'].between(year[0], year[1])
]



st.subheader("📁 Aperçu des données filtrées")
st.dataframe(filtered_df.head(100))


# --------- Statistiques descriptives ----------
st.subheader("📋 Statistiques descriptives")
st.write(filtered_df.describe(include='all'))


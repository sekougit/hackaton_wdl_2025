import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------- Chargement des données traitées ----------
@st.cache_data
def load_data():
    path = "processed_data/"
    datasets = {}
    for file in os.listdir(path):
        if file.endswith(".csv"):
            name = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(path, file))
            datasets[name] = df
    return datasets

# ---------- Streamlit App ----------
st.set_page_config(page_title="Emploi des jeunes dans l'UEMOA", layout="wide")

st.title("📊 Analyse de l'emploi des jeunes (15–35 ans) dans l'UEMOA")
st.markdown("Cette application permet d'explorer les données d'emploi, d'éducation et de secteur d'activité pour les jeunes dans les pays de l'UEMOA.")

datasets = load_data()

# --------- Sélection des données à explorer ----------
section = st.sidebar.selectbox("🔍 Choisir une base de données :", list(datasets.keys()))

df = datasets[section]

# Filtres dynamiques
with st.sidebar.expander("🎛️ Filtres"):
    countries = df['country'].dropna().unique().tolist()
    selected_country = st.selectbox("Pays :", countries)

    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_range = st.slider("Année :", min_value=min_year, max_value=max_year, value=(min_year, max_year))

analyse = st.sidebar.radio("Analyses & modélisation", ["🏠 Accueil", "📊 Analyses", "📝 Performances"])

# --------- Application des filtres ----------
filtered_data = df[
    (df['country'] == selected_country) &
    (df['year'].between(year_range[0], year_range[1]))
]


if analyse == "Accueil"
	# --------- Affichage des données filtrées ----------
	st.subheader("📁 Aperçu des données filtrées")
	st.dataframe(filtered_data.head(100))

	# --------- Statistiques descriptives ----------
	st.subheader("📋 Statistiques descriptives")
	st.write(filtered_data.describe(include='all'))

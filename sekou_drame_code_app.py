import streamlit as st
import pandas as pd
import plotly.express as px
import os
import seaborn as sns
import matplotlib as plt

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


if analyse == "🏠 Accueil":
	# --------- Affichage des données filtrées ----------
	st.subheader("📁 Aperçu des données filtrées")
	st.dataframe(filtered_data.head(100))

	# --------- Statistiques descriptives ----------
	st.subheader("📋 Statistiques descriptives")
	st.write(filtered_data.describe(include='all'))
     
if analyse == "📊 Analyses":
    col1, col2, col3 = st.columns(3)

    with col1:
        available_countries = df['country'].dropna().unique().tolist()
        selected_country = st.selectbox("Pays", available_countries)

    with col2:
        years = sorted(df['year'].dropna().unique().tolist())
        selected_year = st.selectbox("Année", years)

    with col3:
        possible_hues = ['gender', 'urban', 'education', 'sector']
        hue_col = st.selectbox("Couleur (hue)", [h for h in possible_hues if h in df.columns])
    
        # ---------- Filtrage des données ----------
    df_filtered = df[(df['country'] == selected_country) & (df['year'] == selected_year)]

    st.subheader(f"📈 Répartition du statut d’emploi ({selected_country}, {selected_year}) selon : {hue_col}")

    if df_filtered.empty:
        st.warning("Aucune donnée disponible pour cette sélection.")
    else:
        # Création du graphique avec seaborn
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(data=df_filtered, x='status', hue=hue_col, ax=ax)
        ax.set_title(f"{selected_country} - {selected_year}")
        ax.set_xlabel("Statut d'emploi")
        ax.set_ylabel("Effectif")
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        st.pyplot(fig)

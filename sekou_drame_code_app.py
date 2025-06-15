import streamlit as st
import pandas as pd
import plotly.express as px
import os
import seaborn as sns
import matplotlib.pyplot as plt
from models import train_model

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

def data_modele(filename="Data_africa_sector_employed_filtered.csv", folder="processed_data"):
    datasets = {}
    path = os.path.abspath(folder)  # chemin absolu vers le dossier

    if not os.path.exists(path):
        raise FileNotFoundError(f"Dossier introuvable : {path}")

    for file in os.listdir(path):
        if file == filename and file.endswith(".csv"):
            full_path = os.path.join(path, file)
            df = pd.read_csv(full_path)
            name = file.replace(".csv", "")
            datasets[name] = df
            break  # on arrête dès qu'on a trouvé le fichier
    
    if not datasets:
        raise FileNotFoundError(f"Fichier {filename} introuvable dans {path}")
    
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
        country_analyses = st.selectbox("Pays", available_countries, key="repartition_pays")

    with col2:
        years = sorted(df['year'].dropna().unique().tolist())
        selected_year = st.selectbox("Année", years, key="repartition_year")

    with col3:
        possible_hues = ['gender', 'urban', 'education', 'sector']
        hue_col = st.selectbox("Couleur (hue)", [h for h in possible_hues if h in df.columns],key="repartition_hue")
    
        # ---------- Filtrage des données ----------
    df_filtered = df[(df['country'] == country_analyses) & (df['year'] == selected_year)]

    st.subheader(f"📈 Répartition du statut d’emploi ({country_analyses}, {selected_year}) selon : {hue_col}")

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
    
    col4, col5 = st.columns(2)

    with col4:
        available_countries_1 = df['country'].dropna().unique().tolist()
        country_analyses_1 = st.selectbox("Pays", available_countries,key="evolution_pays")

    with col5:
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        status_1 = st.selectbox("variables", categorical_columns, key="evolution_variable")

        # Filtrer les données pour le Sénégal
    df_senegal = df[df['country'] == country_analyses_1]

    # Vérifier si la colonne 'population' existe
    if 'population' not in df_senegal.columns:
        st.error("La colonne 'population' est manquante dans les données sélectionnées.")
    else:
        # Grouper par année et statut pour obtenir la population totale
        df_grouped = df_senegal.groupby(['year', status_1])['population'].sum().reset_index()

        # Tracer la courbe
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=df_grouped, x='year', y='population', hue=status_1, marker='o', ax=ax)
        ax.set_title(f"Évolution de la population par statut d’emploi par {status_1} ({country_analyses_1}, 2015–2030)")
        ax.set_xlabel("Année")
        ax.set_ylabel("Population")
        ax.grid(True)
        plt.tight_layout()

        st.pyplot(fig)

        # Sélection interactive du pays et de l’année
    col1, col2, col3 = st.columns(3)

    with col1:
        country_selected = st.selectbox("Choisir un pays", df['country'].dropna().unique().tolist())

    with col2:
        year_selected = st.selectbox("Choisir une année", sorted(df['year'].dropna().unique().tolist()))

    with col3:
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        var_unique = st.selectbox("variables", categorical_columns, key="variable_unique")

    # Filtrer les données
    df_filtered = df[(df['country'] == country_selected) & (df['year'] == year_selected)]

    if df_filtered.empty:
        st.warning("Aucune donnée disponible pour ce pays et cette année.")
    else:
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(data=df_filtered, x=var_unique, order=df_filtered[var_unique].value_counts().index, ax=ax)
        ax.set_title(f"Niveau d'éducation des jeunes - {country_selected} ({year_selected})")
        ax.tick_params(axis='x', rotation=45)
        ax.set_ylabel("Effectif")
        ax.set_xlabel(f"{var_unique}")
        st.pyplot(fig)

if analyse == "📝 Performances":
    base_modele = data_modele()

    # ⏱️ Entraînement
    model_pipeline, df_modele, coefficients, metrics = train_model(base_modele)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Performances", "📌 Coefficients", "📈 Prévisions"])

    with tab1:
        st.subheader("📊 Performances du modèle")
        st.metric("R²", f"{metrics['r2']:.3f}")
        st.metric("MAE", f"{metrics['mae']:,.0f}")
        st.metric("RMSE", f"{metrics['rmse']:,.0f}")

    with tab2:
        st.subheader("📌 Coefficients")
        st.dataframe(coefficients, use_container_width=True)

    with tab3:
        st.subheader("📈 Prévisions")
        secteur = st.selectbox("Choisir un secteur", df_modele['sector'].unique())
        df_plot = df_modele[df_modele['sector'] == secteur]

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=df_plot, x='year', y='population', hue='gender', linestyle='--', ax=ax, label='Observé')
        sns.lineplot(data=df_plot, x='year', y='predicted_population', hue='gender', linestyle='-', ax=ax, label='Prévu')
        ax.set_title(f"Prévision vs Réalité – {secteur}")
        st.pyplot(fig)
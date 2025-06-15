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

def data_modele():
    path = "processed_data/Data_africa_sector_employed_filtered.csv"
    df = pd.read_csv(path)
    return df

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
    # --- Sélections utilisateurs ---
    col1, col2, col3 = st.columns(3)

    with col1:
        available_countries = df['country'].dropna().unique().tolist()
        country_1 = st.selectbox("Pays 1", available_countries, key="repartition_pays_1")

    with col2:
        country_2 = st.selectbox("Pays 2", available_countries, key="repartition_pays_2")

    with col3:
        years = sorted(df['year'].dropna().unique().tolist())
        selected_year = st.selectbox("Année", years, key="repartition_year")

    hue_options = ['gender', 'urban', 'education', 'sector']
    available_hues = [h for h in hue_options if h in df.columns]
    hue_col = st.selectbox("Variable de couleur (hue)", available_hues, key="repartition_hue")

    # --- Filtrage ---
    df_1 = df[(df['country'] == country_1) & (df['year'] == selected_year)]
    df_2 = df[(df['country'] == country_2) & (df['year'] == selected_year)]

    st.subheader(f"📊 Comparaison de la répartition du statut d’emploi ({selected_year})")

    col_a, col_b = st.columns(2)

    # --- Graphique Pays 1 ---
    with col_a:
        st.markdown(f"### {country_1}")
        if df_1.empty:
            st.warning(f"Aucune donnée pour {country_1} en {selected_year}")
        else:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df_1, x='status', hue=hue_col, ax=ax1)
            ax1.set_title(f"{country_1} - {selected_year}")
            ax1.set_xlabel("Statut d'emploi")
            ax1.set_ylabel("Effectif")
            ax1.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig1)

    # --- Graphique Pays 2 ---
    with col_b:
        st.markdown(f"### {country_2}")
        if df_2.empty:
            st.warning(f"Aucune donnée pour {country_2} en {selected_year}")
        else:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df_2, x='status', hue=hue_col, ax=ax2)
            ax2.set_title(f"{country_2} - {selected_year}")
            ax2.set_xlabel("Statut d'emploi")
            ax2.set_ylabel("Effectif")
            ax2.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)
    
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

    #base_modele = pd.DataFrame(base_modele)

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
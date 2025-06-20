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
    path = "processed_data/Data_africa_sector_employed_imputed.csv"
    df = pd.read_csv(path)
    return df

# ---------- Streamlit App ----------
st.set_page_config(page_title="Emploi des jeunes dans l'UEMOA", 
                   page_icon="https://raw.githubusercontent.com/sekougit/hackaton_wdl_2025/main/processed_data/uemoa.png",
                   layout="wide")


st.title("📊 Analyse de l'emploi des jeunes (15–35 ans) dans l'UEMOA")
st.markdown("Cette application permet d'explorer les données d'emploi, d'éducation et de secteur d'activité pour les jeunes dans les pays de l'UEMOA.")

datasets = load_data()

# --------- Sélection des données à explorer ----------
st.sidebar.image(
    "https://raw.githubusercontent.com/sekougit/hackaton_wdl_2025/main/processed_data/uemoa.png",
    caption="Logo UEMOA"
)
section = st.sidebar.selectbox("🔍 Choisir une base de données :", list(datasets.keys()))

df = datasets[section]

# Filtres dynamiques
with st.sidebar.expander("🎛️ Filtres"):
    countries = df['country'].dropna().unique().tolist()
    selected_country = st.selectbox("Pays :", countries)

    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_range = st.slider("Année :", min_value=min_year, max_value=max_year, value=(min_year, max_year))

analyse = st.sidebar.radio("Analyses & modélisation", ["🏠 Accueil", "🧮 Données","📊 Analyses", "📝 Modéle"])

# --------- Application des filtres ----------
filtered_data = df[
    (df['country'] == selected_country) &
    (df['year'].between(year_range[0], year_range[1]))
]

if analyse == "🏠 Accueil":
        # Image en haut de la page
    st.image(
        "https://raw.githubusercontent.com/sekougit/hackaton_wdl_2025/main/processed_data/logo_wdl.png",  # Remplace par le lien direct vers ton image hébergée
        caption="World Data Lab",
        use_column_width=False
    )

    # Titre de la page
    st.title("🌍 Hackathon World Data Lab 2025")

    # Texte de présentation enrichi
    st.markdown("""
    Bienvenue sur la page de présentation du **Hackathon World Data Lab 2025** !

    ---

    ### 🌍 Présentation du World Data Lab (WDL)

    **World Data Lab (WDL)** est une organisation internationale spécialisée dans la production de données démographiques et économiques prédictives.  
    Son objectif est de **rendre les données accessibles et exploitables** pour orienter les décisions publiques et privées.  
    WDL développe des outils interactifs comme le **World Poverty Clock** et le **Global Education Monitor**.  
    L'organisation collabore avec des gouvernements, ONG et entreprises pour **mieux cibler les politiques sociales**.  
    Elle met un accent particulier sur l’Afrique, avec des projets pour anticiper les enjeux liés à la jeunesse, à l’emploi et à l’éducation.

    ---

    ### 🎯 Le Hackathon

    Le hackathon organisé par le World Data Lab met l’accent sur l’emploi des jeunes dans 
    la zone UEMOA, en mobilisant des données démographiques, éducatives et économiques pour analyser 
    les tendances actuelles, comprendre les facteurs déterminants et prédire l’évolution du marché du 
    travail des 15–35 ans à l’horizon 2030, dans une optique d’aide à la décision publique.

    ---

    ### 🎯 Objectifs
    - Explorer les tendances d'emploi des jeunes dans la région.
    - Identifier les déterminants clés de l'emploi selon le genre, l'âge, le niveau d'éducation et le secteur.
    - Construire des modèles de prédiction fiables et reproductibles.
    - Formuler des recommandations orientées politique publique.

    ---

    ### 🧰 Données utilisées
    - Données démographiques et socio-économiques de la population jeune.
    - Indicateurs liés à l'éducation, à l’urbanisation et aux secteurs d'activité.
    - Projections à l’horizon 2030 selon plusieurs scénarios.

    ---

    ### 🧠 Notre approche
    - Nettoyage et structuration rigoureuse des données.
    - Analyses descriptives et visualisations interactives.
    - Modélisation statistique (régression, splines, interactions).
    - Interface web interactive pour l'exploration des résultats.

    ---

    ### 👥 Membres de l'équipe
    - **Sekou Dramé** – Analyste Statisticien
    - **ENSAE Dakar** – Support pédagogique et encadrement

    ---

    Ce projet est une contribution à l’analyse stratégique de l’emploi des jeunes dans la zone UEMOA.

    **#DataForDevelopment | #WDLHackathon2025**
    """)


if analyse == "🧮 Données":
	# --------- Affichage des données filtrées ----------
	st.subheader("📁 Aperçu des données filtrées")
	st.dataframe(filtered_data.head(100))

	# --------- Statistiques descriptives ----------
	st.subheader("📋 Statistiques descriptives")
	st.write(filtered_data.describe(include='all'))
     
if analyse == "📊 Analyses":
    # --- Sélections utilisateurs ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        available_countries = df['country'].dropna().unique().tolist()
        country_1 = st.selectbox("Pays 1", available_countries, key="repartition_pays_1")

    with col2:
        country_2 = st.selectbox("Pays 2", available_countries, key="repartition_pays_2")

    with col3:
        years = sorted(df['year'].dropna().unique().tolist())
        selected_year = st.selectbox("Année", years, key="repartition_year")

    with col4:
        #hue_options = ['gender', 'urban', 'education', 'sector']
        available_hues = [h for h  in df.select_dtypes(include=['object', 'category']).columns]
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
    
    col4, col5, col3 = st.columns(3)

    with col4:
        available_countries = df['country'].dropna().unique().tolist()
        country_1 = st.selectbox("Pays 1", available_countries, key="evolution_pays_1")

    with col5:
        country_2 = st.selectbox("Pays 2", available_countries, key="evolution_pays_2")

    with col3:
        # Sélection de la variable catégorielle (à regrouper)
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_columns = [col for col in categorical_columns if col not in ['country', 'year', 'population']]  # éviter doublons inutiles
        status_var = st.selectbox("Variable de regroupement", categorical_columns, key="evolution_variable")

    col_a, col_b = st.columns(2)

    # --- Courbe pour le pays 1 ---
    with col_a:
        df_1 = df[df['country'] == country_1]

        st.markdown(f"### {country_1}")
        if 'population' not in df_1.columns or df_1.empty:
            st.warning("Aucune donnée ou colonne 'population' manquante.")
        else:
            df_grouped_1 = df_1.groupby(['year', status_var])['population'].sum().reset_index()

            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.lineplot(data=df_grouped_1, x='year', y='population', hue=status_var, marker='o', ax=ax1)
            ax1.set_title(f"{country_1} - Évolution par {status_var}")
            ax1.set_xlabel("Année")
            ax1.set_ylabel("Population")
            ax1.grid(True)
            st.pyplot(fig1)

    # --- Courbe pour le pays 2 ---
    with col_b:
        df_2 = df[df['country'] == country_2]

        st.markdown(f"### {country_2}")
        if 'population' not in df_2.columns or df_2.empty:
            st.warning("Aucune donnée ou colonne 'population' manquante.")
        else:
            df_grouped_2 = df_2.groupby(['year', status_var])['population'].sum().reset_index()

            fig2, ax2 = plt.subplots(figsize=(8, 5))
            sns.lineplot(data=df_grouped_2, x='year', y='population', hue=status_var, marker='o', ax=ax2)
            ax2.set_title(f"{country_2} - Évolution par {status_var}")
            ax2.set_xlabel("Année")
            ax2.set_ylabel("Population")
            ax2.grid(True)
            st.pyplot(fig2)

    # Sélection interactive des deux pays, de l’année et de la variable catégorielle
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        country_1 = st.selectbox("Pays 1", df['country'].dropna().unique().tolist(), key="pays1_var_unique")

    with col2:
        country_2 = st.selectbox("Pays 2", df['country'].dropna().unique().tolist(), key="pays2_var_unique")

    with col3:
        year_selected = st.selectbox("Année", sorted(df['year'].dropna().unique().tolist()), key="annee_var_unique")

    with col4:
        # Choix de la variable à analyser
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_columns = [col for col in categorical_columns if col not in ['country', 'year']]  # on exclut ces deux colonnes
        var_unique = st.selectbox("Variable catégorielle à analyser", categorical_columns, key="variable_unique_comparaison")

    # Création des deux colonnes pour afficher les figures côte à côte
    col_left, col_right = st.columns(2)

    # --- Figure pour le premier pays ---
    with col_left:
        df_1 = df[(df['country'] == country_1) & (df['year'] == year_selected)]

        st.markdown(f"### {country_1} ({year_selected})")
        if df_1.empty:
            st.warning(f"Aucune donnée disponible pour {country_1} en {year_selected}.")
        else:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df_1, x=var_unique, order=df_1[var_unique].value_counts().index, ax=ax1)
            ax1.set_title(f"{country_1}")
            ax1.set_xlabel(var_unique)
            ax1.set_ylabel("Effectif")
            ax1.tick_params(axis='x', rotation=45)
            st.pyplot(fig1)

    # --- Figure pour le second pays ---
    with col_right:
        df_2 = df[(df['country'] == country_2) & (df['year'] == year_selected)]

        st.markdown(f"### {country_2} ({year_selected})")
        if df_2.empty:
            st.warning(f"Aucune donnée disponible pour {country_2} en {year_selected}.")
        else:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df_2, x=var_unique, order=df_2[var_unique].value_counts().index, ax=ax2)
            ax2.set_title(f"{country_2}")
            ax2.set_xlabel(var_unique)
            ax2.set_ylabel("Effectif")
            ax2.tick_params(axis='x', rotation=45)
            st.pyplot(fig2)

if analyse == "📝 Modéle":
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
        sns.lineplot(data=df_plot, x='year', y='population', hue='gender', linestyle='--', ax=ax)
        sns.lineplot(data=df_plot, x='year', y='predicted_population', hue='gender', linestyle='-', ax=ax)
        ax.set_title(f"Prévision vs Réalité – {secteur}")
        st.pyplot(fig)
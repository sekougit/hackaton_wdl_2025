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

# Sélection de la base de données
section = st.sidebar.selectbox("🔍 Choisir une base de données :", list(data.keys()))

# Sélection de l'analyse
analyse = st.radio("Analyses & modélisation", ["🏠 Analyses", "📊 Modèles", "📝 Performances"])

# Chargement et filtrage de la base sélectionnée
df = data[section]

# Appliquer le filtre jeunes
df = filter_youth(df)

# --------- Filtres dynamiques ----------
with st.sidebar.expander("🎛️ Filtres"):

    # Sélection des pays
    all_countries = df['country'].dropna().unique()
    country = st.multiselect("Pays :", options=sorted(all_countries), default=sorted(all_countries))

    # Sélection de l'année (intervalle)
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year = st.slider("Année :", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# --------- Application des filtres ----------
df_filtered = df[
    df['country'].isin(country) &
    df['year'].between(year[0], year[1])
]

# --------- Visualisations ----------
st.subheader("📈 Visualisations")

col1, col2 = st.columns(2)

with col1:
    if 'education_level' in filtered_df.columns:
        edu_fig = px.histogram(filtered_df, x='education_level', color='sex' if 'sex' in filtered_df.columns else None,
                               title="Niveau d'éducation des jeunes", barmode="group")
        st.plotly_chart(edu_fig, use_container_width=True)

with col2:
    if 'employment_status' in filtered_df.columns:
        emp_fig = px.histogram(filtered_df, x='employment_status', color='sex' if 'sex' in filtered_df.columns else None,
                               title="Statut d'emploi des jeunes", barmode="group")
        st.plotly_chart(emp_fig, use_container_width=True)

if 'sector' in filtered_df.columns:
    st.subheader("📊 Répartition par secteur d'activité")
    sector_fig = px.histogram(filtered_df, x='sector', color='sex' if 'sex' in filtered_df.columns else None,
                              title="Jeunes employés par secteur", barmode="group")
    st.plotly_chart(sector_fig, use_container_width=True)

# --------- Statistiques descriptives ----------
st.subheader("📋 Statistiques descriptives")
st.write(filtered_df.describe(include='all'))


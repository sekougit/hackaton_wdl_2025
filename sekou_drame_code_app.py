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



# ---------- Streamlit App ----------
st.set_page_config(page_title="Emploi des jeunes dans l'UEMOA", layout="wide")

st.title("📊 Analyse de l'emploi des jeunes (15–35 ans) dans l'UEMOA")
st.markdown("Cette application permet d'explorer les données d'emploi, d'éducation et de secteur d'activité pour les jeunes dans les pays de l'UEMOA.")

data = load_data()

# --------- Sélection des données à explorer ----------
section = st.sidebar.selectbox("🔍 Choisir une base de données :", list(data.keys()))

data = data[section]

country = st.sidebar.selectbox("Pays :", df['country'].dropna().unique(), default=df['country'].dropna().unique())
    
year = st.sidebar.slider("Année :", int(df['year'].min()), int(df['year'].max()), (int(df['year'].min()), int(df['year'].max())))

analyse = st.sidebar.radio("Analyses & modélisation", ["🏠 Analyses", "📊 Modeles", "📝 Performances"])

# --------- Application des filtres ----------
data = data[
    data['country'] == country &
    data['year'].between(year[0], year[1])
]



st.subheader("📁 Aperçu des données filtrées")
st.dataframe(data.head(100))


# --------- Statistiques descriptives ----------
st.subheader("📋 Statistiques descriptives")
st.write(data.describe(include='all'))


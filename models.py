# models.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error

def train_model(df_modele):
    # Vérification des colonnes requises
    required_cols = ['year', 'sector', 'gender', 'age', 'country', 'population']
    for col in required_cols:
        if col not in df_modele.columns:
            raise ValueError(f"Colonne manquante dans les données : {col}")

    # Sélection des variables
    X = df_modele[['year', 'sector', 'gender', 'country']].copy()
    y = df_modele['population']

    # Prétraitement
    X['sector'] = X['sector'].astype(str)
    X['gender'] = X['gender'].astype(str)
    X['country'] = X['country'].astype(str)
    X['year'] = X['year'].astype(float)
    X['year_centered'] = X['year'] - X['year'].min()

    # Colonnes catégorielles et numériques
    cat_cols = ['sector', 'gender', 'country']
    num_cols = ['age']
    spline_col = ['year_centered']

    # Pipeline de prétraitement
    preprocessor = ColumnTransformer([
        ('cat', OneHotEncoder(drop='first'), cat_cols),
        ('spline', SplineTransformer(degree=3, n_knots=5), spline_col),
        ('num', 'passthrough', num_cols)
    ])

    # Pipeline complet avec interactions
    model_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('interactions', PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)),
        ('regressor', LinearRegression())
    ])

    # Entraînement
    model_pipeline.fit(X, y)
    y_pred = model_pipeline.predict(X)
    df_modele['predicted_population'] = y_pred

    # Récupération des noms de variables transformées (robuste)
    fitted_preprocessor = model_pipeline.named_steps['preprocessor']
    try:
        ohe_cols = fitted_preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols)
    except Exception as e:
        ohe_cols = []
        print("Erreur OneHotEncoder :", e)

    try:
        spline_transformer = fitted_preprocessor.named_transformers_['spline']
        spline_cols = [f"spline_{i}" for i in range(spline_transformer.n_output_features_)]
    except Exception as e:
        spline_cols = []
        print("Erreur SplineTransformer :", e)

    final_input_features = list(ohe_cols) + spline_cols + num_cols

    try:
        feature_names = model_pipeline.named_steps['interactions'].get_feature_names_out(final_input_features)
    except Exception as e:
        print("Erreur PolynomialFeatures.get_feature_names_out :", e)
        feature_names = [f"feature_{i}" for i in range(len(model_pipeline.named_steps['regressor'].coef_))]

    # Coefficients
    coefficients = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': model_pipeline.named_steps['regressor'].coef_
    }).sort_values(by='Coefficient', key=abs, ascending=False)

    # Performances
    metrics = {
        'r2': model_pipeline.score(X, y),
        'mae': mean_absolute_error(y, y_pred),
        'rmse': np.sqrt(mean_squared_error(y, y_pred))
    }

    return model_pipeline, df_modele, coefficients, metrics

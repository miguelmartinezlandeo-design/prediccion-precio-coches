"""Reentrena el modelo de precios de coches y compara con el modelo actual.

El modelo se reentrena sobre el dataset limpio (used_car_price_analysis_limpio.csv)
usando EXACTAMENTE el mismo pipeline y los mismos hiperparámetros que el modelo
guardado en modelo_coches.pkl, para que la aplicación no necesite cambios de código.

La comparación evalúa tres escenarios sobre el mismo conjunto de test:
  A) modelo actual sobre datos sucios  -> rendimiento "en papel" del modelo actual
  B) modelo actual sobre datos limpios -> lo que hace la aplicación HOY (el bug)
  C) modelo nuevo   sobre datos limpios -> rendimiento real del modelo nuevo
"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from limpiar_datos import limpiar

DIR = os.path.dirname(os.path.abspath(__file__))
CSV_ORIGINAL = os.path.join(DIR, "used_car_price_analysis.csv")
CSV_LIMPIO = os.path.join(DIR, "used_car_price_analysis_limpio.csv")
PKL_ACTUAL = os.path.join(DIR, "modelo_coches.pkl")
PKL_NUEVO = os.path.join(DIR, "modelo_coches_nuevo.pkl")

NUMERICAS = ["year", "mileage", "tax", "mpg", "engineSize"]
CATEGORICAS = ["model", "transmission", "fuelType"]
FEATURES = NUMERICAS + CATEGORICAS

RANDOM_STATE = 42
TEST_SIZE = 0.25


def construir_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "preprocesamiento",
                ColumnTransformer(
                    transformers=[
                        ("numericas", "passthrough", NUMERICAS),
                        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
                    ]
                ),
            ),
            (
                "random_forest",
                RandomForestRegressor(
                    max_depth=20,
                    min_samples_split=15,
                    n_estimators=200,
                    n_jobs=1,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def metricas(y_real, y_pred) -> dict:
    return {
        "R2": r2_score(y_real, y_pred),
        "RMSE": float(np.sqrt(mean_squared_error(y_real, y_pred))),
        "MAE": float(mean_absolute_error(y_real, y_pred)),
    }


def tabla_comparativa(filas: list) -> pd.DataFrame:
    return pd.DataFrame(filas).set_index("escenario")


def main() -> None:
    df_dirty = pd.read_csv(CSV_ORIGINAL)
    df_clean = limpiar(df_dirty)

    # El dataset limpio en disco se reconstruye con limpiar() para conservar el
    # indice original: sin el, df_dirty.loc[test.index] seleccionaria otras filas.
    df_clean_disco = pd.read_csv(CSV_LIMPIO)
    assert len(df_clean) == len(df_clean_disco), (
        f"limpiar() genera {len(df_clean)} filas y el CSV limpio tiene {len(df_clean_disco)}"
    )
    assert list(df_clean.columns) == list(df_clean_disco.columns), "Columnas distintas"

    print("=" * 78)
    print("REENTRENAMIENTO Y COMPARATIVA DE MODELOS")
    print("=" * 78)
    print(f"Filas dataset original (sucio): {len(df_dirty):,}")
    print(f"Filas dataset limpio:           {len(df_clean):,}")
    print()

    df_entrenamiento, df_test = train_test_split(
        df_clean, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    X_entrenamiento = df_entrenamiento[FEATURES]
    y_entrenamiento = df_entrenamiento["price"]
    # El dataset sucio conserva los 3 tax nulos que el modelo no admite,
    # así que se excluyen para que los tres escenarios usen las mismas filas.
    nulos_tax = df_dirty["tax"].isna()
    df_test = df_test[~nulos_tax.loc[df_test.index]]

    X_test = df_test[FEATURES]
    y_test = df_test["price"]
    X_test_sucio = df_dirty.loc[df_test.index, FEATURES]

    print(f"Entrenamiento: {len(df_entrenamiento):,} filas")
    print(f"Test:          {len(df_test):,} filas (excluidos {int(nulos_tax.loc[df_test.index].sum())} con tax nulo)")
    print()

    modelo_nuevo = construir_pipeline()
    modelo_nuevo.fit(X_entrenamiento, y_entrenamiento)
    modelo_actual = joblib.load(PKL_ACTUAL)

    pred = {
        "A) actual / datos sucios (entrenado sobre todo el dataset)": modelo_actual.predict(
            X_test_sucio
        ),
        "B) actual / datos limpios (lo que hace la app hoy)": modelo_actual.predict(X_test),
        "C) nuevo / datos limpios (test limpio)": modelo_nuevo.predict(X_test),
    }

    filas = []
    for escenario, y_pred in pred.items():
        m = metricas(y_test, y_pred)
        filas.append(
            {
                "escenario": escenario,
                "R2": round(m["R2"], 4),
                "RMSE": round(m["RMSE"], 2),
                "MAE": round(m["MAE"], 2),
            }
        )

    print("=" * 78)
    print("COMPARATIVA (mismo conjunto de test)")
    print("=" * 78)
    print(tabla_comparativa(filas).to_string())
    print()

    encoder_actual = modelo_actual.named_steps["preprocesamiento"].named_transformers_[
        "categoricas"
    ]
    encoder_nuevo = modelo_nuevo.named_steps["preprocesamiento"].named_transformers_[
        "categoricas"
    ]
    print(f"Categorias aprendidas por el encoder ACTUAL: {len(encoder_actual.categories_[0])}")
    print(f"  ejemplos: {[repr(c) for c in encoder_actual.categories_[0][:5]]}")
    print(f"Categorias aprendidas por el encoder NUEVO:  {len(encoder_nuevo.categories_[0])}")
    print(f"  ejemplos: {[repr(c) for c in encoder_nuevo.categories_[0][:5]]}")
    print()

    print("=" * 78)
    print("PRUEBA FUNCIONAL: mismos datos numéricos, distinto modelo")
    print("=" * 78)
    modelos = [
        "Fiesta",
        "Focus",
        "Kuga",
        "Puma",
        "Edge",
        "Mustang",
        "EcoSport",
        "KA",
        "Ka+",
        "Mondeo",
    ]
    base = {
        "year": 2020,
        "mileage": 45000,
        "tax": 150,
        "mpg": 55,
        "engineSize": 2.0,
        "transmission": "Manual",
        "fuelType": "Petrol",
    }
    entrada = pd.DataFrame([{**base, "model": m} for m in modelos])
    precios_actual = modelo_actual.predict(entrada)
    precios_nuevo = modelo_nuevo.predict(entrada)

    print(
        f"{'modelo':<12}{'actual':>14}{'nuevo':>14}{'mediana real':>16}"
    )
    for modelo, p_actual, p_nuevo in zip(modelos, precios_actual, precios_nuevo):
        mediana = df_clean.loc[df_clean["model"] == modelo, "price"].median()
        print(
            f"{modelo:<12}{p_actual:>14,.2f}{p_nuevo:>14,.2f}"
            f"{mediana:>16,.0f}"
        )

    distintos_nuevo = len(set(np.round(precios_nuevo, 6)))
    distintos_actual = len(set(np.round(precios_actual, 6)))
    print()
    print(f"Precios DISTINTOS generados -> actual: {distintos_actual}/{len(modelos)}"
          f"   nuevo: {distintos_nuevo}/{len(modelos)}")
    print()

    joblib.dump(modelo_nuevo, PKL_NUEVO)
    print(f"Modelo nuevo guardado en: {PKL_NUEVO}")
    print(f"Modelo actual intacto en: {PKL_ACTUAL}")
    print("=" * 78)


if __name__ == "__main__":
    main()

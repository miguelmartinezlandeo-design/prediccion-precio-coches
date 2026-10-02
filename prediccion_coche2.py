import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Predicción del precio del coche", page_icon="🚗")

# cargamos el modelo entrenado
modelo = joblib.load("modelo_coches.pkl")
df = pd.read_csv("used_car_price_analysis_limpio.csv")
# Lista de modelos derivada de las categorias que el modelo aprendio, ordenadas por
# frecuencia. Asi ningun modelo de la lista puede cair en el 'ignore' del OneHotEncoder.
categorias_modelo = modelo.named_steps["preprocesamiento"].named_transformers_["categoricas"].categories_[0]
frecuencia = df["model"].value_counts()
modelos_disponibles = sorted(
    (m for m in categorias_modelo if m in frecuencia.index),
    key=lambda m: -frecuencia[m],
)
# Soporte de datos: que tan lejos esta la consulta de los coches que hay en el dataset.
# Se mide sobre year, mileage, mpg y engineSize estandarizados; la transmission y el
# fuelType no se filtran porque mpg y engineSize ya los distinguen de forma continua.
MEDIDAS_SOPORTE = ["year", "mileage", "mpg", "engineSize"]
_media_soporte = df[MEDIDAS_SOPORTE].mean()
_desv_soporte = df[MEDIDAS_SOPORTE].std()
_Z_soporte = ((df[MEDIDAS_SOPORTE] - _media_soporte) / _desv_soporte).to_numpy()
_modelos_soporte = df["model"].to_numpy()
RADIO_SOPORTE = 4.0  # radio de 2 desviaciones tipicas al cuadrado
# Titulo
st.title("🚗 Predicción del precio del coche")
st.subheader("🚗🚕Detalles del coche")
model = st.selectbox("Seleccione el modelo del coche", modelos_disponibles)
transmision = st.selectbox("Seleccione el tipo de transmisión", ["Manual", "Automatic", "Semi-Auto"])
combustible = st.selectbox("Seleccione el tipo de combustible",  ["Diesel", "Petrol", "Hybrid", "Electric", "Other"])
st.subheader("💰Datos Numéricos")
year = st.slider("Seleccione el año del coche", min_value=1990, max_value=2025, value=2020)

# Valores iniciales derivados del dataset limpio para la combinacion elegida.
# Cadena de respaldo: modelo+ano+transmision+combustible, luego se van soltando campos.
def grupo_de_referencia(modelo, anio, trans, comb):
    candidatos = [
        (df["model"] == modelo) & (df["year"] == anio)
        & (df["transmission"] == trans) & (df["fuelType"] == comb),
        (df["model"] == modelo) & (df["year"] == anio) & (df["transmission"] == trans),
        (df["model"] == modelo) & (df["transmission"] == trans) & (df["fuelType"] == comb),
        df["model"] == modelo,
    ]
    for mascara in candidatos:
        grupo = df.loc[mascara]
        if not grupo.empty:
            return grupo
    return df

grupo = grupo_de_referencia(model, year, transmision, combustible)
# La moda del motor siempre es un valor real del dataset: multiplo de 0.1, entre 1.0 y 5.0.
engine_size_inicial = float(grupo["engineSize"].mode().iloc[0])
# La mediana se redondea a multiplo de 1000 porque el slider avanza en pasos de 1000.
mileage_inicial = int(round(grupo["mileage"].median() / 1000) * 1000)
combo = f"{model}|{year}|{transmision}|{combustible}"

mileage = st.slider("Ingrese el kilometraje del coche", min_value=0, max_value=300000, value=mileage_inicial, step=1000, key=f"mileage_{combo}")
tax = st.slider("Ingrese el impuesto del coche", min_value=0, max_value= 600 , value=150)
mpg = st.slider("Ingrese el consumo de combustible del coche (mpg)", min_value=0, max_value=250, value=55)
engine_size = st.slider("Ingrese el tamaño del motor del coche (L)", min_value=0.5, max_value=6.0, value=engine_size_inicial, step=0.1, key=f"motor_{combo}")

def formatear_euros(importe):
    entero, _, decimales = f"{importe:,.2f}".partition(".")
    return f"{entero.replace(',', '.')},{decimales} €"


def formatear_miles(numero):
    return f"{numero:,}".replace(",", ".")


def soporte_datos(modelo, anio, kilometraje, consumo, motor):
    """Cuantos coches del mismo modelo estan a menos de 2 desviaciones tipicas."""
    consulta = np.array([
        (anio - _media_soporte["year"]) / _desv_soporte["year"],
        (kilometraje - _media_soporte["mileage"]) / _desv_soporte["mileage"],
        (consumo - _media_soporte["mpg"]) / _desv_soporte["mpg"],
        (motor - _media_soporte["engineSize"]) / _desv_soporte["engineSize"],
    ])
    distancia = ((_Z_soporte - consulta) ** 2).sum(axis=1)
    return int(np.count_nonzero(
        np.where(_modelos_soporte == modelo, distancia, np.inf) <= RADIO_SOPORTE
    ))


if st.button("🔮 Calcular precio", type="primary"):
    datos = pd.DataFrame({
        "model": [model],
        "transmission": [transmision],
        "fuelType": [combustible],
        "year": [year],
        "mileage": [mileage],
        "tax": [tax],
        "mpg": [mpg],
        "engineSize": [engine_size]
    })
    
    prediccion = modelo.predict(datos)
    precio_estimado = prediccion[0]

    diferencias = (df["price"] - precio_estimado).abs()
    coches_en_rango = diferencias <= precio_estimado * 0.10
    coches_cercanos = (
        df.assign(diferencia=diferencias)
        .loc[coches_en_rango]
        .sort_values("diferencia", kind="stable")
        .head(5)
        .drop(columns="diferencia")
        .reset_index(drop=True)
    )
    
    with st.container(border=True):
        st.metric("💰 Precio estimado", formatear_euros(prediccion[0]))
        st.caption("Precio orientativo según las características indicadas.")

        similares = soporte_datos(model, year, mileage, mpg, engine_size)
        if similares == 0:
            st.warning(
                f"No hay ningún {model} parecido a esta configuración en los datos de "
                f"origen (0 coches en un radio de ±4 años, ±38.000 km, ±20 mpg y ±0,85 L). "
                f"El precio es una estimación poco fiable."
            )
        elif similares < 5:
            plural = "coche similar" if similares == 1 else "coches similares"
            st.warning(
                f"Solo {similares} {plural} en los datos de origen. "
                f"El precio estimado es frágil."
            )
        elif similares < 30:
            st.info(
                f"Apoyado en solo {similares} coches similares. "
                f"Úsalo como orden de magnitud."
            )

    with st.container(border=True):
        st.subheader("📋 Datos del coche", icon=":material/car_repair:")
        st.table(
            {
                "🚗 **Modelo**": str(model),
                "📅 **Año**": str(year),
                "⚙️ **Transmisión**": str(transmision),
                "🛣️ **Kilometraje**": f"{formatear_miles(mileage)} km",
                "⛽ **Combustible**": str(combustible),
                "💵 **Impuesto**": str(tax),
                "📊 **MPG**": str(mpg),
                "🔧 **Tamaño del motor**": f"{engine_size:.1f}",
            }
        )

    st.subheader(":material/directions_car: 5 coches más cercanos al precio estimado (±10 %)")
    st.dataframe(
        coches_cercanos,
        column_config={
            "price": st.column_config.NumberColumn("Precio (€)", format="%.0f €"),
            "year": st.column_config.NumberColumn("Año", format="%d"),
            "mileage": st.column_config.NumberColumn("Kilometraje", format="%d"),
            "engineSize": st.column_config.NumberColumn("Motor (L)", format="%.1f"),
            "tax": st.column_config.NumberColumn("Impuesto", format="%d"),
            "mpg": st.column_config.NumberColumn("MPG", format="%.1f"),
        },
        hide_index=True,
    )
    if len(coches_cercanos) < 5:
        n = int(coches_en_rango.sum())
        plural = "coche del dataset" if n == 1 else "coches del dataset"
        st.caption(
            f"Solo {n} {plural} están dentro del ±10 % del precio estimado "
            f"({precio_estimado * 0.90:.0f} € - {precio_estimado * 1.10:.0f} €)."
        )

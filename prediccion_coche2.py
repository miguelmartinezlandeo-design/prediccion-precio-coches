import joblib
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
# Titulo
st.title("🚗 Predicción del precio del coche")
st.subheader("🚗🚕Detalles del coche")
model = st.selectbox("Seleccione el modelo del coche", modelos_disponibles)
transmision = st.selectbox("Seleccione el tipo de transmisión", ["Manual", "Automatic", "Semi-Auto"])
combustible = st.selectbox("Seleccione el tipo de combustible",  ["Diesel", "Petrol", "Hybrid", "Electric", "Other"])
st.subheader("💰Datos Numéricos")
year = st.slider("Seleccione el año del coche", min_value=1990, max_value=2025, value=2020)
mileage = st.slider("Ingrese el kilometraje del coche", min_value=0, max_value=300000, value=45000, step=1000)
tax = st.slider("Ingrese el impuesto del coche", min_value=0, max_value= 600 , value=150)
mpg = st.slider("Ingrese el consumo de combustible del coche (mpg)", min_value=0, max_value=250, value=55)
engine_size = st.slider("Ingrese el tamaño del motor del coche (L)", min_value=0.5, max_value=6.0, value=2.0, step=0.1)

def formatear_euros(importe):
    entero, _, decimales = f"{importe:,.2f}".partition(".")
    return f"{entero.replace(',', '.')},{decimales} €"


def formatear_miles(numero):
    return f"{numero:,}".replace(",", ".")


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

    coches_cercanos = (
        df.assign(diferencia=(df["price"] - precio_estimado).abs())
        .sort_values("diferencia")
        .head(10)
        .drop(columns="diferencia")
        .reset_index(drop=True)
    )
    
    with st.container(border=True):
        st.metric("💰 Precio estimado", formatear_euros(prediccion[0]))
        st.caption("Precio orientativo según las características indicadas.")

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

    st.subheader(":material/directions_car: 10 coches más cercanos al precio estimado")
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

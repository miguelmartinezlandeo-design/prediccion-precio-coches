import streamlit as st

# Esta es la pagina de Dashboard. En este paso solo se crea la estructura y la navegacion:
# aqui no hay todavia ningun grafico. Los graficos se iran anadiendo uno a uno en sesiones
# posteriores, sin tocar el modelo, el .pkl, el dataset ni la pagina de Prediccion.

# Vuelta a la pagina de Prediccion. Mismo mecanismo que el enlace de la pagina de Prediccion:
# al pulsarlo Streamlit ejecuta la pagina de Prediccion en lugar de esta.
st.page_link(
    "app_pages/prediccion.py",
    label="Volver a Predicción",
    icon=":material/arrow_back:",
    width="content",
)

st.title("📊 Dashboard")
st.caption(
    "Espacio preparado para los gráficos. En este paso todavía no hay ninguno: "
    "se añadirán uno a uno."
)

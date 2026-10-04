"""Punto de entrada de la aplicación.

Este archivo NO contiene la lógica de la app: solo declara la navegación y ejecuta la
página activa. Las páginas viven en `app_pages/`:

- `app_pages/prediccion.py` → 🚗 Predicción  (la página que ya existía, sin cambios de lógica)
- `app_pages/dashboard.py`  → 📊 Dashboard   (estructura vacía, sin gráficos todavía)

Se usa `st.navigation` + `st.Page` en vez del directorio `pages/` porque es la API vigente
y la recomendada para aplicaciones multipágina. El nombre del entrypoint se mantiene para
que el comando documentado `streamlit run prediccion_coche2.py` siga siendo válido.

`st.set_page_config` solo puede ejecutarse en el entrypoint, por eso se llama aquí y no en
las páginas.
"""

import streamlit as st

st.set_page_config(page_title="Predicción del precio del coche", page_icon="🚗")

pagina = st.navigation(
    [
        st.Page(
            "app_pages/prediccion.py",
            title="Predicción",
            icon=":material/directions_car:",
        ),
        st.Page(
            "app_pages/dashboard.py",
            title="Dashboard",
            icon=":material/bar_chart:",
        ),
    ]
)

pagina.run()

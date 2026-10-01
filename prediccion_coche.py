import joblib
import pandas as pd
# Cargar el modelo entrenado desde un archivo .pkl
modelo = joblib.load("modelo_coches.pkl")
# Ejemplo de predicción
coche_nuevo = pd.DataFrame({
    "model": ["Kuga"],
    "year": [2020],
    "transmission": ["Manual"],
    "mileage": [45000],
    "fuelType": ["Diesel"],
    "tax": [150],
    "mpg": [55],
    "engineSize": [2.0]
})

prediccion = modelo.predict(coche_nuevo)
print("Predicción del precio del coche:", prediccion[0])


import joblib
import pandas as pd

modelo = joblib.load("modelo_coches.pkl")
print("--------------------------------------------------")
print("🚒 Ingrese los detalles del coche para la predicción:🚗")
print("--------------------------------------------------")

model = input("Ingrese el modelo del coche: ")
year = int(input("Ingrese el año del coche: "))
transmission = input("Ingrese la transmisión del coche: ")
mileage = int(input("Ingrese el kilometraje del coche: "))
fuelType = input("Ingrese el tipo de combustible del coche: ")
tax = int(input("Ingrese el impuesto del coche: "))
mpg = float(input("Ingrese el consumo de combustible (mpg) del coche: "))
engineSize = float(input("Ingrese el tamaño del motor del coche: "))

coche_nuevo = pd.DataFrame({
    "model": [model],
    "year": [year],
    "transmission": [transmission],
    "mileage": [mileage],
    "fuelType": [fuelType],
    "tax": [tax],
    "mpg": [mpg],
    "engineSize": [engineSize]
})

prediccion = modelo.predict(coche_nuevo)
print("Predicción del precio del coche:", prediccion[0])

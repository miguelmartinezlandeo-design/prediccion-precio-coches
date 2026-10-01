## Delegación de tareas

### REGLA OBLIGATORIA

Toda tarea relacionada con datos debe ser delegada al subagente
`data-analyst`.

No analices tú mismo los datos con Pandas, Python u otras herramientas
si la tarea puede ser realizada por `data-analyst`.

Debes utilizar `data-analyst` incluso cuando la consulta sea sencilla.

Ejemplos:

- "Busca los 5 coches más caros."
- "¿Cuántos coches hay?"
- "Busca los valores nulos."
- "Dime la media del precio."
- "Filtra los Ford."
- "Busca los coches más cercanos a 16000 €."
- "Explora el DataFrame."

En todos estos casos debes delegar primero la tarea a `data-analyst`.

El agente principal debe encargarse posteriormente de interpretar,
explicar y presentar al usuario el resultado recibido.

Nunca sustituyas la delegación simplemente porque la tarea sea sencilla.

# Mejorar aplicación prediccion_coche2.py

Quiero mejorar poco a poco mi aplicación de predicción de precios de coches.

## 1. Mostrar el precio de forma destacada

La aplicación ya funciona correctamente y no quiero cambiar el modelo de Machine Learning.

Cuando el usuario pulse el botón:

🔮 Calcular precio
quiero que el precio estimado se muestre de una forma más grande y clara.

Por ejemplo:
💰 Precio estimado
16.078,87 €
No cambies el modelo ni la forma en la que se realiza la predicción.

## 2. Mostrar los datos utilizados

Después de mostrar el precio estimado, quiero mostrar un pequeño resumen
con los datos del coche que el usuario ha introducido.

Por ejemplo:

📋 Datos del coche

Modelo: Kuga
Año: 2020
Transmisión: Manual
Kilometraje: 45.000 km
Combustible: Diesel
Impuesto: 150
MPG: 55
Tamaño del motor: 2.0

Los datos deben ser exactamente los que el usuario ha seleccionado o
introducido.

No modificar el modelo de Machine Learning ni la forma en la que se
realiza la predicción.

Eso sí, cambia la letra. Ponle un estilo mucho más bonito y ponle algún emoticon Para que se vea agradable la vista Además, que esos datos se encuentren dentro de un Bloque Como en un cuadrado Que la cabecera sea Datos del coche Y los demás de abajo En dos celdas Una celda donde estén los títulos y la otra celda al lado, donde estén. Las respuestas

## Delegación de tareas

Utiliza el subagente `data-analyst` para todas las tareas relacionadas
con el análisis de datos.

Debes delegar automáticamente al `data-analyst` cuando el usuario pida:

- Analizar un DataFrame.
- Consultar datos en used_car_price_analysis.csv.
- Filtrar registros.
- Ordenar datos.
- Buscar registros.
- Calcular estadísticas.
- Analizar columnas.
- Buscar valores duplicados o nulos.
- Detectar problemas de calidad de datos.
- Preparar datos para gráficos.

El `data-analyst` debe realizar el análisis y devolver los resultados.

El agente principal debe utilizar esos resultados para responder al
usuario o decidir el siguiente paso.

No realices tú mismo una tarea de análisis de datos si puede ser
delegada al `data-analyst`.

El `data-analyst` no debe modificar la aplicación ni ejecutar
Streamlit. Su función es exclusivamente analizar los datos.

## Resultados de los subagentes

Cuando recibas un resultado del `data-analyst`, conserva su identificación:

📊 DATA-ANALYST
🔐 SUBAGENTE EJECUTADO

No elimines ni sustituyas estas dos líneas al presentar el resultado.
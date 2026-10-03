# AGENTS.md — Modulo11: Predicción del precio de coches

Este archivo es la **memoria del proyecto**. Léelo completo antes de tocar nada.
No repitas las auditorías ni los diagnósticos que aquí ya están resueltos.

---

## 1. Qué es este proyecto

Aplicación Streamlit que estima el precio de un coche de segunda mano a partir de
8 características (modelo, año, transmisión, kilometraje, combustible, impuesto,
mpg y tamaño del motor), usando un RandomForest entrenado sobre datos de coches
británicos.

**App principal: `prediccion_coche2.py`** (las otras dos, `prediccion_coche.py` y
`prediccion_coche1.py`, son borradores antiguos y están abandonadas).

> **Última sesión con cambios: 2026-10-03 (WSL se desconectó a mitad, retomado).**
> Implementada la **opción B**: los rangos y valores por defecto de los widgets se
> derivan del dataset limpio, el **`mpg` pasó a ser dinámico** y se puso el suelo
> `KM_MIN_INICIAL = 1000` que cierra el pendiente de los "0 km". Validado y
> documentado en la **sección 8 sexies**. **Commiteado** (solo
> `prediccion_coche2.py` y este `AGENTS.md`, ambos en el HEAD de `main`).
> Retoma desde la sección 12.
>
> **Sesiones anteriores (2026-10-02):** implementados los **valores iniciales
> dinámicos** de `mileage` y `engineSize` (opción C), el **aviso de soporte de
> datos** (opción D), el **rediseño de la tabla de coches cercanos** (cambio X) y
> el **rango orientativo p5–p95** (opción E). Detalle en las secciones 8 bis, 8 ter,
> 8 quater y 8 quinquies. El modelo, el `.pkl` y los hiperparámetros **no se han
> tocado** en ninguna de las cinco.
>
> **C, D, X y E están commiteados** (`d918107` y `fa66a19`). X se aplicó sin probar en
> su momento, pero se validó en la sesión de E.

---

## 2. REGLA OBLIGATORIA: delegar todo análisis de datos en `data-analyst`

> **Toda tarea relacionada con datos se delega en el subagente `data-analyst`.**
> No analices tú mismo los datos con Pandas, Python o SQL.

Obligatorio delegar cuando el usuario pida: leer o explorar un DataFrame, contar
filas, buscar nulos o duplicados, filtrar, ordenar, buscar registros, calcular
estadísticas, resumir columnas, detectar problemas de calidad, preparar datos
para gráficos, o validar un CSV.

Ejemplos que **sí** se delegan: "¿cuántos coches hay?", "dime la media del
precio", "filtra los Ford", "busca valores nulos", "explora el dataset".

**Límites de `data-analyst`:**

- **NO** modifica la aplicación.
- **NO** ejecuta Streamlit.
- **NO** entrena modelos (su función es exclusivamente analizar datos).
  El entrenamiento y la evaluación los hace el agente principal.

Cuando recibas su resultado, conserva estas dos líneas al presentarlo:

```
📊 DATA-ANALYST
🔐 SUBAGENTE EJECUTADO
```

**Aviso técnico demostrado:** `data-analyst` da índices de fila poco fiables al
comparar dos CSVs con distinto índice (ya devolvió una lista de filas de
kilometraje bajo que no existía). Para contrastar filas entre el CSV original y
el limpio, hay que exigirle que use `df.index` real de pandas y que pegue la
salida literal del comando, o verificar después con un script propio.

---

## 2 bis. Proporcionalidad del análisis

**Regla añadida por el usuario a `mejorar_pred.md` el 2026-10-02 (sin commit).**
Esta sección recoge fielmente su apartado `⏱️ Proporcionalidad del análisis`,
que es la fuente de verdad.

El nivel de análisis y validación debe ser **proporcional a la tarea**. Hay dos
regímenes y no se mezclan.

### Análisis exhaustivo

Utilizar análisis exhaustivo cuando la tarea implique:

- investigar la causa de un problema de datos;
- detectar anomalías;
- estudiar la calidad del dataset;
- comparar modelos;
- validar hipótesis sobre los datos;
- tomar decisiones que puedan afectar al modelo;
- modificar datos de entrenamiento;
- reentrenar o evaluar un modelo.

En estos casos se debe utilizar `data-analyst` y realizar las comprobaciones
necesarias.

### Cambios pequeños de código

Para modificaciones localizadas de la aplicación que **ya están especificadas y
no requieren nuevo análisis de datos**:

- no realizar un análisis exhaustivo del dataset;
- no ejecutar baterías extensas de pruebas salvo que sean necesarias;
- modificar únicamente las líneas necesarias;
- realizar una validación breve y específica del cambio;
- informar del resultado.

Ejemplos textuales del usuario: cambiar el número de resultados mostrados,
cambiar un texto de la interfaz, **añadir un caption**, modificar una condición
ya definida, cambiar una etiqueta, cambiar el formato de presentación.

### Regla importante

**No convertir automáticamente una modificación pequeña de código en una
auditoría completa del proyecto.** Si la tarea ya tiene una especificación
concreta y no requiere nuevo análisis de datos, ejecutar únicamente las
comprobaciones necesarias para verificar ese cambio.

### ⚠️ Relación con la sección 2 (punto abierto)

La sección 2 obliga a delegar en `data-analyst` *"incluso cuando la consulta sea
sencilla"*. La 2 bis dice *"no realizar un análisis exhaustivo"*. **No se
contradicen** con esta lectura, que es la que se está aplicando:

- la **delegación** sigue vigente siempre que haya tarea de datos;
- la **proporcionalidad** decide *cuánto* análisis se hace, no *si* se delega.

O sea: ante un cambio pequeño sin necesidad de datos, la conclusión es que **no
hay tarea de datos que delegar**, no que haya que delegar un análisis enorme.

**Pendiente de confirmar con el usuario** si esta es la interpretación que
quiere, o si la proporcionalidad debe prevalecer sobre la delegación en los
casos triviales.

---

## 3. Arquitectura y ficheros

```
used_car_price_analysis.csv          ORIGINAL, 17.966 filas. NO MODIFICAR NUNCA (tiene backup)
   │
   │  limpiar_datos.py  → función limpiar(df) con reglas R1..R6
   ▼
used_car_price_analysis_limpio.csv   LIMPIO, 17.811 filas. Lo leen el entrenamiento y la app
   │
   │  entrenar_modelo.py → Pipeline + RandomForest
   ▼
modelo_coches.pkl                    El que carga la app. Backup en modelo_coches_backup_*.pkl
```

| Fichero | Rol |
|---|---|
| `prediccion_coche2.py` | La app. Carga el PKL y el CSV limpio. |
| `limpiar_datos.py` | Función `limpiar(df)` (R1..R6) + `__main__` que escribe el CSV limpio e imprime informe. |
| `entrenar_modelo.py` | Reentrena, compara 3 escenarios y hace la prueba funcional. Escribe `modelo_coches_nuevo.pkl` (no toca el de la app). |
| `mejorar_pred.md` | Peticiones originales de mejora de la UI + la regla de delegación + la regla de proporcionalidad (sección 2 bis). |
| `modelo_coches_backup_20261002_005315.pkl` | Backup del modelo con el bug (scikit-learn 1.9.0). |
| `used_car_price_analysis_backup_20261002_005316.csv` | Backup del CSV original. |

### Comandos

```bash
source .venv/bin/activate
python limpiar_datos.py      # regenera el CSV limpio + informe
python entrenar_modelo.py    # reentrena, compara y guarda modelo_coches_nuevo.pkl
streamlit run prediccion_coche2.py
```

Entorno: Python 3.12.3, scikit-learn 1.9.1, pandas 3.0.6, numpy 2.5.3,
joblib 1.6.0, streamlit 1.64.0 (venv en `.venv/`).

---

## 4. EL BUG YA RESUELTO: todos los coches valían lo mismo

**No lo vuelvas a investigar. Ya está diagnosticado y corregido.**

`model` tenía **espacio inicial en 17.965 de 17.966 filas** (`" Fiesta"`,
`" Kuga"`…). El `OneHotEncoder(handle_unknown='ignore')` aprendió las 24
categorías **con espacio**, y la app mandaba `"Kuga"` → categoría desconocida →
vector todo ceros → **los 9 modelos de la app devolvían exactamente 18.032,07 €**.

Arreglo: `.str.strip()` en la limpieza + reentrenamiento.

**Lección permanente:** el `OneHotEncoder` con `handle_unknown='ignore'` falla en
silencio ante un desajuste de espacios. Si algún día todos los precios de la app
salen iguales, es esto.

---

## 5. Reglas de limpieza (R1..R6, en este orden exacto)

El orden importa. Definidas en `limpiar_datos.py`, función `limpiar(df)`.

| # | Regla | Efecto |
|---|---|---|
| R1 | `df["model"] = df["model"].str.strip()` | 0 filas, 24→23 categorías |
| R2 | `df["tax"].fillna(145.0)` | 3 nulos |
| R3 | `engineSize == 0` → **moda del mismo model** | 51 filas, 8 modelos |
| R4 | `drop_duplicates()` sobre las 9 columnas | −154 filas |
| R5 | `df = df[df["year"] != 2060]` | −1 fila |
| R6 | `mileage <= 2` → **mediana del grupo** con fallback | 6 filas |

**Resultado: 17.966 → 17.811 filas** (17.812 tras R4, 17.811 tras R5).
R6 no elimina filas, solo imputa.

**Trampa de orden:** si R6 se aplica *antes* de R4, la fila 7133 deja de ser
duplicado de 6930 y sobrevive → 17.807 filas en vez de 17.811. R4 va antes.

Cadena de fallback de R6:
`(model, year, transmission, fuelType)` → `(model, year, transmission)` →
`(model, fuelType)` → `(model)` → mediana global. Un grupo necesita ≥3 filas
válidas (`mileage > 2`) para usarse.

El CSV limpio tiene **exactamente 9 columnas**, en este orden, sin columnas
extra: la app las lee con `column_config` fijo, así que **no se añaden columnas**.

---

## 6. Decisiones del usuario sobre los datos dudosos

Resueltas y **conservadas deliberadamente**. No las "arregles" sin preguntar.

| Caso | Decisión | Motivo |
|---|---|---|
| `mpg = 201.8` (5 filas, Kuga 2020 Hybrid 2.5) | **DEJAR** | No es un tecleo: es *mpg-equivalent* UK válido de un 2.5 mHEV. Máximo real del dataset (el 2º máximo es 88.3). |
| 4 Focus con precio imposible | **CONSERVAR** | Decisión del usuario. Índices originales 11912 (54.995 €), 17100 (21.500 €), 1039 (38.015 €), 7707 (32.000 €). Son errores de precio reales, pero se dejan. |
| `tax == 0` (2.153 filas) | **NO BORRAR** | Valor legítimo del UK Vehicle Tax (banda mínima), no un sentinel. El 100% de los Electric lo tiene. |
| Coches baratos (495 € – 3.000 €) | **CONSERVAR** | Focus 2003 con 177.644 km a 495 € es real. Definen la cola baja del precio; borrarlos empeoraría el modelo. |
| Mustang (57 filas) y modelos raros | **NO ELIMINAR** | Decisión explícita del usuario. |
| 229 filas "mismo coche, distinto precio" | **NO BORRAR** | Mismo coche anunciado a distinto precio. Solo se borran duplicados **exactos** (154). |
| `Ranger` (1 fila) | **FUERA de la app** | Cayó en el test, el encoder no lo aprendió. La app deriva la lista del encoder, así que no se ofrece. |

**Nota sobre los duplicados:** 154 es el número correcto. Los "302" de una
auditoría previa eran las filas implicadas en duplicación (148 grupos);
302 − 148 = 154 sobrantes. No es una contradicción.

**Nota sobre el kilometraje bajo:** el dataset tiene **137 filas con ≤20 km de
forma natural**. `mileage = 1` no es basura per se. Solo se imputaron las 7 filas
con `mileage <= 2` (6 tras la deduplicación): 6930, 11129, 11173, 13531, 16906,
17193. `3654` (km=4) se conservó intacta.

---

## 7. El modelo

Pipeline **idéntico** al original, para que la app no necesite cambios de código:

```python
ColumnTransformer([
    ("numericas",  "passthrough",          ["year","mileage","tax","mpg","engineSize"]),
    ("categoricas", OneHotEncoder(handle_unknown="ignore"), ["model","transmission","fuelType"]),
])
RandomForestRegressor(max_depth=20, min_samples_split=15,
                      n_estimators=200, n_jobs=1, random_state=42)
```

**No cambies los hiperparámetros sin permiso del usuario.** Se probó bajar
`min_samples_split` a 3/5/10 y **empeora** R² (0,9378 → 0,9341) sin resolver el
problema de precios iguales. 15 es el óptimo.

### Comparativa de referencia (test de 4.452 filas, `random_state=42`, 25%)

| escenario | R² | RMSE | MAE |
|---|---|---|---|
| A) modelo con bug / datos sucios (entrenado sobre todo el dataset, **optimista**) | 0,9512 | 1.053 | 723 |
| B) modelo con bug / datos limpios = **lo que hacía la app** | 0,8382 | 1.917 | 1.329 |
| C) **modelo nuevo / test limpio (honesto, holdout)** | **0,9378** | **1.189** | **829** |

A es contaminado (el modelo viejo se entrenó sobre esas mismas filas), así que la
comparación válida es **B → C: RMSE −38%**.

Si en el futuro R² del test limpio baja de ~0,93, algo se ha roto.

---

## 8. Cambios ya aplicados en `prediccion_coche2.py`

Solo **2 líneas**, el resto de la app intacto:

1. `df = pd.read_csv("used_car_price_analysis_limpio.csv")` (antes leía el
   original sucio) + lista de modelos derivada del encoder:
   ```python
   categorias_modelo = modelo.named_steps["preprocesamiento"] \
       .named_transformers_["categoricas"].categories_[0]
   frecuencia = df["model"].value_counts()
   modelos_disponibles = sorted(
       (m for m in categorias_modelo if m in frecuencia.index),
       key=lambda m: -frecuencia[m],
   )
   ```
   Se ofrece **22 modelos** (antes 9). Derivarla del encoder y no del CSV es
   deliberado: garantiza que ningún modelo propuesto caiga en el
   `handle_unknown='ignore'` y devuelva un precio sin señal de modelo.

2. `st.selectbox(..., modelos_disponibles)` en lugar de la lista fija de 9.

> **Corrección 2026-10-02:** el párrafo original decía que la UI no se tocaba,
> mentioning que la tabla de coches cercanos quedaba intacta. **Eso ya no es
> cierto:** desde el commit `9143a5a` la tabla de coches cercanos **sí se ha
> modificado** (cambio X, sección 8 quater) y ahora muestra 5 coches filtrados
> dentro del ±10 % en lugar de 10 sin filtro. El precio destacado y la tabla
> "Datos del coche" **siguen sin tocarse**.

---

## 8 bis. Defaults dinámicos de `mileage` y `engineSize` (2026-10-02)

**Opción C del diagnóstico de la sección 9. Solo código de la app. El modelo, el
`.pkl` y los hiperparámetros NO se tocaron.**

| Fichero | Cambio |
|---|---|
| `prediccion_coche2.py` | +26 líneas, 2 modificadas. Ningún otro fichero. |

El MD5 de `modelo_coches.pkl` sigue siendo `72441976dd0ba4ba2f95acc3c3bee3f9`
(fecha `Oct 2 01:07`), o sea que no hubo reentrenamiento.

### Qué hace

Insertado en `prediccion_coche2.py:27-48`, **entre el slider del año (línea 25) y
el del kilometraje**, porque es el primer punto donde ya están leídos `model`,
`transmision`, `combustible` (líneas 21-23) y `year`.

La función `grupo_de_referencia(modelo, anio, trans, comb)` busca en `df` (el CSV
limpio que la app ya carga en la línea 9) con esta **cadena de respaldo**, y se
queda con el primer nivel no vacío:

| Nivel | Filtro |
|---|---|
| N1 | `(model, year, transmission, fuelType)` |
| N2 | `(model, year, transmission)` |
| N3 | `(model, transmission, fuelType)` |
| N4 | `(model)` |
| N5 | dataset completo (red de seguridad, nunca se ha necesitado) |

- `engine_size_inicial` = **moda** de `engineSize` del grupo.
- `mileage_inicial` = **mediana** de `mileage` del grupo, redondeada a múltiplo de
  1000 porque el slider avanza en pasos de 1000. El 84% de las medianas no son
  múltiplos de 1000, así que el redondeo es **obligatorio**, no cosmético.

### El `key` dinámico es imprescindible

```python
combo = f"{model}|{year}|{transmision}|{combustible}"
mileage     = st.slider(..., value=mileage_inicial,  key=f"mileage_{combo}")
engine_size = st.slider(..., value=engine_size_inicial, key=f"motor_{combo}")
```

El parámetro `value=` de un widget **solo se aplica la primera vez** que Streamlit
lo dibuja. Sin `key` dinámica los sliders no se moverían al cambiar el modelo y el
cambio sería inútil. Con la clave derivada de la tupla, cuando esa tupla cambia
Streamlit ve un widget nuevo y lo inicializa al valor recién calculado.

**Consecuencia para el usuario:** si mueve un slider a mano, **su valor se
conserva** mientras no cambie la combinación `(modelo, año, transmisión,
combustible)`. Verificado: 123.000 km sobreviven a un rerun; al cambiar a otro
modelo los dos sliders se recalculan. Las claves viejas quedan inertes en
`session_state` (memoria despreciable, no se limpian).

### Validación realizada

- **Arranque:** servidor levantado, `/healthz` responde 200.
- **`AppTest` de `streamlit.testing.v1`** (ejecuta el script y captura
  excepciones, a diferencia de `curl` que solo sirve la cáscara HTML):
  **0 excepciones** en las 12 pruebas y también al pulsar 🔮 Calcular precio.
- **Barrido de las 11.880 combinaciones** (22 modelos × 36 años × 3
  transmisiones × 5 combustibles): **0 grupos vacíos** y **0 valores fuera de
  rango** de los sliders. Ninguna moda de motor fuera de `[0.5, 6.0]` ni no
  múltiplo de 0.1; ninguna mediana redondeada fuera de `[0, 300000]` (rango real
  observado `[0, 143000]`; el `mileage` máximo del dataset es 177.644).
- **12 escenarios reales validados 12/12**, incluidos los que fuerzan el
  fallback:

  | Combinación | Filas | Nivel | Resultado |
  |---|---|---|---|
  | Fiesta 2020 Manual Petrol | 78 | N1 | 1.0 L / 0 km |
  | Focus 2020 Manual Petrol | 31 | N1 | 1.0 L / 1.000 km |
  | Mustang 2020 Manual Petrol | 4 | N1 | 5.0 L / 0 km |
  | Mondeo 2018 Manual Petrol | 5 | N1 | 1.5 L / 25.000 km |
  | KA 2020 Automatic Hybrid | 197 | **N3** | 1.2 L / 33.000 km |
  | Galaxy 2020 Manual Hybrid | 227 | **N4** | 2.0 L / 29.000 km |
  | Fiesta 2024 Semi-Auto Electric | 6.508 | N4 | 1.0 L / 18.000 km |
  | Escort 1990 Manual Petrol | 1 | N4 | 1.8 L / 50.000 km |
  | S-MAX 2025 Semi-Auto Other | 294 | N3 | 2.0 L / 28.000 km |
  | Streetka 2015 Automatic Diesel | 2 | N3 | 1.6 L / 69.000 km |
  | B-MAX 1993 Manual Petrol | 183 | **N3** | 1.0 L / 26.000 km |

### Corrección importante: el combustible por defecto es **Diesel**

El `selectbox` de la línea 23 empieza por `"Diesel"`:

```python
combustible = st.selectbox("...", ["Diesel", "Petrol", "Hybrid", "Electric", "Other"])
```

Por tanto los valores por defecto reales de la app son `Manual + Diesel + 2020`,
**no** `Petrol`. Cualquier análisis futuro que asuma `Petrol` se equivocará.
(Por eso los valores iniciales por defecto ahora son **1.0 L y 0 km**, los de
`Fiesta | 2020 | Manual | Diesel`.)

### Pendiente: los 0 km — RESUELTO en la sección 8 sexies

Varias combinaciones dan `mileage_inicial = 0` porque el dataset es de coches casi
nuevos: las celdas de 2020 tienen kilometraje mediano por debajo de 1.000 km. Aquí
el usuario **decidió expresamente mantenerlo en 0** (es el dato fiel).

> **Actualizado 2026-10-03:** este punto ya no está pendiente. Se resolvió junto a
> la opción B (sección 8 sexies) con `KM_MIN_INICIAL = 1000`: el dataset **no tiene
> ninguna fila con `mileage == 0`** (mínimo real 4 km), así que arrancar en 0 era
> ofrecer un valor que el modelo nunca ha visto. El suelo afecta **solo al valor
> inicial**; el slider sigue ofreciendo 0 km a mano.
>
> El argumento que justifica el cambio: el objetivo de los defaults dinámicos es
> que el usuario arranque en un dato **real**, y 0 km no lo es. Es la misma línea de
> razonamiento que motivó la opción B entera.

---

## 8 ter. Aviso de soporte de datos (2026-10-02) — opción D HECHA

**Solo `prediccion_coche2.py`. El aviso es puramente informativo: no cambia la
predicción, ni el modelo, ni el `.pkl`, ni los hiperparámetros. Sin commit.**

### Por qué no sirve la celda exacta

La definición obvia "nº de coches con `(model, year, transmission, fuelType)`
exactos" está vacía en el **95,75 %** de las 11.880 combinaciones que la app
ofrece. Daría el aviso en casi todo. Las medidas por ventana tampoco valen:
bajan los ceros al 0,41 % pero **mienten**, porque al caer al modelo entero le
dicen a un Edge que tiene 148 coches de apoyo cuando ninguno es de ese modelo.
Midiendo su recall como detector del colapso, esa medida da **≤ 46,7 %**: la
peor de todas.

### La medida que sí funciona: radio en distancia estandarizada

> `soporte` = nº de coches del **mismo `model`** a distancia estandarizada
> **≤ 2 desviaciones típicas** en `(year, mileage, mpg, engineSize)`.

Es decir, un radio de **±4,05 años · ±38.831 km · ±20,3 mpg · ±0,85 L**.
`RADIO_SOPORTE = 4.0` porque es el radio al cuadrado.

**Variables, y por qué las otras no entran:**

| Variable | ¿Entra? | Motivo medido |
|---|---|---|
| `model` | **Sí, exacto** | Es la que más determina el precio. Sin ella la medida no significa nada |
| `year` | **Sí** | La de mayor peso: 1 año cuesta 0,49 unidades, 5× más que 1 mpg |
| `mileage` | **Sí** | El radio de 2 sd ≈ el rango km realista entre coches del mismo modelo y año |
| `mpg` | **Sí** | Su default **55 no existe en el dataset (0 filas)**. Y hace de proxy continuo de motor+combustible: **excluirlo baja la detección del 100 % al 80 %** |
| `engineSize` | **Sí** | |
| `transmission` | **No** | Mantenerlo exacto es lo que produce el 95 % de ceros |
| `fuelType` | **No** | Ídem; `mpg` y `engineSize` ya lo filtran de forma continua |
| `tax` | **No** | Aporta **0,00** de F1. Redundante con `year`+`fuelType` (el impuesto UK sale del CO₂) |

Soltar `transmission` y `fuelType` **no pierde información**: un Fiesta 2019
_manual_diésel_ de 1.0 L es una referencia perfectamente válida para un Fiesta
2020_manual_diésel_ de 1.0 L. Un aviso que saltara ahí sería ruido.

### Los cuatro niveles y los mensajes exactos

| Nivel | Condición | % de las 11.880 combinaciones | Renderizado |
|---|---|---|---|
| 🔴 Sin soporte | `== 0` | 65,8 % | `st.warning` |
| 🟠 Muy poco | `0 < soporte < 5` | 6,9 % | `st.warning` |
| 🟡 Limitado | `5 <= soporte < 30` | 7,2 % | `st.info` |
| ⚪ Sin aviso | `>= 30` | 20,1 % | nada, solo el caption original |

Mensajes literales que muestra la app:

```
🔴 No hay ningún {model} parecido a esta configuración en los datos de origen
   (0 coches en un radio de ±4 años, ±38.000 km, ±20 mpg y ±0,85 L).
   El precio es una estimación poco fiable.

🟠 Solo {soporte} coche similar / coches similares en los datos de origen.
   El precio estimado es frágil.

🟡 Apoyado en solo {soporte} coches similares. Úsalo como orden de magnitud.
```

**El corte que importa es 30, no 5.** Con umbral 5 se detecta el 86,7 % de los
casos problemáticos; con 30, el **100 %**, y **sin introducir ni un solo falso
positivo** en las 88 combinaciones de control con ≥30 coches en su celda exacta.

### Dónde está en el código

`prediccion_coche2.py`:

| Ubicación | Qué |
|---|---|
| Línea 2 | `import numpy as np` |
| Líneas 19-27 | Precomputado: `_media_soporte`, `_desv_soporte`, `_Z_soporte`, `_modelos_soporte`, `RADIO_SOPORTE = 4.0` |
| Líneas 74-85 | Función `soporte_datos(modelo, anio, kilometraje, consumo, motor)` |
| Líneas 115-133 | Los tres niveles, **dentro del `st.container` del precio, justo debajo del caption de la línea 113** |

Coste: **1,74 ms** por consulta (17.811 filas × 4 variables estandarizadas).

### Validación realizada

- **AppTest: 0 excepciones en 22 ejecuciones.**
- **Predicción bit-idéntica:** se capturó una línea base de 15 escenarios con el
  `repr()` del float **antes** de tocar nada, y se repitió después.
  **15/15 predicciones bit-idénticas.** Ejemplos: Fiesta 2020 → `15853.736536803153`,
  Mustang 2020 → `33325.23651838236`, KA 2020 → `15684.600684125182`.
- **`modelo.predict()` no fue modificado.** Tampoco los sliders, sus defaults
  dinámicos, la tabla ni el layout.
  - **Corrección 2026-10-02:** esta validación se hizo **antes** del cambio X. La
    tabla de coches cercanos **sí se modificó después** (sección 8 quater). Lo
    que no se ha modificado en ningún momento es `modelo.predict()` ni el
    cálculo de `soporte_datos`.
- Un caso verificado por nivel:

  | Nivel | Escenario | Soporte | UI |
  |---|---|---|---|
  | 🔴 | B-MAX 1993 Manual Petrol | 0 | 1 warning |
  | 🟠 singular | EcoSport 2010 Manual Petrol | 1 | 1 warning |
  | 🟠 plural | C-MAX 2010 Automatic Petrol | 4 | 1 warning |
  | 🟡 | Tourneo Custom 2020 Manual Diesel | 14 | 1 info |
  | ⚪ | B-MAX 2015 Manual Diesel | 230 | sin aviso |
  | ⚪ | Fiesta 2020 Manual Diesel | 3.245 | sin aviso |

- Arranque del servidor OK, `/` responde HTTP 200.
- El MD5 de `modelo_coches.pkl` sigue siendo `72441976dd0ba4ba2f95acc3c3bee3f9`.

### Lo que el aviso revela sobre la calidad de la predicción

Medido sobre las 11.880 combinaciones, comparando la predicción con la media de
los 30 coches más cercanos del mismo modelo:

| Soporte | Nº combinaciones | Desviación mediana | Error > 50 % |
|---|---|---|---|
| **0** | 7.820 | **65,2 %** | 63,4 % |
| 1-4 | 823 | 40,9 % | 31,5 % |
| 5-29 | 855 | 36,2 % | 10,3 % |
| **≥ 30** | 2.382 | **6,6 %** | **2,1 %** |

Gradiente de **10×**. En los valores por defecto reales de la app saldrían
**9 modelos con aviso, 7 de ellos en rojo** (KA, Mustang, Fusion, Streetka,
Transit Tourneo, Escort, Ranger), todos con 1-4 filas en su celda.

**Advertencia metodológica importante:** el mismo test ejecutado sobre las
**17.811 filas reales** del dataset **NO** muestra relación entre soporte y error
(MAE 680-883 € en todos los tramos). No es contradictorio: una fila real siempre
tiene vecinos por construcción, así que ese test **no puede medir
extrapolación**. Solo la consulta sintética que puede construir el usuario la
revela. Ambas cosas son ciertas: **el modelo es fiable dentro de la nube de
datos y no lo es fuera**. Y la circularidad es parcial: cuando el soporte es 0,
la propia referencia (los 30 más cercanos) está lejos.

### 🔸 Coste de diseño asumido

El aviso saldría en el **65 %** de las combinaciones que ofrece la app. Y es
correcto: **14 de los 36 años del slider no tienen ni una fila** (faltan 1997,
1999 y 2001 dentro del propio rango del dataset). Un aviso que saltara el 20 %
de las veces estaría mintiendo. La solución de fondo es la **opción B**, no relajar
el umbral.

---

## 8 quater. Rediseño de la tabla de coches cercanos (2026-10-02) — cambio X

**Solo `prediccion_coche2.py`. NO toca `modelo.predict()`, ni el `.pkl`, ni los
hiperparámetros, ni ningún dataset. Sin commit y, de momento, SIN validar.**

**Este cambio NO es la opción E** de la sección 9. E pedía mostrar un **rango
mín/mediana/máx** de los coches cercanos y sigue **PENDIENTE**. Lo aplicado aquí
es otra cosa: **acotar la tabla a una banda de precio alrededor de la
predicción**. Son compatibles: se podrían mostrar ambos.

### Qué hace

| Antes (commit `9143a5a`) | Ahora |
|---|---|
| `df.assign(diferencia=...).sort_values("diferencia").head(10)` | Filtro previo `coches_en_rango` |
| Los **10** más próximos en valor absoluto, **sin banda de precio** | Máximo **5**, y solo los que caen **dentro del ±10 %** del precio estimado |
| `sort_values("diferencia")` (desempate no determinista) | `sort_values("diferencia", kind="stable")` |
| Subtítulo "10 coches más cercanos al precio estimado" | "5 coches más cercanos al precio estimado (±10 %)" |
| Sin caption | `st.caption` con el nº de coches de la banda cuando salen menos de 5 |

El cambio de comportamiento real es el **filtro de banda**: antes la tabla
mostraba los 10 coches más cercanos **aunque algunos estuvieran lejos** del
precio estimado; ahora la lista está acotada a la banda.

### Comportamiento exacto

1. Se calculan las diferencias absolutas `|price − precio_estimado|`.
2. Se filtran las filas con `diferencia <= precio_estimado * 0.10`.
3. Se ordenan por `diferencia` ascendente.
4. Se toman las **5 primeras**.
5. Si dentro de la banda había **menos de 5**, se muestran las que haya (puede
   ser 0, 1, 2, 3 o 4) y sale un caption adicional indicando cuántas hay en
   total y el intervalo de precio de la banda.

`kind="stable"` no cambia el criterio de orden, solo hace **determinista el
desempate**: a igual `diferencia` se mantiene el orden original de las filas del
dataset, de modo que la tabla no cambia entre ejecuciones ni entre reruns.

La banda es **multiplicativa y centrada en la predicción**, no en la mediana:
de `precio_estimado * 0.90` a `precio_estimado * 1.10`. El caption imprime
justamente ese intervalo.

**Caso límite que el código contempla:** si la banda está vacía, la tabla se
renderiza **sin filas** y el caption muestra `"Solo 0 coches del dataset están
dentro del ±10 % del precio estimado (… € - … €)"`. Es un caso **posible pero no
medido** (ver abajo), y encaja mal con la sección 8 ter: los casos de soporte 0
son precisamente los que más probabilidades tienen de caer fuera de la banda.

### Dónde está en el código

`prediccion_coche2.py`:

| Ubicación | Qué |
|---|---|
| Líneas 103-104 | `diferencias` y `coches_en_rango = diferencias <= precio_estimado * 0.10` |
| Líneas 105-112 | `coches_cercanos`: `.loc[coches_en_rango]` → `sort_values("diferencia", kind="stable")` → `.head(5)` |
| Línea 152 | Subtítulo con "5 coches" y "±10 %" |
| Líneas 153-164 | `st.dataframe` **sin** cambios (mismo `column_config` y `hide_index=True`) |
| Líneas 165-171 | `st.caption` **nuevo**, solo si `len(coches_cercanos) < 5` |

La llamada al modelo (línea 100, `prediccion = modelo.predict(datos)`) y el
cálculo de `soporte_datos` (líneas 118-135) **no se han tocado**.

### ⚠️ Sin validar

Esta sección describe **lo que hace el código, leído**. En la sesión en que se
aplicó el cambio **no llegó a ejecutarse ninguna prueba**: la sesión se cortó.
Por tanto **no existe**:

- ningún `AppTest` ni verificación de arranque del servidor,
- ninguna captura de línea base de `modelo.predict()` antes/después (aunque la
  línea 100 no se modificó, no está verificado que el resto no lo altere),
- **ninguna medición de cuántas combinaciones de la app muestran 0 coches en la
  banda**, que es justo el dato que decidiría si una tabla de 5 filas es útil
  o si degenera en tabla vacía con frecuencia.

Antes de dar esto por bueno hay que medirlo. El recuento de filas del dataset
que hace falta para eso va delegado en `data-analyst` (sección 2).

---

## 8 quinquies. Rango orientativo (2026-10-02) — opción E HECHA Y VALIDADA

**Solo `prediccion_coche2.py`. +15 líneas, 0 borradas, 0 modificadas. El modelo,
el `.pkl` y los hiperparámetros NO se tocaron. Sin commit.**

### Qué hace

Debajo del precio estimado se muestra un `st.caption` con el **percentil 5 y el
percentil 95 de las 200 predicciones individuales de los árboles**:

```
📊 Rango orientativo: 14.244,60 € – 18.065,63 €
```

Las predicciones por árbol salen de
`modelo.named_steps["random_forest"].estimators_`, previa una única llamada a
`modelo.named_steps["preprocesamiento"].transform(datos)`.

### Dónde está en el código

`prediccion_coche2.py`:

| Ubicación | Qué |
|---|---|
| Líneas 103-112 | `transform` + predicción de los 200 árboles + `np.percentile(..., [5, 95])` |
| Líneas 128-130 | `st.caption` con el rango |
| Línea 100 | `modelo.predict(datos)` — **sin tocar** |
| Líneas 114-123 | Bloque X (5 coches cercanos) — **sin tocar** |
| Líneas 133-150 | Avisos D de soporte — **sin tocar** |

### Las cuatro reglas que hay que respetar si se toca esto

1. **`modelo.predict(datos)` sigue siendo el precio destacado.** La línea 100 no
   se toca. El rango se calcula aparte y **no** sustituye a la predicción del
   ensemble por la media de los árboles.
2. **Se usan p5 y p95, nunca min/max.** El rango se ancla en `precio_estimado`
   (el del ensemble), no en la media de los árboles.
3. **El rótulo es "Rango orientativo". NO es un intervalo de confianza** y no debe
   llamarse así.
4. **No sustituye a los avisos D.** Ambos conviven: D mide *soporte* (datos
   cercanos), E mide *dispersión* (desacuerdo entre árboles).

### ⚠️ Limitación importante

**El rango mide la dispersión entre árboles, no el error predictivo.** No es una
medida completa de lo fiable que es la predicción:

- No cubre el ruido aleatorio (los precios reales están mucho más dispersos de lo
  que indican los percentiles). Medido: `[p5, p95]` contenía el precio real solo
  el **71 %** de las veces, frente al 90 % que su nombre sugiere.
- **Puede ser muy ancho y descentrado con poco soporte.** Con soporte 0 el bosque
  entero se equivoca de rama a la vez y el rango se dispara.
- **Se congela en extrapuración.** Comprobado con Fiesta 2015: a partir de ~90.000
  km la distribución de los 200 árboles es idéntica byte a byte (misma hoja) con
  soporte 0. El rango muestra entonces una confianza falsa y constante.

Por todo esto el rango **complementa a D, nunca lo reemplaza**, y un rango estrecho
**no** significa "fiable".

### Validación

- **AppTest: 0 excepciones** en 7 ejecuciones. Servidor real: `/healthz` **HTTP 200**.
- **El precio estimado NO cambia: 6/6 escenarios bit-idénticos** al baseline
  capturado antes del cambio (defaults reales, Focus 2018, Mustang 2018, KA 2015,
  B-MAX 1993, Fiesta 150.000 km).
- `p5 <= precio estimado <= p95` en los 6.
- **Avisos D y nº de filas de X idénticos** antes/después: X y D intactos.
- MD5 de `modelo_coches.pkl` sigue siendo `72441976dd0ba4ba2f95acc3c3bee3f9`.

### ⚠️ No es la opción E original

La opción E de la tabla de la sección 9 pedía un rango **mín/mediana/máx de los
coches cercanos** (reutilizando el dataframe de la tabla). Lo implementado usa las
**predicciones de los árboles**, que es otra fuente. Se adoptó porque el
usuario lo pidió así tras la investigación. El enfoque original sigue sin hacer,
y **es compatible**: se podrían mostrar ambos.

---

## 8 sexies. Rangos de los widgets derivados del dataset (2026-10-03) — opción B HECHA Y VALIDADA

**Solo `prediccion_coche2.py`. El modelo, el `.pkl` y los hiperparámetros NO se
tocaron** (MD5 `72441976dd0ba4ba2f95acc3c3bee3f9` verificado antes y después).
**Commiteado** en el HEAD de `main` (*"mejoras finales de prediccion y
documentacion"*).

Cierra las dos últimas tareas abiertas: la **opción B** de la sección 9 y el
pendiente de los **0 km** del final de la sección 8 bis.

### El principio: la app no debe ofrecer ningún valor que el modelo no haya visto

Antes, tres widgets ofrecían rangos inventados que incluían valores que **no
existen en ninguna fila** del dataset. Medido (`data-analyst`, 2026-10-03):

| Widget | Antes | Después | Rango fantasma eliminado |
|---|---|---|---|
| Año | `slider(1990, 2025)` | `slider(1996, 2020)` | **5 años enteros** (2021-2025 con **0 filas**) y 6 más al inicio |
| Kilometraje | `slider(0, 300000, step 1000)` | `slider(0, 178000, step 1000)` | 122.000 km por encima del máximo real (177.644) |
| Motor | `slider(0.5, 6.0, step 0.1)` = 56 posiciones | `select_slider` con las **15** cilindradas reales | **41 de 56 posiciones** no existen (1.9, 2.1, 4.0, 5.5…) |
| mpg | `slider(0, 250, step 1)`, default **55** | `selectbox` con los **90** valores reales | el propio default era fantasma: **`mpg == 55` son 0 filas** |
| Tax | `slider(0, 600)`, default 150 | **sin cambios** | el 150 sí existe en el dataset |

Datos verificados: `year` va de **1996 a 2020** (22 años, faltan 14 del rango
1990-2025). `mileage` mínimo real **4**, máximo **177.644**, y **0 filas con 0 km**.
`engineSize` tiene **15 valores distintos** (1.0-1.8, 2.0, 2.2, 2.3, 2.5, 3.2, 5.0),
todos múltiplos de 0.1. `mpg` tiene **90 distintos**, de 20.8 a 201.8.

### El suelo de 1.000 km

```python
KM_MIN_INICIAL = 1000
mileage_inicial = max(KM_MIN_INICIAL, int(round(grupo["mileage"].median() / 1000) * 1000))
```

Solo afecta al **valor inicial**. El slider sigue admitting 0 km a mano. Motivo:
0 km no existe en el dataset, y el objetivo de los defaults dinámicos es arrancar
en un dato real. Hay 425 filas por debajo de 1.000 km, así que el suelo no
imposibilita ningún coche real: solo evita el `0` sin sentido que salía de las
medianas de los coches casi nuevos de 2020.

### El `mpg` pasó a ser dinámico (decisión del usuario, 2026-10-03)

En una primera versión de este cambio el `mpg` se dejó **fijo** en la moda global
del dataset (65,7). El usuario pidió hacerlo **dinámico**, igual que el motor:

```python
mpg_inicial = float(grupo["mpg"].mode().iloc[0])
mpg = st.selectbox(..., options=CONSUMO_VALORES,
                   index=CONSUMO_VALORES.index(mpg_inicial),
                   format_func=lambda v: f"{v:.1f}", key=f"mpg_{combo}")
```

**Por qué importa:** el `mpg` es el proxy continuo que usa el aviso de soporte D
(ver la tabla de variables de la sección 8 ter: excluirlo baja la detección del
100 % al 80 %). Un default de 65,7 para un eléctrico o un V8 degradaba ese aviso.
Efecto medido en los ejemplos:

| Escenario | mpg antes (fijo) | mpg ahora (dinámico) | Aviso de soporte |
|---|---|---|---|
| Fiesta 2020 Manual Diesel | 65,7 | 58,9 | sin aviso → sin aviso |
| Mustang 2020 Manual Petrol | 65,7 | 22,8 | 🟠 → **sin aviso** |
| Mondeo 2018 Manual Diesel | 65,7 | 47,1 | sin aviso → sin aviso |
| Tourneo Custom 2020 Manual Diesel | 65,7 | 44,8 | 🟠 → **sin aviso** |
| B-MAX 1996 Manual Petrol | 65,7 | 74,4 | 🔴 → 🟠 (sigue avisa) |

O sea: los valores por defecto dejaron de ser inventados **y** el aviso D mide
mejor, porque por fin se parece al coche que el usuario está describiendo.

### Dónde está en el código

| Ubicación | Qué |
|---|---|
| Líneas 35-46 | Constantes: `ANIO_MIN/MAX`, `TAMANO_MOTOR_VALORES`, `CONSUMO_VALORES`, `KM_MAX`, `KM_MIN_INICIAL` |
| Línea 48 | `year` con rango real, default `ANIO_MAX` (2020, el mismo de antes) |
| Líneas 70-73 | `mileage_inicial` con el suelo de 1.000 km |
| Línea 76 | `mpg_inicial` = moda de `mpg` del grupo de referencia |
| Línea 78 | `mileage` con `max_value=KM_MAX` (178.000) |
| Líneas 82-89 | `mpg` como `selectbox` de los 90 valores reales, con `key=f"mpg_{combo}"` |
| Líneas 92-99 | `engine_size` como `select_slider` de las 15 cilindradas reales |

`modelo.predict()` (línea 134), `soporte_datos` y el bloque de la tabla X **no se
tocaron**.

### Defaults reales de la app después del cambio

`Fiesta · 2020 · Manual · Diesel · 1.000 km · 150 € tax · 58,9 mpg · 1,0 L`.
El año por defecto **sigue siendo 2020** (era `ANIO_MAX`), así que ese valor no
cambió respecto a la sección 8 bis.

### Validación

- **AppTest: 0 excepciones** en el arranque, en 23 escenarios interactivos (19 de los
  22 modelos) y al pulsar 🔮 Calcular precio en todos ellos.
- **El precio de la UI coincide con `modelo.predict()`** en los 23 escenarios
  (diferencia máxima 0,005 € = redondeo del formato de euros). Esto confirma que
  los valores de los widgets llegan bien al DataFrame, incluidos los dos widgets
  que cambiaron de tipo (`mpg` a `selectbox`, `engine_size` a `select_slider`).
- **Tabla de coches cercanos: 5 filas** en los 23 escenarios (nunca vacía).
- **Barrido de las 8.250 combinaciones** (22 modelos × **25 años** × 3
  transmisiones × 5 combustibles, ya no 36 años): **0 problemas**. Ninguna moda de
  motor ni de mpg fuera de sus listas de opciones, ningún kilometraje inicial fuera
  de `[0, 178000]` ni con step inválido, **0 grupos vacíos** (la cadena de respaldo
  nunca llega a N5).
- Reparto de niveles de la cadena de respaldo en esas 8.250: **N1 505 · N2 1.370 ·
  N3 1.301 · N4 5.074 · N5 0**. Los 505 N1 cuadran con las 506 celdas exactas no
  vacías del dataset: la que falta es `Ranger`, que la app no ofrece (sección 6).
- **Persistencia**: 123.000 km / 1,6 L / 201,8 mpg sobreviven a un rerun con la
  misma combinación; al cambiar de modelo los tres se recalculan con `key` nueva.
- Servidor real: `/healthz` **HTTP 200**, `/` **HTTP 200**, log sin errores.
- MD5 de `modelo_coches.pkl` sin cambios.

### Limitaciones que siguen vivas (no las arregles sin hablar)

1. **La celda por defecto (`2020 · Manual · Diesel`) solo tiene 23 filas en 5 de los
   22 modelos.** Para los otros 17, la cadena arranca en N2/N3/N4 y el default es
   una aproximación. Consecuencia: en los valores por defecto, 17 modelos dan
   alguna señal de aviso 🔴/🟠. Es una propiedad del dataset (el UK casi no tiene
   diésel manual de 2020), no un defecto de la app.
2. **N2 ignora el combustible**, así que un Diésel manual puede arrancar con datos
   de gasolina (es el caso de `Fiesta | 2020 | Manual | Diesel`, que cae en las 78
   filas de `Fiesta 2020 Manual **Petrol**`). Es comportamiento buscado: es
   preferible un modelo adyacente a un `0 filas` que un `IndexError`.
3. **El `tax` sigue con default fijo 150.** No se ha derivado de los datos; es el
   único widget que queda fuera del principio de esta sección.

---

**Residuo del bug, NO resuelto, y no es cosa del modelo.**

Con los valores por defecto de la app (**2020, 45.000 km, 2.0L, Manual, y
combustible = `Diesel`**, ver la corrección en la sección 8 bis)
14 de 22 modelos devuelven **exactamente el mismo precio**.

- **Causa:** esa combinación **no existe en el dataset — 0 filas**. El árbol no
  tiene datos en ese nodo y no llega a dividir por modelo.
- **No es `min_samples_split`** (probado 3/5/10/15, R² empeora al bajar).
- **No se arregla cambiando los defaults:** un combo "realista" probado
  (2019, 30.000 km, 1.4L) solo sube a 13/23 distintos y además mete a Mustang en
  15.103 € (su mediana real es 33.979 €), o sea, empeora.
- **Con coches reales el modelo discrimina bien:** 12 casos comprobados, todos
  con precios distintos y **12,1% de desviación media** frente a la mediana real
  de su grupo. Mustang 2018 → 29.321 € (mediana 30.249), KA 2015 → 4.641 €
  (mediana 4.996), S-MAX 2017 → 17.926 € (mediana 17.925).

**Si el usuario se queja de precios iguales:** explícale que solo ocurre con
combinaciones imposibles, y **no cambies los hyperparameters por tu cuenta**.

> **Ojo, esta medición es anterior a la sección 8 bis.** El "14 de 22" se midió
> con los valores por defecto antiguos (2.0 L / 45.000 km). Con los defaults
> dinámicos de ahora la combinación por defecto es otra, así que el número
> exacto puede haber cambiado. Lo que no cambia es el diagnóstico de abajo: el
> mecanismo es falta de soporte, no el modelo.

### 9 bis. Diagnóstico detallado (2026-10-02, solo lectura, sin reentrenar)

Medido recorriendo los 200 árboles del modelo con los valores por defecto:

| Métrica | Valor |
|---|---|
| Profundidad media de la hoja alcanzada | **9-10** (de un máximo de 20) |
| Árboles que llegan a profundidad 20 | **0 de 200** |
| Nº de filas de entrenamiento en esa hoja | **mediana 6, máximo 14** |

Consecuencias:

1. **`max_depth=20` NO es el culpable.** El nodo para porque tiene **menos de 15
   filas**, es decir por `min_samples_split=15`. Por eso bajar ese hiperparámetro
   no lo arregla: aunque bajara, el nodo tiene 1-14 filas y **ninguna es de esos
   modelos**.
2. **Los 15 modelos colapsados recorren literalmente los mismos nodos en los 200
   árboles.** El árbol nunca corta por `modelo` en esa rama (aunque sí hay cortes
   por `modelo`, el árbol 0 tiene uno en profundidad 2), así que el bit one-hot
   del modelo es irrelevante para el recorrido. Misma hoja → misma media →
   mismo número.
3. Solo hay **8 precios distintos entre 22 modelos**: 18.297,57 € ×15, Focus
   18.733,40, Kuga 18.016,46, Mondeo 18.070,62, Edge 21.811,26, S-MAX 24.558,88,
   Galaxy 25.065,05, Mustang 27.663,41.

Datos que explican el hueco (los tres defaults estaban fuera de soporte a la vez):

| Hecho medido | Valor |
|---|---|
| Coincidencia exacta `(2020, Manual, Petrol)` + 45.000 km + 2.0 L | **0 filas** |
| Con tolerancia amplia (±0,6 L y ±5.000 km) | **0 filas** |
| Gasolinas de 2.0 L de 2020 en todo el dataset | **0** (los 25 coches de 2.0 L de 2020 son Diésel/Hybrid) |
| Motor en `(2020, Manual, Petrol)`: 185 filas | 167 son 1.0 L; salto de 1,5 L a 2,3 L sin nada en medio |
| Kilometraje en `(2020, Manual, Petrol)` | de 5 a **8.786 km**, mediana 641. El default estaba **5,1× por encima del máximo** |
| `mpg == 55` exacto | **0 filas** (cuarto desajuste del default) |
| Años **2021-2025** del slider | **0 filas cada uno** |
| Coches de 2020 en todo el dataset | 252 filas, kilometraje mediano **708 km** |
| Modelos de la app que **nunca** han tenido un 2.0 L | **12 de 22** (Mustang incluido: solo 2.3 y 5.0) |
| Coche real más cercano a los defaults | Focus 2018, 46.286 km, 2.0 L, Manual, Petrol → **15.790 €** |
| Último año con datos de 2.0 L Manual Petrol | **2018** (144 filas, todas Focus). 2019 tiene 1, 2020 ninguna |

**Veredicto: es el comportamiento matemáticamente correcto, no un bug ni una
regresión.** Con soporte cero un árbol solo puede devolver el promedio del grupo
más parecido. Lo que sí son defectos reales son de la **app**, no del modelo:
ofrece por defecto una combinación fuera de su propio dataset, y muestra
`18.297,57 €` con dos decimales para una consulta con 0 filas de apoyo.

### Opciones que quedaron sobre la mesa (todas implementadas)

| # | Opción | Coste |
|---|---|---|
| **A** | Aviso de soporte: contar las filas que casan con la combinación y avisar si son 0 | Bajo, usa el `df` ya cargado. **Absorbida por D**, que es la versión robusta |
| **B** | **Rangos de los widgets derivados de los datos → HECHA** (sección 8 sexies) | — |
| **C** | **Defaults dependientes de la combinación → HECHA** (sección 8 bis) | — |
| **D** | **Aviso de soporte por radio en distancia estandarizada → HECHA** (sección 8 ter) | — |
| **E** | Mostrar rango mín/mediana/máx de los 10 coches cercanos en vez de un punto | Casi cero, reutiliza el dataframe que la app ya calcula. **HECHA en otra forma** (sección 8 quinquies: rango de los 200 árboles, no de los coches cercanos) |
| **F** | Cambiar solo los defaults (paliativo: 2017 + 1.5 L + 45.000 km → 15/22 distintos) | Bajo, pero solo esconde el problema. **Superada por C** |
| **G** | No llamar al modelo si el soporte es 0 y usar la mediana de los k más cercanos | **Roca `mejorar_pred.md`**, necesita permiso explícito |

**Descartado:** tocar hiperparámetros (ya demostrado contraproducente), añadir
features o cambiar a kNN/Gradient Boosting. Eso ya es cambiar el modelo, que es
justo lo que está descartado.

> **El cambio X (sección 8 quater) no figura en esta tabla porque no es una de
> las opciones A–G**: fue una petición posterior del usuario para acotar la tabla
> de coches cercanos a una banda de ±10 %.

**Pendientes reales: ninguno.** B se hizo el 2026-10-03 (sección 8 sexies).

**Impacto medido de C + D sobre el síntoma original:** con los defaults dinámicos
de C, la configuración real de la app (`2020 · Manual · Diesel`) da **22 precios
distintos de 22 modelos**, cuando antes eran 8 con 15 colapsados. Barrido de las
**94 configuraciones** (año × transmisión × combustible con datos): **0 colapsos**.
O sea que C ya resolvió el síntoma y D quedó como indicador de fiabilidad, no
como aviso de error.

---

## 10. Reglas de trabajo para futuras sesiones

1. **No repitas la auditoría.** Los hallazgos están en las secciones 4 a 7.
   Y no conviertas un cambio pequeño en una auditoría completa: ver la sección
   2 bis.
2. **Antes de reemplazar `modelo_coches.pkl`, crea un backup con fecha:**
   `cp modelo_coches.pkl modelo_coches_backup_$(date +%Y%m%d_%H%M%S).pkl`.
3. **El CSV original es Sacred.** Se limpia con `limpiar()` hacia un archivo
   nuevo, nunca sobreescribiendo.
4. **Reentrenar ≠ mejorar.** Compara siempre contra la tabla de la sección 7 con
   el mismo split (`random_state=42`, 25%) antes de dar por bueno un PKL nuevo.
5. **`entrenar_modelo.py` escribe `modelo_coches_nuevo.pkl`, no el de la app.**
   El reemplazo es un paso explícito y consciente.
6. Si se cambia `limpiar()`, hay que **reentrenar** el modelo. El dataset limpio
   y el PKL deben estar siempre sincronizados.
7. Comenta el trabajo **en español**.
8. **No hagas commits** salvo que el usuario lo pida explícitamente.
9. Si editas `AGENTS.md`, commitea el cambio en la misma sesión: es la memoria
   del proyecto y solo sirve si está en el repo.

---

## 11. Estado de Git

### Estado real verificado (2026-10-03, tras el cierre de sesión)

| Dato | Valor |
|---|---|
| Rama | `main` |
| HEAD | el commit *"mejoras finales de prediccion y documentacion"* (opción **B** + documentación de este fichero). Su hash está en `git log` |
| Working tree | **Limpio.** Sin nada sin commitear |
| `modelo_coches.pkl` | **Sin tocar.** MD5 `72441976dd0ba4ba2f95acc3c3bee3f9` |

Historial reciente:

```
(HEAD)  mejoras finales de prediccion y documentacion   <- opción B + mpg dinámico + suelo de 1.000 km
fa66a19 añadir rango orientativo de predicción          <- opción E (rango p5-p95)
d918107 si vamos a mejorar la predicción del coche, ... <- C, D y X
0528228 chore: ignore Modulo12 (independent repo)
e14039d commit message here
```

**Lo que estaba pendiente y ahora está commiteado:** la **opción B** de la sección 9
(rangos de los widgets derivados del dataset), el **`mpg` dinámico** y el suelo
`KM_MIN_INICIAL = 1000` que cierra el pendiente de los 0 km. Todo en
`prediccion_coche2.py`, más la sección 8 sexies y las correcciones de las secciones
1, 8 bis, 9 y 12 de este fichero.

`_antes_F.py` (copia de seguridad del fichero antes de la opción B) se ha
**borrado**: nunca estuvo versionado y la versión anterior ya está en `fa66a19`.
`git log --oneline` es la fuente de verdad para el hash exacto del HEAD.

### Estado anterior (2026-10-02), ya superseded

| Dato | Valor |
|---|---|
| HEAD | `0528228` |
| Sin commitear | `AGENTS.md`, `prediccion_coche2.py`, `mejorar_pred.md` |

Esos tres ficheros correspondían a **C**, **D** y **X** más su documentación.
**Ninguno requería tocar el modelo ni los datasets.**

### Historial

**Hecho el 2026-10-02**, commit `9143a5a` *"Corrige el bug que hacia que todos los
coches valieran 18.032,07 €"*: se versionaron los 18 ficheros de `Modulo11/`
(código, `AGENTS.md`, notebooks, CSV original y limpio, tema de Streamlit).

Se creó `Modulo11/.gitignore` con:

```
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
*.pkl          # 67 MB entre modelo y backup; se regenera con entrenar_modelo.py
*_backup_*     # copias byte a byte de archivos ya versionados
prueba_*.zip
```

**Verificado: 0 ficheros `.pkl` dentro del repo.** `modelo_coches.pkl` y
`modelo_coches_backup_20261002_005315.pkl` siguen en disco, solo fuera de git.
`.opencode/node_modules` ya lo ignoraba su propio `.gitignore`.

### Sigue pendiente

- El usuario commiteó por su cuenta `Modulo10/`, `.agents/` y `.claude/` en el
  commit `a0881d1` *"si hacerlo"* (2026-10-02 01:18). **Ya están versionados**,
  así que el punto anterior queda cerrado.
- **No hay `.gitignore` en la raíz del repo** (`/home/miguel/mi_entorno/Python`),
  solo en `Modulo11/`. Por eso el commit `a0881d1` arrastró
  `Modulo10/__pycache__/*.pyc` (ruido). Si vuelve a aparecer basura así, crear
  un `.gitignore` en la raíz con `__pycache__/` y `*.pyc`.
- **Los tres cambios C, D y X están commiteados** (en `d918107`). La regla 9 de la
  sección 10 pide commitear `AGENTS.md` en la misma sesión en que se edita, así que
  el commit de la **opción B** y de esta documentación sigue pendiente.

---

## 12. Cómo retomar el proyecto

```bash
cd /home/miguel/mi_entorno/Python/Modulo11
source .venv/bin/activate
streamlit run prediccion_coche2.py
```

Estado: **funcionando**, con una salvedad importante. CSV limpio sincronizado
con el PKL, app arrancada sin errores, comparativa de métricas hecha. Lo único
abierto de fondo es el punto de la sección 9 (precios idénticos con combinaciones
imposibles), que está diagnosticado; de sus opciones están implementadas:

| Cambio | Sección | Validado | Commiteado |
|---|---|---|---|
| **C** — defaults dinámicos | 8 bis | Sí | Sí (`d918107`) |
| **D** — aviso de soporte | 8 ter | Sí | Sí (`d918107`) |
| **X** — tabla de coches cercanos acotada al ±10 % | 8 quater | Sí (2026-10-02) | Sí (`d918107`) |
| **E** — rango orientativo p5–p95 de los 200 árboles | 8 quinquies | Sí | Sí (`fa66a19`) |
| **B** — rangos de los widgets derivados del dataset | 8 sexies | Sí (2026-10-03) | Sí (HEAD) |
| **TAX dinámico** — tax inicial por grupo N1–N4 (n≥3), mediana ajustada | 8 septies | Sí (2026-10-03) | **No commiteado aún** |

**Ya no queda ninguna opción A–G pendiente.** Los dos puntos abiertos que restaban —**B** y el caso de los **0 km** como valor inicial— se cerraron juntas el 2026-10-03 con `KM_MIN_INICIAL = 1000`.

> **Nota sobre X:** la sección 8 quater se escribió afirmando que estaba sin
> validar. Ya se validó (6/6 escenarios, nº de filas ≤ 5) en la misma sesión que
> E. Su texto original se conserva como constancia del estado en el momento en que
> se aplicó el cambio.

---

## 8 septies. Tax dinámico (2026-10-03)

**Solo `prediccion_coche2.py`. El modelo, el `.pkl` y los hiperparámetros NO se tocaron** (MD5 `72441976dd0ba4ba2f95acc3c3bee3f9`).

Implementada la propuesta del análisis: valor inicial de `tax` dinámico con la misma cadena de respaldo N1→N2→N3→N4, umbral mínimo **>= 3 filas** por nivel, **mediana ajustada al valor real de `tax` más cercano** (con empate exacto de distancia → menor valor), y **fallback global 145.0**.

### Regla aplicada

1. **N1**: `(model, year, transmission, fuelType)` — si `len(g) >= 3`: `tax_inicial = valor_real_más_cercano_a(mediana(g.tax), g.tax.unique())`; con desempate = menor valor.
2. **N2**: `(model, year, transmission)` — mismo criterio si n>=3.
3. **N3**: `(model, transmission, fuelType)` — mismo criterio si n>=3.
4. **N4**: `(model)` — mismo criterio si n>=3.
5. **N5 (fallback):** 145.0 (ningún nivel tenía >=3 filas).

### Cambios en código

`prediccion_coche2.py`:

| Ubicación | Qué |
|---|---|
| Líneas ~90–128 (bloque de inicialización tras mpg_inicial) | Cálculo de `tax_inicial` con los 4 niveles y fallback 145.0. |
| Línea ~130 | `tax = st.slider("Ingrese el impuesto del coche", min_value=0, max_value=600, value=int(round(tax_inicial)), step=5, key=f"tax_{combo}")` |

**Notas:** Se usa `int(round(tax_inicial))` para cumplir con el tipo esperado por Streamlit (evita warning de tipo float/int). Se añade **`key=f"tax_{combo}"`** (dinámica). **No se cambia** el rango (0–600) ni `step=5`.

### Validación

- **AppTest:** Sin excepciones al arrancar y ejecutar.
- **Casos validados:**
  - `Fiesta 2020 Manual Diesel` → **145** (N1 vacío < 3 → N2 con 78>=3)
  - `Fiesta 2016 Manual Diesel` → **0** (N1 con 94>=3)
  - `Mondeo 2016 Automatic Electric` → **125** (N1 2<3 → N2 con 23>=3; **no usa las 2 filas de N1**)
- **Garantía:** `tax_inicial` es **siempre un valor real** del grupo seleccionado (se elige de `tax.unique()` del nivel que cumple n>=3).
- **Persistencia:** con `key=f"tax_{combo}"`, el valor manual se conserva mientras no cambia la combinación; al cambiar combinación, se recalcula.
- **Integración:** C, D, X, E, B, F **intactos**. `modelo.predict()`, pipeline y columnas **sin cambios**.
- **PKL:** MD5 **72441976dd0ba4ba2f95acc3c3bee3f9** (sin modificar).

### Qué queda pendiente después de Tax dinámico

Tras esta mejora, **no quedan opciones A–G pendientes**. Único punto menor documentado: `tax` sigue siendo un slider con rango 0–600 y 35 valores reales (patrón de "rango fantasma" que ya se corrigió en mpg/engineSize). Esto **no afecta a la predicción** y no requiere implementación ahora.

## Auditorías largas y puntos de control

Las auditorías que requieran mucho tiempo deben ejecutarse por fases.

Después de completar cada fase significativa, actualizar AGENTS.md
con:

- fase completada
- hallazgos importantes
- archivos afectados
- pruebas realizadas
- fase siguiente
- estado de la auditoría

Si la sesión se interrumpe, una nueva sesión debe leer primero el
estado guardado y continuar desde la última fase completada.

NO repetir fases ya documentadas salvo que exista una razón para
verificar un resultado anterior.



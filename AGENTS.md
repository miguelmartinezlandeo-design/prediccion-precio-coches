# AGENTS.md — Modulo11: Predicción del precio de coches

Este fichero es la **memoria del proyecto**. Está organizado en dos bloques:

- **Estado y reglas (secciones 0-9).** Describe cómo está el sistema **hoy**. Si algo de
  aquí contradice al código, el código manda: Corrige este fichero en la misma sesión.
- **Historial (secciones 10-11).** Cronología de lo que se hizo y de **cómo se estaba
  antes**. Sirve para entender por qué se decidió lo que se decidió. **No son reglas
  vigentes ni mediciones del estado actual.**

> **No vuelvas a investigar lo que ya está diagnosticado** (§4, §5, §7.3, §9.1). Está
> aquí para evitar repetirlo.

---

## 0. Cómo usar este fichero

- **Empieza por §1 (ESTADO ACTUAL)**, luego §2 (Reglas) y §9 (Problemas conocidos).
- Las mediciones de §10 están medidas sobre widgets y defaults que **ya no existen**.
  Cita §10 solo como "por qué se decidió así", nunca como descripción de la app actual.
- **Actualizar este fichero es parte del trabajo.** Si en una sesión cambias el
  comportamiento de la app, actualiza §1 y la sección correspondiente de §6/§7/§8 en la
  **misma sesión** (regla 9 de §2.4). Un fichero de memoria desactualizado induce a
  error, que es peor que no tenerlo.
- **No uses números de línea** para referenciar el código. Usa el nombre del símbolo
  (`soporte_datos()`, `grupo_de_referencia()`, `st.selectbox("... mpg")`,
  `modelo.predict()`). Los números de línea caducan con cada commit.
- Los ficheros `.pkl` y `*_backup_*` están **fuera de git** a propósito (ver §3.4).

---

## 1. ESTADO ACTUAL

> Verificado el **2026-10-03**; estado de git re-verificado el **2026-10-04**. Si algo de
> esta sección no cuadra con `git status`, `git log`, `md5sum` o el código, esta sección
> está mal y hay que corregirla.

### 1.1 Última sesión (2026-10-03)

1. **Tax dinámico** (sección 8 septies de la versión anterior de este fichero → §8).
2. **Aviso 🔴 de soporte compacto**: el mensaje del nivel "sin soporte" se reescribió
   para que sea **una línea corta** en vez del párrafo largo. Ver §7.3. **Es un cambio
   intencionado: no lo reviertas.**
3. **Reorganización de este `AGENTS.md`** (estructura de 12 secciones, estado actual
   separado del historial).

### 1.2 Estado del repositorio

| Dato | Valor |
|---|---|
| Rama | `main` |
| HEAD | `a4610ee` — *"aviso de soporte rojo compacto y reorganizacion de AGENTS.md"* |
| Commits sin pushear | **5** (`main` está 5 commits por delante de `origin/main`) |
| Working tree | **Limpio.** El aviso 🔴 y la reorganización de este `AGENTS.md` ya están commiteados en `a4610ee` |
| `modelo_coches.pkl` | **Sin tocar.** MD5 `72441976dd0ba4ba2f95acc3c3bee3f9`, fecha `Oct 2 01:07` |
| CSV original | **Sin tocar.** 17.966 filas |
| CSV limpio | 17.811 filas |

### 1.3 Invariantes del proyecto

Estas cuatro cosas **no se tocan** sin permiso explícito del usuario. Están aquí para
que no haya que deducirlas:

| Invariante | Por qué |
|---|---|
| **El `.pkl` no se reemplaza sin proceso explícito** | Antes hay que hacer backup con fecha y comparar métricas contra la tabla de §5.2 |
| **Los hiperparámetros no se cambian** | Probado: empeora R² y no arregla nada (§5.2) |
| **El modelo, el pipeline y las 9 columnas no se tocan** | Si se cambia `limpiar()`, hay que reentrenar; dataset limpio y PKL siempre sincronizados (§2.4 regla 6) |
| **El CSV original es sacred** | Se limpia hacia un archivo nuevo, nunca sobreescribiendo |

### 1.4 Valores por defecto reales de la app (verificados)

Estos son los valores con los que la app arranca, medidos ejecutando la app:

```
modelo      Fiesta          (el más frecuente del dataset: 6.508 filas)
transmisión Manual          (primera opción del selector)
combustible Diesel          (primera opción del selector)
año         2020            (= ANIO_MAX, el máximo real del dataset)
kilometraje 1.000 km        (suelo KM_MIN_INICIAL; la mediana del grupo da 0)
impuesto    145 €           (dinámico, §6.3 y §8.6 — el valor fijo 150 ya no existe)
mpg         58,9            (dinámico, §6.3 y §8.5)
motor       1,0 L           (dinámico, §6.3 y §8.5)
```

Resultado con esos valores: **15.736,71 €**, rango orientativo 14.686,91 – 16.692,08,
**sin aviso** de soporte, y 5 coches en la tabla de cercanos.

> ⚠️ Cualquier análisis que asuma `Petrol`, `45.000 km`, `2.0 L`, `mpg = 55` o
> `tax = 150` está usando valores que la app **ya no ofrece**. Están en §10 por
> historial.

### 1.5 Validación realizada en esta sesión

Sobre el estado de §1.2, sin modificar código:

- **AppTest: 0 excepciones** al arrancar y también al pulsar 🔮 Calcular precio, en el
  escenario de defaults y en un escenario con soporte 0.
- Los valores por defecto de §1.4 **verificados sobre la app renderizada**, no deducidos.
- Aviso 🔴 **verificado renderizando**: 1 `st.warning` con el texto nuevo (§7.3).

---

## 2. Reglas permanentes

### 2.1 Delegar todo análisis de datos en `data-analyst`

> **Toda tarea relacionada con datos se delega en el subagente `data-analyst`.**
> No analices tú mismo los datos con Pandas, Python o SQL.

Delegar cuando el usuario pida: leer o explorar un DataFrame, contar filas, buscar nulos
o duplicados, filtrar, ordenar, buscar registros, calcular estadísticas, resumir columnas,
detectar problemas de calidad, preparar datos para gráficos, o validar un CSV.

Ejemplos que **sí** se delegan: "¿cuántos coches hay?", "dime la media del precio",
"filtra los Ford", "busca valores nulos", "explora el dataset".

**Límites de `data-analyst`:**

- **NO** modifica la aplicación.
- **NO** ejecuta Streamlit.
- **NO** entrena modelos (su función es exclusivamente analizar datos). El
  entrenamiento y la evaluación los hace el agente principal.

Cuando recibas su resultado, conserva estas dos líneas al presentarlo:

```
📊 DATA-ANALYST
🔐 SUBAGENTE EJECUTADO
```

**Aviso técnico demostrado:** `data-analyst` da índices de fila poco fiables al comparar
dos CSVs con distinto índice (ya devolvió una lista de filas de kilometraje bajo que no
existía). Para contrastar filas entre el CSV original y el limpio, hay que exigirle que
use `df.index` real de pandas y que pegue la salida literal del comando, o verificar
después con un script propio.

### 2.2 Proporcionalidad del análisis

El nivel de análisis y validación debe ser **proporcional a la tarea**. Hay dos regímenes
y no se mezclan.

**Análisis exhaustivo** cuando la tarea implique: investigar la causa de un problema de
datos; detectar anomalías; estudiar la calidad del dataset; comparar modelos; validar
hipótesis sobre los datos; tomar decisiones que puedan afectar al modelo; modificar
datos de entrenamiento; reentrenar o evaluar un modelo. En esos casos se usa
`data-analyst` y se hacen las comprobaciones necesarias.

**Cambios pequeños de código**, ya especificados y sin necesidad de nuevo análisis de
datos: no hacer análisis exhaustivo del dataset; no ejecutar baterías extensas de
pruebas salvo que sean necesarias; modificar solo las líneas necesarias; hacer una
validación breve y específica del cambio; informar del resultado.

Ejemplos textuales del usuario: cambiar el número de resultados mostrados, cambiar un
texto de la interfaz, **añadir un caption**, modificar una condición ya definida,
cambiar una etiqueta, cambiar el formato de presentación.

> **Regla importante:** no conviertas automáticamente una modificación pequeña de
> código en una auditoría completa del proyecto. Si la tarea ya tiene una
> especificación concreta y no requiere nuevo análisis de datos, ejecuta únicamente las
> comprobaciones necesarias para verificar ese cambio.

### 2.3 Relación entre 2.1 y 2.2 — *pregunta abierta*

Las dos reglas se aplican así:

- la **delegación** sigue vigente siempre que haya tarea de datos;
- la **proporcionalidad** decide *cuánto* análisis se hace, no *si* se delega.

O sea: ante un cambio pequeño sin necesidad de datos, la conclusión es que **no hay tarea
de datos que delegar**, no que haya que delegar un análisis enorme.

> 🗣️ **PENDIENTE DE CONFIRMAR CON EL USUARIO** (lleva abierto desde 2026-10-02): si
> esta es la interpretación que quiere, o si la proporcionalidad debe prevalecer sobre la
> delegación también en los casos triviales. **Pregúntalo si surge la ocasión.**

### 2.4 Reglas de trabajo para futuras sesiones

1. **No repitas la auditoría.** Los hallazgos están en §4 a §7 y §9. Y no conviertas un
   cambio pequeño en una auditoría completa (§2.2).
2. **Antes de reemplazar `modelo_coches.pkl`, crea un backup con fecha:**
   `cp modelo_coches.pkl modelo_coches_backup_$(date +%Y%m%d_%H%M%S).pkl`.
3. **El CSV original es sacred.** Se limpia con `limpiar()` hacia un archivo nuevo,
   nunca sobreescribiendo.
4. **Reentrenar ≠ mejorar.** Compara siempre contra la tabla de §5.2 con el mismo split
   (`random_state=42`, 25 %) antes de dar por bueno un PKL nuevo.
5. **`entrenar_modelo.py` escribe `modelo_coches_nuevo.pkl`, no el de la app.** El
   reemplazo es un paso explícito y consciente.
6. Si se cambia `limpiar()`, hay que **reentrenar** el modelo. El dataset limpio y el
   PKL deben estar siempre sincronizados.
7. Comenta el trabajo **en español**.
8. **No hagas commits** salvo que el usuario lo pida explícitamente.
9. Si editas `AGENTS.md`, commitea el cambio en la misma sesión: es la memoria del
   proyecto y solo sirve si está en el repo.

### 2.5 Auditorías largas

Ejecútalas **por fases**. Después de cada fase significativa, actualizar `AGENTS.md` con:
fase completada, hallazgos importantes, archivos afectados, pruebas realizadas, fase
siguiente y estado de la auditoría. Si la sesión se interrumpe, la nueva sesión lee
primero el estado guardado y continúa desde la última fase completada.

**No repitas fases ya documentadas** salvo que exista una razón para verificar un
resultado anterior.

---

## 3. Arquitectura y entorno

### 3.1 Flujo de datos

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

### 3.2 Ficheros

| Fichero | Rol |
|---|---|
| `prediccion_coche2.py` | **La app.** Carga el PKL y el CSV limpio. |
| `prediccion_coche.py`, `prediccion_coche1.py` | Borradores antiguos. **Abandonados.** |
| `limpiar_datos.py` | Función `limpiar(df)` (R1..R6) + `__main__` que escribe el CSV limpio e imprime informe. |
| `entrenar_modelo.py` | Reentrena, compara 3 escenarios y hace la prueba funcional. Escribe `modelo_coches_nuevo.pkl` (no toca el de la app). |
| `mejorar_pred.md` | Peticiones originales de mejora de la UI + la regla de delegación + la regla de proporcionalidad (§2.2). |
| `modelo_coches_backup_20261002_005315.pkl` | Backup del modelo con el bug de espacios (scikit-learn 1.9.0). |
| `used_car_price_analysis_backup_20261002_005316.csv` | Backup del CSV original. |

### 3.3 Comandos y entorno

```bash
cd /home/miguel/mi_entorno/Python/Modulo11
source .venv/bin/activate
streamlit run prediccion_coche2.py    # la app
python limpiar_datos.py               # regenera el CSV limpio + informe
python entrenar_modelo.py             # reentrena, compara y guarda modelo_coches_nuevo.pkl
```

Entorno: Python 3.12.3, scikit-learn 1.9.1, pandas 3.0.6, numpy 2.5.3, joblib 1.6.0,
streamlit 1.64.0 (venv en `.venv/`).

### 3.4 `Modulo11/.gitignore`

```
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
*.pkl          # 67 MB entre modelo y backup; se regenera con entrenar_modelo.py
*_backup_*     # copias byte a byte de archivos ya versionados
prueba_*.zip
```

**Verificado: 0 ficheros `.pkl` dentro del repo.** `modelo_coches.pkl` y su backup
siguen en disco, solo fuera de git. El `.gitignore` de la raíz del repo
(`/home/miguel/mi_entorno/Python/.gitignore`) existe pero **solo ignora `Modulo12/`**:
no tiene `__pycache__/` ni `*.pyc`, así que un commit desde la raíz puede arrastrar
`.pyc`. Si vuelve a aparecer basura así, amplíalo.

---

## 4. Dataset y limpieza

### 4.1 El bug ya resuelto: espacios iniciales en `model`

**No lo vuelvas a investigar. Ya está diagnosticado y corregido.**

`model` tenía **espacio inicial en 17.965 de 17.966 filas** (`" Fiesta"`, `" Kuga"`…). El
`OneHotEncoder(handle_unknown='ignore')` aprendió las 24 categorías **con espacio**, y la
app mandaba `"Kuga"` → categoría desconocida → vector todo ceros → **todos los modelos de
la app devolvían exactamente 18.032,07 €**.

Arreglo: `.str.strip()` en la limpieza (regla R1 de §4.2) + reentrenamiento.

> **Lección permanente:** el `OneHotEncoder` con `handle_unknown='ignore'` falla **en
> silencio** ante un desajuste de espacios. **Si algún día todos los precios de la app
> salen iguales, es esto primero.**

### 4.2 Reglas de limpieza R1..R6 (en este orden exacto)

Definidas en `limpiar_datos.py`, función `limpiar(df)`. El orden importa.

| # | Regla | Efecto |
|---|---|---|
| R1 | `df["model"] = df["model"].str.strip()` | 0 filas, 24 → 23 categorías |
| R2 | `df["tax"].fillna(145.0)` | 3 nulos |
| R3 | `engineSize == 0` → **moda del mismo model** | 51 filas, 8 modelos |
| R4 | `drop_duplicates()` sobre las 9 columnas | −154 filas |
| R5 | `df = df[df["year"] != 2060]` | −1 fila |
| R6 | `mileage <= 2` → **mediana del grupo** con fallback | 6 filas |

**Resultado: 17.966 → 17.811 filas** (17.812 tras R4, 17.811 tras R5). R6 no elimina
filas, solo imputa.

> **Trampa de orden:** si R6 se aplica *antes* de R4, la fila 7133 deja de ser duplicado
> de 6930 y sobrevive → 17.807 filas en vez de 17.811. **R4 va antes.**

Cadena de fallback de R6:
`(model, year, transmission, fuelType)` → `(model, year, transmission)` →
`(model, fuelType)` → `(model)` → mediana global. Un grupo necesita ≥3 filas válidas
(`mileage > 2`) para usarse.

> **El CSV limpio tiene exactamente 9 columnas**, en este orden y sin columnas extra: la
> app las lee con `column_config` fijo, así que **no se añaden columnas.**

### 4.3 Decisiones del usuario sobre los datos dudosos

Resueltas y **conservadas deliberadamente**. No las "arregles" sin preguntar.

| Caso | Decisión | Motivo |
|---|---|---|
| `mpg = 201.8` (5 filas, Kuga 2020 Hybrid 2.5) | **DEJAR** | No es un tecleo: es *mpg-equivalent* UK válido de un 2.5 mHEV. Máximo real del dataset (el 2º máximo es 88.3) |
| 4 Focus con precio imposible | **CONSERVAR** | Decisión del usuario. Índices originales 11912 (54.995 €), 17100 (21.500 €), 1039 (38.015 €), 7707 (32.000 €) |
| `tax == 0` (2.153 filas) | **NO BORRAR** | Valor legítimo del UK Vehicle Tax (banda mínima), no un sentinel. El 100 % de los Electric lo tiene |
| Coches baratos (495 € – 3.000 €) | **CONSERVAR** | Focus 2003 con 177.644 km a 495 € es real. Definen la cola baja del precio; borrarlos empeoraría el modelo |
| Mustang (57 filas) y modelos raros | **NO ELIMINAR** | Decisión explícita del usuario |
| 229 filas "mismo coche, distinto precio" | **NO BORRAR** | Mismo coche anunciado a distinto precio. Solo se borran duplicados **exactos** (154) |
| `Ranger` (1 fila) | **FUERA de la app** | Cayó en el test, el encoder no lo aprendió. La app deriva la lista del encoder, así que no se ofrece |

**Notas que evitan recirculaciones:**

- **Duplicados: 154 es el número correcto.** Los "302" de una auditoría previa eran las
  *filas implicadas* en duplicación (148 grupos): 302 − 148 = 154 sobrantes. No es una
  contradicción.
- **Kilometraje bajo: el dataset tiene 137 filas con ≤20 km de forma natural.**
  `mileage = 1` no es basura per se. Solo se imputaron las 7 filas con `mileage <= 2`
  (6 tras la deduplicación): 6930, 11129, 11173, 13531, 16906, 17193. La fila 3654
  (km = 4) se conservó intacta.

### 4.4 Datos verificados del dataset limpio

17.811 filas, `RangeIndex` 0-17810, 9 columnas, **0 nulos**. Base de todo lo que la app
ofrece (§6):

| Columna | Rango / valores reales |
|---|---|
| `year` | **1996 – 2020**: el slider ofrece los 25 años enteros del rango, pero el dataset solo tiene filas de **23** (faltan 1997 y 1999) |
| `mileage` | mínimo **4**, máximo **177.644**. **0 filas con 0 km** |
| `engineSize` | **15 valores distintos**: 1.0-1.8, 2.0, 2.2, 2.3, 2.5, 3.2, 5.0 (todos múltiplos de 0.1) |
| `mpg` | **90 valores distintos**, de 20.8 a 201.8 |
| `transmission` | Manual, Automatic, Semi-Auto |
| `fuelType` | Diesel, Petrol, Hybrid, Electric, Other |
| `model` | **23 en el CSV, 22 en la app** (Ranger queda fuera, §4.3) |

Frecuencias de los 22 que ofrece la app, en el orden en que los muestra el selector:
Fiesta 6.508 · Focus 4.556 · Kuga 2.208 · EcoSport 1.127 · C-MAX 542 · Ka+ 523 ·
Mondeo 512 · B-MAX 350 · S-MAX 294 · Grand C-MAX 247 · Galaxy 227 · Edge 205 · KA 197 ·
Puma 79 · Tourneo Custom 69 · Grand Tourneo Connect 57 · Mustang 57 ·
Tourneo Connect 32 · Fusion 16 · Streetka 2 · Escort 1 · Transit Tourneo 1.

---

## 5. El modelo

### 5.1 Pipeline

**Idéntico al original**, para que la app no necesite cambios de código:

```python
ColumnTransformer([
    ("numericas",  "passthrough",          ["year","mileage","tax","mpg","engineSize"]),
    ("categoricas", OneHotEncoder(handle_unknown="ignore"), ["model","transmission","fuelType"]),
])
RandomForestRegressor(max_depth=20, min_samples_split=15,
                      n_estimators=200, n_jobs=1, random_state=42)
```

> **No cambies los hiperparámetros sin permiso del usuario.** Se probó bajar
> `min_samples_split` a 3/5/10 y **empeora** R² (0,9378 → 0,9341) sin resolver el
> problema de precios iguales. 15 es el óptimo. Descartado además: añadir features o
> cambiar a kNN/Gradient Boosting — eso ya es cambiar el modelo.

### 5.2 Comparativa de referencia

Test de 4.452 filas, `random_state=42`, 25 % de split:

| escenario | R² | RMSE | MAE |
|---|---|---|---|
| A) modelo con bug / datos sucios (entrenado sobre todo el dataset, **optimista**) | 0,9512 | 1.053 | 723 |
| B) modelo con bug / datos limpios = **lo que hacía la app** | 0,8382 | 1.917 | 1.329 |
| C) **modelo nuevo / test limpio (honesto, holdout)** | **0,9378** | **1.189** | **829** |

A está contaminado (el modelo viejo se entrenó sobre esas mismas filas), así que la
comparación válida es **B → C: RMSE −38 %**.

> **Si en el futuro el R² del test limpio baja de ~0,93, algo se ha roto.**

---

## 6. Cómo funciona la app HOY

Todo lo de esta sección está en `prediccion_coche2.py` y **sí es vigente**.

### 6.1 Los widgets y sus rangos

| # | Widget | Tipo | Rango / opciones | Valor inicial |
|---|---|---|---|---|
| 1 | Modelo | `selectbox` | Los **22** del encoder ∩ CSV, por frecuencia | `Fiesta` |
| 2 | Transmisión | `selectbox` | Manual, Automatic, Semi-Auto | `Manual` |
| 3 | Combustible | `selectbox` | Diesel, Petrol, Hybrid, Electric, Other | `Diesel` |
| 4 | Año | `slider` | `ANIO_MIN`–`ANIO_MAX` = **1996–2020** | `ANIO_MAX` = **2020** |
| 5 | Kilometraje | `slider` | 0 – `KM_MAX` = **178.000**, step 1000 | mediana del grupo, con suelo de 1.000 |
| 6 | Impuesto | `slider` | 0 – 600, step 5 | **dinámico** (§6.3) |
| 7 | mpg | `selectbox` | Los **90** valores reales | **dinámico** = moda del grupo |
| 8 | Motor | `select_slider` | Las **15** cilindradas reales | **dinámico** = moda del grupo |

**Principio detrás de los widgets 4-8:** *la app no debe ofrecer ningún valor que el
modelo no haya visto nunca*. Antes se ofrecían rangos inventados que incluían valores
inexistentes: 5 años enteros sin ninguna fila (2021-2025), 122.000 km por encima del
máximo real, 41 de 56 posiciones de motor sin ningún coche, y un default de `mpg = 55`
que no aparece en **ninguna** fila. Todo eso está eliminado.

> **Lo único que queda fuera del principio:** el rango del `tax` (0-600 con step 5).
> Hay 35 valores reales de `tax`; el 0-600 no es el rango natural. No afecta a la
> predicción y está pendiente de decisión (§9.5).

### 6.2 La cadena de respaldo de los valores iniciales

`grupo_de_referencia(modelo, anio, trans, comb)` busca en el CSV limpio el primer grupo
**no vacío** de esta cadena:

| Nivel | Filtro | % de las 8.250 combinaciones¹ |
|---|---|---|
| **N1** | `(model, year, transmission, fuelType)` | 6,12 % (505) |
| **N2** | `(model, year, transmission)` | 16,61 % (1.370) |
| **N3** | `(model, transmission, fuelType)` | 15,77 % (1.301) |
| **N4** | `(model)` | 61,50 % (5.074) |
| **N5** | dataset completo | **0 % — nunca se usa** (es la red de seguridad) |

¹ 22 modelos × 25 años (1996-2020) × 3 transmisiones × 5 combustibles. Los 505 N1 cuadran
con las 505 celdas exactas no vacías de esos 22 modelos.

### 6.3 Criterio por widget

| Widget | Criterio sobre el grupo | Umbral | Suelo / fallback |
|---|---|---|---|
| **Motor** | **moda** de `engineSize` | el grupo solo tiene que ser no vacío | — |
| **Kilometraje** | **mediana** de `mileage`, redondeada a múltiplo de 1000 (el slider avanza en pasos de 1000; el 84 % de las medianas no son múltiplos, así que el redondeo es **obligatorio**) | grupo no vacío | `KM_MIN_INICIAL = 1000` (§6.4) |
| **mpg** | **moda** de `mpg` | grupo no vacío | — |
| **Impuesto** | **mediana ajustada al valor real más cercano**: se calcula la mediana del grupo y se elige el valor de `tax.unique()` más próximo a ella; en empate de distancia, el **menor** | **`n >= 3` filas** por nivel | **145.0** (valor de R2) si ningún nivel llega a 3 filas |

El criterio del `tax` garantiza que **`tax_inicial` es siempre un valor real** del grupo
elegido, nunca una mediana inventada que el modelo no haya visto.

### 6.4 El suelo de 1.000 km

```python
KM_MIN_INICIAL = 1000
mileage_inicial = max(KM_MIN_INICIAL, int(round(grupo["mileage"].median() / 1000) * 1000))
```

El dataset **no tiene ninguna fila con `mileage == 0`** (mínimo real 4 km), así que
arrancar en 0 era ofrecer un valor que el modelo nunca ha visto. Hay 425 filas por debajo
de 1.000 km, así que el suelo **no imposibilita ningún coche real**: solo evita el `0` sin
sentido que salía de las medianas de los coches casi nuevos de 2020.

> El suelo afecta **solo al valor inicial**. El slider sigue ofreciendo 0 km a mano.

### 6.5 La `key` dinámica es imprescindible

```python
combo = f"{model}|{year}|{transmision}|{combustible}"
mileage     = st.slider(..., key=f"mileage_{combo}")
tax         = st.slider(..., key=f"tax_{combo}")
mpg         = st.selectbox(..., key=f"mpg_{combo}")
engine_size = st.select_slider(..., key=f"motor_{combo}")
```

El parámetro `value=` de un widget **solo se aplica la primera vez** que Streamlit lo
dibuja. Sin `key` dinámica los widgets no se moverían al cambiar de modelo y el cambio
sería inútil. Con la clave derivada de la tupla, cuando esa tupla cambia Streamlit ve un
widget nuevo y lo inicializa al valor recién calculado.

**Consecuencia para el usuario:** si mueve un widget a mano, **su valor se conserva**
mientras no cambie la combinación `(modelo, año, transmisión, combustible)`. Al cambiar
de modelo, los cuatro se recalculan. Las claves viejas quedan inertes en `session_state`
(memoria despreciable, no se limpian).

### 6.6 La lista de modelos viene del encoder

```python
categorias_modelo = modelo.named_steps["preprocesamiento"] \
    .named_transformers_["categoricas"].categories_[0]
frecuencia = df["model"].value_counts()
modelos_disponibles = sorted(
    (m for m in categorias_modelo if m in frecuencia.index),
    key=lambda m: -frecuencia[m],
)
```

Es **deliberado** derivarla del encoder y no del CSV: garantiza que ningún modelo
propuesto caiga en el `handle_unknown='ignore'` y devuelva un precio sin señal de modelo.
Por eso `Ranger` (que sí está en el CSV) no se ofrece.

---

## 7. Qué ve el usuario

### 7.1 El precio y el rango orientativo

Debajo del `st.metric` con el precio hay dos captions:

```
Precio orientativo según las características indicadas.
📊 Rango orientativo: 14.686,91 € – 16.692,08 €
```

El rango es el **percentil 5 y el percentil 95 de las 200 predicciones individuales de los
árboles** del bosque. Sale de
`modelo.named_steps["random_forest"].estimators_`, previa una única llamada a
`modelo.named_steps["preprocesamiento"].transform(datos)`.

**Las cuatro reglas a respetar si se toca esto:**

1. **`modelo.predict()` sigue siendo el precio destacado.** El rango se calcula aparte y
   **no** sustituye a la predicción del ensemble por la media de los árboles.
2. **Se usan p5 y p95, nunca min/max.** El rango se ancla en el precio del ensemble, no
   en la media de los árboles.
3. **El rótulo es "Rango orientativo". NO es un intervalo de confianza** y no debe
   llamarse así.
4. **No sustituye a los avisos de §7.3.** Ambos conviven: §7.3 mide *soporte* (datos
   cercanos), el rango mide *dispersión* (desacuerdo entre árboles).

> **Limitaciones importantes — el rango NO mide el error predictivo:**
>
> - **No cubre el ruido aleatorio.** Los precios reales están mucho más dispersos de lo
>   que indican los percentiles. Medido: `[p5, p95]` contenía el precio real solo el
>   **71 %** de las veces, frente al 90 % que su nombre sugiere.
> - **Puede ser muy ancho y descentrado con poco soporte.** Con soporte 0 el bosque
>   entero se equivoca de rama a la vez.
> - **Se congela en extrapuración.** Comprobado con Fiesta 2015: a partir de ~90.000 km
>   la distribución de los 200 árboles es idéntica byte a byte (misma hoja). El rango
>   muestra entonces una confianza falsa y constante.
>
> Por todo esto **complementa a §7.3, nunca lo reemplaza**, y un rango estrecho **no**
> significa "fiable".

### 7.2 La tabla de coches cercanos

Encabezado: *"5 coches más cercanos al precio estimado (±10 %)"*.

Comportamiento exacto:

1. Se calculan las diferencias absolutas `|price − precio_estimado|`.
2. Se filtran las filas con `diferencia <= precio_estimado * 0.10`.
3. Se ordenan por `diferencia` ascendente con `kind="stable"`.
4. Se toman las **5 primeras**.
5. Si en la banda había menos de 5, se muestran las que haya (puede ser 0, 1, 2, 3 o 4)
   y sale un caption adicional: `"Solo N coches del dataset están dentro del ±10 % del
   precio estimado (X € - Y €)"`.

`kind="stable"` no cambia el criterio de orden, solo hace **determinista el desempate**:
a igual `diferencia` se mantiene el orden original de las filas del dataset, de modo que
la tabla no cambia entre ejecuciones ni entre reruns.

La banda es **multiplicativa y centrada en la predicción**, de `precio × 0.90` a
`precio × 1.10`. El caso de banda vacía está contemplado en el código y se verificó
**nunca** en los barridos (siempre 5 filas).

### 7.3 Los avisos de soporte de datos

**Son avisos informativos: no cambian la predicción, ni el modelo, ni el `.pkl`, ni los
hiperparámetros.**

#### Qué mide

> `soporte` = nº de coches del **mismo `model`** a distancia estandarizada **≤ 2
> desviaciones típicas** en `(year, mileage, mpg, engineSize)`.

Es decir un radio de **±4,05 años · ±38.831 km · ±20,3 mpg · ±0,85 L**.
`RADIO_SOPORTE = 4.0` porque es el radio **al cuadrado** (distancia euclídea en z-score).
Coste: ~1,7 ms por consulta (17.811 filas × 4 variables).

#### Por qué esas variables y no otras

| Variable | ¿Entra? | Motivo medido |
|---|---|---|
| `model` | **Sí, exacto** | Es la que más determina el precio. Sin ella la medida no significa nada |
| `year` | **Sí** | La de mayor peso: 1 año cuesta 0,49 unidades, 5× más que 1 mpg |
| `mileage` | **Sí** | El radio de 2 sd ≈ el rango km realista entre coches del mismo modelo y año |
| `mpg` | **Sí** | Hace de proxy continuo de motor + combustible: **excluirlo baja la detección del 100 % al 80 %** |
| `engineSize` | **Sí** | Ídem |
| `transmission` | **No** | Mantenerlo exacto es lo que produce la mayoría de los ceros |
| `fuelType` | **No** | Ídem; `mpg` y `engineSize` ya lo filtran de forma continua |
| `tax` | **No** | Aporta **0,00** de F1. Redundante con `year` + `fuelType` (el impuesto UK sale del CO₂) |

Soltar `transmission` y `fuelType` **no pierde información**: un Fiesta 2019 manual
diésel de 1.0 L es una referencia perfectamente válida para un Fiesta 2020 manual diésel
de 1.0 L. Un aviso que saltara ahí sería ruido.

La alternativa obvia — contar los coches con `(model, year, transmission, fuelType)`
exactos — **no sirve**: está vacía en la enorme mayoría de las combinaciones que la app
ofrece, así que el aviso saltaría en casi todo.

#### Los cuatro niveles y los mensajes literales

| Nivel | Condición | % de las 8.250 combinaciones¹ | Renderizado |
|---|---|---|---|
| 🔴 Sin soporte | `== 0` | **55,35 %** | `st.warning` compacto (una línea) |
| 🟠 Muy poco | `0 < soporte < 5` | 9,42 % | `st.warning` |
| 🟡 Limitado | `5 <= soporte < 30` | 8,93 % | `st.info` |
| ⚪ Sin aviso | `>= 30` | 26,30 % | nada, solo el caption original |

¹ 22 modelos × 25 años (1996-2020) × 3 transmisiones × 5 combustibles. Medido el
2026-10-03 sobre los valores iniciales que calcula la app. La mediana del soporte en las
8.250 combinaciones es **0**; el máximo, 5.494.

Mensajes literales que muestra la app:

```
🔴 Soporte de datos bajo: 0 coches similares encontrados en el dataset.

🟠 Solo {soporte} coche similar / coches similares en los datos de origen.
   El precio estimado es frágil.

🟡 Apoyado en solo {soporte} coches similares. Úsalo como orden de magnitud.
```

> **El mensaje 🔴 es nuevo (2026-10-03).** Antes era un párrafo largo de tres líneas que
> repetía el radio de búsqueda; ahora es una línea compacta. **El cambio es intencionado
> y no debe revertirse.** Los otros dos mensajes no han cambiado.
>
> Detalle técnico: el literal del código empieza por `⚠️ `, pero Streamlit ya antepone su
> propio icono a `st.warning`, así que el emoji del texto es redundante. Medido con
> `AppTest`, el valor del elemento es `"Soporte de datos bajo: 0 coches similares
> encontrados en el dataset."` (sin el emoji). Sin revisar en navegador.

**El corte que importa es 30, no 5.** Con umbral 5 se detectaba el 86,7 % de los casos
problemáticos; con 30, el **100 %**, y **sin introducir ni un solo falso positivo** en las
combinaciones de control con ≥30 coches en su celda exacta.

#### Qué se ve al abrir la app

Con los valores por defecto de §1.4 (`2020 · Manual · Diesel`): de los 22 modelos,
**5 en rojo** (KA, Transit Tourneo, Fusion, Streetka, Escort), **0 en naranja**,
**2 en amarillo** (Tourneo Connect 15, B-MAX 27) y **15 sin aviso**.

#### Qué revela el aviso sobre la calidad de la predicción

Comparando la predicción con la media de los 30 coches más cercanos del mismo modelo:

| Soporte | Desviación mediana | Error > 50 % |
|---|---|---|
| **0** | **65,2 %** | 63,4 % |
| 1-4 | 40,9 % | 31,5 % |
| 5-29 | 36,2 % | 10,3 % |
| **≥ 30** | **6,6 %** | **2,1 %** |

Gradiente de **10×** entre soporte 0 y soporte ≥30.

> **Advertencia metodológica importante:** el mismo test ejecutado sobre las **17.811
> filas reales** del dataset **NO** muestra relación entre soporte y error (MAE 680-883 €
> en todos los tramos). No es contradictorio: una fila real siempre tiene vecinos por
> construcción, así que ese test **no puede medir extrapolación**. Solo la consulta
> sintética que puede construir el usuario la revela. Ambas cosas son ciertas: **el
> modelo es fiable dentro de la nube de datos y no lo es fuera**. Y la circularidad es
> parcial: cuando el soporte es 0, la propia referencia (los 30 más cercanos) está lejos.

#### Coste de diseño asumido

El aviso saldría en más de la mitad de las combinaciones que ofrece la app. Y es correcto:
el dataset tiene huecos reales (faltan 1997 y 1999, y muchas combinaciones
modelo+año+transmisión+combustible están vacías). Un aviso que saltara el 20 % de las
veces estaría mintiendo. La solución de fondo fue derivar los widgets de los datos (§8.5).

---

## 8. Mejoras implementadas

Todas son cambios **solo de la app**. Ninguna tocó el modelo, el `.pkl`, los
hiperparámetros ni los datasets.

| # | Cambio | Qué hace | Validado | Commit |
|---|---|---|---|---|
| 1 | **CSV limpio + lista de modelos del encoder** | La app lee el CSV limpio y ofrece los 22 modelos del encoder en vez de una lista fija de 9 | Sí | `9143a5a` |
| 2 | **C** — Valores iniciales dinámicos | Kilometraje, mpg y motor se derivan del grupo de referencia (§6) | Sí | `d918107` |
| 3 | **D** — Aviso de soporte de datos | 4 niveles por radio en distancia estandarizada (§7.3) | Sí | `d918107` |
| 4 | **X** — Tabla de cercanos acotada | Máx. 5 coches dentro del ±10 % del precio, con desempate estable (§7.2) | Sí | `d918107` |
| 5 | **E** — Rango orientativo p5-p95 | Percentiles 5 y 95 de los 200 árboles, en un caption (§7.1) | Sí | `fa66a19` |
| 6 | **B** — Rangos de los widgets desde los datos | Año, kilometraje, motor y mpg derivan su rango de los valores reales (§6.1) | Sí | `c119671` |
| 7 | **TAX dinámico** | Valor inicial del impuesto por grupo N1-N4, mediana ajustada (§6.3) | Sí | `31adbea` |
| 8 | **Aviso 🔴 compacto** | Mensaje de soporte 0 en una línea (§7.3) | Sí | `a4610ee` |

### 8.1-8.4 — Cómo implementaron C, D, X y E

Están descritos donde corresponden: **C** en §6.2-§6.5, **D** en §7.3, **X** en §7.2,
**E** en §7.1. No se repiten aquí.

### 8.5 — B: los rangos de los widgets derivados del dataset

Cierra dos tareas que estaban abiertas: la opción B (rangos fantasma) y el caso de los
**0 km** como valor inicial.

| Widget | Antes | Después | Rango fantasma eliminado |
|---|---|---|---|
| Año | `slider(1990, 2025)` | `slider(1996, 2020)` | **5 años enteros** (2021-2025 con 0 filas) y 6 más al inicio |
| Kilometraje | `slider(0, 300000, step 1000)` | `slider(0, 178000, step 1000)` | 122.000 km por encima del máximo real (177.644) |
| Motor | `slider(0.5, 6.0, step 0.1)` = 56 posiciones | `select_slider` con las **15** cilindradas reales | **41 de 56 posiciones** no existen (1.9, 2.1, 4.0, 5.5…) |
| mpg | `slider(0, 250, step 1)`, default **55** | `selectbox` con los **90** valores reales | el propio default era fantasma: **`mpg == 55` son 0 filas** |
| Tax | `slider(0, 600)`, default 150 | rango igual, default **dinámico** (§8.6) | el 150 sí existe en el dataset |

**El `mpg` pasó a ser dinámico** (decisión del usuario). En una primera versión de este
cambio se dejó fijo en la moda global del dataset (65,7); el usuario pidió hacerlo
dinámico igual que el motor.

**Por qué importa:** el `mpg` es el proxy continuo que usa el aviso de soporte (§7.3).
Un default de 65,7 para un eléctrico o un V8 degradaba ese aviso. Efecto medido:

| Escenario | mpg antes (fijo) | mpg ahora | Aviso de soporte |
|---|---|---|---|
| Fiesta 2020 Manual Diesel | 65,7 | 58,9 | sin aviso → sin aviso |
| Mustang 2020 Manual Petrol | 65,7 | 22,8 | 🟠 → **sin aviso** |
| Mondeo 2018 Manual Diesel | 65,7 | 47,1 | sin aviso → sin aviso |
| Tourneo Custom 2020 Manual Diesel | 65,7 | 44,8 | 🟠 → **sin aviso** |
| B-MAX 1996 Manual Petrol | 65,7 | 74,4 | 🔴 → 🟠 (sigue avisando) |

Los valores por defecto dejaron de ser inventados **y** el aviso mide mejor, porque por fin
se parece al coche que el usuario está describiendo.

### 8.6 — Tax dinámico

Valor inicial del impuesto con la misma cadena de respaldo N1→N2→N3→N4 de §6.2, con
**umbral mínimo de 3 filas por nivel**, **mediana ajustada al valor real de `tax` más
cercano** (en empate de distancia, el menor) y **fallback global 145.0**. Detalle del
criterio en §6.3.

Casos verificados: `Fiesta 2020 Manual Diesel` → **145** (N1 vacío, N2 con 78 filas) ·
`Fiesta 2016 Manual Diesel` → **0** (N1 con 94) · `Mondeo 2016 Automatic Electric` →
**125** (N1 con 2 filas < 3, así que **no usa las 2 filas de N1**; usa N2 con 23) ·
`B-MAX 1996 Manual Diesel` → **20** (N3).

---

## 9. Problemas conocidos y límites vivos

### 9.1 Precios iguales = falta de soporte, no es el modelo

**Síntoma (histórico):** con una configuración que **no existe en el dataset** (0 filas),
varios modelos devolvían exactamente el mismo precio.

**Causa:** con soporte cero el árbol no tiene datos en ese nodo y no llega a dividir por
modelo, así que devuelve el promedio del grupo más parecido.

**Diagnóstico (recorriendo los 200 árboles):**

| Métrica | Valor |
|---|---|
| Profundidad media de la hoja alcanzada | **9-10** (de un máximo de 20) |
| Árboles que llegan a profundidad 20 | **0 de 200** |
| Nº de filas de entrenamiento en esa hoja | **mediana 6, máximo 14** |

Consecuencias:

1. **`max_depth=20` NO es el culpable.** El nodo para porque tiene **menos de 15 filas**,
   es decir por `min_samples_split=15`. Por eso bajar ese hiperparámetro no lo arregla:
   aunque bajara, el nodo tiene 1-14 filas y **ninguna es de esos modelos**.
2. **Los modelos colapsados recorrían literalmente los mismos nodos en los 200 árboles.**
   El árbol nunca corta por `modelo` en esa rama, así que el bit one-hot del modelo es
   irrelevante para el recorrido. Misma hoja → misma media → mismo número.
3. Solo había **8 precios distintos entre 22 modelos**.

**Veredicto: es el comportamiento matemáticamente correcto, no un bug ni una regresión.**

**Impacto de las mejoras: el síntoma está resuelto.** Con los valores iniciales dinámicos
(C), la configuración real de la app da **22 precios distintos de 22 modelos**, cuando
antes eran 8 con 15 colapsados. Barrido de las **94 configuraciones** (año × transmisión ×
combustible con datos): **0 colapsos**.

> **Si el usuario se queja de precios iguales:** explícale que solo ocurre con
> combinaciones imposibles, y **no cambies los hyperparameters por tu cuenta**. El aviso
> de §7.3 es lo que avisa de ello en la interfaz.

### 9.2 Limitaciones de la lógica de valores iniciales

1. **La celda por defecto (`2020 · Manual · Diesel`) solo tiene 23 filas en 5 de los 22
   modelos.** Para los otros 17, la cadena arranca en N2/N3/N4 y el default es una
   aproximación. Es una propiedad del dataset (el UK casi no tiene diésel manual de 2020),
   no un defecto de la app.
2. **N2 ignora el combustible**, así que un Diésel manual puede arrancar con datos de
   gasolina (es el caso de `Fiesta | 2020 | Manual | Diesel`, que cae en las filas de
   `Fiesta 2020 Manual **Petrol**`). Es comportamiento buscado: es preferible un modelo
   adyacente a un "0 filas" que un `IndexError`.
3. **El rango del `tax` sigue siendo 0-600 con step 5**, cuando el conjunto real de
   valores de `tax` tiene 35 elementos. Es el patrón de "rango fantasma" que ya se
   corrigió en año, kilometraje, mpg y motor. **No afecta a la predicción.**

### 9.3 La E original nunca se implementó

La opción E de la lista de opciones (§10.3) pedía un rango **mín/mediana/máx de los coches
cercanos**. Lo que se implementó (§7.1) usa las **predicciones de los árboles**, que es
otra fuente: el usuario lo pidió así tras la investigación. **El enfoque original sigue
sin hacer, y es compatible**: se podrían mostrar ambos.

### 9.4 Opción G: nunca aplicada, requiere permiso

"No llamar al modelo si el soporte es 0 y usar la mediana de los k más cercanos". Está en
la lista de opciones del usuario como una de las queelled. **Necesita permiso explícito**
para implementarse.

### 9.5 Otros puntos menores

- **`Ranger` no se puede consultar** en la app (el encoder no lo aprendió). Está en el
  CSV con 1 fila. Si algún día se quiere ofrecer, hay que reentrenar (§4.3).
- **La lista de claves viejas de `session_state` no se limpia.** Memoria despreciable.
- 🗣️ **Pregunta abierta de §2.3** sobre delegación vs proporcionalidad.

---

## 10. Historial

> Todo lo de esta sección es **cronológico**. Describe cómo se estaba el proyecto y por
> qué se tomaron las decisiones. **No son reglas vigentes ni el estado actual** (que está
> en §1-§9).

### 10.1 Cronología de commits

| Commit | Qué llevó |
|---|---|
| `a4610ee` | **Aviso 🔴 compacto** (§7.3) + **reorganización de este `AGENTS.md`** (§10 y §11 como historial). Es el HEAD actual |
| `31adbea` | **Tax dinámico** (§8.6) + documentación |
| `c119671` | **Opción B**: rangos de los widgets derivados del dataset + `mpg` dinámico + suelo `KM_MIN_INICIAL` (§8.5) + documentación |
| `fa66a19` | **Opción E**: rango orientativo p5-p95 (§7.1) |
| `d918107` | **C** (defaults dinámicos), **D** (aviso de soporte), **X** (tabla ±10 %) + `mejorar_pred.md` |
| `0528228` | `chore: ignore Modulo12` (repositorio independiente) |
| `e14039d` | Estado de Git en `AGENTS.md`: Modulo10 ya versionado por el usuario |
| `b260e6d` | Estado de Git tras el commit `9143a5a` |
| `9143a5a` | *"Corrige el bug que hacía que todos los coches valieran 18.032,07 €"*. Se versionaron los 18 ficheros de `Modulo11/` (código, este `AGENTS.md`, notebooks, CSV original y limpio, tema de Streamlit) y se creó `Modulo11/.gitignore` (§3.4) |

**5 de estos commits están sin pushear** a `origin/main` (los 5 primeros de la tabla).

Copia de seguridad `_antes_F.py` (el fichero de la app antes de la opción B): se borró,
nunca estuvo versionada y la versión anterior está en `fa66a19`. `git log --oneline` es
la fuente de verdad para los hashes.

### 10.2 Opciones que se evaluaron (todo cerrado salvo G)

| # | Opción | Estado |
|---|---|---|
| **A** | Aviso de soporte contando las filas que casan con la combinación | **Absorbida por D**, que es la versión robusta |
| **B** | Rangos de los widgets derivados de los datos | **HECHA** (§8.5) |
| **C** | Valores iniciales dependientes de la combinación | **HECHA** (§6.2-§6.5) |
| **D** | Aviso de soporte por radio en distancia estandarizada | **HECHA** (§7.3) |
| **E** | Rango mín/mediana/máx de los coches cercanos | **HECHA en otra forma**: el rango de los 200 árboles (§7.1). La versión original sigue pendiente (§9.3) |
| **F** | Cambiar solo los defaults (paliativo) | **Superada por C** |
| **G** | No llamar al modelo si el soporte es 0 y usar la mediana de los k más cercanos | **Necesita permiso explícito** (§9.4) |

**Descartado:** tocar hiperparámetros (ya demostrado contraproducente), añadir features,
cambiar a kNN o Gradient Boosting. Eso ya es cambiar el modelo, que es justo lo que está
descartado.

El **cambio X** no figura en esta tabla porque nunca fue una de las opciones A-G: fue una
petición posterior del usuario para acotar la tabla de coches cercanos a una banda de
±10 %.

### 10.3 Cómo estaba la app antes de la opción B

Todas estas cifras están medidas sobre una configuración que **la app ya no ofrece**
(`2020 · Manual · Petrol · 45.000 km · 2.0 L · mpg 55`). Se conservan porque explican por
qué se hicieron los cambios de §8.5.

**Rangos fantasma que existían:**

- El slider de año iba de 1990 a 2025, pero **2021-2025 no tienen ninguna fila** (y el
  dataset empieza en 1996).
- El de kilometraje llegaba a 300.000 km con máximo real de 177.644.
- El de motor ofrecía 56 posiciones, 41 de ellas sin ningún coche.
- El `mpg` tenía default **55**, y `mpg == 55` son **0 filas** en el dataset.

**Consecuencia medida:** con esos defaults, **14 de 22 modelos devolvían exactamente el
mismo precio** (18.297,57 € ×15, Focus 18.733,40, Kuga 18.016,46, Mondeo 18.070,62, Edge
21.811,26, S-MAX 24.558,88, Galaxy 25.065,05, Mustang 27.663,41).

**Por qué:** la combinación `(2020, Manual, Petrol)` + 45.000 km + 2.0 L **no existe en el
dataset — 0 filas**. Con tolerancia amplia (±0,6 L y ±5.000 km) tampoco. En
`(2020, Manual, Petrol)` el kilometraje iba de 5 a 8.786 km con mediana 641: el default
estaba **5,1× por encima del máximo**. Los 25 coches de 2.0 L de 2020 son todos Diésel o
Hybrid. El último año con datos de 2.0 L Manual Petrol fue **2018**.

**Lo que se probó y NO funcionó:** un combo "realista" (2019, 30.000 km, 1.4 L) solo subió
a 13/23 precios distintos y además metía a Mustang en 15.103 € cuando su mediana real es
33.979 €, o sea, empeoraba. Por eso el problema se atacó en la app (valores por defecto y
rangos) y no en el modelo.

**Avisos de soporte, antes de la opción B** (medidos sobre 11.880 combinaciones de 22
modelos × **36** años): 🔴 65,8 % · 🟠 6,9 % · 🟡 7,2 % · ⚪ 20,1 %, y **9 modelos con
aviso, 7 de ellos en rojo**. El nivel 🔴 bajó al **55,35 %** (§7.3) al derivar los widgets
de los datos reales y hacer el `mpg` dinámico. La cifra antigua no es reproducible con la
configuración actual.

**Escenarios de validación ya inalcanzables:** se validaron en su día `Escort 1990`,
`Fiesta 2024` y `S-MAX 2025`. Con el rango de años 1996-2020 **la interfaz ya no puede
llegar a esas filas**.

**Lección de entonces:** con soporte cero un árbol solo puede devolver el promedio del
grupo más parecido. Lo que sí eran defectos reales eran de la **app**, no del modelo:
ofrecía por defecto una combinación fuera de su propio dataset y mostraba un precio con
dos decimales para una consulta con 0 filas de apoyo. Eso es lo que corrigieron C y B.

### 10.4 Estado de Git del 2026-10-02 (superado)

Contexto de la sesión en que se commitearon C, D y X:

| Dato | Valor |
|---|---|
| HEAD | `0528228` |
| Sin commitear | `AGENTS.md`, `prediccion_coche2.py`, `mejorar_pred.md` |
| Después | El usuario commiteó `Modulo10/`, `.agents/` y `.claude/` por su cuenta en `a0881d1` |

Ese commit desde la raíz arrastró `Modulo10/__pycache__/*.pyc` porque el `.gitignore` de
la raíz no cubría `__pycache__`. Ver el estado actual de ese fichero en §3.4.

---

## 11. Cómo continuar

```bash
cd /home/miguel/mi_entorno/Python/Modulo11
source .venv/bin/activate
streamlit run prediccion_coche2.py
```

**Checklist de arranque de una sesión nueva:**

1. Leer **§1** (estado actual) y **§2** (reglas).
2. `git log --oneline -3` y `git status`: confirmar HEAD y si hay cambios sin commitear.
3. `md5sum modelo_coches.pkl`: debe ser `72441976dd0ba4ba2f95acc3c3bee3f9`. Si no, se
   cambió el modelo sin documentarlo.
4. Para una tarea de datos, delegar en `data-analyst` (§2.1) y decidir cuánto análisis
   hace falta (§2.2).
5. Antes de tocar la app, mirar §6 (cómo funciona) y §7 (qué ve el usuario): lo que
   cambio ya está resuelto, no lo rehagas.

**Estado de las opciones A-G:** todas cerradas salvo **G**, que necesita permiso
explicito (§9.4). **Los puntos realmente abiertos** son:

- El **rango del `tax`** (0-600, 35 valores reales) — §9.2.3.
- La **pregunta de delegación vs proporcionalidad** — §2.3.
- La **E original** (rango de los coches cercanos) — §9.3.
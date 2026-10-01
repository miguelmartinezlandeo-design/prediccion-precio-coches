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
| `mejorar_pred.md` | Peticiones originales de mejora de la UI + la regla de delegación. |
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

La UI (precio destacado, tabla "Datos del coche", 10 coches más cercanos) **no se
toca** salvo que el usuario lo pida.

---

## 9. Problema abierto: precios idénticos con los sliders por defecto

**Residuo del bug, NO resuelto, y no es cosa del modelo.**

Con los valores por defecto de la app (2020, 45.000 km, 2.0L, Manual, Petrol)
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
combinaciones imposibles, y **no cambies los hyperparameters por su cuenta**.

---

## 10. Reglas de trabajo para futuras sesiones

1. **No repitas la auditoría.** Los hallazgos están en las secciones 4 a 7.
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

---

## 11. Pendiente conocido: higiene de Git

- La raíz del repo es `/home/miguel/mi_entorno/Python` y **la carpeta `Modulo11/`
  entera está sin trackear** (`git status` → `?? ./`).
- **No hay `.gitignore` en ninguna de las dos carpetas.** Si se hace `git add`,
  los `.pkl` (33 MB y 35 MB) y los `.ipynb` (hasta 1,5 MB) entran al repo.
  Crea un `.gitignore` con al menos:
  ```
  .venv/
  __pycache__/
  *.pkl
  ```
  y decide con el usuario si los backups se versionan.

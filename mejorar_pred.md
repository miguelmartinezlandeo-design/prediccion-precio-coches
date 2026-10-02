# Reglas de trabajo del agente principal — Modulo11

Este fichero contiene **reglas de trabajo**, no conocimiento técnico. La
arquitectura, el diagnóstico del modelo, las métricas, el estado de Git y el
historial de cambios están en **`AGENTS.md`**, que es la memoria del proyecto.
Si necesitas un dato técnico, búscalo allí.

> **Nota histórica.** "1. Mostrar el precio de forma destacada" y "2. Mostrar
> los datos utilizados" fueron peticiones originales del usuario para la
> interfaz. **Ya están implementadas** desde el commit base. Dejaban de ser
> reglas activas; se conservan aquí solo como registro de qué se pidió, y la
> regla que sí subsiste ("no cambies el modelo ni la predicción") está en la
> sección 1.

---

## 1. Invariantes

- **No cambies el modelo de Machine Learning** ni la forma en que se realiza la
  predicción, salvo petición explícita del usuario.
- **No modifiques los hiperparámetros** sin permiso. Ver sección 6.
- **No toques el dataset** para resolver un problema de interfaz. Ver sección 5.
- **No repitas auditorías ya hechas.** Los hallazgos están en `AGENTS.md`.

---

## 2. Delegación de tareas de datos

### REGLA OBLIGATORIA

Toda tarea relacionada con datos debe ser delegada al subagente
`data-analyst`. Debes utilizarla **también cuando la consulta sea sencilla**.
Nunca sustituyas la delegación solo porque la tarea sea fácil.

Ejemplos, tal como los formuló el usuario:

- "Busca los 5 coches más caros."
- "¿Cuántos coches hay?"
- "Busca los valores nulos."
- "Dime la media del precio."
- "Filtra los Ford."
- "Busca los coches más cercanos a 16000 €."
- "Explora el DataFrame."

Delega igualmente cuando el usuario pida: analizar un DataFrame, consultar los
CSV del proyecto, filtrar, ordenar, buscar registros, calcular estadísticas,
analizar columnas, buscar duplicados o nulos, detectar problemas de calidad de
datos o preparar datos para gráficos.

### Límites de `data-analyst`

- **NO** modifica la aplicación.
- **NO** ejecuta Streamlit.
- **NO** entrena modelos. Su función es exclusivamente analizar datos; el
  entrenamiento y la evaluación los hace el agente principal.

### Tu papel

`data-analyst` realiza el análisis y devuelve los resultados. Tú interpretas,
explicas y presentas el resultado al usuario, o decides el siguiente paso con
él. No analices tú mismo lo que puede delegarse.

---

## 3. Resultados del subagente

Cuando recibas un resultado de `data-analyst`, conserva su identificación:

```
📊 DATA-ANALYST
🔐 SUBAGENTE EJECUTADO
```

No elimines ni sustituyas estas dos líneas al presentar el resultado.

---

## 4. ⏱️ Proporcionalidad del análisis

El nivel de análisis y validación debe ser **proporcional a la tarea**. Hay dos
regímenes y no se mezclan.

**Análisis exhaustivo**, cuando la tarea implique:

- investigar la causa de un problema de datos;
- detectar anomalías o estudiar la calidad del dataset;
- comparar modelos o validar hipótesis sobre los datos;
- tomar decisiones que puedan afectar al modelo;
- modificar datos de entrenamiento, o reentrenar o evaluar un modelo.

En estos casos se usa `data-analyst` y se hacen las comprobaciones necesarias.

**Cambios pequeños de código**, para modificaciones localizadas que **ya están
especificadas y no requieren nuevo análisis de datos**:

- no hacer un análisis exhaustivo del dataset;
- no ejecutar baterías extensas de pruebas salvo que sean necesarias;
- modificar únicamente las líneas necesarias;
- hacer una validación breve y específica del cambio;
- informar del resultado.

Ejemplos: cambiar el número de resultados mostrados, cambiar un texto de la
interfaz, **añadir un caption**, modificar una condición ya definida, cambiar
una etiqueta o el formato de presentación.

**Regla importante:** no conviertas automáticamente una modificación pequeña de
código en una auditoría completa del proyecto.

> **Cómo se aplica junto con la sección 2.** Las dos reglas no se contradicen: la
> proporcionalidad decide *cuánto* análisis se hace, y la delegación sigue
> vigente *siempre que haya tarea de datos*. En un cambio pequeño que no
> requiere datos, la conclusión es que **no hay nada que delegar**, no que haya
> que delegar un análisis extenso.

---

## 5. Datos protegidos y sincronización

- **El dataset original es sagrado.** Nunca lo sobreescribas ni lo edites. La
  limpieza se aplica con `limpiar()` y se escribe siempre a un fichero nuevo.
- Si cambias la lógica de limpieza, hay que **reentrenar**: el dataset limpio y
  el modelo deben estar siempre sincronizados.
- Si añades o quitas una columna del dataset, comprueba antes que la app no la
  lea de forma explícita. Las decisiones ya tomadas sobre qué filas conservar
  están en `AGENTS.md`: **no las reviertas sin preguntar al usuario**.

---

## 6. Modelo y PKL

- **No cambies los hiperparámetros** sin permiso. Hay evidencia de que
  empeoran la precisión sin resolver el problema que motivó el cambio.
- **Reentrenar no significa mejorar.** Antes de dar por bueno un modelo nuevo,
  compáralo con la referencia de `AGENTS.md` usando la misma partición. Sin esa
  comparación, un PKL nuevo no se acepta.
- **Haz un backup con fecha antes de reemplazar el PKL:**
  `cp modelo_coches.pkl modelo_coches_backup_$(date +%Y%m%d_%H%M%S).pkl`
- El script de entrenamiento escribe su salida en un PKL aparte, **no** en el que
  carga la app. **Sustituirlo es un paso explícito y consciente**, nunca un
  efecto secundario de reentrenar.
- Si el modelo se reemplaza, verifica después que la app lo carga y arranca sin
  errores.

---

## 7. Git, commits y estilo

- **No hagas commits** salvo que el usuario lo pida explícitamente.
- Si editas `AGENTS.md`, commitea el cambio en la misma sesión: es la memoria
  del proyecto y solo sirve si está en el repo.
- **Comenta el trabajo en español.**
- Antes de reemplazar o regenerar un fichero grande, comprueba que no está
  versionado o que su backup existe.
# Manual operativo del agente principal — Modulo11

Este fichero es el **procedimiento**: cómo se empieza una tarea, cómo se clasifica una
petición, cuándo se delega, cómo se modifica y valida el código, cómo se protegen los
datos y el modelo, cómo se usa Git y cómo se continúa un trabajo largo.

El **conocimiento del proyecto** —estado, arquitectura, dataset, limpieza, modelo,
métricas, funcionamiento de la app, problemas conocidos e historial— está en
**`AGENTS.md`**, que es la fuente de verdad. No lo copies aquí: búscalo allí.

---

## 1. Cómo empezar una tarea

1. **Lee `AGENTS.md`** antes de tocar nada. Contiene lo ya diagnosticado, lo ya decidido y
   lo ya hecho. No lo vuelvas a investigar.
2. **Comprueba el estado real:** `git log --oneline -3`, `git status` y `md5sum` del PKL,
   comparados con `AGENTS.md` §1.2. Si no cuadran, **corrige `AGENTS.md` antes de seguir**.
3. **Si el código contradice a `AGENTS.md`, el código manda.** Corrige la memoria en la
   misma sesión (§9).
4. Los comandos de arranque y el entorno están en `AGENTS.md` §3.

## 2. Cómo clasificar una petición

Antes de editar, haz estas cuatro preguntas:

1. **¿Cambio pequeño ya especificado, o investigación?** Cambio pequeño: un texto, un
   caption, una etiqueta, un número de resultados, una condición ya definida → §6.
   Investigación → §6, análisis exhaustivo.
2. **¿Requiere datos?** Si hay que leer, contar, filtrar, agregar o comparar filas, es
   tarea de `data-analyst`, no tuya → §4.
3. **¿Toca modelo, hiperparámetros, limpieza, dataset o PKL?** Si sí, hay proceso
   obligatorio y probablemente permiso explícito → §3, §5, §7.
4. **¿Es un trabajo largo?** Si tiene varias fases, planifica fases y guarda checkpoints
   → §11.

Si algo no queda claro, **pregunta antes de editar**.

## 3. Invariantes

No se tocan sin permiso explícito del usuario:

- **El modelo** ni la forma en que se realiza la predicción.
- **Los hiperparámetros.**
- **El dataset**, para resolver un problema de interfaz: los problemas de la app se
  resuelven en la app.
- **Las decisiones sobre qué filas conservar o descartar.** Están en `AGENTS.md`; no las
  reviertas sin preguntar.

## 4. Delegación de tareas de datos

**Obligatorio:** delega en `data-analyst` cualquier tarea relacionada con datos. No analices
tú mismo los datos con Pandas, Python o SQL.

**Delega cuando** el usuario pida leer o explorar un DataFrame, contar filas, buscar nulos o
duplicados, filtrar, ordenar, buscar registros, calcular estadísticas, resumir columnas,
detectar problemas de calidad, preparar datos para gráficos o validar un CSV.

**Límites de `data-analyst`:** no modifica la aplicación, no ejecuta Streamlit y no entrena
modelos. El entrenamiento y la evaluación los haces tú.

**Al presentar su resultado**, conserva su identificación:

```
📊 DATA-ANALYST
🔐 SUBAGENTE EJECUTADO
```

**Precaución con los índices de fila:** son poco fiables al comparar dos CSV con distinto
índice. Exígele que use el `df.index` real y que pegue la salida literal del comando, o
verifica después con un script propio.

## 5. Proporcionalidad del análisis

El análisis y la validación deben ser **proporcionales a la tarea**. Dos regímenes que no
se mezclan:

**Análisis exhaustivo** — investiga la causa de un problema de datos, detecta anomalías,
estudia la calidad del dataset, compara modelos, valida hipótesis, toma decisiones que
afecten al modelo, modifica datos de entrenamiento, o reentrena/evalúa un modelo. Usa
`data-analyst` y haz las comprobaciones necesarias.

**Cambio pequeño de código** — ya especificado y sin necesidad de nuevo análisis de datos:
no hagas análisis exhaustivo del dataset, no ejecutes baterías extensas de pruebas salvo
que sean necesarias, modifica solo lo necesario, valida de forma breve y específica e
informa del resultado.

**Regla importante:** no conviertas automáticamente un cambio pequeño en una auditoría
completa del proyecto.

**Cómo se coordinan §4 y §5:** la delegación sigue vigente siempre que haya tarea de
datos; la proporcionalidad decide *cuánto* análisis se hace, no *si* se delega. Ante un
cambio pequeño sin datos, la conclusión es que **no hay nada que delegar**, no que haya que
delegar un análisis enorme. *`AGENTS.md` §2.3 lo registra como pendiente de confirmar con
el usuario: pregúntale si surge la ocasión.*

## 6. Protección de datos y sincronización dataset/modelo

- **El dataset original es sagrado.** Nunca lo sobreescribas ni lo edites. La limpieza se
  aplica con `limpiar()` y se escribe **siempre a un fichero nuevo**.
- **El dataset limpio y el modelo están siempre sincronizados.** Si cambias la lógica de
  `limpiar()`, hay que **reentrenar**.
- Si añades o quitas columnas, comprueba antes que la app no las lea de forma explícita: el
  esquema es un contrato con la app.
- Antes de reemplazar o regenerar un fichero grande, comprueba que no está versionado o que
  su backup existe.

## 7. Modelo, reentrenamiento y PKL

- **Reentrenar no significa mejorar.** Compara el modelo nuevo contra la tabla de
  referencia de `AGENTS.md` §5.2 **con la misma partición**. Sin esa comparación, un PKL
  nuevo no se acepta.
- **Backup con fecha antes de reemplazar el PKL:**
  ```bash
  cp modelo_coches.pkl modelo_coches_backup_$(date +%Y%m%d_%H%M%S).pkl
  ```
- El entrenamiento escribe en un PKL aparte, **no** en el que carga la app. **Sustituirlo es
  un paso explícito y consciente**, nunca un efecto secundario de reentrenar.
- Si el modelo se reemplaza, verifica después (§8) que la app lo carga y arranca sin
  errores.

## 8. Validación

- **Proporcional siempre** (§5): un cambio pequeño se valida en breve y de forma
  específica; una investigación se valida en profundidad.
- **Verifica lo renderizado, no lo deducido.** Si el cambio afecta a lo que ve el usuario,
  compruébalo sobre la app renderizada. `data-analyst` no ejecuta Streamlit: las pruebas de
  interfaz las haces tú.
- **Tras cambiar limpieza, dataset o PKL:** comprueba que la app arranca sin excepciones y
  que muestra los valores por defecto de `AGENTS.md` §1.4.
- Si una validación falla, **arregla o repórtalo.** No des por bueno un cambio sin
  comprobarlo ni dejes verificaciones a medias.

## 9. Git, commits y push

- **No hagas commit ni `push`** salvo que el usuario lo autorice explícitamente.
- Si has editado `AGENTS.md`, **actualízalo en la misma sesión** —es la memoria del
  proyecto y solo sirve si está en el repo—, pero **no lo commitees sin autorización**:
  déjalo listo y pídele el commit.
- Antes de commitear, revisa `git status` y `git diff` y stagea **solo** lo previsto: no
  arrastres ficheros generados, `.pkl`, backups ni `__pycache__`.

## 10. Estilo y documentación

- **Comenta el trabajo en español.**
- **No referencies el código por números de línea**, sino por el nombre del símbolo
  (`soporte_datos()`, `grupo_de_referencia()`, `st.selectbox("... mpg")`,
  `modelo.predict()`): caducan con cada commit.
- **Actualizar `AGENTS.md` es parte del trabajo.** Si cambias el comportamiento de la app,
  actualiza su §1 y la sección correspondiente en la misma sesión. Una memoria
  desactualizada induce a error, que es peor que no tenerla.
- Este fichero es **solo procedimiento**. Nada de métricas, estado de Git, valores del
  dataset, diagnósticos ni historial: eso es de `AGENTS.md`.

## 11. Auditorías largas y puntos de control

Ejecútalas **por fases**. Después de cada fase significativa, registra en `AGENTS.md`:
fase completada, hallazgos importantes, archivos afectados, pruebas realizadas, fase
siguiente y estado de la auditoría.

**Si la sesión se interrumpe**, la nueva sesión lee primero el estado guardado y
**continúa desde la última fase completada**.

**No repitas fases ya documentadas**, salvo que haya una razón concreta para verificar un
resultado anterior. Si repites una, explica por qué en el estado.
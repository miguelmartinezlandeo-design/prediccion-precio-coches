import os
import pandas as pd
import numpy as np


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia el DataFrame de coches usados siguiendo las reglas R1..R6 en orden estricto.
    
    Reglas (orden importa):
    R1. df["model"] = df["model"].str.strip()
    R2. df["tax"] = df["tax"].fillna(145.0)
    R3. Imputar df["engineSize"] == 0 con moda de engineSize del MISMO model (sin espacios). 
        Fallback: mediana global si el model no tiene moda (todas 0).
        Loguea (model, valor_imputado, nº_filas).
    R4. df = df.drop_duplicates() sobre las 9 columnas
    R5. df = df[df["year"] != 2060]
    R6. Imputar df["mileage"] <= 2 con mediana de mileage VÁLIDO (>2) del grupo:
        (model, year, transmission, fuelType) → (model, year, transmission) → (model, fuelType) → (model) → mediana global.
        Redondear a entero. Loguea cada fila imputada (original y nuevo).
    
    No se añaden columnas nuevas. Se conservan exactamente 9 columnas en este orden:
    ['model','year','transmission','mileage','fuelType','tax','mpg','engineSize','price']
    
    Decisiones ya tomadas (no se modifican): mpg==201.8 Kuga Hybrid se deja; Focus con precio "absurdo" se conservan;
    tax==0 (2153 filas) se considera legítimo; precios bajos reales se conservan; Mustang y modelos no se eliminan.
    """
    df_limpio = df.copy()

    # Orden esperado de columnas
    columnas_esperadas = [
        "model",
        "year",
        "transmission",
        "mileage",
        "fuelType",
        "tax",
        "mpg",
        "engineSize",
        "price",
    ]
    # Aseguramos orden si vienen diferentes
    df_limpio = df_limpio.reindex(columns=columnas_esperadas, copy=False)

    # Logs de imputación
    logs_tax = []
    logs_engine = []
    logs_mileage = []

    # R1: strip model (NO elimina filas)
    df_limpio["model"] = df_limpio["model"].astype(str).str.strip()

    # R2: tax nulos -> 145.0
    mask_tax_na = df_limpio["tax"].isna()
    n_tax_na = int(mask_tax_na.sum())
    if n_tax_na > 0:
        filas_tax_imp = df_limpio.loc[mask_tax_na].copy()
        for _, r in filas_tax_imp.iterrows():
            logs_tax.append(
                {
                    "col": "tax",
                    "model": r["model"],
                    "year": int(r["year"]) if pd.notna(r["year"]) else r["year"],
                    "transmission": r["transmission"],
                    "fuelType": r["fuelType"],
                    "engineSize": r["engineSize"],
                    "mpg": r["mpg"],
                    "price": r["price"],
                    "valor_original": r["tax"],
                    "valor_imputado": 145.0,
                }
            )
        df_limpio.loc[mask_tax_na, "tax"] = 145.0

    # R3: engineSize == 0 (51 filas) imputar por moda del MISMO model
    mask_es_cero = df_limpio["engineSize"] == 0
    n_es_cero = int(mask_es_cero.sum())
    if n_es_cero > 0:
        # Calcular moda por modelo para engineSize > 0
        df_es_valid = df_limpio[df_limpio["engineSize"] > 0].copy()
        moda_por_modelo = {}
        if not df_es_valid.empty:
            for m, grp in df_es_valid.groupby("model", sort=False):
                es_vals = grp["engineSize"].dropna()
                if es_vals.empty:
                    continue
                mod = es_vals.mode()
                if not mod.empty:
                    moda_por_modelo[m] = float(mod.iloc[0])
        # Mediana global
        mediana_global_es = float(df_limpio["engineSize"].median()) if df_limpio["engineSize"].notna().any() else 0.0

        # Logs por modelo afectado
        conteo_es0_por_model = df_limpio.loc[mask_es_cero, "model"].value_counts().to_dict()
        for m, n_filas_m in conteo_es0_por_model.items():
            if m in moda_por_modelo:
                valor_imp_m = moda_por_modelo[m]
                fuente_m = "moda_modelo"
            else:
                valor_imp_m = mediana_global_es
                fuente_m = "mediana_global_engineSize"
            logs_engine.append(
                {
                    "model": m,
                    "valor_imputado": valor_imp_m,
                    "n_filas": int(n_filas_m),
                    "fuente": fuente_m,
                }
            )
            df_limpio.loc[(df_limpio["model"] == m) & (df_limpio["engineSize"] == 0), "engineSize"] = valor_imp_m

    # R4: drop_duplicates sobre las 9 columnas
    shape_antes_r4 = df_limpio.shape
    df_limpio = df_limpio.drop_duplicates()
    shape_desp_r4 = df_limpio.shape
    filas_eliminadas_r4 = shape_antes_r4[0] - shape_desp_r4[0]

    # R5: year != 2060
    shape_antes_r5 = df_limpio.shape
    mask_year2060 = df_limpio["year"] == 2060
    n_year2060 = int(mask_year2060.sum())
    df_limpio = df_limpio[df_limpio["year"] != 2060].copy()
    shape_desp_r5 = df_limpio.shape
    filas_eliminadas_r5 = shape_antes_r5[0] - shape_desp_r5[0]

    # R6: mileage <= 2
    mask_mil_le2 = df_limpio["mileage"] <= 2
    n_mil_le2 = int(mask_mil_le2.sum())
    if n_mil_le2 > 0:
        mil_valid_global = df_limpio.loc[df_limpio["mileage"] > 2, "mileage"]
        mediana_mil_global = float(mil_valid_global.median()) if not mil_valid_global.empty else 0.0

        idx_m = df_limpio.index[mask_mil_le2]
        for i in idx_m:
            fila = df_limpio.loc[i]
            m_mod = fila["model"]
            y = fila["year"]
            trans = fila["transmission"]
            fuel = fila["fuelType"]
            mil_orig = fila["mileage"]
            valor_imp_mil = None
            fuente = "mediana_global_mileage"

            def mediana_grupo(cond_mask):
                g = df_limpio.loc[cond_mask & (df_limpio["mileage"] > 2), "mileage"]
                if len(g) >= 3:
                    return float(g.median())
                return None

            # 1
            valor_imp_mil = mediana_grupo(
                (df_limpio["model"] == m_mod)
                & (df_limpio["year"] == y)
                & (df_limpio["transmission"] == trans)
                & (df_limpio["fuelType"] == fuel)
            )
            if valor_imp_mil is not None:
                fuente = "grupo(model,year,transmission,fuelType)"
            else:
                # 2
                valor_imp_mil = mediana_grupo(
                    (df_limpio["model"] == m_mod)
                    & (df_limpio["year"] == y)
                    & (df_limpio["transmission"] == trans)
                )
                if valor_imp_mil is not None:
                    fuente = "grupo(model,year,transmission)"
                else:
                    # 3
                    valor_imp_mil = mediana_grupo(
                        (df_limpio["model"] == m_mod) & (df_limpio["fuelType"] == fuel)
                    )
                    if valor_imp_mil is not None:
                        fuente = "grupo(model,fuelType)"
                    else:
                        # 4
                        valor_imp_mil = mediana_grupo((df_limpio["model"] == m_mod))
                        if valor_imp_mil is not None:
                            fuente = "grupo(model)"
                        else:
                            valor_imp_mil = mediana_mil_global
                            fuente = "mediana_global_mileage"

            valor_imp_mil_int = int(round(valor_imp_mil))
            logs_mileage.append(
                {
                    "index_original_pos": int(i),
                    "model": m_mod,
                    "year": int(y) if pd.notna(y) else y,
                    "transmission": trans,
                    "fuelType": fuel,
                    "mileage_original": float(mil_orig) if pd.notna(mil_orig) else mil_orig,
                    "mileage_imputado": valor_imp_mil_int,
                    "fuente": fuente,
                }
            )
            df_limpio.at[i, "mileage"] = valor_imp_mil_int

    df_limpio = df_limpio[columnas_esperadas].copy()

    # Guardar metadatos
    limpiar._logs_tax = logs_tax
    limpiar._logs_engine = logs_engine
    limpiar._logs_mileage = logs_mileage
    limpiar._rows_elim_r4 = filas_eliminadas_r4
    limpiar._rows_elim_r5 = filas_eliminadas_r5

    return df_limpio


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_origen = os.path.join(script_dir, "used_car_price_analysis.csv")
    csv_limpio = os.path.join(script_dir, "used_car_price_analysis_limpio.csv")

    df_orig = pd.read_csv(csv_origen)

    print("=== INFORME DE LIMPIEZA DE DATOS ===")
    print(f"Directorio: {script_dir}")
    print(f"Origen:     {csv_origen}")
    print(f"Destino:    {csv_limpio}")
    print("")
    print(f"Filas al INICIO:                        {len(df_orig):,}")
    print("")

    df_clean = limpiar(df_orig.copy())

    logs_tax = getattr(limpiar, "_logs_tax", [])
    logs_engine = getattr(limpiar, "_logs_engine", [])
    logs_mileage = getattr(limpiar, "_logs_mileage", [])
    rows_elim_r4 = getattr(limpiar, "_rows_elim_r4", 0)
    rows_elim_r5 = getattr(limpiar, "_rows_elim_r5", 0)
    final_rows = len(df_clean)

    filas_tras_r1 = len(df_orig)
    filas_tras_r2 = len(df_orig)
    filas_tras_r3 = len(df_orig)
    filas_tras_r4 = len(df_orig) - rows_elim_r4
    filas_tras_r5 = filas_tras_r4 - rows_elim_r5
    filas_final = final_rows

    print(f"R1: strip(model)                        → Filas tras R1: {filas_tras_r1:,}  (sin eliminar filas)")
    print(f"R2: tax.fillna(145.0)                  → Filas tras R2: {filas_tras_r2:,}  (imputados: {len(logs_tax)})")
    print(f"R3: engineSize==0 por moda/model        → Filas tras R3: {filas_tras_r3:,}  (modelos afectados: {len(logs_engine)})")
    print(f"R4: drop_duplicates(9 columnas)         → Filas tras R4: {filas_tras_r4:,}  (-{rows_elim_r4} filas)")
    print(f"R5: year != 2060                        → Filas tras R5: {filas_tras_r5:,}  (-{rows_elim_r5} fila(s))")
    print(f"R6: mileage <= 2 (imputación por grupos)→ Filas tras R6: {filas_final:,}  (filas imputadas: {len(logs_mileage)})")
    print("")
    print(f"TOTAL FINAL:                            {filas_final:,} filas")
    print("Columnas:                              model,year,transmission,mileage,fuelType,tax,mpg,engineSize,price")
    print("")

    print("=== IMPUTACIONES TAX (R2) ===")
    if logs_tax:
        pd.set_option("display.max_columns", None)
        df_tax_log = pd.DataFrame(logs_tax)
        print(df_tax_log[["model", "year", "transmission", "fuelType", "valor_original", "valor_imputado"]].to_string(index=False))
    else:
        print("No hubo imputaciones de tax (sin nulos).")
    print("")

    print("=== IMPUTACIONES ENGINESIZE (R3) ===")
    if logs_engine:
        df_eng_log = pd.DataFrame(logs_engine)
        print(df_eng_log[["model", "valor_imputado", "n_filas", "fuente"]].to_string(index=False))
    else:
        print("No hubo imputaciones de engineSize (sin valores == 0).")
    print("")

    print("=== IMPUTACIONES MILEAGE (R6) ===")
    if logs_mileage:
        df_mil_log = pd.DataFrame(logs_mileage)
        print(df_mil_log[["index_original_pos", "model", "year", "transmission", "fuelType", "mileage_original", "mileage_imputado", "fuente"]].to_string(index=False))
    else:
        print("No hubo imputaciones de mileage (sin valores <= 2).")
    print("")

    df_clean.to_csv(csv_limpio, index=False)
    print(f"✓ Guardado CSV limpio: {csv_limpio}")
    print(f"✓ Shape final: {df_clean.shape}")
    print("=== FIN DEL INFORME ===")
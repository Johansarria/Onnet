import pandas as pd
import numpy as np
from datetime import datetime

def generar_reportes_gerenciales():
    print("--- INICIANDO PROCESO DE AUDITORÍA GERENCIAL ONNET ---")
    
    try:
        # 1. Extracción: Cargar datos facturados y el maestro GIS
        print("[1/5] Extrayendo datos...")
        df_contratista = pd.read_excel('maestro_inventario_gis.xlsx', sheet_name=0)
        df_gis = pd.read_excel('facturacion_contratista.xlsx', sheet_name=0)

        # 2. Transformación: Limpieza básica para el cruce
        print("[2/5] Limpiando datos...")
        df_contratista.dropna(subset=['id_caja_nap'], inplace=True)
        df_contratista['id_caja_nap'] = df_contratista['id_caja_nap'].str.upper().str.strip()
        df_gis['id_caja_nap'] = df_gis['id_caja_nap'].str.upper().str.strip()

        # Convertir a Fecha-Hora (si existen las columnas)
        if 'fecha_apertura' in df_contratista.columns:
            df_contratista['fecha_apertura'] = pd.to_datetime(df_contratista['fecha_apertura'], errors='coerce')
        if 'fecha_cierre' in df_contratista.columns:
            df_contratista['fecha_cierre'] = pd.to_datetime(df_contratista['fecha_cierre'], errors='coerce')

        # 3. Transformación (Cruce de Datos / JOIN)
        print("[3/5] Ejecutando cruce de datos (JOIN)...")
        # Hacemos un cruce por la izquierda (Left Join) para ver qué cobró el contratista
        auditoria = pd.merge(df_contratista, df_gis, on='id_caja_nap', how='left', indicator=True)

        # Detectar Inventario Fantasma (Facturado pero no existe en GIS)
        inventario_fantasma = auditoria[auditoria['_merge'] == 'left_only'].copy()

        # Detectar Mantenimientos en Cajas No Activas (Fuga de dinero)
        # Si el estado en GIS es 'Inactivo' o 'En Construccion', no deberían cobrar correctivos ahí.
        cajas_inactivas = auditoria[auditoria['estado_gis'].isin(['Inactivo', 'En Construccion'])]

        # 4. Cálculo de SLA (Acuerdo de Nivel de Servicio)
        print("[4/5] Analizando cumplimiento de SLA...")
        # Calcular la diferencia en horas si existen las columnas
        if 'fecha_apertura' in auditoria.columns and 'fecha_cierre' in auditoria.columns:
            auditoria['tiempo_atencion_horas'] = (auditoria['fecha_cierre'] - auditoria['fecha_apertura']).dt.total_seconds() / 3600
            # Filtrar los que superaron el SLA (Ejemplo: 4 horas)
            incumplimientos_sla = auditoria[auditoria['tiempo_atencion_horas'] > 4]
        else:
            auditoria['tiempo_atencion_horas'] = np.nan
            incumplimientos_sla = pd.DataFrame(columns=auditoria.columns)

        # 5. Carga (Exportar Evidencia para el Dashboard)
        print("[5/5] Exportando hallazgos para la gerencia...")
        inventario_fantasma.to_excel('1_Fugas_Inventario_Fantasma.xlsx', index=False)
        incumplimientos_sla.to_excel('2_Penalizaciones_SLA.xlsx', index=False)

        print("\n" + "="*40)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print(f"Reporte 1 (Fugas): {len(inventario_fantasma)} registros")
        print(f"Reporte 2 (SLA):   {len(incumplimientos_sla)} registros")
        print("="*40)

    except Exception as e:
        print(f"Error durante el proceso: {e}")

if __name__ == "__main__":
    generar_reportes_gerenciales()

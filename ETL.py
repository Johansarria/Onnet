import pandas as pd
import numpy as np
from datetime import datetime

def ejecutar_auditoria():
    print("--- INICIANDO AUDITORÍA TÉCNICA ONNET ---")
    
    try:
        # 1. Extracción de Datos
        print("[1/4] Extrayendo datos de la zona de guerra...")
        df_contratista = pd.read_excel('maestro_inventario_gis.xlsx', sheet_name=0)
        df_gis = pd.read_excel('facturacion_contratista.xlsx', sheet_name=0)

        # 2. Transformación y Limpieza Agresiva
        print("[2/4] Ejecutando limpieza de datos...")
        
        # Eliminar registros sin ID de NAP (no auditables)
        df_contratista.dropna(subset=['id_caja_nap'], inplace=True)
        
        # Estandarización de IDs
        df_contratista['id_caja_nap'] = df_contratista['id_caja_nap'].astype(str).str.upper().str.strip()
        df_gis['id_caja_nap'] = df_gis['id_caja_nap'].astype(str).str.upper().str.strip()

        # Conversión estricta de fechas (si existen las columnas)
        if 'fecha_apertura' in df_contratista.columns:
            df_contratista['fecha_apertura'] = pd.to_datetime(df_contratista['fecha_apertura'], errors='coerce')
        if 'fecha_cierre' in df_contratista.columns:
            df_contratista['fecha_cierre'] = pd.to_datetime(df_contratista['fecha_cierre'], errors='coerce')
        
        # 3. Cruce de Auditoría (Conciliación)
        print("[3/4] Cruzando información con Maestro GIS...")
        
        # Unimos para verificar existencia en GIS
        df_resultado = pd.merge(
            df_contratista,
            df_gis[['id_caja_nap']], 
            on='id_caja_nap',
            how='left',
            indicator=True
        )

        # Identificar NAPs "Fantasmas" (Facturadas pero no en GIS)
        df_resultado['es_valido_gis'] = df_resultado['_merge'] == 'both'
        
        # Cálculo de Tiempos de Atención (SLA) en días
        if 'fecha_apertura' in df_resultado.columns and 'fecha_cierre' in df_resultado.columns:
            df_resultado['tiempo_atencion_dias'] = (
                df_resultado['fecha_cierre'] - df_resultado['fecha_apertura']
            ).dt.total_seconds() / (3600 * 24)
        else:
            df_resultado['tiempo_atencion_dias'] = np.nan

        # 4. Clasificación de Hallazgos
        df_resultado['hallazgo'] = 'OK'
        df_resultado.loc[df_resultado['es_valido_gis'] == False, 'hallazgo'] = 'NAP NO EXISTE EN GIS'
        
        # Limpieza de columnas auxiliares
        df_resultado.drop(columns=['_merge'], inplace=True)

        # 5. Exportación de Reporte Final
        nombre_archivo = f"Reporte_Auditoria_Onnet_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df_resultado.to_excel(nombre_archivo, index=False)
        
        # Resumen Ejecutivo
        print("\n" + "="*30)
        print("RESUMEN DE AUDITORÍA")
        print(f"Registros procesados: {len(df_contratista)}")
        print(f"NAPs válidas en GIS:  {df_resultado['es_valido_gis'].sum()}")
        print(f"NAPs no encontradas:  {len(df_resultado[df_resultado['hallazgo'] == 'NAP NO EXISTE EN GIS'])}")
        print(f"Reporte generado:     {nombre_archivo}")
        print("="*30)

    except FileNotFoundError as e:
        print(f"Error: No se encontraron los archivos Excel. Verifique que estén en la misma carpeta que el script.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    ejecutar_auditoria()

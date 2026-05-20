import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def inyectar_datos_sql():
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    print("--- INICIANDO CARGA A POSTGRESQL ---")
    
    # 1. Preparación de datos (Igual a la limpieza inicial)
    try:
        print("Cargando y limpiando datos para SQL...")
        df_contratista = pd.read_excel('maestro_inventario_gis.xlsx', sheet_name=0)
        df_contratista.dropna(subset=['id_caja_nap'], inplace=True)
        df_contratista['id_caja_nap'] = df_contratista['id_caja_nap'].str.upper().str.strip()
        
        # 2. Configuración de conexión
        # Credenciales cargadas de las variables de entorno
        usuario = os.getenv('DB_USER')
        contraseña = os.getenv('DB_PASSWORD')
        host = os.getenv('DB_HOST')
        puerto = os.getenv('DB_PORT')
        base_datos = os.getenv('DB_NAME')

        print(f"Conectando a la base de datos: {base_datos}...")
        engine = create_engine(f'postgresql://{usuario}:{contraseña}@{host}:{puerto}/{base_datos}')

        # 3. Carga (Subir el DataFrame limpio a una tabla SQL)
        print("Inyectando registros en la tabla 'cierres_contratista'...")
        df_contratista.to_sql('cierres_contratista', engine, if_exists='replace', index=False)
        
        print("Datos inyectados en PostgreSQL exitosamente.")

    except Exception as e:
        print(f"Error durante la carga a SQL: {e}")

if __name__ == "__main__":
    inyectar_datos_sql()

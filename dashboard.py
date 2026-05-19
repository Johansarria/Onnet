import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Dashboard Auditoría Onnet", layout="wide")

st.title("📊 Dashboard de Auditoría Técnica - Onnet")
st.sidebar.header("Opciones de Visualización")

# Función para cargar datos
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return None

# Carga de reportes generados por auditoria_gerencial.py
df_fugas = load_data('1_Fugas_Inventario_Fantasma.xlsx')
df_sla = load_data('2_Penalizaciones_SLA.xlsx')

tab1, tab2 = st.tabs(["👻 Inventario Fantasma", "⏱️ Penalizaciones SLA"])

with tab1:
    st.header("Reporte de Fugas (Inventario Fantasma)")
    if df_fugas is not None:
        st.write(f"Total de registros encontrados: {len(df_fugas)}")
        
        # Filtros rápidos
        search = st.text_input("Buscar por ID de NAP (Fugas):")
        if search:
            df_fugas = df_fugas[df_fugas['id_caja_nap'].str.contains(search, case=False, na=False)]
            
        st.dataframe(df_fugas, use_container_width=True)
        
        # Botón de descarga
        csv = df_fugas.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV", csv, "fugas_fantasma.csv", "text/csv")
    else:
        st.warning("No se encontró el archivo '1_Fugas_Inventario_Fantasma.xlsx'. Ejecute primero auditoria_gerencial.py")

with tab2:
    st.header("Incumplimientos de SLA (> 4 Horas)")
    if df_sla is not None:
        st.write(f"Total de registros con retraso: {len(df_sla)}")
        
        # Métrica de tiempo promedio
        if 'tiempo_atencion_horas' in df_sla.columns:
            promedio = df_sla['tiempo_atencion_horas'].mean()
            st.metric("Tiempo Promedio de Retraso", f"{promedio:.2f} Horas")

        st.dataframe(df_sla, use_container_width=True)
    else:
        st.warning("No se encontró el archivo '2_Penalizaciones_SLA.xlsx'. Ejecute primero auditoria_gerencial.py")

# Footer
st.divider()
st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

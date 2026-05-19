import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Liquidación de Infraestructura",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual styling
st.markdown("""
<style>
    .reportview-container {
        background-color: #F8F9FA;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #1F4E79;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 14px;
        color: #6C757D;
        font-weight: 500;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        color: #1F4E79;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_months_by_year(cosecha_date, target_date=pd.to_datetime('2025-06-01')):
    if pd.isna(cosecha_date):
        return {2024: 0, 2025: 0}
    cosecha_date = pd.to_datetime(cosecha_date)
    months = pd.date_range(start=cosecha_date, end=target_date, freq='MS')
    years_count = {2024: 0, 2025: 0}
    for m in months:
        if m.year in years_count:
            years_count[m.year] += 1
    return years_count

def get_perf_key(desempeno):
    if not isinstance(desempeno, str):
        return 'alto,moderado,incipiente'
    d = desempeno.lower().strip()
    if d in ['alto', 'moderado', 'incipiente']:
        return 'alto,moderado,incipiente'
    elif d in ['bajo', 'limitado']:
        return 'bajo,limitado'
    else:
        return 'alto,moderado,incipiente'

@st.cache_data
def load_all_data(excel_path):
    # Cargar liquidacion
    df_liq = pd.read_excel(excel_path, sheet_name='Ots para liquidación', header=1)
    df_liq = df_liq[df_liq['OT'].notna() & (df_liq['OT'] != "TOTAL GENERAL")].copy()
    
    # Cargar inventario
    df_inv = pd.read_excel(excel_path, sheet_name='Inventario OTs').dropna(subset=['OT_ORIGINAL'])
    df_inv_filtered = df_inv[df_inv['OT_ORIGINAL'].isin(df_liq['OT'])].copy()
    
    # Asegurar tipos de datos
    height_cols = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21]
    all_qty_cols = height_cols + ['Torre', 'Q Ductos']
    for c in all_qty_cols:
        df_inv_filtered[c] = pd.to_numeric(df_inv_filtered[c], errors='coerce').fillna(0.0)
        
    return df_liq, df_inv_filtered

# Main Execution
excel_file = "Liquidacion_Junio_2025.xlsx"

try:
    df_liq, df_inv = load_all_data(excel_file)
except Exception as e:
    st.error(f"Error al cargar el archivo Excel '{excel_file}': {e}")
    st.info("Asegúrese de haber ejecutado el script 'calcular_liquidacion.py' para generar la data.")
    st.stop()

# Título y Cabecera
st.title("⚡ Dashboard de Liquidación de Infraestructura")
st.markdown("### Período de Liquidación: **Junio 2025** (Con Retroactivos)")
st.caption("Esta herramienta permite interactuar con los escenarios de liquidación de postes y ductos y auditar los valores resultantes.")

# Sidebar Filters
st.sidebar.image("https://www.onnetfibra.com/wp-content/uploads/2022/07/logo-onnet.png", width=150)
st.sidebar.header("Filtros de Control")

# Selector de Escenario
escenario = st.sidebar.radio(
    "Escenario de Ductos:",
    ["Escenario 1 (1 Ducto de Compartición)", "Escenario 2 (2 Ductos de Compartición)"],
    index=0
)

# Filtro de Municipio
municipios = sorted(df_inv['Municipio'].dropna().unique())
sel_municipios = st.sidebar.multiselect("Municipios:", municipios, default=[])

# Filtro de Cosecha (Meses)
df_inv['Cosecha_str'] = pd.to_datetime(df_inv['Cosecha']).dt.strftime('%Y-%m')
cosechas = sorted(df_inv['Cosecha_str'].dropna().unique())
sel_cosechas = st.sidebar.multiselect("Mes de Cosecha (Inicio de uso):", cosechas, default=[])

# Aplicar filtros
df_filtered = df_inv.copy()
if sel_municipios:
    df_filtered = df_filtered[df_filtered['Municipio'].isin(sel_municipios)]
if sel_cosechas:
    df_filtered = df_filtered[df_filtered['Cosecha_str'].isin(sel_cosechas)]

# Cargar Precios dinámicamente desde el excel para los cálculos en caliente
df_precios_raw = pd.read_excel(excel_file, sheet_name='Precios')
prices_raw = {
    'Electrificadora': {
        'alto,moderado,incipiente': {2024: {}, 2025: {}},
        'bajo,limitado': {2024: {}, 2025: {}}
    },
    'Telecomunicaciones': {
        'alto,moderado,incipiente': {2024: {}, 2025: {}},
        'bajo,limitado': {2024: {}, 2025: {}}
    }
}

# Carga rápida de matriz de precios
def normalize_key(s):
    import unicodedata
    if not isinstance(s, str): return ""
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    return s.strip().lower()

for idx in range(1, 7):
    name = normalize_key(df_precios_raw.iloc[idx, 0])
    prices_raw['Electrificadora']['alto,moderado,incipiente'][2024][name] = float(df_precios_raw.iloc[idx, 2])
    prices_raw['Electrificadora']['bajo,limitado'][2024][name] = float(df_precios_raw.iloc[idx, 3])
    prices_raw['Electrificadora']['alto,moderado,incipiente'][2025][name] = float(df_precios_raw.iloc[idx, 4])
    prices_raw['Electrificadora']['bajo,limitado'][2025][name] = float(df_precios_raw.iloc[idx, 5])
for idx in range(10, 15):
    name = normalize_key(df_precios_raw.iloc[idx, 0])
    prices_raw['Telecomunicaciones']['alto,moderado,incipiente'][2024][name] = float(df_precios_raw.iloc[idx, 2])
    prices_raw['Telecomunicaciones']['bajo,limitado'][2024][name] = float(df_precios_raw.iloc[idx, 3])
    prices_raw['Telecomunicaciones']['alto,moderado,incipiente'][2025][name] = float(df_precios_raw.iloc[idx, 4])
    prices_raw['Telecomunicaciones']['bajo,limitado'][2025][name] = float(df_precios_raw.iloc[idx, 5])
for perf in ['alto,moderado,incipiente', 'bajo,limitado']:
    for year in [2024, 2025]:
        prices_raw['Telecomunicaciones'][perf][year]['poste/torre'] = 0.0

# Recalcular valores dinámicos para la data filtrada
calc_rows = []
for _, row in df_filtered.iterrows():
    empresa = row['Electrificacora/Telco']
    desempeno = row['Desempeño']
    cosecha = row['Cosecha']
    emp_key = 'Electrificadora' if 'electri' in str(empresa).lower() else 'Telecomunicaciones'
    perf_key = get_perf_key(desempeno)
    
    months = get_months_by_year(cosecha)
    m_2024 = months[2024]
    m_2025 = months[2025]
    
    q_le8 = float(row[8])
    q_8_10 = float(row[9] + row[10])
    q_gt10 = float(sum(row[h] for h in [11, 12, 13, 14, 15, 16, 17, 18, 20, 21]))
    q_torre = float(row['Torre'])
    q_ductos = float(row['Q Ductos'])
    
    p_le8_2024 = prices_raw[emp_key][perf_key][2024]['poste menor o igual a 8m']
    p_le8_2025 = prices_raw[emp_key][perf_key][2025]['poste menor o igual a 8m']
    p_8_10_2024 = prices_raw[emp_key][perf_key][2024]['poste mayor a 8m menor o igual a 10m']
    p_8_10_2025 = prices_raw[emp_key][perf_key][2025]['poste mayor a 8m menor o igual a 10m']
    p_gt10_2024 = prices_raw[emp_key][perf_key][2024]['poste mayor a 10m']
    p_gt10_2025 = prices_raw[emp_key][perf_key][2025]['poste mayor a 10m']
    p_torre_2024 = prices_raw[emp_key][perf_key][2024]['poste/torre']
    p_torre_2025 = prices_raw[emp_key][perf_key][2025]['poste/torre']
    
    # Precios de ductos según escenario
    if "Escenario 1" in escenario:
        p_duct_2024 = prices_raw[emp_key][perf_key][2024]['1 ducto de comparticion']
        p_duct_2025 = prices_raw[emp_key][perf_key][2025]['1 ducto de comparticion']
    else:
        p_duct_2024 = prices_raw[emp_key][perf_key][2024]['2 ductos de comparticion']
        p_duct_2025 = prices_raw[emp_key][perf_key][2025]['2 ductos de comparticion']
        
    val_le8 = q_le8 * (m_2024 * p_le8_2024 + m_2025 * p_le8_2025)
    val_8_10 = q_8_10 * (m_2024 * p_8_10_2024 + m_2025 * p_8_10_2025)
    val_gt10 = q_gt10 * (m_2024 * p_gt10_2024 + m_2025 * p_gt10_2025)
    val_torre = q_torre * (m_2024 * p_torre_2024 + m_2025 * p_torre_2025)
    val_ductos = q_ductos * (m_2024 * p_duct_2024 + m_2025 * p_duct_2025)
    
    calc_rows.append({
        'OT': row['OT_ORIGINAL'],
        'Municipio': row['Municipio'],
        'Cosecha_str': row['Cosecha_str'],
        'Q_Postes': q_le8 + q_8_10 + q_gt10 + q_torre,
        'Q_Ductos': q_ductos,
        'Val_le8': val_le8,
        'Val_8_10': val_8_10,
        'Val_gt10': val_gt10,
        'Val_Torre': val_torre,
        'Val_Postes': val_le8 + val_8_10 + val_gt10 + val_torre,
        'Val_Ductos': val_ductos,
        'Val_Total': val_le8 + val_8_10 + val_gt10 + val_torre + val_ductos
    })

df_calc = pd.DataFrame(calc_rows)

if df_calc.empty:
    st.warning("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# KPIs principales
st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_settlement = df_calc['Val_Total'].sum()
total_poles_val = df_calc['Val_Postes'].sum()
total_ducts_val = df_calc['Val_Ductos'].sum()
total_poles_qty = df_calc['Q_Postes'].sum()
total_ducts_qty = df_calc['Q_Ductos'].sum()

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">TOTAL LIQUIDACIÓN</div>
        <div class="metric-value">${total_settlement:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">VALOR POSTES</div>
        <div class="metric-value">${total_poles_val:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #2E7D32;">
        <div class="metric-title">VALOR DUCTOS</div>
        <div class="metric-value">${total_ducts_val:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #ED6C02;">
        <div class="metric-title">INFRAESTRUCTURA TOTAL</div>
        <div class="metric-value">{int(total_poles_qty):,} Postes / {total_ducts_qty:,.1f}m</div>
    </div>
    """, unsafe_allow_html=True)

# Sección de Gráficos
st.markdown("---")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### Distribución de Costos por Infraestructura")
    pie_data = pd.DataFrame({
        'Infraestructura': ['Postes <= 8m', 'Postes 8-10m', 'Postes > 10m', 'Postes/Torre', 'Ductos'],
        'Valor': [
            df_calc['Val_le8'].sum(),
            df_calc['Val_8_10'].sum(),
            df_calc['Val_gt10'].sum(),
            df_calc['Val_Torre'].sum(),
            df_calc['Val_Ductos'].sum()
        ]
    })
    fig_pie = px.pie(
        pie_data, 
        values='Valor', 
        names='Infraestructura', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.markdown("#### Evolución de Costo por Mes de Cosecha")
    trend_data = df_calc.groupby('Cosecha_str')[['Val_Postes', 'Val_Ductos', 'Val_Total']].sum().reset_index()
    fig_trend = px.line(
        trend_data, 
        x='Cosecha_str', 
        y=['Val_Postes', 'Val_Ductos', 'Val_Total'],
        labels={'value': 'Valor ($)', 'Cosecha_str': 'Mes de Cosecha', 'variable': 'Categoría'},
        color_discrete_map={'Val_Postes': '#1F4E79', 'Val_Ductos': '#2E7D32', 'Val_Total': '#ED6C02'}
    )
    fig_trend.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_trend, use_container_width=True)

# Sección de Municipios
st.markdown("---")
st.markdown("#### Top 10 Municipios por Valor Liquidado")
mun_data = df_calc.groupby('Municipio')['Val_Total'].sum().reset_index().sort_values(by='Val_Total', ascending=False).head(10)
fig_mun = px.bar(
    mun_data,
    x='Val_Total',
    y='Municipio',
    orientation='h',
    color='Val_Total',
    color_continuous_scale='Viridis',
    labels={'Val_Total': 'Valor Total Liquidación ($)', 'Municipio': 'Municipio'}
)
fig_mun.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=400)
st.plotly_chart(fig_mun, use_container_width=True)

# Tabla de Datos
st.markdown("---")
st.markdown("#### Detalle de OTs Liquidadas")

# Buscador de texto
search_query = st.text_input("🔍 Buscar por Código de OT:")
df_table = df_calc.copy()
if search_query:
    df_table = df_table[df_table['OT'].str.contains(search_query, case=False, na=False)]

# Mostrar tabla formateada
df_display = df_table[[
    'OT', 'Municipio', 'Cosecha_str', 'Q_Postes', 'Q_Ductos', 'Val_Postes', 'Val_Ductos', 'Val_Total'
]].copy()

df_display.columns = [
    'OT', 'Municipio', 'Mes Cosecha', 'Cant. Postes', 'Metros Ductos', 'Valor Postes ($)', 'Valor Ductos ($)', 'Valor Total ($)'
]

st.dataframe(
    df_display.style.format({
        'Cant. Postes': '{:,.0f}',
        'Metros Ductos': '{:,.1f}',
        'Valor Postes ($)': '${:,.2f}',
        'Valor Ductos ($)': '${:,.2f}',
        'Valor Total ($)': '${:,.2f}'
    }),
    use_container_width=True,
    height=400
)

# Descargar reporte filtrado
csv = df_display.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Tabla Filtrada (CSV)",
    data=csv,
    file_name=f"Liquidacion_Filtrada_{datetime.now().strftime('%Y%md')}.csv",
    mime="text/csv"
)

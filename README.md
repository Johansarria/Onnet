# Liquidador y Auditor de Infraestructura - Onnet

Este repositorio contiene las herramientas automáticas de ETL, auditoría y cálculo de liquidación de infraestructura de red (postes y ductos) desarrolladas para **Onnet**.

---

## 📋 Estructura del Proyecto

El repositorio se compone de los siguientes módulos principales:

### 1. Auditoría Técnica (`auditoria_gerencial.py`)
Módulo encargado de auditar la facturación del contratista contra los registros GIS de inventario:
* **Fugas de Inventario (Cajas NAP Fantasma)**: Identifica cajas NAP reportadas en facturación pero inexistentes en el inventario GIS, exportando el reporte en `1_Fugas_Inventario_Fantasma.xlsx`.
* **Cumplimiento de SLA**: Analiza los tiempos de atención y penalizaciones asociadas a tickets que excedieron el SLA de 4 horas, generando `2_Penalizaciones_SLA.xlsx`.

### 2. Calculadora de Liquidación (`calcular_liquidacion.py`)
Script principal para la liquidación masiva de infraestructura del periodo **Junio 2025** con retroactivos:
* Mapea de forma dinámica la infraestructura según su altura y tipo de red (Eléctricos / Telecomunicaciones).
* Calcula meses exactos de servicio en **2024** (desde el mes de `Cosecha` hasta diciembre de 2024) y en **2025** (de enero a junio de 2025).
* Genera la liquidación financiera con tarifas indexadas por año y clasificadas según el nivel de desempeño del municipio.
* Evalúa de forma simultánea dos escenarios de compartición para ductos (Escenario 1: Tarifa de 1 Ducto; Escenario 2: Tarifa de 2 Ductos).
* Guarda el resultado en `Liquidacion_Junio_2025.xlsx` con el detalle completo y una pestaña de resumen gerencial.

### 3. Dashboard Ejecutivo (`dashboard_liquidacion.py`)
Una aplicación interactiva en **Streamlit** para la visualización ejecutiva del reporte final:
* **KPIs Clave**: Visualización del total liquidado, valor de postes, valor de ductos y volumen total de activos.
* **Filtros Dinámicos**: Selección de escenario de compartición, multiselección por municipios y meses de cosecha.
* **Gráficos**: Distribución de costos por altura, evolución de costos retroactivos por mes de cosecha y Top 10 municipios por facturación.
* **Auditoría de OTs**: Tabla interactiva con buscador rápido por código de OT y descarga de datos filtrados en formato CSV.

---

## 🚀 Requisitos e Instalación

Para ejecutar este proyecto de forma local, asegúrese de tener instalado Python 3.10+ y las dependencias requeridas.

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Onnet
```

### 2. Instalar dependencias
```bash
pip install pandas openpyxl streamlit plotly
```

---

## 🛠️ Instrucciones de Uso

### Paso 1: Ejecutar la Auditoría Técnica
Este script genera los reportes de fugas de inventario y penalizaciones por SLA:
```bash
python auditoria_gerencial.py
```

### Paso 2: Calcular la Liquidación Financiera
Procesa las hojas de inventario, OTs a liquidar y matriz de precios para generar la liquidación con retroactivos:
```bash
python calcular_liquidacion.py
```
*Genera el archivo `Liquidacion_Junio_2025.xlsx`.*

### Paso 3: Lanzar el Dashboard de Visualización
Inicia el servidor local de Streamlit para interactuar con los reportes:
```bash
streamlit run dashboard_liquidacion.py
```
*El dashboard se abrirá automáticamente en su navegador web bajo la dirección `http://localhost:8501`.*

---

## 📐 Reglas de Negocio Aplicadas en la Liquidación

* **Desempeño Municipal**: Los precios unitarios de arrendamiento de infraestructura están vinculados al desempeño del municipio. De acuerdo con el inventario actual, todos los municipios corresponden al nivel **"Moderado"**, aplicando las tarifas de la columna **"alto,moderado,incipiente"**. El script está parametrizado para escalar a otros niveles (ej. Bajo/Limitado) si se actualizan los datos.
* **Equivalencias de Altura (Postes)**:
  * **<= 8m**: Tarifa "Poste menor o igual a 8m".
  * **8.1m a 10m**: Tarifa "Poste mayor a 8m menor o igual a 10m".
  * **> 10m**: Tarifa "Poste mayor a 10m".
  * **Torres**: Tarifa "Poste/Torre".
* **Fórmula de Retroactivos**:
  $$\text{Valor Total OT} = (\text{Cant.} \times \text{Precio 2024} \times \text{Meses 2024}) + (\text{Cant.} \times \text{Precio 2025} \times \text{Meses 2025})$$
* **Escenarios de Ductos**:
  * **Escenario 1**: Asume la tarifa de **1 Ducto de Compartición**.
  * **Escenario 2**: Asume la tarifa de **2 Ductos de Compartición**.

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Segmentos logísticos",
    page_icon="🧭",
    layout="wide"
)

# ============================================================
# CARGA DE DATOS
# ============================================================

DATA_DIR = Path("data")

@st.cache_data
def cargar_csv(nombre_archivo):
    return pd.read_csv(DATA_DIR / nombre_archivo)

segmentos = cargar_csv("metricas_segmento.csv")

# ============================================================
# TÍTULO E INTRODUCCIÓN
# ============================================================

st.title("🧭 Segmentos logísticos")

st.markdown("""
En esta sección se compara el desempeño logístico según la complejidad geográfica de la entrega.

Los pedidos se agrupan en tres segmentos:

- **Mismo Estado:** comprador y vendedor se encuentran en el mismo estado.
- **Misma Región:** comprador y vendedor están en estados distintos, pero dentro de la misma región.
- **Distinta Región:** comprador y vendedor pertenecen a regiones diferentes.

El objetivo es analizar si la complejidad territorial se asocia con un mayor riesgo de fallas extremas.
""")

st.markdown("---")

# ============================================================
# TABLA RESUMEN
# ============================================================

st.subheader("Resumen por segmento")

tabla_segmentos = segmentos.copy()
tabla_segmentos["tasa_fallas_extremas"] = tabla_segmentos["tasa_fallas_extremas"].round(2)
tabla_segmentos["indice_riesgo"] = tabla_segmentos["indice_riesgo"].round(2)

st.dataframe(tabla_segmentos, use_container_width=True)

# ============================================================
# GRÁFICO PRINCIPAL
# ============================================================

st.subheader("Tasa de fallas extremas por segmento logístico")

fig = px.bar(
    segmentos,
    x="segmento_logistico",
    y="tasa_fallas_extremas",
    text="tasa_fallas_extremas",
    title="A mayor complejidad geográfica, mayor tasa de fallas extremas",
    labels={
        "segmento_logistico": "Segmento logístico",
        "tasa_fallas_extremas": "Tasa de fallas extremas (%)"
    }
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig.update_layout(
    yaxis_title="Tasa de fallas extremas (%)",
    xaxis_title="Segmento logístico"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# INTERPRETACIÓN
# ============================================================

st.info("""
La tasa de fallas extremas aumenta a medida que crece la complejidad geográfica del pedido.

Los pedidos dentro del **mismo estado** presentan el menor riesgo relativo, mientras que los pedidos de **misma región**
y especialmente de **distinta región** muestran una proporción mayor de entregas extremadamente largas.

Esto refuerza la idea de que la distancia territorial y el cruce regional agregan fricción logística.
""")

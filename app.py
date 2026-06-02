import streamlit as st
import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURACIÓN GENERAL DEL DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Dashboard Logístico Olist",
    page_icon="🚚",
    layout="wide"
)

# ============================================================
# RUTAS DE ARCHIVOS
# ============================================================

DATA_DIR = Path("data")

# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def cargar_csv(nombre_archivo):
    return pd.read_csv(DATA_DIR / nombre_archivo)

kpis = cargar_csv("kpis_generales.csv")

# ============================================================
# PORTADA
# ============================================================

st.title("🚚 Dashboard logístico de Olist")

st.subheader("Desempeño de entregas, rutas críticas y satisfacción del cliente")

st.markdown("""
Este dashboard resume los principales hallazgos del análisis logístico realizado sobre el dataset público de Olist.

El objetivo es analizar el desempeño de las entregas, identificar segmentos y rutas con mayor riesgo operativo,
evaluar el impacto de las fallas extremas en la satisfacción del cliente y presentar una primera aproximación
predictiva mediante regresión lineal.
""")

st.markdown("---")

# ============================================================
# RESUMEN EJECUTIVO
# ============================================================

st.header("Resumen ejecutivo")

cols = st.columns(4)

for i, row in kpis.iterrows():
    col = cols[i % 4]

    valor = row["valor"]
    unidad = row["unidad"]

    if unidad == "%":
        texto_valor = f"{valor:.2f}%"
    elif unidad == "días":
        texto_valor = f"{valor:.2f} días"
    elif unidad == "pedidos":
        texto_valor = f"{valor:,.0f}".replace(",", ".")
    else:
        texto_valor = str(valor)

    col.metric(row["kpi"], texto_valor)

st.markdown("---")

st.info("""
La operación presenta un alto cumplimiento frente a la fecha prometida, pero ese indicador no cuenta toda la historia.
Al analizar el tiempo real de entrega, los segmentos logísticos, las rutas y las fallas extremas, aparecen diferencias
operativas relevantes que impactan en la experiencia del cliente.
""")
st.markdown("---")


st.markdown("""
### Lectura ejecutiva

El dashboard organiza el análisis en torno a una idea central: **la logística de Olist no debe evaluarse solo por la tasa de retraso oficial**.

Aunque el cumplimiento frente a la fecha prometida es alto, el análisis del tiempo real de entrega permite identificar
diferencias entre segmentos logísticos, estados, rutas críticas y casos extremos que afectan la satisfacción del cliente.
""")

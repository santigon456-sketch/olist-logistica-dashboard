import streamlit as st

# ============================================================
# CONFIGURACIÓN GENERAL DEL DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Dashboard Logístico Olist",
    page_icon="🚚",
    layout="wide"
)

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

st.header("Resumen ejecutivo")

col1, col2, col3 = st.columns(3)

col1.metric("Pedidos analizados", "96.470")
col2.metric("Tiempo promedio de entrega", "12,09 días")
col3.metric("Fallas extremas", "1,37%")

st.info("""
La operación presenta un alto cumplimiento frente a la fecha prometida, pero ese indicador no cuenta toda la historia.
Al analizar el tiempo real de entrega, los segmentos logísticos, las rutas y las fallas extremas, aparecen diferencias
operativas relevantes que impactan en la experiencia del cliente.
""")

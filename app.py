import streamlit as st
import pandas as pd
import plotly.express as px
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
segmentos = cargar_csv("metricas_segmento.csv")
fallas = cargar_csv("fallas_vs_no_fallas.csv")

# ============================================================
# MENÚ LATERAL
# ============================================================

st.sidebar.title("🚚 Olist Logística")

seccion = st.sidebar.radio(
    "Navegación",
    [
        "Resumen ejecutivo",
        "Segmentos logísticos",
        "Fallas extremas y satisfacción"
    ]
)

# ============================================================
# SECCIÓN 1 — RESUMEN EJECUTIVO
# ============================================================

if seccion == "Resumen ejecutivo":

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

    st.markdown("""
    ### Lectura ejecutiva

    El dashboard organiza el análisis en torno a una idea central: **la logística de Olist no debe evaluarse solo por la tasa de retraso oficial**.

    Aunque el cumplimiento frente a la fecha prometida es alto, el análisis del tiempo real de entrega permite identificar
    diferencias entre segmentos logísticos, estados, rutas críticas y casos extremos que afectan la satisfacción del cliente.
    """)

# ============================================================
# SECCIÓN 2 — SEGMENTOS LOGÍSTICOS
# ============================================================

elif seccion == "Segmentos logísticos":

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

    st.subheader("Resumen por segmento")

    tabla_segmentos = segmentos.copy()
    tabla_segmentos["tasa_fallas_extremas"] = tabla_segmentos["tasa_fallas_extremas"].round(2)
    tabla_segmentos["indice_riesgo"] = tabla_segmentos["indice_riesgo"].round(2)

    st.dataframe(tabla_segmentos, use_container_width=True)

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

    st.info("""
    La tasa de fallas extremas aumenta a medida que crece la complejidad geográfica del pedido.

    Los pedidos dentro del **mismo estado** presentan el menor riesgo relativo, mientras que los pedidos de **misma región**
    y especialmente de **distinta región** muestran una proporción mayor de entregas extremadamente largas.

    Esto refuerza la idea de que la distancia territorial y el cruce regional agregan fricción logística.
    """)

# ============================================================
# SECCIÓN 3 — FALLAS EXTREMAS Y SATISFACCIÓN
# ============================================================

elif seccion == "Fallas extremas y satisfacción":

    st.title("⭐ Fallas extremas y satisfacción del cliente")

    st.markdown("""
    En esta sección se compara la operación estándar contra los pedidos clasificados como **fallas extremas**.

    Una falla extrema corresponde a un pedido cuyo tiempo real de entrega supera el umbral extremo definido en el análisis exploratorio.
    En este proyecto, ese umbral fue de **más de 42 días**.
    """)

    st.markdown("---")

    st.subheader("Comparación general")

    st.dataframe(fallas, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_review = px.bar(
            fallas,
            x="tipo_pedido",
            y="review_promedio",
            text="review_promedio",
            title="Review promedio según tipo de pedido",
            labels={
                "tipo_pedido": "Tipo de pedido",
                "review_promedio": "Review promedio"
            }
        )

        fig_review.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig_review.update_layout(
            yaxis_range=[0, 5]
        )

        st.plotly_chart(fig_review, use_container_width=True)

    with col2:
        fig_bajas = px.bar(
            fallas,
            x="tipo_pedido",
            y="porcentaje_reviews_bajas",
            text="porcentaje_reviews_bajas",
            title="Porcentaje de reviews bajas según tipo de pedido",
            labels={
                "tipo_pedido": "Tipo de pedido",
                "porcentaje_reviews_bajas": "Reviews bajas (%)"
            }
        )

        fig_bajas.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        st.plotly_chart(fig_bajas, use_container_width=True)

    st.subheader("Tiempo de entrega promedio")

    fig_tiempo = px.bar(
        fallas,
        x="tipo_pedido",
        y="tiempo_promedio",
        text="tiempo_promedio",
        title="Tiempo promedio de entrega: pedidos no extremos vs fallas extremas",
        labels={
            "tipo_pedido": "Tipo de pedido",
            "tiempo_promedio": "Tiempo promedio de entrega (días)"
        }
    )

    fig_tiempo.update_traces(
        texttemplate="%{text:.2f} días",
        textposition="outside"
    )

    st.plotly_chart(fig_tiempo, use_container_width=True)

    st.error("""
    Las fallas extremas representan una proporción baja del total de pedidos, pero tienen un impacto muy alto
    en la experiencia del cliente.

    Mientras los pedidos no extremos tienen una review promedio alta, las fallas extremas muestran una caída fuerte
    en la satisfacción y concentran una proporción mucho mayor de reviews bajas.
    """)

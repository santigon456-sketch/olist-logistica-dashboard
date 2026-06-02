import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
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
ASSETS_DIR = Path("assets")

# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def cargar_csv(nombre_archivo):
    return pd.read_csv(DATA_DIR / nombre_archivo)

@st.cache_data
def cargar_geojson(nombre_archivo):
    with open(ASSETS_DIR / nombre_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

kpis = cargar_csv("kpis_generales.csv")
segmentos = cargar_csv("metricas_segmento.csv")
fallas = cargar_csv("fallas_vs_no_fallas.csv")
estados = cargar_csv("metricas_estado.csv")
geojson_brasil = cargar_geojson("brasil_estados.geojson")

# ============================================================
# PREPARACIÓN DE DATOS PARA MAPA
# ============================================================

codigos_ibge_uf = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17",
    "MA": "21", "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28", "BA": "29",
    "MG": "31", "ES": "32", "RJ": "33", "SP": "35",
    "PR": "41", "SC": "42", "RS": "43",
    "MS": "50", "MT": "51", "GO": "52", "DF": "53"
}

estados["codarea"] = estados["customer_state"].map(codigos_ibge_uf)

# Aseguramos que el código del GeoJSON sea texto
# y creamos un ID explícito para que Plotly pueda matchear cada estado
for feature in geojson_brasil["features"]:
    codarea = str(feature["properties"]["codarea"])
    feature["properties"]["codarea"] = codarea
    feature["id"] = codarea
# ============================================================
# MENÚ LATERAL
# ============================================================

st.sidebar.title("🚚 Olist Logística")

seccion = st.sidebar.radio(
    "Navegación",
    [
        "Resumen ejecutivo",
        "Segmentos logísticos",
        "Riesgo por estado",
        "Mapa de riesgo",
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
# SECCIÓN 3 — RIESGO POR ESTADO
# ============================================================

elif seccion == "Riesgo por estado":

    st.title("🗺️ Riesgo logístico por estado")

    st.markdown("""
    En esta sección se analiza cómo se distribuyen las fallas extremas según el estado de destino del cliente.

    Es importante distinguir entre dos miradas:

    - **Cantidad de fallas extremas:** muestra dónde se acumula mayor volumen de problemas.
    - **Tasa de fallas extremas:** muestra el riesgo relativo, es decir, qué proporción de pedidos termina en una entrega extremadamente larga.

    Un estado puede tener muchas fallas simplemente porque tiene muchos pedidos. Por eso, la tasa permite una comparación más justa entre estados.
    """)

    st.markdown("---")

    st.subheader("Tabla de métricas por estado")

    tabla_estados = estados.copy()

    columnas_redondear = [
        "tasa_fallas_extremas",
        "tiempo_promedio",
        "tiempo_mediano",
        "review_promedio"
    ]

    for col in columnas_redondear:
        if col in tabla_estados.columns:
            tabla_estados[col] = tabla_estados[col].round(2)

    st.dataframe(tabla_estados, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Top estados por cantidad de fallas extremas")

        top_fallas = (
            estados
            .sort_values("fallas_extremas", ascending=False)
            .head(10)
        )

        fig_fallas = px.bar(
            top_fallas,
            x="fallas_extremas",
            y="customer_state",
            orientation="h",
            text="fallas_extremas",
            title="Estados con mayor cantidad de fallas extremas",
            labels={
                "fallas_extremas": "Cantidad de fallas extremas",
                "customer_state": "Estado"
            }
        )

        fig_fallas.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        fig_fallas.update_traces(
            textposition="outside"
        )

        st.plotly_chart(fig_fallas, use_container_width=True)

    with col2:

        st.subheader("Top estados por tasa de fallas extremas")

        top_tasa = (
            estados
            .sort_values("tasa_fallas_extremas", ascending=False)
            .head(10)
        )

        fig_tasa = px.bar(
            top_tasa,
            x="tasa_fallas_extremas",
            y="customer_state",
            orientation="h",
            text="tasa_fallas_extremas",
            title="Estados con mayor riesgo relativo",
            labels={
                "tasa_fallas_extremas": "Tasa de fallas extremas (%)",
                "customer_state": "Estado"
            }
        )

        fig_tasa.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        fig_tasa.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        st.plotly_chart(fig_tasa, use_container_width=True)

    st.info("""
    Esta comparación permite separar volumen de riesgo.

    Los estados con mayor cantidad de fallas extremas pueden estar asociados a mayor volumen de pedidos.
    En cambio, los estados con mayor tasa de fallas extremas indican mayor riesgo relativo para los pedidos que llegan a ese destino.

    En la sección de mapa, esta misma información se representa geográficamente sobre Brasil.
    """)

# ============================================================
# SECCIÓN 4 — MAPA DE RIESGO
# ============================================================

elif seccion == "Mapa de riesgo":

    st.title("🗺️ Mapa de riesgo logístico por estado")

    st.markdown("""
    Este mapa colorea los estados de Brasil según una métrica logística seleccionada.

    Permite observar visualmente que el riesgo operativo no se distribuye de manera homogénea en el territorio.
    """)

    st.markdown("---")

    metrica = st.radio(
        "Seleccioná la métrica a visualizar",
        [
            "tasa_fallas_extremas",
            "fallas_extremas",
            "tiempo_promedio",
            "review_promedio"
        ],
        horizontal=True
    )

    nombres_metricas = {
        "tasa_fallas_extremas": "Tasa de fallas extremas (%)",
        "fallas_extremas": "Cantidad de fallas extremas",
        "tiempo_promedio": "Tiempo promedio de entrega (días)",
        "review_promedio": "Review promedio"
    }

    estados_mapa = estados.copy()

    fig_mapa = go.Figure(
        go.Choroplethmapbox(
            geojson=geojson_brasil,
            locations=estados_mapa["codarea"],
            z=estados_mapa[metrica],
            featureidkey="id",
            colorscale="Reds",
            marker_opacity=0.85,
            marker_line_width=0.6,
            text=estados_mapa["customer_state"],
            customdata=estados_mapa[
                [
                    "pedidos",
                    "fallas_extremas",
                    "tasa_fallas_extremas",
                    "tiempo_promedio",
                    "review_promedio"
                ]
            ],
            hovertemplate=(
                "<b>Estado: %{text}</b><br>"
                "Pedidos: %{customdata[0]}<br>"
                "Fallas extremas: %{customdata[1]}<br>"
                "Tasa de fallas extremas: %{customdata[2]:.2f}%<br>"
                "Tiempo promedio: %{customdata[3]:.2f} días<br>"
                "Review promedio: %{customdata[4]:.2f}<extra></extra>"
            ),
            colorbar_title=nombres_metricas[metrica]
        )
    )

    fig_mapa.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3.1,
        mapbox_center={"lat": -14.2, "lon": -51.9},
        height=650,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title=nombres_metricas[metrica]
    )

    st.plotly_chart(fig_mapa, use_container_width=True)

    st.info("""
    El mapa permite diferenciar entre volumen y riesgo relativo.

    La cantidad de fallas extremas muestra dónde se acumulan más problemas.
    La tasa de fallas extremas muestra qué estados tienen mayor proporción de entregas extremadamente largas sobre el total de pedidos recibidos.
    """)
# ============================================================
# SECCIÓN 5 — FALLAS EXTREMAS Y SATISFACCIÓN
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

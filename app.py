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
metricas_modelo = cargar_csv("metricas_modelo.csv")
rutas = cargar_csv("metricas_rutas.csv")
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
        "Rutas críticas",
        "Fallas extremas y satisfacción",
        "Modelo predictivo",
        "Conclusiones y recomendaciones"
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

# ============================================================
# SECCIÓN 6 — MODELO PREDICTIVO
# ============================================================

elif seccion == "Modelo predictivo":

    st.title("🤖 Modelo predictivo simple")

    st.markdown("""
    En esta sección se resume la primera aproximación al modelado predictivo del proyecto.

    El objetivo del modelo fue estimar el **tiempo real de entrega** de un pedido a partir de variables logísticas,
    geográficas y operativas.

    Se compararon tres enfoques:

    - **Baseline:** predice siempre el promedio del tiempo real de entrega.
    - **Regresión lineal simple:** usa solamente el tiempo estimado de entrega.
    - **Regresión lineal múltiple:** incorpora variables logísticas adicionales, como región, segmento, peso, flete y rutas específicas.
    """)

    st.markdown("---")

    st.subheader("Comparación de modelos")

    tabla_modelo = metricas_modelo.copy()

    columnas_redondear = [
        "R2",
        "MAE_dias",
        "MSE_dias",
        "RMSE_dias",
        "mejora_MAE_vs_baseline_pct",
        "mejora_RMSE_vs_baseline_pct"
    ]

    for col in columnas_redondear:
        if col in tabla_modelo.columns:
            tabla_modelo[col] = tabla_modelo[col].round(2)

    st.dataframe(tabla_modelo, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Error promedio absoluto")

        fig_mae = px.bar(
            metricas_modelo,
            x="Modelo",
            y="MAE_dias",
            text="MAE_dias",
            title="MAE por modelo",
            labels={
                "Modelo": "Modelo",
                "MAE_dias": "MAE (días)"
            }
        )

        fig_mae.update_traces(
            texttemplate="%{text:.2f} días",
            textposition="outside"
        )

        fig_mae.update_layout(
            xaxis_tickangle=-20
        )

        st.plotly_chart(fig_mae, use_container_width=True)

    with col2:

        st.subheader("Capacidad explicativa del modelo")

        fig_r2 = px.bar(
            metricas_modelo,
            x="Modelo",
            y="R2",
            text="R2",
            title="R² por modelo",
            labels={
                "Modelo": "Modelo",
                "R2": "R²"
            }
        )

        fig_r2.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig_r2.update_layout(
            xaxis_tickangle=-20
        )

        st.plotly_chart(fig_r2, use_container_width=True)

    st.info("""
    El modelo múltiple obtiene el mejor desempeño: reduce el error promedio absoluto a **5,25 días**
    y alcanza un **R² de 0,24**.

    Esto indica que las variables logísticas aportan información para estimar el tiempo real de entrega.
    Sin embargo, el R² moderado-bajo muestra que una parte importante de la variabilidad sigue sin explicarse,
    lo cual es esperable en un fenómeno logístico con rutas críticas, outliers y factores operativos no observados.
    """)

    st.markdown("""
    ### Lectura ejecutiva

    El modelado no busca reemplazar el análisis exploratorio, sino complementarlo.

    La regresión lineal simple muestra que el tiempo estimado de entrega contiene información útil.
    La regresión lineal múltiple mejora el resultado al incorporar variables logísticas adicionales.

    Por lo tanto, el modelo refuerza la idea central del proyecto: **la logística importa y no puede evaluarse únicamente con la fecha prometida de entrega**.
    """)
# ============================================================
# SECCIÓN 7 — CONCLUSIONES Y RECOMENDACIONES
# ============================================================

elif seccion == "Conclusiones y recomendaciones":

    st.title("✅ Conclusiones y recomendaciones")

    st.markdown("""
    Esta sección resume los principales aprendizajes del análisis logístico y propone líneas de acción
    orientadas a mejorar el monitoreo operativo de la red de entregas.
    """)

    st.markdown("---")

    st.header("Conclusiones principales")

    st.markdown("""
    ### 1. El cumplimiento oficial no cuenta toda la historia

    La operación presenta una tasa de cumplimiento alta frente a la fecha prometida. Sin embargo,
    el análisis del tiempo real de entrega y del colchón de seguridad muestra que la promesa comercial
    puede estar incorporando márgenes amplios.

    Por eso, evaluar solo la tasa de retraso oficial puede ocultar diferencias reales de desempeño logístico.
    """)

    st.markdown("""
    ### 2. La complejidad geográfica aumenta el riesgo operativo

    Los pedidos dentro del mismo estado presentan menor riesgo relativo, mientras que los pedidos de misma región
    y distinta región concentran una mayor proporción de fallas extremas.

    Esto indica que la distancia territorial y el cruce regional agregan fricción a la operación logística.
    """)

    st.markdown("""
    ### 3. El riesgo logístico no se distribuye de forma homogénea

    El análisis por estado y el mapa de riesgo muestran que algunos destinos presentan mayor proporción de entregas
    extremadamente largas.

    Esta mirada territorial permite diferenciar entre volumen de pedidos y riesgo relativo.
    """)

    st.markdown("""
    ### 4. Las fallas extremas son pocas, pero impactan mucho en la satisfacción

    Aunque las fallas extremas representan una proporción reducida del total de pedidos, presentan tiempos de entrega
    muy superiores y una caída fuerte en las calificaciones de los clientes.

    Esto muestra que los eventos extremos tienen un impacto desproporcionado sobre la experiencia del cliente.
    """)

    st.markdown("""
    ### 5. El modelo predictivo confirma que las variables logísticas aportan información

    La regresión lineal múltiple mejora al baseline y al modelo simple, lo que indica que variables como región,
    segmento logístico, rutas específicas y características del pedido ayudan a estimar el tiempo real de entrega.

    Sin embargo, el desempeño del modelo también muestra que la logística tiene variabilidad no explicada y factores
    operativos que no están presentes en el dataset.
    """)

    st.markdown("---")

    st.header("Recomendaciones operativas")

    col1, col2 = st.columns(2)

    with col1:
        st.success("""
        **1. Separar indicadores de cumplimiento y eficiencia real**

        Monitorear por separado la tasa de retraso oficial, el tiempo real de entrega y el colchón de seguridad.
        Esto evita evaluar la operación únicamente desde la promesa comercial.
        """)

        st.success("""
        **2. Definir alertas por segmento logístico**

        Utilizar umbrales diferenciados para pedidos de mismo estado, misma región y distinta región,
        ya que no presentan el mismo nivel de riesgo operativo.
        """)

        st.success("""
        **3. Priorizar fallas extremas**

        Aunque son pocos casos, las fallas extremas tienen alto impacto en satisfacción.
        Conviene tratarlas como eventos críticos y no solo como outliers estadísticos.
        """)

    with col2:
        st.success("""
        **4. Monitorear estados y rutas críticas**

        Usar mapas y rankings para identificar destinos o rutas con mayor concentración de problemas
        y mayor riesgo relativo.
        """)

        st.success("""
        **5. Revisar promesas de entrega por región**

        El colchón de seguridad debería analizarse por segmento y región para detectar promesas demasiado amplias
        o zonas con mayor incertidumbre logística.
        """)

        st.success("""
        **6. Profundizar el modelo con variables operativas adicionales**

        Para una predicción más robusta sería útil incorporar información como transportista, centros logísticos,
        capacidad operativa, clima o eventos excepcionales.
        """)

    st.markdown("---")

    st.info("""
    En síntesis, el análisis muestra que la logística de Olist debe evaluarse desde tres dimensiones:
    **cumplimiento comercial**, **eficiencia operativa real** y **experiencia del cliente**.

    El dashboard permite transformar los hallazgos técnicos del Colab en una herramienta visual para comunicar
    riesgos, prioridades y oportunidades de mejora.
    """)
# ============================================================
# SECCIÓN 8 — RUTAS CRÍTICAS
# ============================================================

elif seccion == "Rutas críticas":

    st.title("🛣️ Rutas críticas")

    st.markdown("""
    Esta sección analiza las rutas entre estado de vendedor y estado de cliente.

    Una ruta se representa como:

    **estado de origen → estado de destino**

    Por ejemplo: **SP → RJ** o **SP → PA**.

    El objetivo es diferenciar entre rutas que acumulan muchas fallas por volumen operativo
    y rutas que presentan mayor riesgo relativo por su tasa de fallas extremas.
    """)

    st.markdown("---")

    # ------------------------------------------------------------
    # PREPARACIÓN DE DATOS
    # ------------------------------------------------------------

    rutas_dashboard = rutas.copy()

    # Definimos rutas críticas como rutas con tasa de fallas superior a la tasa global
    tasa_global_fallas = 1.37

    rutas_dashboard["ruta_critica"] = (
        rutas_dashboard["tasa_fallas_extremas"] > tasa_global_fallas
    )

    # Redondeo para tabla
    tabla_rutas = rutas_dashboard.copy()

    columnas_redondear = [
        "tiempo_promedio",
        "tiempo_mediano",
        "p90_tiempo_entrega",
        "tasa_retraso",
        "tasa_fallas_extremas"
    ]

    for col in columnas_redondear:
        if col in tabla_rutas.columns:
            tabla_rutas[col] = tabla_rutas[col].round(2)

    # ------------------------------------------------------------
    # KPIS DE RUTAS
    # ------------------------------------------------------------

    st.subheader("Resumen de rutas analizadas")

    total_rutas = rutas_dashboard["ruta"].nunique()
    rutas_criticas = rutas_dashboard["ruta_critica"].sum()
    tasa_rutas_criticas = rutas_criticas / total_rutas * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Rutas analizadas", f"{total_rutas:,.0f}".replace(",", "."))
    col2.metric("Rutas críticas", f"{rutas_criticas:,.0f}".replace(",", "."))
    col3.metric("Rutas críticas (%)", f"{tasa_rutas_criticas:.2f}%")

    st.info("""
    Se consideran rutas críticas aquellas rutas con una tasa de fallas extremas superior a la tasa global del proyecto,
    estimada en **1,37%**.

    Este criterio permite identificar rutas cuyo riesgo relativo está por encima del promedio general de la operación.
    """)

    st.markdown("---")

    # ------------------------------------------------------------
    # TABLA
    # ------------------------------------------------------------

    st.subheader("Tabla de rutas")

    st.dataframe(
        tabla_rutas[
            [
                "ruta",
                "seller_state",
                "customer_state",
                "segmento_logistico",
                "pedidos",
                "tiempo_promedio",
                "p90_tiempo_entrega",
                "fallas_extremas",
                "tasa_fallas_extremas",
                "ruta_critica"
            ]
        ],
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------------------
    # GRÁFICOS PRINCIPALES
    # ------------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Top rutas por cantidad de fallas extremas")

        top_fallas = (
            rutas_dashboard
            .sort_values("fallas_extremas", ascending=False)
            .head(15)
        )

        fig_top_fallas = px.bar(
            top_fallas,
            x="fallas_extremas",
            y="ruta",
            orientation="h",
            text="fallas_extremas",
            title="Rutas con mayor cantidad de fallas extremas",
            labels={
                "fallas_extremas": "Fallas extremas",
                "ruta": "Ruta"
            },
            hover_data=[
                "pedidos",
                "segmento_logistico",
                "tasa_fallas_extremas",
                "tiempo_promedio"
            ]
        )

        fig_top_fallas.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        fig_top_fallas.update_traces(
            textposition="outside"
        )

        st.plotly_chart(fig_top_fallas, use_container_width=True)

    with col2:

        st.subheader("Top rutas por tasa de fallas extremas")

        top_tasa = (
            rutas_dashboard
            .sort_values("tasa_fallas_extremas", ascending=False)
            .head(15)
        )

        fig_top_tasa = px.bar(
            top_tasa,
            x="tasa_fallas_extremas",
            y="ruta",
            orientation="h",
            text="tasa_fallas_extremas",
            title="Rutas con mayor riesgo relativo",
            labels={
                "tasa_fallas_extremas": "Tasa de fallas extremas (%)",
                "ruta": "Ruta"
            },
            hover_data=[
                "pedidos",
                "segmento_logistico",
                "fallas_extremas",
                "tiempo_promedio"
            ]
        )

        fig_top_tasa.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        fig_top_tasa.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        st.plotly_chart(fig_top_tasa, use_container_width=True)

    st.markdown("---")

    # ------------------------------------------------------------
    # RUTAS CRÍTICAS POR SEGMENTO
    # ------------------------------------------------------------

    st.subheader("Rutas críticas por segmento logístico")

    rutas_por_segmento = (
        rutas_dashboard
        .groupby("segmento_logistico")
        .agg(
            rutas_totales=("ruta", "nunique"),
            rutas_criticas=("ruta_critica", "sum")
        )
        .reset_index()
    )

    rutas_por_segmento["porcentaje_rutas_criticas"] = (
        rutas_por_segmento["rutas_criticas"] /
        rutas_por_segmento["rutas_totales"] * 100
    )

    fig_segmento = px.bar(
        rutas_por_segmento,
        x="segmento_logistico",
        y="rutas_criticas",
        text="rutas_criticas",
        title="Cantidad de rutas críticas por segmento logístico",
        labels={
            "segmento_logistico": "Segmento logístico",
            "rutas_criticas": "Cantidad de rutas críticas"
        },
        hover_data=[
            "rutas_totales",
            "porcentaje_rutas_criticas"
        ]
    )

    fig_segmento.update_traces(
        textposition="outside"
    )

    st.plotly_chart(fig_segmento, use_container_width=True)

    # ------------------------------------------------------------
    # GRÁFICO DE BURBUJAS
    # ------------------------------------------------------------

    st.subheader("Volumen operativo vs riesgo relativo")

    fig_burbujas = px.scatter(
        rutas_dashboard,
        x="pedidos",
        y="tasa_fallas_extremas",
        size="fallas_extremas",
        color="segmento_logistico",
        hover_name="ruta",
        hover_data=[
            "tiempo_promedio",
            "p90_tiempo_entrega",
            "fallas_extremas"
        ],
        title="Relación entre volumen de pedidos y tasa de fallas extremas",
        labels={
            "pedidos": "Cantidad de pedidos",
            "tasa_fallas_extremas": "Tasa de fallas extremas (%)",
            "segmento_logistico": "Segmento logístico"
        }
    )

    fig_burbujas.add_hline(
        y=tasa_global_fallas,
        line_dash="dash",
        annotation_text="Tasa global de fallas extremas: 1,37%",
        annotation_position="top left"
    )

    st.plotly_chart(fig_burbujas, use_container_width=True)

    st.info("""
    La sección de rutas permite separar dos dimensiones distintas:

    - **Volumen operativo:** rutas con muchos pedidos pueden acumular más fallas en términos absolutos.
    - **Riesgo relativo:** rutas con mayor tasa de fallas extremas presentan mayor proporción de entregas anormalmente largas.

    Las rutas más prioritarias para monitoreo son aquellas que combinan alto volumen con una tasa de fallas superior al promedio general.
    """)

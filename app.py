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
coeficientes_modelo = cargar_csv("coeficientes_modelo.csv")
rutas = cargar_csv("metricas_rutas.csv")
top_rutas_mapa = cargar_csv("top_rutas_mapa.csv")
pedidos = cargar_csv("base_dashboard_pedidos.csv")
impacto_sp_rj = cargar_csv("impacto_sp_rj_misma_region.csv")
paciencia_diaria = cargar_csv("paciencia_segmento_diaria.csv")
umbrales_paciencia = cargar_csv("umbrales_paciencia_segmento.csv")
geojson_brasil = cargar_geojson("brasil_estados.geojson")
riesgo_region_comprador = cargar_csv("riesgo_operativo_region_comprador.csv")

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
regiones_brasil_uf = {
    "RO": "Norte", "AC": "Norte", "AM": "Norte", "RR": "Norte", "PA": "Norte", "AP": "Norte", "TO": "Norte",
    "MA": "Nordeste", "PI": "Nordeste", "CE": "Nordeste", "RN": "Nordeste", "PB": "Nordeste", "PE": "Nordeste", "AL": "Nordeste", "SE": "Nordeste", "BA": "Nordeste",
    "MG": "Sudeste", "ES": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "SC": "Sul", "RS": "Sul",
    "MS": "Centro-Oeste", "MT": "Centro-Oeste", "GO": "Centro-Oeste", "DF": "Centro-Oeste"
}
estados["codarea"] = estados["customer_state"].map(codigos_ibge_uf)
estados["region_brasil"] = estados["customer_state"].map(regiones_brasil_uf)

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
    "Seleccioná una sección",
    [
        "Resumen ejecutivo",
        "Desempeño logístico general",
        "Segmentos logísticos",
        "Riesgo por estado",
        "Mapa de riesgo",
        "Riesgo por región del comprador",
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
    st.markdown("""
    ### Ficha técnica del análisis

    - **Dataset:** Brazilian E-Commerce Public Dataset by Olist.
    - **Fuente:** Kaggle / Olist.
    - **Período principal:** pedidos realizados entre septiembre de 2016 y octubre de 2018.
    - **Alcance geográfico:** Brasil.
    - **Unidad principal de análisis:** pedido.
    - **Enfoque del proyecto:** desempeño logístico, tiempos de entrega, rutas críticas, fallas extremas y satisfacción del cliente.
    """)

    with st.expander("📘 Glosario de variables utilizadas en el análisis"):
        st.markdown("""
        Para facilitar la lectura del dashboard, se resumen a continuación las principales variables utilizadas:

        - **Tiempo real de entrega:** cantidad de días que tardó efectivamente un pedido en llegar al cliente.

        - **Tiempo estimado de entrega:** cantidad de días prometida o prevista por la plataforma para entregar el pedido.

        - **Días de retraso:** diferencia entre la fecha real de entrega y la fecha estimada. Si el valor es positivo, el pedido llegó después de lo prometido.

        - **Pedido retrasado:** indica si el pedido llegó después de la fecha estimada de entrega.

        - **Cumplimiento oficial:** porcentaje de pedidos que llegaron dentro de la fecha estimada o antes.

        - **Colchón de seguridad:** margen de días entre el tiempo estimado y el tiempo real de entrega.  
          En términos simples, mide cuánto margen tenía la promesa de entrega.  
          Por ejemplo, si un pedido estaba prometido para 20 días y llegó en 12, hubo un colchón de 8 días.

        - **Falla extrema:** pedido con un tiempo real de entrega anormalmente alto. En este proyecto se considera falla extrema cuando el pedido tarda más de **42 días**.

        - **Review promedio:** calificación promedio dada por el cliente, en una escala de 1 a 5 estrellas.

        - **Review baja:** calificación negativa o insatisfactoria, definida en el análisis como una review de 1 o 2 estrellas.

        - **Segmento logístico:** clasificación del pedido según la relación geográfica entre vendedor y comprador: mismo estado, misma región o distinta región.

        - **Tasa de fallas extremas:** porcentaje de pedidos que terminaron siendo fallas extremas dentro de un grupo, estado, ruta o segmento.

        - **Índice de riesgo:** comparación entre la tasa de fallas de un segmento y la tasa global del proyecto. Un valor mayor a 1 indica riesgo superior al promedio.
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

    st.subheader("Mapa de macro-regiones de Brasil")

    st.markdown("""
    Este mapa divide Brasil en sus cinco macro-regiones: **Norte, Nordeste, Centro-Oeste, Sudeste y Sul**.

    La división regional ayuda a interpretar los segmentos logísticos del proyecto.  
    Un pedido clasificado como **Misma Región** no necesariamente implica cercanía operativa baja:
    puede involucrar rutas de alto volumen o alta complejidad, como **SP → RJ** dentro del Sudeste.
    """)

    estados_regiones = estados.copy()

    fig_regiones = px.choropleth_mapbox(
        estados_regiones,
        geojson=geojson_brasil,
        locations="codarea",
        color="region_brasil",
        featureidkey="id",
        hover_name="customer_state",
        hover_data={
            "region_brasil": True,
            "pedidos": True,
            "fallas_extremas": True,
            "tasa_fallas_extremas": ":.2f",
            "codarea": False
        },
        mapbox_style="carto-positron",
        zoom=3.1,
        center={"lat": -14.2, "lon": -51.9},
        opacity=0.75,
        title="División de Brasil por macro-regiones"
    )

    fig_regiones.update_layout(
        height=650,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend_title_text="Región"
    )

    st.plotly_chart(fig_regiones, use_container_width=True)

    st.info("""
    La región **Sudeste** concentra estados logísticamente relevantes como **SP** y **RJ**.
    Por eso, aunque la ruta **SP → RJ** pertenezca al segmento **Misma Región**,
    puede comportarse como una ruta crítica por volumen, densidad operativa o complejidad de distribución.
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
    
    st.markdown("---")

    st.subheader("¿Por qué 'Misma Región' falla más de lo esperado?")

    st.markdown("""
    En principio, podría esperarse que los pedidos dentro de una misma región tengan un riesgo logístico intermedio:
    mayor que los pedidos dentro del mismo estado, pero menor que los pedidos entre regiones distintas.

    Sin embargo, el segmento **Misma Región** presenta una tasa de fallas extremas relativamente elevada.
    Para entender si ese comportamiento es general del segmento o está concentrado en alguna ruta específica,
    se compara el segmento completo contra el mismo segmento excluyendo la ruta **SP → RJ**.
    """)

    impacto_segmento = impacto_sp_rj.copy()

    columnas_numericas_impacto = [
        "pedidos",
        "tiempo_promedio",
        "tiempo_mediano",
        "tasa_retraso_oficial",
        "fallas_extremas",
        "tasa_fallas_extremas"
    ]

    for columna in columnas_numericas_impacto:
        if columna in impacto_segmento.columns:
            impacto_segmento[columna] = pd.to_numeric(
                impacto_segmento[columna],
                errors="coerce"
            )

    escenario_completo = impacto_segmento[
        impacto_segmento["escenario"].str.contains("completa", case=False, na=False)
    ].iloc[0]

    escenario_sin_sp_rj = impacto_segmento[
        impacto_segmento["escenario"].str.contains("sin", case=False, na=False)
    ].iloc[0]

    tasa_completa = escenario_completo["tasa_fallas_extremas"]
    tasa_sin_sp_rj = escenario_sin_sp_rj["tasa_fallas_extremas"]
    diferencia_tasa = tasa_completa - tasa_sin_sp_rj

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Misma Región completa",
        f"{tasa_completa:.2f}%",
        help="Tasa de fallas extremas considerando todas las rutas de Misma Región."
    )

    col2.metric(
        "Misma Región sin SP → RJ",
        f"{tasa_sin_sp_rj:.2f}%",
        help="Tasa de fallas extremas excluyendo la ruta SP → RJ."
    )

    col3.metric(
        "Diferencia",
        f"{diferencia_tasa:.2f} p.p.",
        help="Diferencia en puntos porcentuales entre ambos escenarios."
    )

    tabla_impacto = impacto_segmento.rename(columns={
        "escenario": "Escenario",
        "pedidos": "Pedidos",
        "tiempo_promedio": "Tiempo promedio",
        "tiempo_mediano": "Tiempo mediano",
        "tasa_retraso_oficial": "Tasa de retraso oficial (%)",
        "fallas_extremas": "Fallas extremas",
        "tasa_fallas_extremas": "Tasa de fallas extremas (%)"
    })

    st.dataframe(
        tabla_impacto.round(2),
        use_container_width=True
    )

    fig_impacto_sp_rj = px.bar(
        impacto_segmento,
        x="escenario",
        y="tasa_fallas_extremas",
        text="tasa_fallas_extremas",
        title="Impacto de la ruta SP → RJ sobre el segmento Misma Región",
        labels={
            "escenario": "Escenario",
            "tasa_fallas_extremas": "Tasa de fallas extremas (%)"
        }
    )

    fig_impacto_sp_rj.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_impacto_sp_rj.update_layout(
        xaxis_title="Escenario",
        yaxis_title="Tasa de fallas extremas (%)"
    )

    st.plotly_chart(fig_impacto_sp_rj, use_container_width=True)

    if diferencia_tasa > 0:
        st.success(f"""
        Al excluir la ruta **SP → RJ**, la tasa de fallas extremas del segmento **Misma Región**
        baja de **{tasa_completa:.2f}%** a **{tasa_sin_sp_rj:.2f}%**.

        Esto sugiere que el peor desempeño relativo de **Misma Región** no es homogéneo,
        sino que está fuertemente influido por una ruta crítica específica: **SP → RJ**.
        """)
    else:
        st.info("""
        La comparación muestra que la exclusión de SP → RJ no reduce la tasa de fallas extremas.
        En ese caso, el problema del segmento Misma Región debería interpretarse como más distribuido
        entre varias rutas del segmento.
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
    st.markdown("---")

    st.subheader("Umbral de paciencia por segmento logístico")

    st.markdown("""
    Además de comparar pedidos extremos contra no extremos, es útil analizar cómo cambia la satisfacción
    a medida que aumenta el tiempo real de entrega.

    El **umbral de paciencia** se define como el primer día en que el promedio suavizado de review
    cae por debajo de **4 estrellas**. Esta lectura permite observar si la tolerancia del cliente cambia
    según el segmento logístico.
    """)

    paciencia_plot = paciencia_diaria.copy()
    umbrales_plot = umbrales_paciencia.copy()

    columnas_numericas_paciencia = [
        "tiempo_entrega_real",
        "pedidos",
        "review_promedio",
        "porcentaje_reviews_bajas",
        "review_promedio_suavizado",
        "reviews_bajas_suavizado"
    ]

    for columna in columnas_numericas_paciencia:
        if columna in paciencia_plot.columns:
            paciencia_plot[columna] = pd.to_numeric(
                paciencia_plot[columna],
                errors="coerce"
            )

    if "umbral_paciencia_dias" in umbrales_plot.columns:
        umbrales_plot["umbral_paciencia_dias"] = pd.to_numeric(
            umbrales_plot["umbral_paciencia_dias"],
            errors="coerce"
        )

    fig_paciencia = px.line(
        paciencia_plot,
        x="tiempo_entrega_real",
        y="review_promedio_suavizado",
        color="segmento_logistico",
        markers=True,
        title="Paciencia del cliente según tiempo de entrega y segmento logístico",
        labels={
            "tiempo_entrega_real": "Tiempo real de entrega (días)",
            "review_promedio_suavizado": "Review promedio suavizado",
            "segmento_logistico": "Segmento logístico"
        },
        hover_data={
            "pedidos": True,
            "review_promedio": ":.2f",
            "porcentaje_reviews_bajas": ":.2f",
            "reviews_bajas_suavizado": ":.2f"
        }
    )

    fig_paciencia.add_hline(
        y=4.0,
        line_dash="dash",
        annotation_text="Umbral de satisfacción: 4.0",
        annotation_position="bottom right"
    )

    fig_paciencia.update_layout(
        xaxis_title="Tiempo real de entrega (días)",
        yaxis_title="Review promedio suavizado",
        yaxis_range=[1, 5.1]
    )

    st.plotly_chart(fig_paciencia, use_container_width=True)

    st.markdown("### Tabla de umbrales por segmento")

    tabla_umbrales = umbrales_plot.rename(columns={
        "segmento_logistico": "Segmento logístico",
        "umbral_paciencia_dias": "Umbral de paciencia (días)",
        "criterio_umbral": "Criterio",
        "minimo_pedidos_por_dia": "Mínimo de pedidos por día",
        "pedidos_analizados": "Pedidos analizados",
        "review_promedio_general": "Review promedio general",
        "porcentaje_reviews_bajas_promedio": "% reviews bajas promedio"
    })

    st.dataframe(
        tabla_umbrales.round(2),
        use_container_width=True
    )

    st.info("""
    El gráfico muestra que la satisfacción no cae de la misma manera en todos los segmentos logísticos.
    El umbral de paciencia permite identificar desde qué punto el tiempo de entrega empieza a deteriorar
    de forma más clara la experiencia del cliente.

    Esta lectura complementa el análisis de fallas extremas: no solo importa detectar entregas muy largas,
    sino también entender desde cuándo el cliente empieza a penalizar la experiencia.
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
    st.markdown("---")

    st.subheader("Coeficientes principales del modelo múltiple")

    st.markdown("""
    Los coeficientes permiten interpretar qué variables aparecen asociadas con aumentos o disminuciones
    en el tiempo real de entrega estimado por el modelo.

    Un coeficiente positivo indica que la variable está asociada con un aumento del tiempo de entrega estimado.
    Un coeficiente negativo indica que la variable está asociada con una disminución del tiempo de entrega estimado.

    En el caso de variables categóricas, la comparación se realiza contra una categoría base o de referencia.
    """)

    tabla_coeficientes = coeficientes_modelo.copy()

    columnas_coeficientes = [
        "variable_limpia",
        "coeficiente",
        "direccion"
    ]

    columnas_coeficientes = [
        col for col in columnas_coeficientes
        if col in tabla_coeficientes.columns
    ]

    if "coeficiente" in tabla_coeficientes.columns:
        tabla_coeficientes["coeficiente"] = tabla_coeficientes["coeficiente"].round(3)

    st.dataframe(
        tabla_coeficientes[columnas_coeficientes],
        use_container_width=True
    )

    coeficientes_grafico = coeficientes_modelo.copy()

    if "coeficiente_abs" in coeficientes_grafico.columns:
        coeficientes_grafico = (
            coeficientes_grafico
            .sort_values("coeficiente_abs", ascending=True)
            .tail(15)
        )
    else:
        coeficientes_grafico["coeficiente_abs"] = coeficientes_grafico["coeficiente"].abs()
        coeficientes_grafico = (
            coeficientes_grafico
            .sort_values("coeficiente_abs", ascending=True)
            .tail(15)
        )

    fig_coef = px.bar(
        coeficientes_grafico,
        x="coeficiente",
        y="variable_limpia",
        orientation="h",
        color="direccion",
        title="Principales coeficientes del modelo múltiple",
        labels={
            "coeficiente": "Coeficiente",
            "variable_limpia": "Variable",
            "direccion": "Dirección del efecto"
        }
    )

    fig_coef.update_layout(
        xaxis_title="Coeficiente estimado",
        yaxis_title="Variable"
    )

    st.plotly_chart(fig_coef, use_container_width=True)

    st.info("""
    Los coeficientes refuerzan la interpretación logística del modelo: algunas regiones, segmentos y rutas específicas
    aparecen asociadas con mayores tiempos de entrega estimados.

    Estos valores no deben interpretarse como causalidad directa, sino como asociaciones dentro del modelo lineal.
    """)
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
    st.markdown("---")

    st.subheader("Top 5 rutas críticas: volumen vs tasa de fallas")

    st.markdown("""
    Para priorizar acciones operativas, no alcanza con mirar un solo indicador.

    Una ruta puede ser crítica porque concentra muchas fallas extremas en términos absolutos,
    o porque tiene una tasa de fallas muy alta en relación con su propio volumen de pedidos.

    Por eso se comparan dos rankings complementarios:
    """)

    col1, col2 = st.columns(2)

    # ------------------------------------------------------------
    # TOP 5 POR VOLUMEN DE FALLAS EXTREMAS
    # ------------------------------------------------------------

    top5_volumen_fallas = (
        rutas
        .sort_values("fallas_extremas", ascending=False)
        .head(5)
        .copy()
    )

    with col1:
        st.markdown("### Mayor volumen de fallas")

        st.dataframe(
            top5_volumen_fallas[
                [
                    "ruta",
                    "segmento_logistico",
                    "pedidos",
                    "fallas_extremas",
                    "tasa_fallas_extremas",
                    "tiempo_promedio"
                ]
            ].round(2),
            use_container_width=True
        )

        fig_top5_volumen = px.bar(
            top5_volumen_fallas.sort_values("fallas_extremas", ascending=True),
            x="fallas_extremas",
            y="ruta",
            orientation="h",
            text="fallas_extremas",
            title="Top 5 rutas por cantidad de fallas extremas",
            labels={
                "fallas_extremas": "Fallas extremas",
                "ruta": "Ruta"
            }
        )

        fig_top5_volumen.update_traces(
            textposition="outside"
        )

        fig_top5_volumen.update_layout(
            xaxis_title="Cantidad de fallas extremas",
            yaxis_title="Ruta"
        )

        st.plotly_chart(fig_top5_volumen, use_container_width=True)

    # ------------------------------------------------------------
    # TOP 5 POR TASA DE FALLAS EXTREMAS
    # ------------------------------------------------------------

    top5_tasa_fallas = (
        rutas
        .sort_values("tasa_fallas_extremas", ascending=False)
        .head(5)
        .copy()
    )

    with col2:
        st.markdown("### Mayor tasa de fallas")

        st.dataframe(
            top5_tasa_fallas[
                [
                    "ruta",
                    "segmento_logistico",
                    "pedidos",
                    "fallas_extremas",
                    "tasa_fallas_extremas",
                    "tiempo_promedio"
                ]
            ].round(2),
            use_container_width=True
        )

        fig_top5_tasa = px.bar(
            top5_tasa_fallas.sort_values("tasa_fallas_extremas", ascending=True),
            x="tasa_fallas_extremas",
            y="ruta",
            orientation="h",
            text="tasa_fallas_extremas",
            title="Top 5 rutas por tasa de fallas extremas",
            labels={
                "tasa_fallas_extremas": "Tasa de fallas extremas (%)",
                "ruta": "Ruta"
            }
        )

        fig_top5_tasa.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_top5_tasa.update_layout(
            xaxis_title="Tasa de fallas extremas (%)",
            yaxis_title="Ruta"
        )

        st.plotly_chart(fig_top5_tasa, use_container_width=True)

    st.info("""
    El ranking por **volumen de fallas** permite identificar rutas que concentran muchos casos críticos
    y, por lo tanto, tienen mayor impacto operativo total.

    El ranking por **tasa de fallas** permite detectar rutas proporcionalmente más riesgosas,
    incluso si su volumen absoluto de pedidos es menor.

    En conjunto, ambos rankings ayudan a priorizar rutas: unas por impacto total y otras por riesgo relativo.
    """)
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
    st.markdown("---")

    st.subheader("Mapa de top rutas críticas")

    st.markdown("""
    Este mapa muestra las rutas más críticas desde dos perspectivas complementarias:

    - **Volumen:** rutas que concentran mayor cantidad absoluta de fallas extremas.
    - **Tasa:** rutas con mayor proporción de fallas extremas respecto de sus pedidos.
    - **Ambas:** rutas que aparecen en los dos rankings.

    Esta distinción es importante porque una ruta puede ser prioritaria por impacto operativo total,
    aunque su tasa no sea la más alta, o puede ser riesgosa proporcionalmente aunque tenga menor volumen.
    """)

    rutas_mapa = top_rutas_mapa.copy()

    columnas_numericas_mapa = [
        "pedidos",
        "fallas_extremas",
        "tasa_fallas_extremas",
        "tiempo_promedio",
        "lat_origen",
        "lon_origen",
        "lat_destino",
        "lon_destino"
    ]

    for columna in columnas_numericas_mapa:
        if columna in rutas_mapa.columns:
            rutas_mapa[columna] = pd.to_numeric(rutas_mapa[columna], errors="coerce")

    colores_criticidad = {
        "Volumen": "red",
        "Tasa": "blue",
        "Ambas": "purple"
    }

    fig_rutas_mapa = go.Figure()

    # Base del mapa: estados de Brasil
    fig_rutas_mapa.add_trace(
        go.Choroplethmapbox(
            geojson=geojson_brasil,
            locations=estados["codarea"],
            z=[1] * len(estados),
            featureidkey="id",
            colorscale=[[0, "lightgray"], [1, "lightgray"]],
            marker_opacity=0.25,
            marker_line_width=0.5,
            showscale=False,
            hoverinfo="skip"
        )
    )

    # Líneas de rutas críticas
    for _, fila in rutas_mapa.iterrows():

        tipo = fila["tipo_criticidad"]
        color = colores_criticidad.get(tipo, "gray")

        texto_hover = (
            f"<b>Ruta: {fila['ruta']}</b><br>"
            f"Tipo de criticidad: {tipo}<br>"
            f"Segmento: {fila['segmento_logistico']}<br>"
            f"Pedidos: {fila['pedidos']:.0f}<br>"
            f"Fallas extremas: {fila['fallas_extremas']:.0f}<br>"
            f"Tasa de fallas extremas: {fila['tasa_fallas_extremas']:.2f}%<br>"
            f"Tiempo promedio: {fila['tiempo_promedio']:.2f} días"
        )

        fig_rutas_mapa.add_trace(
            go.Scattermapbox(
                mode="lines+markers",
                lon=[fila["lon_origen"], fila["lon_destino"]],
                lat=[fila["lat_origen"], fila["lat_destino"]],
                line=dict(width=4, color=color),
                marker=dict(size=8, color=color),
                name=tipo,
                text=texto_hover,
                hovertemplate="%{text}<extra></extra>",
                showlegend=False
            )
        )

    # Leyenda manual
    for tipo, color in colores_criticidad.items():
        if tipo in rutas_mapa["tipo_criticidad"].unique():
            fig_rutas_mapa.add_trace(
                go.Scattermapbox(
                    mode="markers",
                    lon=[None],
                    lat=[None],
                    marker=dict(size=10, color=color),
                    name=tipo,
                    showlegend=True
                )
            )

    fig_rutas_mapa.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3.3,
        mapbox_center={"lat": -14.2, "lon": -51.9},
        height=700,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title="Top rutas críticas por volumen y por tasa de fallas extremas",
        legend_title_text="Tipo de criticidad"
    )

    st.plotly_chart(fig_rutas_mapa, use_container_width=True)

    st.info("""
    El mapa permite distinguir rutas críticas por **impacto absoluto** y por **riesgo relativo**.

    Las rutas marcadas por volumen concentran más fallas extremas en cantidad total.
    Las rutas marcadas por tasa muestran un peor desempeño proporcional.
    Si una ruta aparece como **Ambas**, debería considerarse especialmente prioritaria.
    """)
# ============================================================
# SECCIÓN 9 — DESEMPEÑO LOGÍSTICO GENERAL
# ============================================================

elif seccion == "Desempeño logístico general":

    st.title("📦 Desempeño logístico general")

    st.markdown("""
    Esta sección presenta una mirada general sobre los tiempos reales de entrega.

    Antes de analizar segmentos, estados o rutas específicas, es importante observar cómo se distribuye el tiempo
    de entrega en toda la operación y dónde aparecen los pedidos con comportamiento extremo.
    """)

    st.markdown("---")

    # ------------------------------------------------------------
    # PREPARACIÓN DE DATOS
    # ------------------------------------------------------------

    pedidos_dashboard = pedidos.copy()

    pedidos_dashboard["falla_extrema_bool"] = (
        pedidos_dashboard["falla_extrema"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "sí", "si"])
    )

    pedidos_dashboard["tipo_pedido"] = pedidos_dashboard["falla_extrema_bool"].map(
        {
            True: "Fallas extremas",
            False: "Pedidos no extremos"
        }
    )

    # ------------------------------------------------------------
    # KPIS
    # ------------------------------------------------------------

    st.subheader("Indicadores generales de entrega")

    total_pedidos = pedidos_dashboard["order_id"].nunique()
    tiempo_promedio = pedidos_dashboard["tiempo_entrega_real"].mean()
    tiempo_mediano = pedidos_dashboard["tiempo_entrega_real"].median()
    p90_entrega = pedidos_dashboard["tiempo_entrega_real"].quantile(0.90)
    fallas_extremas_total = pedidos_dashboard["falla_extrema_bool"].sum()
    tasa_fallas = fallas_extremas_total / total_pedidos * 100

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Pedidos analizados", f"{total_pedidos:,.0f}".replace(",", "."))
    col2.metric("Tiempo promedio", f"{tiempo_promedio:.2f} días")
    col3.metric("Tiempo mediano", f"{tiempo_mediano:.2f} días")
    col4.metric("P90 entrega", f"{p90_entrega:.2f} días")
    col5.metric("Fallas extremas", f"{tasa_fallas:.2f}%")

    st.markdown("---")

    # ------------------------------------------------------------
    # HISTOGRAMA
    # ------------------------------------------------------------

    st.subheader("Distribución del tiempo real de entrega")

    fig_hist = px.histogram(
        pedidos_dashboard,
        x="tiempo_entrega_real",
        nbins=70,
        title="Distribución del tiempo real de entrega",
        labels={
            "tiempo_entrega_real": "Tiempo real de entrega (días)",
            "count": "Cantidad de pedidos"
        }
    )

    fig_hist.add_vline(
        x=42,
        line_dash="dash",
        line_color="red",
        annotation_text="Umbral extremo: 42 días",
        annotation_position="top right"
    )

    fig_hist.update_layout(
        xaxis_title="Tiempo real de entrega (días)",
        yaxis_title="Cantidad de pedidos"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    st.info("""
    La distribución muestra que la mayoría de los pedidos se concentra en tiempos de entrega relativamente bajos,
    pero existe una cola de pedidos con tiempos muy superiores al comportamiento habitual.

    En el análisis exploratorio, se definió como falla extrema a los pedidos con **más de 42 días** de entrega real.
    """)

    st.markdown("---")

    # ------------------------------------------------------------
    # COMPARACIÓN ENTRE PEDIDOS NO EXTREMOS Y FALLAS EXTREMAS
    # ------------------------------------------------------------

    st.subheader("Comparación entre pedidos no extremos y fallas extremas")

    resumen_tipo = (
        pedidos_dashboard
        .groupby("tipo_pedido")
        .agg(
            pedidos=("order_id", "nunique"),
            tiempo_promedio=("tiempo_entrega_real", "mean"),
            tiempo_mediano=("tiempo_entrega_real", "median"),
            p90_tiempo=("tiempo_entrega_real", lambda x: x.quantile(0.90))
        )
        .reset_index()
    )

    st.dataframe(resumen_tipo.round(2), use_container_width=True)

    fig_box = px.box(
        pedidos_dashboard,
        x="tipo_pedido",
        y="tiempo_entrega_real",
        points=False,
        title="Distribución del tiempo real según tipo de pedido",
        labels={
            "tipo_pedido": "Tipo de pedido",
            "tiempo_entrega_real": "Tiempo real de entrega (días)"
        }
    )

    st.plotly_chart(fig_box, use_container_width=True)

    st.info("""
    Esta comparación permite ver que las fallas extremas no son simplemente valores altos aislados:
    forman un grupo de pedidos con tiempos de entrega muy superiores al resto de la operación.

    Por eso, en el proyecto se analizan como eventos críticos y no se eliminan como simples outliers.
    """)
    # ============================================================
# SECCIÓN: RIESGO POR REGIÓN DEL COMPRADOR
# ============================================================

elif seccion == "Riesgo por región del comprador":

    st.title("🌎 Riesgo operativo por región del comprador")

    st.markdown(
        """
        En esta sección se analiza si el riesgo operativo cambia según la región donde se encuentra el comprador.
        La hipótesis es que algunos destinos presentan mayor probabilidad de fallas extremas, incluso si no concentran
        el mayor volumen absoluto de pedidos.
        """
    )

    df_region = riesgo_region_comprador.copy()

    # Orden lógico de regiones
    orden_regiones = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
    df_region["region_comprador"] = pd.Categorical(
        df_region["region_comprador"],
        categories=orden_regiones,
        ordered=True
    )
    df_region = df_region.sort_values("region_comprador")

    # Tasa global recalculada desde la tabla
    tasa_global = (
        df_region["fallas_extremas"].sum() /
        df_region["pedidos"].sum() * 100
    )

    # Filas clave
    fila_norte = df_region[df_region["region_comprador"] == "Norte"].iloc[0]
    fila_nordeste = df_region[df_region["region_comprador"] == "Nordeste"].iloc[0]
    fila_sudeste = df_region[df_region["region_comprador"] == "Sudeste"].iloc[0]

    st.subheader("Lectura principal")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Mayor riesgo relativo",
            "Norte",
            f"{fila_norte['indice_riesgo_operativo']:.2f}x promedio"
        )

    with col2:
        st.metric(
            "Tasa de fallas Norte",
            f"{fila_norte['tasa_fallas_extremas']:.2f}%",
            f"+{fila_norte['diferencia_vs_tasa_global_pp']:.2f} pp vs global"
        )

    with col3:
        st.metric(
            "Mayor volumen absoluto",
            "Sudeste",
            f"{int(fila_sudeste['fallas_extremas'])} fallas"
        )

    st.info(
        "El Norte presenta el mayor riesgo relativo de fallas extremas, "
        "mientras que el Sudeste concentra más fallas absolutas por su mayor volumen de pedidos."
    )

    # ------------------------------------------------------------
    # Gráfico 1: tasa de fallas extremas por región
    # ------------------------------------------------------------

    colores_regiones = {
        "Norte": "#003B73",
        "Nordeste": "#005A9C",
        "Centro-Oeste": "#247BA0",
        "Sudeste": "#6BAED6",
        "Sul": "#A6CEE3"
    }

    fig_tasa_region = px.bar(
        df_region,
        x="region_comprador",
        y="tasa_fallas_extremas",
        color="region_comprador",
        color_discrete_map=colores_regiones,
        text="tasa_fallas_extremas",
        title="Tasa de fallas extremas por región del comprador",
        labels={
            "region_comprador": "Región del comprador",
            "tasa_fallas_extremas": "Tasa de fallas extremas (%)"
        }
    )

    fig_tasa_region.add_hline(
        y=tasa_global,
        line_dash="dash",
        line_color="#1F2937",
        annotation_text=f"Promedio global: {tasa_global:.2f}%",
        annotation_position="top left"
    )

    fig_tasa_region.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_tasa_region.update_layout(
        showlegend=False,
        height=520,
        yaxis_title="Tasa de fallas extremas (%)",
        xaxis_title="Región del comprador"
    )

    st.plotly_chart(fig_tasa_region, use_container_width=True)

    st.markdown(
        """
        **Interpretación:**  
        La región Norte tiene una tasa de fallas extremas de **5,23%**, muy por encima del promedio global.
        Su índice de riesgo operativo es **3,83**, lo que significa que el riesgo relativo es casi cuatro veces
        superior al promedio de la operación.
        """
    )

    # ------------------------------------------------------------
    # Gráfico 2: volumen vs riesgo relativo
    # ------------------------------------------------------------

    fig_volumen_riesgo = px.scatter(
        df_region,
        x="pedidos",
        y="tasa_fallas_extremas",
        size="fallas_extremas",
        color="region_comprador",
        color_discrete_map=colores_regiones,
        text="region_comprador",
        title="Volumen de pedidos vs riesgo relativo",
        labels={
            "pedidos": "Cantidad de pedidos",
            "tasa_fallas_extremas": "Tasa de fallas extremas (%)",
            "fallas_extremas": "Fallas extremas",
            "region_comprador": "Región"
        }
    )

    fig_volumen_riesgo.update_traces(
        textposition="top center",
        marker=dict(opacity=0.8, line=dict(width=1, color="white"))
    )

    fig_volumen_riesgo.update_layout(
        height=520,
        xaxis_title="Cantidad de pedidos",
        yaxis_title="Tasa de fallas extremas (%)"
    )

    st.plotly_chart(fig_volumen_riesgo, use_container_width=True)

    st.markdown(
        """
        **Lectura operativa:**  
        Este gráfico separa dos conceptos importantes: **riesgo relativo** e **impacto absoluto**.
        El Norte es crítico por tasa de fallas, mientras que el Sudeste requiere seguimiento por volumen,
        ya que concentra una gran cantidad de pedidos y fallas absolutas.
        """
    )

    # ------------------------------------------------------------
    # Tabla comparativa destacada
    # ------------------------------------------------------------

    st.subheader("Comparación de regiones clave")

    tabla_region = df_region[
        [
            "region_comprador",
            "pedidos",
            "fallas_extremas",
            "tasa_fallas_extremas",
            "indice_riesgo_operativo",
            "tasa_retraso_oficial",
            "review_promedio",
            "porcentaje_reviews_bajas"
        ]
    ].copy()

    tabla_region = tabla_region.rename(columns={
        "region_comprador": "Región",
        "pedidos": "Pedidos",
        "fallas_extremas": "Fallas extremas",
        "tasa_fallas_extremas": "Tasa fallas extremas (%)",
        "indice_riesgo_operativo": "Índice riesgo",
        "tasa_retraso_oficial": "Tasa retraso oficial (%)",
        "review_promedio": "Review promedio",
        "porcentaje_reviews_bajas": "Reviews bajas (%)"
    })

    st.dataframe(
        tabla_region.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "Conclusión: la región Norte presenta el mayor riesgo relativo, "
        "el Nordeste combina riesgo alto con peor satisfacción promedio, "
        "y el Sudeste concentra mayor volumen absoluto de fallas."
    )

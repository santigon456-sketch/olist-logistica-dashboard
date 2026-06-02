# Dashboard logístico de Olist 🚚

Este repositorio contiene un dashboard interactivo desarrollado en Streamlit para comunicar los principales hallazgos de un análisis logístico sobre el dataset público **Brazilian E-Commerce Public Dataset by Olist**.

## Link al dashboard

[Ver dashboard en Streamlit](PEGAR_ACÁ_EL_LINK_DE_TU_APP)

## Objetivo del proyecto

El objetivo del análisis es estudiar el desempeño logístico de los pedidos de Olist en Brasil, identificando diferencias en tiempos de entrega, segmentos logísticos, estados de destino, rutas críticas, fallas extremas e impacto sobre la satisfacción del cliente.

El dashboard funciona como complemento visual del Google Colab técnico, donde se realizó la limpieza, preparación, análisis exploratorio y modelado predictivo.

## Dataset

- **Fuente:** Kaggle / Olist.
- **Período principal:** pedidos realizados entre septiembre de 2016 y octubre de 2018.
- **Alcance geográfico:** Brasil.
- **Unidad principal de análisis:** pedido.
- **Enfoque:** logística operativa, tiempos de entrega, rutas críticas y satisfacción del cliente.

## Secciones del dashboard

El dashboard incluye las siguientes secciones:

1. **Resumen ejecutivo**  
   Presenta los principales KPIs del análisis y la ficha técnica del dataset.

2. **Desempeño logístico general**  
   Muestra la distribución del tiempo real de entrega y el umbral de fallas extremas.

3. **Segmentos logísticos**  
   Compara el riesgo operativo entre pedidos de mismo estado, misma región y distinta región.

4. **Riesgo por estado**  
   Analiza la cantidad y tasa de fallas extremas por estado de destino.

5. **Mapa de riesgo**  
   Visualiza geográficamente el riesgo logístico por estado en Brasil.

6. **Rutas críticas**  
   Identifica rutas con mayor cantidad y tasa de fallas extremas.

7. **Fallas extremas y satisfacción**  
   Compara pedidos no extremos contra fallas extremas y su impacto en reviews.

8. **Modelo predictivo**  
   Resume una primera aproximación de Machine Learning mediante regresión lineal simple y múltiple.

9. **Conclusiones y recomendaciones**  
   Sintetiza los hallazgos principales y propone líneas de acción operativa.

## Tecnologías utilizadas

- Python
- Pandas
- Plotly
- Streamlit
- GitHub
- Google Colab

## Idea central del análisis

La logística de Olist no debe evaluarse únicamente por la tasa de retraso oficial. Aunque el cumplimiento frente a la fecha prometida es alto, el análisis del tiempo real de entrega muestra diferencias relevantes por segmento, estado, ruta y casos extremos.

Las fallas extremas representan una proporción baja del total de pedidos, pero tienen un impacto muy fuerte sobre la satisfacción del cliente.

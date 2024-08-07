import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
from folium.plugins import Geocoder


#-------------------------------------------------------------------------
# CODIGO DEL MAPA


# Cargar el dataframe
data = pd.read_csv(f'./assets/P062024.csv')
available_rankings = ['1', '2', '3']
data = data[data['Ranking'].isin(available_rankings)]

st.markdown(
    """
    <style>
    .small-font {
        font-size:14px;
    }
    </style>
    """, 
    unsafe_allow_html=True)
# Agregar barra de búsqueda
search = Geocoder(add_marker=False)

# Título de la aplicación
st.subheader("Mapa de calor para graficar la densidad de muestras")

# Sidebar
with st.sidebar:
    # Segmentador para seleccionar el ranking de los datos
    ranking_option = st.multiselect(
    "**Selecciona el ranking de los datos que quieres mostrar:**",
    available_rankings,
    default=available_rankings)
    st.markdown(
        '<p class="small-font">'
        '<strong>Se presentan 2 capas con mapas de tipo Heatmap con las mediciones de Facebook:</strong><br>'
        '- En una se presenta la densidad de las muestras de Claro.<br>'
        '- Y en la otra capa la densidad del THP de Claro.<br>'
        'En ambos casos es posible filtrar los datos según la posición de Claro en el Ranking (1°, 2° o 3°).'
        '</p>',
        unsafe_allow_html=True)
    st.image(f'./assets/logo.png', width=75)

# Filtrar el dataframe según el ranking seleccionado
filtered_df = data[data['Ranking'].isin(ranking_option)]
# Escala de colores personalizada para Muestras Claro
gradient_colors_muestras = {
        0.0: '#2C7BB6',
        0.65: '#00CCBC',
        0.77: '#FFFF8C',
        0.87: '#F29E2E',
        0.95: '#D7191C'}
# Escala de colores personalizada para THP Claro
gradient_colors_thp = {
    0.0: '#2C7BB6',
    0.25: '#00CCBC',
    0.5: '#FFFF8C',
    0.75: '#F29E2E',
    0.95: '#D7191C'}
# Valores fijos para los ajustes del mapa de calor
radius = 20 #15
blur = 8 #10
min_opacity = 0.18 #0.16

# Crear mapa de calor
def create_heatmap(dataframe, radius, blur, min_opacity, gradient_colors_muestras, gradient_colors_thp):
    mapa1 = leafmap.Map(center=[dataframe['latitud_bin'].mean(), dataframe['longitud_bin'].mean()], zoom=6)
    mapa1.add_heatmap(
        data=dataframe,
        latitude="latitud_bin",
        longitude="longitud_bin",
        value="Muestras Claro",
        name="Muestras Claro",
        radius=radius,
        blur=blur,
        min_opacity=min_opacity,
        max_zoom=18,
        gradient=gradient_colors_muestras)
    mapa1.add_heatmap(
        data=dataframe,
        latitude="latitud_bin",
        longitude="longitud_bin",
        value="THP Claro",
        name="THP Claro",
        radius=radius,
        blur=blur,
        min_opacity=min_opacity,
        max_zoom=18,
        gradient=gradient_colors_thp)
    mapa1.add_child(search)
    return mapa1
    
# Generar y mostrar el mapa de calor
heatmap = create_heatmap(filtered_df, radius, blur, min_opacity, gradient_colors_muestras, gradient_colors_thp)
heatmap.to_streamlit(height=600)
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import leafmap.foliumap as leafmap


#-------------------------------------------------------------------------
# CODIGO DEL MAPA
# Cargar el dataframe
data = pd.read_csv(f'./assets/P062024.csv')
data = data[data['Ranking'].isin(['1', '2', '3'])].reset_index()
data = data[['THP Claro','Muestras Claro','latitud_bin','longitud_bin','provincia','localidad','Ranking','portadoras']]
data['Muestras Port'] = data['Muestras Claro'] / data['portadoras']

# Escala de colores personalizada para Muestras Claro
gradient_colors_muestras = {
        0.0: '#2C7BB6',
        0.65: '#00CCBC',
        0.77: '#FFFF8C',
        0.87: '#F29E2E',
        0.95: '#D7191C'}
# Escala de colores personalizada para Muestras Claro Port
gradient_colors_muestrasPort = {
        0.0: '#2C7BB6',
        0.65: '#00CCBC',
        0.77: '#FFFF8C',
        0.87: '#F29E2E',
        0.95: '#D7191C'}
# Valores fijos para los ajustes del mapa de calor
radius = 20
blur = 8
min_opacity = 0.18


#--------------------------------------------------------------------------
# CODIGO DE LA PAGINA
# Sidebar
with st.sidebar:
    st.markdown(
        '<p class="small-font">'
        '<strong>Utilizando los filtros se presentan 2 capas de tipo Heatmap con las mediciones de Facebook:</strong><br>'
        '- Una muestra la densidad de las Muestras de Claro.<br>'
        '- La otra la densidad del THP de Claro.<br></p>',
        unsafe_allow_html=True)
    st.image(f'./assets/logo.png', width=75)
st.markdown(
    """
    <style>
    .small-font {
        font-size:14px;
    }
    </style>
    """, 
    unsafe_allow_html=True)

# Título de la aplicación
st.subheader("Mapa de calor para graficar la densidad de muestras")

# Crear columnas para los selectores
col1, col2, col3 = st.columns(3)
# Selectores para filtrar los datos
with col1:
    provincia_options = sorted(data['provincia'].unique())
    provincia_selected = st.multiselect("Provincia (puede ser más de 1)", provincia_options)
# Filtrar localidades basadas en la selección de provincias
if provincia_selected:
    filtered_data = data[data['provincia'].isin(provincia_selected)]
else:
    filtered_data = data
with col2:
    localidad_options = sorted(filtered_data['localidad'].unique())
    localidad_selected = st.multiselect("Localidad (puede ser más de 1)", localidad_options)
# Filtrar rankings basados en la selección de provincias y localidades
if provincia_selected or localidad_selected:
    filtered_data = data[
        (data['provincia'].isin(provincia_selected) if provincia_selected else True) &
        (data['localidad'].isin(localidad_selected) if localidad_selected else True)]
else:
    filtered_data = data
with col3:
    ranking_options = sorted(filtered_data['Ranking'].unique())
    ranking_selected = st.multiselect("Ranking (puede ser más de 1)", ranking_options)
      
# Botón para generar el mapa
if st.button("Generar mapa"):
    # Filtrar los datos según las selecciones del usuario
    filtered_data = data[
        (data['provincia'].isin(provincia_selected)) &
        (data['localidad'].isin(localidad_selected)) &
        (data['Ranking'].isin(ranking_selected))]
    # Asegúrate de que filtered_data no esté vacío antes de generar el mapa
    if not filtered_data.empty:
        # Crear el mapa dividido
        m = leafmap.Map(center=(filtered_data['latitud_bin'].mean(), filtered_data['longitud_bin'].mean()), zoom=10)
        # Crear capas de heatmap
        heatmap_muestras = HeatMap(
            data=filtered_data[['latitud_bin', 'longitud_bin', 'Muestras Claro']].values.tolist(),
            radius=radius,
            blur=blur,
            min_opacity=min_opacity,
            max_zoom=18,
            gradient=gradient_colors_muestras,
            name='Muestras Claro')
        heatmap_muestrasPort = HeatMap(
            data=filtered_data[['latitud_bin', 'longitud_bin', 'Muestras Port']].values.tolist(),
            radius=radius,
            blur=blur,
            min_opacity=min_opacity,
            max_zoom=18,
            gradient=gradient_colors_muestrasPort,
            name='Muestras s/ Portadoras')

        # Crear folium mapas para agregar heatmaps
        m1 = folium.Map(location=[filtered_data['latitud_bin'].mean(), filtered_data['longitud_bin'].mean()], zoom_start=10)
        m2 = folium.Map(location=[filtered_data['latitud_bin'].mean(), filtered_data['longitud_bin'].mean()], zoom_start=10)
        
        heatmap_muestras.add_to(m1)
        heatmap_muestrasPort.add_to(m2)

        # Añadir los folium mapas como capas base al mapa dividido
        m.add_layer(m1)
        m.add_layer(m2)

        m.split_map(left_layer='Muestras Claro', right_layer='Muestras s/ Portadoras')
        
        # Mostrar el mapa en Streamlit
        m.to_streamlit(width=1024)
    else:
        st.warning("No se encontraron datos para los filtros seleccionados.")

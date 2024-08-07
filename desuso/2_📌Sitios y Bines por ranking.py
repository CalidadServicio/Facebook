import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import folium
import folium.map
import folium.plugins as plugins
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from folium.plugins import Geocoder


#---------------------------------------------------------------------------------------
## CODIGO DEL MAPA
#bines = pd.read_csv(fr"./assets/P062024.csv", sep=',')
#sitios = pd.read_csv(fr"./assets/Data_Sitios.csv", sep=';', encoding='latin1')
#
## FUNCIÓN para quitar NaN
#def fueraNaN(row):
#    if pd.isna(row['Muestras Claro']):
#        return 0
#    else:
#        return row['Muestras Claro']
#bines['Muestras Claro'] = bines.apply(fueraNaN, axis=1)
#
##Crear los Dataframe por Ranking
#binesR1 = bines.loc[bines['Ranking'] == '1']
#binesR2 = bines.loc[bines['Ranking'] == '2']
#binesR3 = bines.loc[bines['Ranking'] == '3']
## Asegurarse de que las columnas sean de tipo string antes de reemplazar
#bines['latitud_bin'] = bines['latitud_bin'].astype(str)
#bines['longitud_bin'] = bines['longitud_bin'].astype(str)
#sitios['latitud'] = sitios['latitud'].astype(str)
#sitios['longitud'] = sitios['longitud'].astype(str)
## Reemplazar comas por puntos y convertir las columnas a tipo float
#bines['latitud_bin'] = bines['latitud_bin'].str.replace(',', '.').astype(float)
#bines['longitud_bin'] = bines['longitud_bin'].str.replace(',', '.').astype(float)
#sitios['latitud'] = sitios['latitud'].str.replace(',', '.').astype(float)
#sitios['longitud'] = sitios['longitud'].str.replace(',', '.').astype(float)
## Crear las listas para las capas
#sitio_lat = list(sitios["latitud"])
#sitio_lon = list(sitios["longitud"])
#sitio = list(sitios["U_TECNICA"])
#binR1_lat = list(binesR1["latitud_bin"])
#binR1_lon = list(binesR1["longitud_bin"])
#binR1 = list(binesR1["location"])
#binR2_lat = list(binesR2["latitud_bin"])
#binR2_lon = list(binesR2["longitud_bin"])
#binR2 = list(binesR2["location"])
#binR3_lat = list(binesR3["latitud_bin"])
#binR3_lon = list(binesR3["longitud_bin"])
#binR3 = list(binesR3["location"])
#
#
## Crear el mapa
#mapa2 = folium.Map(location=(-42.5747, -64.1814), 
#                 control_scale=True, 
#                 zoom_control=True, 
#                 zoom_start=5, 
#                 min_zoom=5, 
#                 max_zoom=17,
#                 tiles='OpenStreetMap')
#
## Función para crear íconos de clúster personalizados
#def create_cluster_icon(color):
#    return f"""
#    function(cluster) {{
#        return new L.DivIcon({{
#            html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
#            className: 'marker-cluster',
#            iconSize: new L.Point(10, 10)
#        }});
#    }}
#    """
#
#
## CAPA DE SITIOS
#mc_sitio = MarkerCluster(icon_create_function=create_cluster_icon("gray"), maxClusterRadius=35)
#for lat, lon, ut in zip(sitio_lat, sitio_lon, sitio):
#    mc_sitio.add_child(folium.Marker(
#        location=[lat, lon],
#        popup=ut,
#        icon= folium.Icon(
#            color="gray", 
#            icon="tower-cell", 
#            prefix="fa")))
##        icon=folium.Icon(
##            color="gray",
##            icon="none"  # Cambiar a "none" para un simple punto)))
## Crear una capa de características y agregar el MarkerCluster
#capaSitio_st = folium.FeatureGroup(name="Sitios", show=False)
#capaSitio_st.add_child(mc_sitio)
## Agregar la capa de características al mapa
#mapa2.add_child(capaSitio_st)
## CAPA DE BINES en Ranking 1
#mc_binR1 = MarkerCluster(icon_create_function=create_cluster_icon("#70AD25"), maxClusterRadius=1)
#for latR1, lonR1, locR1 in zip(binR1_lat, binR1_lon, binR1):
#    mc_binR1.add_child(folium.Marker(
#        location=[latR1, lonR1],
#        popup=locR1,
#        icon=plugins.BeautifyIcon(
#            icon_size=(15, 15),
#            icon_shape="doughnut",
#            border_color="green",
#            text_color="#007799",
#            background_color='#FFFFFF')))
##    icon= folium.Icon(color="green", 
##                      icon="thermometer-full", 
##                      prefix="fa", )))
## Crear una capa de características y agregar el MarkerCluster
#capaBinR1_st = folium.FeatureGroup(name="Bines Ranking 1", show=False)
#capaBinR1_st.add_child(mc_binR1)
## Agregar la capa de características al mapa
#mapa2.add_child(capaBinR1_st)
## CAPA DE BINES en Ranking 2
#mc_binR2 = MarkerCluster(icon_create_function=create_cluster_icon("orange"), maxClusterRadius=1)
#for latR2, lonR2, locR2 in zip(binR2_lat, binR2_lon, binR2):
#    mc_binR2.add_child(folium.Marker(
#        location=[latR2, lonR2],
#        popup=locR2,
#        icon=plugins.BeautifyIcon(
#            icon_size=(15, 15),
#            icon_shape="doughnut",
#            border_color="orange",
#            text_color="#007799",
#            background_color='#FFFFFF')))
##    icon= folium.Icon(color="orange", 
##                      icon="thermometer-half", 
##                      prefix="fa")))
## Crear una capa de características y agregar el MarkerCluster
#capaBinR2_st = folium.FeatureGroup(name="Bines Ranking 2", show=False)
#capaBinR2_st.add_child(mc_binR2)
## Agregar la capa de características al mapa
#mapa2.add_child(capaBinR2_st)
## CAPA DE BINES en Ranking 3
#mc_binR3 = MarkerCluster(icon_create_function=create_cluster_icon("#D23D29"), maxClusterRadius=1)
#for latR3, lonR3, locR3 in zip(binR3_lat, binR3_lon, binR3):
#    mc_binR3.add_child(folium.Marker(
#        location=[latR3, lonR3],
#        popup=locR3,
#        icon=plugins.BeautifyIcon(
#            icon_size=(15, 15),
#            icon_shape="doughnut",
#            border_color="red",
#            text_color="#007799",
#            background_color='#FFFFFF')))
##   icon= folium.Icon(color="red", 
##                     icon="thermometer-0", 
##                     prefix="fa")))
## Crear una capa de características y agregar el MarkerCluster
#capaBinR3_st = folium.FeatureGroup(name="Bines Ranking 3", show=False)
#capaBinR3_st.add_child(mc_binR3)
## Agregar la capa de características al mapa
#mapa2.add_child(capaBinR3_st)
#
## Agregar barra de búsqueda
#search = Geocoder(add_marker=False)
#mapa2.add_child(search)
## Agregar el control de capas
#folium.LayerControl(collapsed=False).add_to(mapa2)
## Guardar el mapa
#mapa2.save('./assets/Sitios_Ranking.html')
##mapa


# ----------------------------------------------------------------------------------------------
# PAGINA DE STREAMLIT


# Título de la aplicación
st.subheader('Localizacion de Sitios y Bines (por ranking)')

st.markdown(
    """
    <style>
    .small-font {
        font-size:14px;}
    </style>
    """, 
    unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(
        '<p class="small-font">'
        '<strong>Se presentan 4 capas con la ubicación de los Sitios y Bines de Facebook:</strong><br>'
        '- Los Sitios están localizados por su par de coordenadas.<br>'
        '- Los Bines se agrupan según la posición de Claro en el Ranking (1°, 2° o 3°).<br>',
        unsafe_allow_html=True)
    st.image(f'./assets/logo.png', width=75)


# Función para cargar el contenido HTML en caché
@st.cache_data
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
# Especifica la ruta al archivo HTML
html_file = './assets/Sitios_Ranking.html'
# Leer el contenido del archivo HTML en caché
html_content = load_html(html_file)
# Mostrar el contenido HTML en Streamlit
components.html(html_content, height=600, width=800)
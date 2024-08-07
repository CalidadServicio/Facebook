import pandas as pd
import streamlit as st
import folium
import folium.map
import folium.plugins as plugins
import streamlit.components.v1 as components
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from folium.plugins import Geocoder


#-------------------------------------------------------------------------------
## CODIGO DEL MAPA
#
#
## Cargar los datos
#bines = pd.read_csv(fr"./assets/P062024.csv", sep=',')
#sitios = pd.read_csv(fr"./assets/Data_Sitios.csv", sep=';', encoding='latin1')
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
## Columna de Muestras por portadoras
#bines['Muestras s/ Portadoras'] = bines['Muestras Claro'] / bines['portadoras']# Asegurarse de que la columna 'portadoras' sea de tipo entero
#sitios['portadoras'] = sitios['portadoras'].astype(int)
#sitio_lat = list(sitios["latitud"])
#sitio_lon = list(sitios["longitud"])
#sitio_portadoras = list(sitios["portadoras"])
#sitio_utecnica = list(sitios["U_TECNICA"])
#
#
## Función para crear íconos de clúster personalizados
#def create_cluster_icon(color):
#    return f"""
#    function(cluster) {{
#        return new L.DivIcon({{
#            html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
#            className: 'marker-cluster',
#            iconSize: new L.Point(10, 10)   }});    }}  """
## Escala de colores personalizada para Muestras Claro
#gradient_colors_muestras = {
#        0.0: '#2C7BB6',
#        0.65: '#00CCBC',
#        0.77: '#FFFF8C',
#        0.87: '#F29E2E',
#        0.95: '#D7191C'}
## Colores para las portadoras
#portadora_colors = {
#    1: 'red',
#    2: 'red',
#    3: 'orange',
#    4: 'green',
#    5: 'green'}
#
#
#mapa3 = folium.Map(location=(-42.5747, -64.1814), 
#                 control_scale=True, 
#                 zoom_control=True, 
#                 zoom_start=5, 
#                 min_zoom=5, 
#                 max_zoom=17,
#                 tiles='OpenStreetMap')
## Agregar capa de mapa de calor
#heatmap_data = bines[['latitud_bin', 'longitud_bin', 'Muestras s/ Portadoras']].dropna().values.tolist()
#heatmap_layer = HeatMap(heatmap_data, name='Mapa de Calor',
#                        gradient=gradient_colors_muestras,
#                        radius=20,
#                        blur=8,
#                        min_opacity=0.18)
#mapa3.add_child(heatmap_layer)
## Crear capa de portadoras
#for port in portadora_colors.keys():
#    mc_port = MarkerCluster(icon_create_function=create_cluster_icon(portadora_colors[port]),
#                            maxClusterRadius=1)
#    for lat, lon, portadora, ut in zip(sitio_lat, sitio_lon, sitio_portadoras, sitio_utecnica):
#        if portadora == port:
#            mc_port.add_child(folium.Marker(
#                location=[lat, lon],
#                popup=f"U_TECNICA: {ut}, Portadoras: {portadora}",
#                icon=plugins.BeautifyIcon(
#                     icon_size=(10,10),
#                     icon_shape="doughnut",
#                     border_color=portadora_colors[port],
#                     text_color="#007799",
#                     background_color='#FFFFFF' #portadora_colors[port]
#                 )
#            ))
#    capaport_st = folium.FeatureGroup(name=f'Portadoras {port}', show=False, overlay=True)
#    capaport_st.add_child(mc_port)
#    mapa3.add_child(capaport_st)
## Agregar barra de búsqueda    
#Geocoder().add_to(mapa3)
#
## Agregar el control de capas
#folium.LayerControl(collapsed=False).add_to(mapa3)
#
## Guardar el mapa
#mapa3.save('./assets/HeatMap_Portadoras.html')
##mapa


# ----------------------------------------------------------------------------------------------
# PAGINA DE STREAMLIT


# Título de la aplicación
st.subheader('Densidad de muestras y ubicación de Sitios (por cantidad de portadoras)')

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
        '<strong>Se presentan 6 capas con la ubicación de los Sitios y un mapa de calor con las muestras de Claro:</strong><br>'
        '- Los Sitios están localizados por su par de coordenadas, diferenciando la cantidad de Portadoras que poseen.<br>'
        '- El mapa de calor muestra la densidad de muestras.<br>',
        unsafe_allow_html=True)
    st.image(f'./assets/logo.png', width=75)


# Función para cargar el contenido HTML en caché
@st.cache_data
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
# Especifica la ruta al archivo HTML
html_file = './assets/Heatmap_Portadoras.html'
# Leer el contenido del archivo HTML en caché
html_content = load_html(html_file)
# Mostrar el contenido HTML en Streamlit
components.html(html_content, height=600, width=800)
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
## Función para crear íconos de clúster personalizados
#def create_cluster_icon(color):
#    return f"""
#    function(cluster) {{
#        return new L.DivIcon({{
#            html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
#            className: 'marker-cluster',
#            iconSize: new L.Point(10, 10)   }});    }}  """
#            
#            
## Cargar los datos
#plan = pd.read_csv(fr"./assets/Data_Plan.csv", sep=';')
#plan.replace('#N/D', 0, inplace=True)
## Asegurarse de que las columnas sean de tipo string antes de reemplazar
#plan['Latitud'] = plan['Latitud'].astype(str)
#plan['Longitud'] = plan['Longitud'].astype(str)
## Reemplazar comas por puntos y convertir las columnas a tipo float
#plan['Latitud'] = plan['Latitud'].str.replace(',', '.').astype(float)
#plan['Longitud'] = plan['Longitud'].str.replace(',', '.').astype(float)
#
## Colores según el Plan General
#plan_colors = {
#    'Sin Plan / Alta Carga': 'orange',
#    'Sin Plan': 'red',
#    'Restricciones para Implementar': 'gray',
#    'Expansiones 2024': 'blue',
#    'Sectorizaciones 2024': 'purple',
#    '5G - Fase 1 (432)': 'green',
#    '5G - 45': 'green',
#    'Baja Definitiva': 'black'}
#
#mapa4 = folium.Map(location=(-42.5747, -64.1814), 
#                 control_scale=True, 
#                 zoom_control=True, 
#                 zoom_start=5, 
#                 min_zoom=5, 
#                 max_zoom=17,
#                 tiles='OpenStreetMap')
#
## Crear capa de planes
#for planpg, color in plan_colors.items():
#    mc_plan = plugins.MarkerCluster(icon_create_function=create_cluster_icon(color),
#                                    maxClusterRadius=35)
#    for index, row in plan.iterrows():
#        if row['Plan General'] == planpg:
#            mc_plan.add_child(folium.Marker(
#                location=[row['Latitud'], row['Longitud']],
#                popup=f"U_TECNICA: {row['U_TECNICA']}, {planpg}",
#                icon=plugins.BeautifyIcon(
#                     icon_size=(10,10),
#                     icon_shape="doughnut",
#                     border_color=color,
#                     text_color="#007799",
#                     background_color='#FFFFFF'
#                 )
#            ))
#    capaport_st = folium.FeatureGroup(name=f'{planpg}', show=False, overlay=True)
#    capaport_st.add_child(mc_plan)
#    mapa4.add_child(capaport_st)
#
## Agregar barra de búsqueda    
#plugins.Geocoder().add_to(mapa4)
#
## Agregar el control de capas
#folium.LayerControl(collapsed=False).add_to(mapa4)
#
## Guardar el mapa
#mapa4.save('./assets/Sitios_Plan.html')
##mapa


# ----------------------------------------------------------------------------------------------
# PAGINA DE STREAMLIT

# Título de la aplicación
st.subheader('Sitios según Plan General')

st.markdown(
    """
    <style>
    .small-font {
        font-size:14px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# SIDEBAR
with st.sidebar:
    st.markdown(
        '<p class="small-font">'
        '<strong>Se presentan varias capas con la ubicación de los Sitios según el Plan.</strong><br>'
        '- Cada capa tiene un color según la clasificación del Plan General.<br>',
        unsafe_allow_html=True
    )
    st.image(f'./assets/logo.png', width=75)


# Función para cargar el contenido HTML en caché
@st.cache_data
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
# Especifica la ruta al archivo HTML
html_file = './assets/Sitios_Plan.html'
# Leer el contenido del archivo HTML en caché
html_content = load_html(html_file)
# Mostrar el contenido HTML en Streamlit
components.html(html_content, height=600, width=800)
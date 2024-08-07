import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import folium_static
import folium.plugins as plugins
from folium.plugins import FloatImage

@st.cache_data
def load_data():
    bines = pd.read_csv(f'./assets/P062024.csv')
    bines = bines[bines['Ranking'].isin(['1', '2', '3'])].reset_index()
    bines = bines[['Muestras Claro','latitud_bin','longitud_bin','provincia','localidad']]
    sitios = pd.read_csv(fr'./assets/Data_Sitios.csv', sep=';', encoding='latin1')
    sitios = sitios[['U_TECNICA','portadoras','latitud','longitud','provincia','localidad']]
    # Asegurarse de que las columnas sean de tipo string antes de reemplazar
    bines['latitud_bin'] = bines['latitud_bin'].astype(str)
    bines['longitud_bin'] = bines['longitud_bin'].astype(str)
    sitios['latitud'] = sitios['latitud'].astype(str)
    sitios['longitud'] = sitios['longitud'].astype(str)
    # Reemplazar comas por puntos y convertir las columnas a tipo float
    bines['latitud_bin'] = bines['latitud_bin'].str.replace(',', '.').astype(float)
    bines['longitud_bin'] = bines['longitud_bin'].str.replace(',', '.').astype(float)
    sitios['latitud'] = sitios['latitud'].str.replace(',', '.').astype(float)
    sitios['longitud'] = sitios['longitud'].str.replace(',', '.').astype(float)
    return bines, sitios

bines, sitios = load_data()

# Inicializar valores en el estado de la sesión si no están definidos
if 'provincia_selected' not in st.session_state:
    st.session_state['provincia_selected'] = []
if 'localidad_selected' not in st.session_state:
    st.session_state['localidad_selected'] = []

# Escala de colores personalizada para Muestras Claro
gradient_colors_muestras = {
    0.0: '#2C7BB6',
    0.65: '#00CCBC',
    0.77: '#FFFF8C',
    0.87: '#F29E2E',
    0.95: '#D7191C'}

# Función para crear íconos de clúster personalizados
def create_cluster_icon(color):
    return f"""
    function(cluster) {{
        return new L.DivIcon({{
            html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
            className: 'marker-cluster',
            iconSize: new L.Point(40, 40)
        }});}}"""

# Colores para las portadoras
portadora_colors = {
    1: 'red',
    2: 'red',
    3: 'orange',
    4: 'green',
    5: 'green'}

# Valores fijos para los ajustes del mapa de calor
radius = 20
blur = 8
min_opacity = 0.18

# Imagen de leyenda
image_file = f'./assets/leyenda_port.png'

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
    unsafe_allow_html=True,)

# Título de la aplicación
st.subheader("Mapa de Sitios por portadora y densidad de Muestras")

# Crear columnas para los selectores
col1, col2 = st.columns(2)
# Selectores para filtrar los datos
with col1:
    provincia_options = sorted(sitios['provincia'].unique())
    st.session_state['provincia_selected'] = st.multiselect("Provincia (puede ser más de 1)", provincia_options, st.session_state['provincia_selected'])
# Filtrar localidades basadas en la selección de provincias
if st.session_state['provincia_selected']:
    filtered_sitios = sitios[sitios['provincia'].isin(st.session_state['provincia_selected'])]
    filtered_bines = bines[bines['provincia'].isin(st.session_state['provincia_selected'])]
else:
    filtered_sitios = sitios
    filtered_bines = bines
with col2:
    localidad_options = sorted(filtered_sitios['localidad'].unique())
    st.session_state['localidad_selected'] = st.multiselect("Localidad (puede ser más de 1)", localidad_options, st.session_state['localidad_selected'])
# Filtrar datos basados en la selección de provincias y localidades
if st.session_state['provincia_selected'] or st.session_state['localidad_selected']:
    filtered_sitios = filtered_sitios[
        (filtered_sitios['provincia'].isin(st.session_state['provincia_selected']) if st.session_state['provincia_selected'] else True) &
        (filtered_sitios['localidad'].isin(st.session_state['localidad_selected']) if st.session_state['localidad_selected'] else True)]
    filtered_bines = filtered_bines[
        (filtered_bines['provincia'].isin(st.session_state['provincia_selected']) if st.session_state['provincia_selected'] else True) &
        (filtered_bines['localidad'].isin(st.session_state['localidad_selected']) if st.session_state['localidad_selected'] else True)]
    
# Botón para generar el mapa
if st.button("Generar mapa"):
    # Calcular la ubicación inicial del mapa como el promedio de latitudes y longitudes de los datos filtrados
    if not filtered_bines.empty or not filtered_sitios.empty:
        mean_lat = filtered_sitios['latitud'].mean()
        mean_lng = filtered_sitios['longitud'].mean()
    else:
        mean_lat, mean_lng = -34.0, -64.0  # Valores por defecto
    mapa = folium.Map(location=[mean_lat, mean_lng], zoom_start=8)
    # Agregar heatmap de muestras si hay datos disponibles
    if not filtered_bines.empty:
        heatmap_muestras = HeatMap(
            data=filtered_bines[['latitud_bin', 'longitud_bin', 'Muestras Claro']].values.tolist(),
            name="Muestras Claro",
            radius=radius,
            blur=blur,
            min_opacity=min_opacity,
            max_zoom=18,
            gradient=gradient_colors_muestras,
            show=True
        ).add_to(mapa)
    else:
        st.warning("No se encontraron datos de Muestras Claro para los filtros seleccionados.")
    # Agregar marcadores de sitios por portadora si hay datos disponibles
    if not filtered_sitios.empty:
        for port in portadora_colors.keys():
            filtered_port = filtered_sitios[filtered_sitios['portadoras'] == port]
            if not filtered_port.empty:
                mc_port = MarkerCluster(icon_create_function=create_cluster_icon(portadora_colors[port]), 
                                        name=f'Portadoras {port}', 
                                        maxClusterRadius=5)
                for _, row in filtered_port.iterrows():
                    mc_port.add_child(folium.Marker(
                        location=[row['latitud'], row['longitud']],
                        popup=f"U_TECNICA: {row['U_TECNICA']}, Portadoras: {row['portadoras']}",
                        icon=plugins.BeautifyIcon(
                            icon_size=(10,10),
                            icon_shape="doughnut",
                            border_color=portadora_colors[port],
                            text_color="#007799",
                            background_color=portadora_colors[port],
                            show=False)))
                mapa.add_child(mc_port)  
        FloatImage(image='./assets/leyenda_port.PNG', bottom=40, left=40, ).add_to(mapa)
        folium.LayerControl(collapsed=False).add_to(mapa)  
        # Guardar el mapa en el estado de la sesión
        st.session_state['mapa'] = mapa
        # Mostrar el mapa en Streamlit
        #folium_static(mapa, width=1024)
    else:
        st.warning("No se encontraron datos de sitios para los filtros seleccionados.")
        
# Mostrar el mapa guardado en el estado de la sesión si existe
if 'mapa' in st.session_state:
    folium_static(st.session_state['mapa'], width=1024)

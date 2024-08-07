import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import folium.plugins as plugins
from streamlit_folium import folium_static

# Cargar los datos
plan = pd.read_csv(fr'./assets/Data_Plan.csv', sep=';', encoding='latin1')
plan = plan[plan['Longitud'] != '#N/D']
# Asegurarse de que las columnas sean de tipo string antes de reemplazar
plan['Latitud'] = plan['Latitud'].astype(str)
plan['Longitud'] = plan['Longitud'].astype(str)
plan['Provincia'] = plan['Provincia'].astype(str)
plan['Localidad'] = plan['Localidad'].astype(str)
plan['Plan General'] = plan['Plan General'].astype(str)
# Reemplazar comas por puntos y convertir las columnas a tipo float
plan['Latitud'] = plan['Latitud'].str.replace(',', '.').astype(float)
plan['Longitud'] = plan['Longitud'].str.replace(',', '.').astype(float)
# Colores según el Plan General
plan_colors = {
    '5G - Fase 1 (432)': 'green',
    '5G - 45': 'green',
    'Expansiones 2024': 'blue',
    'Sectorizaciones 2024': 'purple',
    'Sin Plan / Alta Carga': 'orange',
    'Sin Plan': 'red',
    'Restricciones para Implementar': 'gray',
    'Baja Definitiva': 'black'}

def create_cluster_icon(color):
    return f"""
    function(cluster) {{
        return new L.DivIcon({{
            html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
            className: 'marker-cluster',
            iconSize: new L.Point(10, 10)
        }});
    }}
    """

# Sidebar
with st.sidebar:
    st.markdown(
        '<p class="small-font">'
        '<strong>Se presentan varias capas con la ubicación de los Sitios según el Plan.</strong><br>'
        '- Cada capa tiene un color según la clasificación del Plan General.<br>',
        unsafe_allow_html=True)
    st.image(f'./assets/logo.png', width=75)

# Configurar la interfaz de usuario
st.subheader("Sitios sobre umbral THP")

# Crear columnas para los selectores
col1, col2 = st.columns(2)
# Selectores para filtrar los datos
with col1:
    provincia_options = sorted(plan['Provincia'].unique())
    provincia_selected = st.multiselect("Provincia (puede ser más de 1)", provincia_options)
# Filtrar localidades basadas en la selección de provincias
if provincia_selected:
    filtered_data = plan[plan['Provincia'].isin(provincia_selected)]
else:
    filtered_data = plan
with col2:
    localidad_options = sorted(filtered_data['Localidad'].unique())
    localidad_selected = st.multiselect("Localidad (puede ser más de 1)", localidad_options)
# Filtrar datos basados en la selección de provincias y localidades
if provincia_selected or localidad_selected:
    filtered_data = plan[
        (plan['Provincia'].isin(provincia_selected) if provincia_selected else True) &
        (plan['Localidad'].isin(localidad_selected) if localidad_selected else True)]
else:
    filtered_data = plan

# Botón para generar el mapa
if st.button("Generar mapa"):
    # Filtrar los datos según las selecciones del usuario
    filtered_data = plan[
        (plan['Provincia'].isin(provincia_selected)) &
        (plan['Localidad'].isin(localidad_selected))]

    # Asegúrate de que filtered_data no esté vacío antes de generar el mapa
    if not filtered_data.empty:
        # Generar el mapa
        mapa = folium.Map(location=[filtered_data['Latitud'].mean(), filtered_data['Longitud'].mean()], zoom_start=10)
        # Crear capa de planes solo si tienen datos
        for planpg, color in plan_colors.items():
            mc_plan = MarkerCluster(icon_create_function=create_cluster_icon(color),
                                    maxClusterRadius=20)
            for index, row in filtered_data.iterrows():
                if row['Plan General'] == planpg:
                    mc_plan.add_child(folium.Marker(
                        location=[row['Latitud'], row['Longitud']],
                        popup=f"U_TECNICA: {row['U_TECNICA']}, {planpg}",
                        icon=plugins.BeautifyIcon(
                             icon_size=(10,10),
                             icon_shape="doughnut",
                             border_color=color,
                             text_color="#007799",
                             background_color=color)))
            # Añadir la capa de marcadores solo si hay datos para esa capa
            if len(mc_plan._children) > 0:
                capaport_st = folium.FeatureGroup(name=f'<span style="color:{color}">{planpg}</span>', show=False, overlay=True)
                capaport_st.add_child(mc_plan)
                mapa.add_child(capaport_st)
                
        folium.LayerControl(collapsed=False).add_to(mapa)
        # Mostrar el mapa en Streamlit
        folium_static(mapa, width=1024)
    else:
        st.warning("No se encontraron datos para los filtros seleccionados.")

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
import folium.plugins as plugins
import os

# Define gradient colors and other constants
gradient_colors_muestras = {
    0.0: '#2C7BB6',
    0.65: '#00CCBC',
    0.77: '#FFFF8C',
    0.87: '#F29E2E',
    0.95: '#D7191C'}
gradient_colors_thp = {
    0.0: '#2C7BB6',
    0.65: '#00CCBC',
    0.77: '#FFFF8C',
    0.87: '#F29E2E',
    0.95: '#D7191C'}
radius = 20
blur = 8
min_opacity = 0.18

# Load Plan data
plan = pd.read_csv(fr'./assets/Data_Plan.csv', sep=';', encoding='latin1')
plan = plan[plan['Longitud'] != '#N/D']
plan['Latitud'] = plan['Latitud'].astype(str)
plan['Longitud'] = plan['Longitud'].astype(str)
plan['Provincia'] = plan['Provincia'].astype(str)
plan['Localidad'] = plan['Localidad'].astype(str)
plan['Plan General'] = plan['Plan General'].astype(str)
plan['Latitud'] = plan['Latitud'].str.replace(',', '.').astype(float)
plan['Longitud'] = plan['Longitud'].str.replace(',', '.').astype(float)

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
st.subheader("Densidad de muestras y Plan General por Sitio")

# Inicializar session state si no existe
if 'provincia_selected' not in st.session_state:
    st.session_state.provincia_selected = []
if 'localidad_selected' not in st.session_state:
    st.session_state.localidad_selected = []
if 'ranking_selected' not in st.session_state:
    st.session_state.ranking_selected = []
if 'mapa1' not in st.session_state:
    st.session_state.mapa1 = None
if 'mapa2' not in st.session_state:
    st.session_state.mapa2 = None

# Crear columnas para los selectores
col0, col1, col2, col3 = st.columns(4)
# Selectores para filtrar los datos
with col0:
    folder_path = './assets/Dataset'
    periodo_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    periodo_options = {f[1:7]: f for f in periodo_files}  # Diccionario de opciones
    periodo_display = list(periodo_options.keys())  # Opciones a mostrar

    if 'periodo_selected' not in st.session_state:
        st.session_state.periodo_selected = periodo_display[0] if periodo_display else None
    # Asegurar que el valor seleccionado esté en la lista de opciones
    if st.session_state.periodo_selected not in periodo_display:
        st.session_state.periodo_selected = periodo_display[0] if periodo_display else None

    periodo_selected_display = st.selectbox('Periodo', periodo_display, index=periodo_display.index(st.session_state.periodo_selected))
    st.session_state.periodo_selected = periodo_selected_display
    periodo_selected = periodo_options[periodo_selected_display]

    if periodo_selected:
        file_path = os.path.join(folder_path, periodo_selected)
        data = pd.read_csv(file_path)
        
        # Mapa de densidad
        data = data[data['Ranking'].isin(['1', '2', '3'])].reset_index()
        data = data[['THP Claro', 'Muestras Claro', 'latitud_bin', 'longitud_bin', 'provincia', 'localidad', 'Ranking', 'portadoras']]
        data['Muestras Port'] = data['Muestras Claro'] / data['portadoras']

with col1:
    if periodo_selected:
        provincia_options = sorted(data['provincia'].unique())
        provincia_selected = st.multiselect("Provincia (puede ser más de 1)", provincia_options, st.session_state.provincia_selected)
    if provincia_selected:
        st.session_state.provincia_selected = provincia_selected
        filtered_data = data[data['provincia'].isin(provincia_selected)]
        filtered_plan = plan[plan['Provincia'].isin(provincia_selected)]
    else:
        filtered_data = data
        filtered_plan = plan

with col2:
    localidad_options = sorted(filtered_data['localidad'].unique())
    localidad_selected = st.multiselect("Localidad (puede ser más de 1)", localidad_options, st.session_state.localidad_selected)
    if provincia_selected or localidad_selected:
        st.session_state.localidad_selected = localidad_selected
        filtered_data = data[
            (data['provincia'].isin(provincia_selected) if provincia_selected else True) &
            (data['localidad'].isin(localidad_selected) if localidad_selected else True)]
        filtered_plan = plan[
            (plan['Provincia'].isin(provincia_selected) if provincia_selected else True) &
            (plan['Localidad'].isin(localidad_selected) if localidad_selected else True)]
    else:
        filtered_data = data
        filtered_plan = plan

with col3:
    ranking_options = sorted(filtered_data['Ranking'].unique())
    ranking_selected = st.multiselect("Ranking (puede ser más de 1)", ranking_options, st.session_state.ranking_selected)

# Botón para generar el mapa
if st.button("Generar mapa"):
    st.session_state.ranking_selected = ranking_selected
    filtered_data = data[
        (data['provincia'].isin(provincia_selected)) &
        (data['localidad'].isin(localidad_selected)) &
        (data['Ranking'].isin(ranking_selected))]
    
    filtered_plan = plan[
        (plan['Provincia'].isin(provincia_selected)) &
        (plan['Localidad'].isin(localidad_selected))]

    if not filtered_data.empty and not filtered_plan.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Mapa de Calor")
            mapa1 = folium.Map(location=[filtered_data['latitud_bin'].median(), filtered_data['longitud_bin'].median()], zoom_start=12)
            HeatMap(
                data=filtered_data[['latitud_bin', 'longitud_bin', 'Muestras Claro']].values.tolist(),
                name="Muestras Claro",
                radius=radius,
                blur=blur,
                min_opacity=min_opacity,
                max_zoom=18,
                gradient=gradient_colors_muestras,
                show=True
            ).add_to(mapa1)
            HeatMap(
                data=filtered_data[['latitud_bin', 'longitud_bin', 'Muestras Port']].values.tolist(),
                name="Muestras s/ Portadoras",
                radius=radius,
                blur=blur,
                min_opacity=min_opacity,
                max_zoom=18,
                gradient=gradient_colors_muestras,
                show=False
            ).add_to(mapa1)
            HeatMap(
                data=filtered_data[['latitud_bin', 'longitud_bin', 'THP Claro']].values.tolist(),
                name="THP Claro",
                radius=radius,
                blur=blur,
                min_opacity=min_opacity,
                max_zoom=18,
                gradient=gradient_colors_thp,
                show=False
            ).add_to(mapa1)
            folium.LayerControl(collapsed=False).add_to(mapa1)
            st.session_state.mapa1 = mapa1

        with col2:
            st.subheader("Sitios sobre umbral THP")
            mapa2 = folium.Map(location=[filtered_plan['Latitud'].mean(), filtered_plan['Longitud'].mean()], zoom_start=10)
            for planpg, color in plan_colors.items():
                mc_plan = MarkerCluster(icon_create_function=create_cluster_icon(color), maxClusterRadius=20)
                for index, row in filtered_plan.iterrows():
                    if row['Plan General'] == planpg:
                        mc_plan.add_child(folium.Marker(
                            location=[row['Latitud'], row['Longitud']],
                            popup=f"U_TECNICA: {row['U_TECNICA']}, {planpg}",
                            icon=plugins.BeautifyIcon(
                                number=index,
                                border_color=color,
                                text_color='black',
                                inner_icon_style='margin-top:0px;')
                        ))
                mc_plan.add_to(mapa2)
            folium.LayerControl(collapsed=False).add_to(mapa2)
            st.session_state.mapa2 = mapa2

# Mostrar los mapas guardados en session state
if st.session_state.mapa1:
    st.subheader("Mapa de Calor")
    folium_static(st.session_state.mapa1)
if st.session_state.mapa2:
    st.subheader("Sitios sobre umbral THP")
    folium_static(st.session_state.mapa2)

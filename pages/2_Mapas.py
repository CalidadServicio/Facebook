import os
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
import folium.plugins as plugins
from folium.plugins import HeatMap, DualMap, MarkerCluster
import time
from PIL import Image


icon_path = 'assets/icon.png'
icon_image = Image.open(icon_path)

st.set_page_config(page_title='Mapas',
                   page_icon=icon_image,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items=None)


# IMPORTAR LOS ARCHIVOS NECESARIOS
@st.cache_data
def load_data():
    # Cargar Data_Sitios
    sitios = pd.read_csv('./assets/Data_Sitios.csv', sep=';', encoding='latin1')
    sitios = sitios[['U_TECNICA', 'portadoras', 'latitud', 'longitud', 'provincia', 'localidad', 'plan', 'plan general']]
    # Asegurarse de que las columnas sean de tipo string antes de reemplazar
    sitios['latitud'] = sitios['latitud'].astype(str)
    sitios['longitud'] = sitios['longitud'].astype(str)
    # Reemplazar comas por puntos y convertir las columnas a tipo float
    sitios['latitud'] = sitios['latitud'].str.replace(',', '.').astype(float)
    sitios['longitud'] = sitios['longitud'].str.replace(',', '.').astype(float) 
    
    # Lista de archivos en la carpeta Dataset
    folder_path = './assets/Dataset'
    dataset_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    
    return sitios, dataset_files
sitios, dataset_files = load_data()

def color_fila_por_columna(row):
    if row['Plan'] == 'No' or row['Plan'] == 'Carga':
        return ['background-color: pink'] * len(row)
    else:
        return [''] * len(row)

# SELECTORES PARA FILTRAR LOS DATOS
# Inicializar valores en el estado de la sesión si no están definidos
# Inicializar valores en el estado de la sesión si no están definidos
if 'periodo_selected' not in st.session_state:
    st.session_state['periodo_selected'] = None
if 'provincia_selected' not in st.session_state:
    st.session_state['provincia_selected'] = None
if 'localidad_selected' not in st.session_state:
    st.session_state['localidad_selected'] = None
if 'ranking_selected' not in st.session_state:
    st.session_state['ranking_selected'] = []

with st.sidebar:
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('Filtros')
    with col2:
        buton = st.button("Generar Mapa")
    # Filtrar los archivos para mostrar solo los primeros 6 caracteres
    periodos_options = [f[1:7] for f in dataset_files]
    periodos_dict = {f[1:7]: f for f in dataset_files}
    if periodos_options:
        periodo_selected = st.selectbox('Periodo', periodos_options, index=len(periodos_options) - 1)
        st.session_state['periodo_selected'] = periodo_selected
        time.sleep(1)
    else:
        st.warning("No se encontraron archivos en la carpeta Dataset.")
    if st.session_state['periodo_selected']:
        # Obtener el nombre completo del archivo basado en la selección del periodo
        selected_file = periodos_dict[st.session_state['periodo_selected']]
        file_path = os.path.join('./assets/Dataset', selected_file)
        bines = pd.read_csv(file_path)
        bines = bines[bines['Ranking'].isin(['1', '2', '3'])].reset_index()
        bines = bines[['THP Claro','THP Personal','THP Movistar','Muestras Claro','latitud_bin','longitud_bin','U_TECNICA','latitud_sitio','longitud_sitio','provincia','localidad','Ranking','portadoras']]
        # Asegurarse de que las columnas sean de tipo string antes de reemplazar
        bines['latitud_bin'] = bines['latitud_bin'].astype(str)
        bines['longitud_bin'] = bines['longitud_bin'].astype(str)
        bines['latitud_sitio'] = bines['latitud_sitio'].astype(str)
        bines['longitud_sitio'] = bines['longitud_sitio'].astype(str)
        # Reemplazar comas por puntos y convertir las columnas a tipo float
        bines['latitud_bin'] = bines['latitud_bin'].str.replace(',', '.').astype(float)
        bines['longitud_bin'] = bines['longitud_bin'].str.replace(',', '.').astype(float)
        bines['latitud_sitio'] = bines['latitud_sitio'].str.replace(',', '.').astype(float)
        bines['longitud_sitio'] = bines['longitud_sitio'].str.replace(',', '.').astype(float)
        provincia_options = sorted(bines['provincia'].unique())
        provincia_selected = st.selectbox("Provincia", provincia_options)
        st.session_state['provincia_selected'] = provincia_selected
        if st.session_state['provincia_selected']:
            filtered_binesP = bines[bines['provincia'] == st.session_state['provincia_selected']]
            filtered_sitiosP = sitios[sitios['provincia'] == st.session_state['provincia_selected']]
            localidad_options = sorted(filtered_binesP['localidad'].unique())
            localidad_selected = st.selectbox("Localidad", localidad_options)
            st.session_state['localidad_selected'] = localidad_selected
            if st.session_state['localidad_selected']:
                filtered_binesL = filtered_binesP[filtered_binesP['localidad'] == st.session_state['localidad_selected']]
                filtered_sitiosL = filtered_sitiosP[sitios['localidad'] == st.session_state['localidad_selected']]
                ranking_options = sorted(filtered_binesL['Ranking'].unique())
                # Ajustar las opciones predeterminadas
                default_ranking = [r for r in ['2', '3'] if r in ranking_options]
                ranking_selected = st.multiselect("Ranking", ranking_options, default_ranking)
                st.session_state['ranking_selected'] = ranking_selected
    # Filtrar datos basados en los filtros seleccionados
    if st.session_state['periodo_selected'] and st.session_state['provincia_selected'] and st.session_state['localidad_selected'] and st.session_state['ranking_selected']:
        filtered_binesZ = filtered_binesL[filtered_binesL['Ranking'].isin(st.session_state['ranking_selected'])]
        filtered_sitios = filtered_sitiosL[filtered_sitiosL['portadoras'] > 0]  # Filtrar sitios con portadoras > 0
    else:
        st.warning("Por favor, seleccione todos los filtros para mostrar los datos.")

    st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 1;
        bottom: 0;
        width: 14%;
        background-color: #5A82A6;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
    }
    .footer img {
        margin-right: 20px;
    }
    .footer span {
        color: #333835; /* Cambia este valor por el color que desees */
        font-weight: bold; /* Para poner el texto en negrita */
    }
    </style>
    """,
    unsafe_allow_html=True)

    # Agregar imagen y texto como footer
    st.markdown(
    """
    <div class="footer">
        <img src="https://www.bidi.la/imagenes/home/clientes/Claro.png" width="75">
        <span>Servicios E2E</span>
    </div>
    """,
    unsafe_allow_html=True)


st.markdown("<h3 style='color: #537a9b'; >Análisis gráfico de datos.</h3>", unsafe_allow_html=True)
    

# PRIMER PAR DE MAPAS (DENSIDAD Y SITIOS SOBRE UMBRAL)
# Agregar botón para generar el mapa
if buton:
    if st.session_state['periodo_selected'] and st.session_state['provincia_selected'] and st.session_state['localidad_selected'] and st.session_state['ranking_selected']:
        filtered_data = filtered_binesZ[filtered_binesZ['Ranking'].isin(st.session_state['ranking_selected'])]        
        if not filtered_data.empty:
            #st.divider()
        # Crear columnas para los selectores
            col1, col2 = st.columns([1.1,2])
            with col1:
                st.markdown("<h5 style='color: #537a9b'; >Densidad de muestras y portadoras por Sitio.</h5>", unsafe_allow_html=True)
                #st.markdown(f'**Densidad de muestras y portadoras por Sitio**')
            with col2:
                THP_P = filtered_binesP['THP Personal'].mean()
                THP_M = filtered_binesP['THP Movistar'].mean()
                THP_C = filtered_binesP['THP Claro'].mean()
                st.session_state['umbral_thp'] = max(THP_P, THP_M, THP_C)
                st.markdown(f"<h5 style='color: #537a9b'; >Sitios sobre umbral THP: {st.session_state['umbral_thp']:.2f} Mb.</h5>", unsafe_allow_html=True)
                #st.markdown(f"**Sitios sobre umbral    /    THP > {st.session_state['umbral_thp']:.2f} Mb.**")


#-------------------------------------------------------------------------------------------------------------


    # Crear el DualMap
            dual_map1 = DualMap(location=[filtered_binesL['latitud_sitio'].mean(), filtered_binesL['longitud_sitio'].mean()], zoom_start=11)

    # Añadir marcadores al primer mapa (m1)
            portadora_colors = {
                1: 'red',
                2: 'red',
                3: 'orange',
                4: 'green',
                5: 'green'}
            gradient_colors_muestras = {
                0.0: '#2C7BB6',
                0.65: '#00CCBC',
                0.77: '#FFFF8C',
                0.87: '#F29E2E',
                0.95: '#D7191C'}
            radius = 20
            blur = 8
            min_opacity = 0.18
            def create_cluster_icon(color):
                return f"""
                function(cluster) {{
                    return new L.DivIcon({{
                        html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
                        className: 'marker-cluster',
                        iconSize: new L.Point(40, 40)
                    }});}}"""
            heatmap_muestras = HeatMap(
                    data=filtered_data[['latitud_bin', 'longitud_bin', 'Muestras Claro']].values.tolist(),
                    name="Muestras Claro",
                    radius=radius,
                    blur=blur,
                    min_opacity=min_opacity,
                    max_zoom=18,
                    gradient=gradient_colors_muestras,
                    show=True)
            heatmap_muestras.add_to(dual_map1.m1)
            for port in portadora_colors.keys():
                filtered_port = filtered_sitios[filtered_sitios['portadoras'] == port]
                if not filtered_port.empty:
                    mc_port = MarkerCluster(icon_create_function=create_cluster_icon(portadora_colors[port]), 
                                name=f'{port} portadora/s', 
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
                    mc_port.add_to(dual_map1.m1)
            folium.LayerControl(collapsed=False).add_to(dual_map1.m1)


    # Añadir marcadores al segundo mapa (m2)          
            data = filtered_binesL.groupby(['U_TECNICA', 'Ranking']).agg({
                'THP Personal': 'mean',
                'THP Movistar': 'mean',
                'THP Claro': 'mean',
                'latitud_sitio': 'first',
                'longitud_sitio': 'first',
                'provincia': 'first',
                'localidad': 'first'})
            if not filtered_binesL.empty:
                for index, row in filtered_binesL.iterrows():
                    color = 'green' if row['THP Claro'] > st.session_state['umbral_thp'] else 'red'
                    mc_plan = folium.Marker([row['latitud_sitio'], row['longitud_sitio']],            
                        popup = f"U_TECNICA: {row['U_TECNICA']}<br>THP Claro: {row['THP Claro']:.2f}",
                        icon=plugins.BeautifyIcon(
                            icon_size=(10,10),
                            icon_shape="doughnut",
                            border_color=color,
                            text_color="#007799",
                            background_color=color))
                    mc_plan.add_to(dual_map1.m2)
            folium_static(dual_map1, width=920)

            st.empty()
                    # Crear columnas para los selectores
            col1, col2 = st.columns([1.1,2])
            with col1:
                st.image('./assets/leyenda_port.png')
            with col2:
                st.image('./assets/leyenda_umb.png')
            #st.divider()
            st.text("")
            st.text("")


#------------------------------------------------------------------------------------------------------------------------


            # Crear columnas para los selectores
            col11, col22 = st.columns([1.1,2])
            with col11:
                st.markdown("<h5 style='color: #537a9b'; >Densidad de muestras por cantidad de portadoras</h5>", unsafe_allow_html=True)
                #st.markdown(f"**Densidad de muestras por cantidad de portadoras**")
            with col22:
                st.markdown("<h5 style='color: #537a9b'; >Plan por Sitio</h5>", unsafe_allow_html=True)
                #st.markdown(f'**Plan por Sitio**')
            # Crear columnas para las referencias

            # Crear el DualMap
            # Crear el segundo DualMap
            dual_map2 = DualMap(location=[filtered_binesL['latitud_sitio'].mean(), filtered_binesL['longitud_sitio'].mean()], zoom_start=11)

            # Añadir la capa de calor al primer mapa (m1) de dual_map2
            gradient_colors_muestrasPort = {
                0.0: '#2C7BB6',
                0.65: '#00CCBC',
                0.77: '#FFFF8C',
                0.87: '#F29E2E',
                0.95: '#D7191C'
            }
            radius = 20
            blur = 8
            min_opacity = 0.18

            filtered_data['Muestras Port'] = filtered_data['Muestras Claro'] / filtered_data['portadoras']

            heatmap_muestrasPort = HeatMap(
                data=filtered_data[['latitud_bin', 'longitud_bin', 'Muestras Port']].values.tolist(),
                name="Muestras s/ Portadoras",
                radius=radius,
                blur=blur,
                min_opacity=min_opacity,
                max_zoom=18,
                gradient=gradient_colors_muestrasPort,
                show=True
            )
            heatmap_muestrasPort.add_to(dual_map2.m1)

            # Añadir marcadores al segundo mapa (m2) de dual_map2
            plan_colors = {
                '5G - Fase 1 (432)': 'green',
                '5G - 45': 'green',
                'Expansiones 2024': 'blue',
                'Sectorizaciones 2024': 'purple',
                'Sin Plan / Alta Carga': 'orange',
                'Sin Plan': 'red',
                'Restric. para Implem.': 'gray',
                'Baja Definitiva': 'black'
            }

            # Función para crear íconos de clúster personalizados
            def create_cluster_icon(color):
                return f"""
                function(cluster) {{
                    return new L.DivIcon({{
                        html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
                        className: 'marker-cluster',
                        iconSize: new L.Point(40, 40)
                    }});}}
                """

            for planpg, color in plan_colors.items():
                mc_plan = MarkerCluster(icon_create_function=create_cluster_icon(color),
                                        maxClusterRadius=1)
                for index, row in filtered_sitios.iterrows():
                    if row['plan general'] == planpg:
                        folium.Marker(
                            location=[row['latitud'], row['longitud']],
                            popup=f"U_TECNICA: {row['U_TECNICA']}, {planpg}",
                            icon=plugins.BeautifyIcon(
                                icon_size=(6, 6),
                                icon_shape="doughnut",
                                border_color=color,
                                text_color="#007799",
                                background_color=color
                            )
                        ).add_to(mc_plan)
                # Añadir la capa de marcadores solo si hay datos para esa capa
                if len(mc_plan._children) > 0:
                    capaport_st = folium.FeatureGroup(name=f'<span style="color:{color}">{planpg}</span>', show=True, overlay=True)
                    capaport_st.add_child(mc_plan)
                    dual_map2.m2.add_child(capaport_st)
            folium.LayerControl(collapsed=False).add_to(dual_map2.m2)
            # Renderizar el segundo DualMap
            folium_static(dual_map2, width=920)

            st.empty()
            # Crear columnas para los selectores
            col4, col5 = st.columns([1.1,2])
            with col4:
                st.image('./assets/leyenda_dens.png')            
            with col5:
                st.image('./assets/leyenda_plan.png')
            st.divider()


#------------------------------------------------------------------------------------------------------------------------


    st.markdown("<h4 style='color: #537a9b'; >Tabla de datos y Sitios por cantidad de muestras</h4>", unsafe_allow_html=True)
    #st.markdown('**Tabla de datos y Sitios por cantidad de muestras**')

    columnas = ['U_TECNICA','provincia','localidad','Muestras Claro','THP Claro']
    bines = filtered_binesP[columnas]
    bines['Muestras Claro'] = bines['Muestras Claro'].astype(int)
    bines = pd.merge(bines, sitios[['U_TECNICA','plan','plan general']], on=['U_TECNICA'])
    bines = bines.rename(columns={
        'provincia': 'Provincia',
        'localidad': 'Localidad',
        'plan': 'Plan',
        'plan general': 'Plan General'})
    bines = bines.sort_values(by='Muestras Claro', ascending=False)
    bines['THP Claro'] = bines['THP Claro'].round(2)
    st.dataframe(bines.style.apply(color_fila_por_columna, axis=1),width=920, hide_index=True)


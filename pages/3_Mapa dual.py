import os
import numpy as np
import pandas as pd
import streamlit as st
import folium
import folium.plugins as plugins
from streamlit_folium import folium_static
from folium.plugins import DualMap, MarkerCluster
from PIL import Image


icon_path = 'assets/icon.png'
icon_image = Image.open(icon_path)

st.set_page_config(page_title='Mapa Dual',
                   page_icon=icon_image,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items=None)



# Inicializar valores en el estado de la sesión si no están definidos
if 'periodo_selected1' not in st.session_state:
    st.session_state['periodo_selected1'] = None
if 'periodo_selected2' not in st.session_state:
    st.session_state['periodo_selected2'] = None
if 'provincia_selected' not in st.session_state:
    st.session_state['provincia_selected'] = None
if 'localidad_selected' not in st.session_state:
    st.session_state['localidad_selected'] = None

# Lista de archivos en la carpeta Dataset
folder_path = './assets/Dataset'
dataset_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

def categorizar(val):
    if val < 0:
        return "Sube"
    elif val > 0:
        return "Baja"
    else:
        return "-"
    
def color_fila_por_columna(row):
    if row['Variación'] == 'Baja':
        return ['background-color: pink'] * len(row)
    else:
        return [''] * len(row)

with st.sidebar:
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader('Filtros')
    with col2:
        button = st.button("Generar Mapa")

    col1, col2 = st.columns(2)
    with col1:
        periodos_options1 = [f[1:7] for f in dataset_files]
        periodos_dict1 = {f[1:7]: f for f in dataset_files}
        
        if periodos_options1:
            periodo_selected1 = st.selectbox('Periodo 1', periodos_options1, index=len(periodos_options1) - 2)
            st.session_state['periodo_selected1'] = periodo_selected1
            selected_file1 = periodos_dict1[st.session_state['periodo_selected1']]
            file_path1 = os.path.join(folder_path, selected_file1)
            bines1 = pd.read_csv(file_path1)
        else:
            st.warning("No se encontraron archivos en la carpeta Dataset.")
            bines1 = pd.DataFrame()

    with col2:
        periodos_options2 = [f[1:7] for f in dataset_files]
        periodos_dict2 = {f[1:7]: f for f in dataset_files}
        
        if periodos_options2:
            periodo_selected2 = st.selectbox('Periodo 2', periodos_options2, index=len(periodos_options2) - 1)
            st.session_state['periodo_selected2'] = periodo_selected2
            selected_file2 = periodos_dict2[st.session_state['periodo_selected2']]
            file_path2 = os.path.join(folder_path, selected_file2)
            bines2 = pd.read_csv(file_path2)
        else:
            st.warning("No se encontraron archivos en la carpeta Dataset.")
            bines2 = pd.DataFrame()

    if not bines1.empty:
        provincia_options = sorted(bines1['provincia'].unique())
        provincia_selected = st.selectbox("Provincia", provincia_options)
        st.session_state['provincia_selected'] = provincia_selected
        if st.session_state['provincia_selected']:
            filtered_bines1 = bines1[bines1['provincia'] == st.session_state['provincia_selected']]
            filtered_bines2 = bines2[bines2['provincia'] == st.session_state['provincia_selected']]
            localidad_options = sorted(filtered_bines1['localidad'].unique())
            localidad_selected = st.selectbox("Localidad", localidad_options)
            st.session_state['localidad_selected'] = localidad_selected
            if st.session_state['localidad_selected']:
                filtered_bines1 = filtered_bines1[filtered_bines1['localidad'] == st.session_state['localidad_selected']]
                filtered_bines2 = filtered_bines2[filtered_bines2['localidad'] == st.session_state['localidad_selected']]
    else:
        filtered_bines1 = pd.DataFrame()
        filtered_bines2 = pd.DataFrame()

    columnas = ['U_TECNICA','localidad','provincia','latitud_sitio','longitud_sitio','Ranking']
    filtered_bines1 = filtered_bines1[columnas]
    filtered_bines2 = filtered_bines2[columnas]

    filtered_bines1 = filtered_bines1[~filtered_bines1['Ranking'].astype(str).str.contains('!')]
    filtered_bines2 = filtered_bines2[~filtered_bines2['Ranking'].astype(str).str.contains('!')]

    filtered_bines1['Ranking'] = filtered_bines1['Ranking'].astype(int)
    filtered_bines1 = filtered_bines1.groupby('U_TECNICA', as_index=False).agg({'Ranking': 'mean', 'latitud_sitio': 'first', 'longitud_sitio': 'first', 'provincia': 'first', 'localidad': 'first'})
    filtered_bines1['Ranking'] = np.ceil(filtered_bines1['Ranking']).astype(int)
    filtered_bines1['Ranking'] = filtered_bines1['Ranking'].astype(int).round(0)
    filtered_bines1 = filtered_bines1.sort_values(by='U_TECNICA')
    filtered_bines2['Ranking'] = filtered_bines2['Ranking'].astype(int)
    filtered_bines2 = filtered_bines2.groupby('U_TECNICA', as_index=False).agg({'Ranking': 'mean', 'latitud_sitio': 'first', 'longitud_sitio': 'first', 'provincia': 'first', 'localidad': 'first'})
    filtered_bines2['Ranking'] = np.ceil(filtered_bines2['Ranking']).astype(int)
    filtered_bines2['Ranking'] = filtered_bines2['Ranking'].astype(int).round(0)
    filtered_bines2 = filtered_bines2.sort_values(by='U_TECNICA')
    

    filtered_bines1['latitud_sitio'] = filtered_bines1['latitud_sitio'].astype(str)
    filtered_bines1['longitud_sitio'] = filtered_bines1['longitud_sitio'].astype(str)
    filtered_bines2['latitud_sitio'] = filtered_bines2['latitud_sitio'].astype(str)
    filtered_bines2['longitud_sitio'] = filtered_bines2['longitud_sitio'].astype(str)
    # Reemplazar comas por puntos y convertir las columnas a tipo float
    filtered_bines1['latitud_sitio'] = filtered_bines1['latitud_sitio'].str.replace(',', '.').astype(float)
    filtered_bines1['longitud_sitio'] = filtered_bines1['longitud_sitio'].str.replace(',', '.').astype(float)
    filtered_bines2['latitud_sitio'] = filtered_bines2['latitud_sitio'].str.replace(',', '.').astype(float)
    filtered_bines2['longitud_sitio'] = filtered_bines2['longitud_sitio'].str.replace(',', '.').astype(float)
    #Crear dataframe con el detalle combinado de ambas tablas
    tabla = pd.merge(filtered_bines1, filtered_bines2[['U_TECNICA','Ranking']], on=['U_TECNICA'])
    columnas2 = ['U_TECNICA','provincia','localidad','Ranking_x','Ranking_y']
    tabla = tabla.reindex(columns=columnas2)
    tabla['Variación'] = tabla['Ranking_y'] - tabla['Ranking_x']
    # Aplicar la función a la columna 'Valores'
    tabla['Variación'] = tabla['Variación'].apply(categorizar)
    tabla = tabla.rename(columns={
    'Ranking_x': f'Ranking {periodo_selected1}',
    'Ranking_y': f'Ranking {periodo_selected2}.',
    'provincia': 'Provincia',
    'localidad': 'Localidad'})
    tabla = tabla.sort_values(by='Variación', ascending=False)

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
    
    
# Verificar si se ha presionado el botón "Generar Mapa"
if periodo_selected1 == periodo_selected2:
    st.warning('Debe seleccionar distintos períodos')
else:   

    if button:
        ranking_colors = {1: 'green', 2: 'orange', 3: 'red'}

        # Función para crear íconos de clúster personalizados
        def create_cluster_icon(color):
            return f"""
            function(cluster) {{
                return new L.DivIcon({{
                    html: '<div style="background-color: {color}; border-radius: 50%;"><span>' + cluster.getChildCount() + '</span></div>',
                    className: 'marker-cluster',
                    iconSize: new L.Point(40, 40)
                }});}}"""


        st.markdown("<h3 style='color: #537a9b'; >Comparación de Sitios por Ranking</h3>", unsafe_allow_html=True)
        #st.subheader('Comparación de Sitios por Ranking')
        #st.divider()
        col1, col2 = st.columns([1.1,2])
        with col1:
            st.markdown(f"<h5 style='color: #537a9b'; >Periodo: {periodo_selected1}", unsafe_allow_html=True)
            #st.markdown(f'**Periodo: {periodo_selected1}**')
        with col2:
            st.markdown(f"<h5 style='color: #537a9b'; >Periodo: {periodo_selected2}", unsafe_allow_html=True)
            #st.markdown(f'**Periodo: {periodo_selected2}**')

        # Crear el mapa dual
        dual_map = DualMap(location=[filtered_bines1['latitud_sitio'].mean(), filtered_bines1['longitud_sitio'].mean()], zoom_start=10)

        if not filtered_bines1.empty:
            for ranking1 in ranking_colors.keys():
                filtered_ranking1 = filtered_bines1[filtered_bines1['Ranking'] == ranking1]
                if not filtered_ranking1.empty:
                    mc1 = MarkerCluster(icon_create_function=create_cluster_icon(ranking_colors[ranking1]), 
                    name=f'Ranking {ranking1}', 
                    maxClusterRadius=5)
                    for _, row in filtered_ranking1.iterrows():
                        mc1.add_child(folium.Marker(
                            location=[row['latitud_sitio'], row['longitud_sitio']],
                            popup=f"U_TECNICA: {row['U_TECNICA']}",
                            icon=plugins.BeautifyIcon(
                                icon_size=(10,10),
                                icon_shape="doughnut",
                                border_color=ranking_colors[ranking1],
                                text_color="#007799",
                                background_color=ranking_colors[ranking1],
                                show=True))) 
                    mc1.add_to(dual_map.m1)

        if not filtered_bines2.empty:
            for ranking2 in ranking_colors.keys():
                filtered_ranking = filtered_bines2[filtered_bines2['Ranking'] == ranking2]
                if not filtered_ranking.empty:
                    mc2 = MarkerCluster(icon_create_function=create_cluster_icon(ranking_colors[ranking2]), 
                    name=f'Ranking {ranking2}', 
                    maxClusterRadius=5)
                    for _, row in filtered_ranking.iterrows():
                        mc2.add_child(folium.Marker(
                            location=[row['latitud_sitio'], row['longitud_sitio']],
                            popup=f"U_TECNICA: {row['U_TECNICA']}",
                            icon=plugins.BeautifyIcon(
                                icon_size=(10,10),
                                icon_shape="doughnut",
                                border_color=ranking_colors[ranking2],
                                text_color="#007799",
                                background_color=ranking_colors[ranking2],
                                show=True)))  
                    mc2.add_to(dual_map.m2)
        # Mostrar el mapa en Streamlit
        folium_static(dual_map, width=920)

        col3, col4 = st.columns([1.1,2])
        with col3:
            st.image('./assets/leyenda_ranking.png')
        with col4:
            st.image('./assets/leyenda_ranking.png')

        st.divider()
        st.markdown(f"<h3 style='color: #537a9b'; >Tabla de comparación de Ranking entre los períodos {periodo_selected1} y {periodo_selected2}</h3>", unsafe_allow_html=True)
        #st.markdown(f'**Tabla de comparación de Ranking entre los períodos {periodo_selected1} y {periodo_selected2}**')
        st.dataframe(tabla.style.apply(color_fila_por_columna, axis=1),width=720, hide_index=True)
    
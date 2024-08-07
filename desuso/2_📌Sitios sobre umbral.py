import streamlit as st
import pandas as pd
import folium
import folium.plugins as plugins
from streamlit_folium import folium_static

@st.cache_data
def load_data():
    data = pd.read_csv('./assets/P062024.csv')
    data = data[data['Ranking'].isin(['1', '2', '3'])].reset_index()
    data['Ranking'] = data['Ranking'].astype(int)
    data = data[['location','U_TECNICA','THP Claro','THP Movistar','THP Personal','latitud_sitio','longitud_sitio','provincia','localidad','Ranking']]
    data = data.groupby(['U_TECNICA', 'Ranking']).agg({
        'THP Personal': 'mean',
        'THP Movistar': 'mean',
        'THP Claro': 'mean',
        'latitud_sitio': 'first',
        'longitud_sitio': 'first',
        'provincia': 'first',
        'localidad': 'first' 
    }).reset_index()
    data['Ranking'] = data['Ranking'].round().astype(int)
    data['Ranking'] = data['Ranking'].astype(str)
    data['latitud_sitio'] = data['latitud_sitio'].astype(str)
    data['longitud_sitio'] = data['longitud_sitio'].astype(str)
    data['latitud_sitio'] = data['latitud_sitio'].str.replace(',', '.').astype(float)
    data['longitud_sitio'] = data['longitud_sitio'].str.replace(',', '.').astype(float)
    return data

data = load_data()

# Inicializar valores en el estado de la sesión si no están definidos
if 'provincia_selected' not in st.session_state:
    st.session_state['provincia_selected'] = []
if 'localidad_selected' not in st.session_state:
    st.session_state['localidad_selected'] = []
if 'ranking_selected' not in st.session_state:
    st.session_state['ranking_selected'] = []
if 'umbral_thp' not in st.session_state:
    st.session_state['umbral_thp'] = 0.0

#-------------------------------------------------------------------------------------------
# CODIGO DEL MAPA
# SIDEBAR
with st.sidebar:
    st.markdown(
        '<p class="small-font">'
        '<strong>Utilizando los filtros se arma un mapa de Sitios, se compara el THP de Claro con el umbral de THP.</strong><br>'
        '- El umbral de THP se calcula como el promedio de los THP Max de cada sitio filtrado.<br>'
        '- Si el THP de Claro es mayor al umbral, el sitio figura en verde, sino en rojo.<br>',
        unsafe_allow_html=True)
    st.image(f'./assets/logo.png', width=75)

# Configurar la interfaz de usuario
st.subheader("Sitios sobre umbral THP")

# Crear columnas para los selectores
col1, col2, col3 = st.columns(3)
# Selectores para filtrar los datos
with col1:
    provincia_options = sorted(data['provincia'].unique())
    st.session_state['provincia_selected'] = st.multiselect("Provincia (puede ser más de 1)", provincia_options, st.session_state['provincia_selected'])
# Filtrar localidades basadas en la selección de provincias
if st.session_state['provincia_selected']:
    filtered_data1 = data[data['provincia'].isin(st.session_state['provincia_selected'])]
else:
    filtered_data1 = data
with col2:
    localidad_options = sorted(filtered_data1['localidad'].unique())
    st.session_state['localidad_selected'] = st.multiselect("Localidad (puede ser más de 1)", localidad_options, st.session_state['localidad_selected'])
# Filtrar rankings basados en la selección de provincias y localidades
if st.session_state['provincia_selected'] or st.session_state['localidad_selected']:
    filtered_data2 = data[
        (data['provincia'].isin(st.session_state['provincia_selected']) if st.session_state['provincia_selected'] else True) &
        (data['localidad'].isin(st.session_state['localidad_selected']) if st.session_state['localidad_selected'] else True)]
else:
    filtered_data2 = data
with col3:
    ranking_options = sorted(filtered_data2['Ranking'].unique())
    st.session_state['ranking_selected'] = st.multiselect("Ranking (puede ser más de 1)", ranking_options, st.session_state['ranking_selected'])

# Botón para generar el mapa
if st.button("Generar mapa"):
    # Filtrar los datos según las selecciones del usuario
    filtered_data3 = data[
        (data['Ranking'].isin(st.session_state['ranking_selected'])) &
        (data['provincia'].isin(st.session_state['provincia_selected'])) &
        (data['localidad'].isin(st.session_state['localidad_selected']))]
    
    # Calcular el valor promedio de THP Max
    THP_P = filtered_data2['THP Personal'].mean()
    THP_M = filtered_data2['THP Movistar'].mean()
    THP_C = filtered_data2['THP Claro'].mean()
    st.session_state['umbral_thp'] = max(THP_P, THP_M, THP_C)
    # Mostrar el valor de Umbral THP
    st.markdown(f"### Umbral THP: {st.session_state['umbral_thp']:.2f}")
    
    # Asegúrate de que filtered_data3 no esté vacío antes de generar el mapa
    if not filtered_data3.empty:
        # Generar el mapa
        mapa = folium.Map(location=[filtered_data3['latitud_sitio'].mean(), filtered_data3['longitud_sitio'].mean()], zoom_start=10)  # Ajusta la ubicación y el zoom según tus necesidades
        # Añadir marcadores al mapa
        for index, row in filtered_data3.iterrows():
            # Determinar el color del marcador
            color = 'green' if row['THP Claro'] > st.session_state['umbral_thp'] else 'red'
            folium.Marker(
                [row['latitud_sitio'], row['longitud_sitio']],            
                popup = f"U_TECNICA: {row['U_TECNICA']}<br>THP Claro: {row['THP Claro']:.2f}",
                icon=plugins.BeautifyIcon(
                    icon_size=(10,10),
                    icon_shape="doughnut",
                    border_color=color,
                    text_color="#007799",
                    background_color=color)
            ).add_to(mapa)
        # Guardar el mapa en el estado de la sesión
        st.session_state['mapa'] = mapa
        # Mostrar el mapa en Streamlit
        folium_static(mapa, width=1024)
    else:
        st.warning("No se encontraron datos para los filtros seleccionados.")
        
# Mostrar el mapa guardado en el estado de la sesión si existe
if 'mapa' in st.session_state:
    st.markdown(f"### Umbral THP: {st.session_state['umbral_thp']:.2f}")
    folium_static(st.session_state['mapa'], width=1024)

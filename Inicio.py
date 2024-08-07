import streamlit as st
from PIL import Image
import os
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder


#--------------------------------------------------------------------------------------------
# CONFIGURACION DE LA PAGINA #
icon_path = 'assets/icon.png'
icon_image = Image.open(icon_path)
iconFB_path = 'assets/iconFB.png'
iconFB_image = Image.open(iconFB_path)

st.set_page_config(page_title='Throughput Claro',
                   page_icon=icon_image,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items=None)

folder_path = './assets/Dataset'
dataset_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
periodos_options = [f[1:7] for f in dataset_files]
periodos_dict = {f[1:7]: f for f in dataset_files}

def color_fila_por_columna(row):
    if row['Variación'] == 'Baja':
        return ['background-color: pink'] * len(row)
    else:
        return [''] * len(row)
    

# SIDEBAR

st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        color: #FFFFFF;  /* Cambia este valor por el color que desees */
    }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    # Filtrar los archivos para mostrar solo los primeros 6 caracteres
    periodo_selected = st.selectbox('Periodo', periodos_options, index=len(periodos_options) - 1)
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
        

# Función para cargar los datos
def cargarDatos(periodo):
    selected_file = periodos_dict[periodo]
    file_path = os.path.join(folder_path, selected_file)
    df = pd.read_csv(file_path, encoding='utf-8')
    return df

# Cargar datos del periodo seleccionado y del periodo anterior
data = cargarDatos(periodo_selected)

# Determinar el periodo anterior
periodo_index = periodos_options.index(periodo_selected)
if periodo_index > 0:
    periodo_anterior = periodos_options[periodo_index - 1]
    data_anterior = cargarDatos(periodo_anterior)
else:
    data_anterior = pd.DataFrame()  # Si no hay periodo anterior, crear un DataFrame vacío

# Procesar los datos actuales
TotMuestras = data['Muestras Claro'].sum()
data = data.groupby('localidad').agg({
    'provincia': 'first',  # Mantener el primer valor de la provincia
    'mercado': 'first',
    'pais': 'first',
    'Muestras Claro': 'sum'})
data['Muestras Claro'] = data['Muestras Claro'].astype(int)
data['Fracción'] = data['Muestras Claro'] / TotMuestras
data = data.sort_values(by='Fracción', ascending=False)
data['Fracción'] = data['Fracción'].apply(lambda x: '{:.2f}%'.format(x * 100))
data = data.reset_index()
data = data.rename(columns={
    'provincia': 'Provincia',
    'localidad': 'Localidad',
    'mercado': 'Mercado',
    'pais': 'País'})
data.insert(0, 'Posición', range(1, len(data) + 1))
data = data.head(20)

# Procesar los datos del periodo anterior
if not data_anterior.empty:
    TotMuestras_anterior = data_anterior['Muestras Claro'].sum()
    data_anterior['Localidad'] = data_anterior['localidad'].apply(lambda x: 'AMBA' if x.startswith('Comuna') else x)
    data_anterior = data_anterior.groupby('Localidad').agg({
        'provincia': 'first',
        'mercado': 'first',
        'pais': 'first',
        'Muestras Claro': 'sum'})
    data_anterior['Muestras Claro'] = data_anterior['Muestras Claro'].astype(int)
    data_anterior['Fracción'] = data_anterior['Muestras Claro'] / TotMuestras_anterior
    data_anterior = data_anterior.sort_values(by='Fracción', ascending=False)
    data_anterior = data_anterior.reset_index()
    data_anterior['Pos. Ant.'] = range(1, len(data_anterior) + 1)
else:
    data_anterior = pd.DataFrame(columns=['Localidad', 'Pos. Ant.'])

# Combinar datos actuales con datos del periodo anterior
data = pd.merge(data, data_anterior[['Localidad', 'Pos. Ant.']], on='Localidad', how='left')

# Calcular el cambio de posición
data['Cambio'] = data['Pos. Ant.'] - data['Posición']
data = data.fillna({'Pos. Ant.': '-', 'Cambio': '-'})
data['Cambio'] = data['Cambio'].apply(lambda x: '{:+d}'.format(int(x)) if isinstance(x, (int, float)) else x)

orden = ['Posición', 'Provincia', 'Localidad', 'Mercado', 'País', 'Muestras Claro', 'Fracción', 'Cambio']
data = data.reindex(columns=orden)

#---------------------------------------------------------------------------------------------------
# CODIGO DE LA PAGINA

titulo = st.container()
col1,col2 = st.columns([2.2 ,2.1])
with titulo:
    with col1:
        st.markdown("<h1 style='padding: 0px; color: #537a9b'; >Análisis de datos de Facebook</h1>", unsafe_allow_html=True)
    with col2:
        st.image(iconFB_image, width=50)

st.markdown("<h5 style='color: #537a9b'; >En el menú a tu izquierda puede acceder a las páginas del análisis.</h5>", unsafe_allow_html=True)
st.markdown("<h5 style='color: #537a9b'; >Los datos se extraen y cargan en la base de datos del Área, asegurando un proceso eficiente</h5>", unsafe_allow_html=True)

st.divider()

st.markdown("<h3 style='color: #537a9b'; >Ranking de localidades por muestras</h3>", unsafe_allow_html=True)
# Convertir el DataFrame a HTML con estilo CSS para centrar y ajustar el ancho
st.dataframe(data.style.apply(color_fila_por_columna, axis=1),width=720, hide_index=True)




#gb = GridOptionsBuilder.from_dataframe(data)
#gb.configure_pagination()
##gb.configure_side_bar()
#gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
#gridOptions = gb.build()
#AgGrid(data, gridOptions=gridOptions, height=650)
#
#
#table_html = data.to_html(index=False, escape=False, classes='mystyle', justify='center')
#
## CSS para centrar el contenido y ajustar el ancho de la tabla
#css = """
#<style>
#.mystyle {
#    font-size: 11pt; 
#    font-family: Arial, Helvetica, sans-serif;
#    border-collapse: collapse; 
#    width: 100%; 
#    margin: 0;
#    padding: 0;
#    text-align: center;
#    color: #717171
#}
#.mystyle th {
#    background-color: #f2f2f2;
#    text-align: center;
#    padding: 8px;
#}
#.mystyle td {
#    padding: 8px;
#    text-align: center;
#}
#.mystyle tr:nth-child(even) {
#    background-color: #f9f9f9;
#}
#</style>
#"""
#
## Mostrar la tabla con estilo CSS
#st.markdown(css + table_html, unsafe_allow_html=True)

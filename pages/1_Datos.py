import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
from PIL import Image


icon_path = 'assets/icon.png'
icon_image = Image.open(icon_path)

st.set_page_config(page_title='Datos',
                   page_icon=icon_image,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items=None)


with st.sidebar:
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
    

# Ruta local del archivo CSV
file_path = (f'./assets/Datos_reporteFB.csv')

@st.cache_data
def cargar_datos(file_path):
    # Leer el CSV especificando la codificación y el separador
    df = pd.read_csv(file_path, encoding='utf-8', sep=';')
    # Convertir las columnas THP a numéricas si es posible
    df['THP Claro'] = pd.to_numeric(df['THP Claro'].str.replace(',', '.'), errors='coerce')
    df['THP Personal'] = pd.to_numeric(df['THP Personal'].str.replace(',', '.'), errors='coerce')
    df['THP Movistar'] = pd.to_numeric(df['THP Movistar'].str.replace(',', '.'), errors='coerce')
    
    # Eliminar las comas de las columnas de muestras y convertir a numérico
    df['Muestras Claro'] = pd.to_numeric(df['Muestras Claro'].str.replace(',', ''), errors='coerce')
    df['Muestras Personal'] = pd.to_numeric(df['Muestras Personal'].str.replace(',', ''), errors='coerce')
    df['Muestras Movistar'] = pd.to_numeric(df['Muestras Movistar'].str.replace(',', ''), errors='coerce')

    return df

try:
    # Cargar los datos
    df = cargar_datos(file_path)

    # Orden Meses
    meses_ordenados = pd.read_csv(file_path, encoding='utf-8', sep=';')
    meses_ordenados = df['Periodo'].unique()
    meses_ordenados = (meses_ordenados.tolist())
    
    # Calcular promedios THP para cada periodo y operador
    promedios = df.groupby('Periodo')[['THP Claro', 'THP Personal', 'THP Movistar']].mean().round(2).reset_index()

    # Asegurar que el periodo esté en el orden correcto 
    promedios['Periodo'] = pd.Categorical(promedios['Periodo'], categories=meses_ordenados, ordered=True)
    promedios = promedios.sort_values('Periodo')

     # Verificar si hay datos antes de continuar
    if promedios.empty:
        st.warning("No hay datos disponibles para los períodos seleccionados.")
    else:
        # Columnas de THP   
        thp_columns = ['THP Claro', 'THP Personal', 'THP Movistar']   


        # Función para obtener el valor del THP y la variación respecto al mes anterior
        def obtener_valores(promedios, mes, columna):
            valor_mes = promedios.loc[promedios['Periodo'] == mes, columna].values[0]
            mes_anterior = meses_ordenados[meses_ordenados.index(mes) - 1] if meses_ordenados.index(mes) > 0 else None
            if mes_anterior:
                valor_anterior = promedios.loc[promedios['Periodo'] == mes_anterior, columna].values[0]
                variacion = (valor_mes - valor_anterior) / valor_anterior * 100
            else:
                variacion = None
            return valor_mes, variacion
        cols = st.columns([1,1,1,1])
        with cols[0]:
            # Crear un filtro para seleccionar el mes
            mes_seleccionado = st.selectbox("Seleccionar Mes", meses_ordenados)
            
        for i, metrica in enumerate(thp_columns):
            with cols[i + 1]:
                #st.markdown(metrica)
                valor_mes, variacion = obtener_valores(promedios, mes_seleccionado, metrica)
                if variacion is not None:
                    st.metric(label=metrica, value=f'{valor_mes:.2f} MB', delta=f'{variacion:.2f}%')
                else:
                    st.metric(label="", value=f'{valor_mes:.2f} MB')
                    

    # Widget de selección única para la Provincia
    provincia_seleccionada = st.sidebar.selectbox("Provincia", df["Provincia"].unique())

    # Filtrar por Provincia seleccionada
    df_filtered = df[df["Provincia"] == provincia_seleccionada]

    # Widget de selección múltiple para la localidad
    localidad_seleccionada = st.sidebar.multiselect("Localidad", df_filtered["Departamento"].unique())

    # Filtrar por localidad seleccionada
    if not localidad_seleccionada:
        df_filtered_localidades = df_filtered.copy()
    else:
        df_filtered_localidades = df_filtered[df_filtered["Departamento"].isin(localidad_seleccionada)]

    # Convertir la columna Periodo a categoría con el orden deseado
    df_filtered['Periodo'] = pd.Categorical(df_filtered['Periodo'], categories=meses_ordenados, ordered=True)
    df_filtered_localidades['Periodo'] = pd.Categorical(df_filtered_localidades['Periodo'], categories=meses_ordenados, ordered=True)

    if not df_filtered.empty:
        # Gráfico de líneas por provincia (THP Claro)
        df_grouped_line_provincias_claro = df_filtered.groupby(['Periodo', 'Provincia'])['THP Claro'].mean().round(2).reset_index()

        fig_line_provincias_claro = px.line(df_grouped_line_provincias_claro, x='Periodo', y='THP Claro', color='Provincia',
                                            line_group='Provincia', markers=True, 
                                            labels={'THP Claro': 'THP (GB)'},
                                            title='Provincia',text='THP Claro')

        # Configurar el gráfico de líneas para mostrar los valores al pasar el mouse
        fig_line_provincias_claro.update_traces(mode='lines+markers', hovertemplate='%{y}')
        fig_line_provincias_claro.update_layout(hovermode='closest', yaxis=dict(range=[0, df_grouped_line_provincias_claro['THP Claro'].max() * 2]))

        # Asignar color específico
        fig_line_provincias_claro.update_traces(line=dict(color='red'))

    # Gráfico de líneas por localidad solo si hay selección de localidades (THP Claro)
    if localidad_seleccionada and not df_filtered_localidades.empty:
        df_grouped_line_localidades = df_filtered_localidades.groupby(['Periodo', 'Provincia', 'Departamento'])['THP Claro'].mean().reset_index()

        fig_line_localidades = px.line(df_grouped_line_localidades, x='Periodo', y='THP Claro', color='Departamento',
                                       markers=True, labels={'THP Claro': 'THP (GB)'},
                                       title='Localidad')

        # Configurar el gráfico de líneas para mostrar los valores al pasar el mouse
        fig_line_localidades.update_traces(mode='lines+markers', hovertemplate='%{y}')
        fig_line_localidades.update_layout(hovermode='closest', yaxis=dict(range=[0, df_grouped_line_localidades['THP Claro'].max() * 2]))
        
  # Verificar si hay datos antes de continuar
    if promedios.empty:
        st.warning("No hay datos disponibles para los períodos seleccionados.")
    else:
        # Crear un DataFrame para almacenar las variaciones porcentuales
        variaciones = pd.DataFrame({'Periodo': promedios['Periodo']})

        # Calcular las variaciones porcentuales mes a mes para cada operadora
        for operadora in ['THP Claro', 'THP Personal', 'THP Movistar']:
            variaciones[operadora] = (promedios[operadora].pct_change() * 100).round(2)

        # DataFrame para que sea compatible con Plotly
        variaciones = variaciones.melt(id_vars='Periodo', var_name='Operadora', value_name='Variacion')

        # Toggle para seleccionar entre promedios y variaciones
        
        st.markdown("<hr style='border: 1px solid darkred;'>", unsafe_allow_html=True)
        col1, col2 = st.columns((2,4))
        with col1:
           st.markdown("<h2 style='padding: 10px; color: #537a9b'; >THP Argentina</h2>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)  # Espacio vertical superior
            toggle = st.toggle("Evolucion Porcentual")

        # Seleccionar el conjunto de datos basado en el estado del toggle
        if toggle:
            selected_data = variaciones
            # Crear el gráfico de líneas para variaciones
            fig = px.line(selected_data, x='Periodo', y='Variacion', color='Operadora', 
                          labels={'Variacion': 'Variación (%)', 'Periodo': 'Mes'},
                           markers=True,
                           text='Variacion')
                          

            # Configurar el gráfico de líneas para mostrar los valores al pasar el mouse
            fig.update_traces(hovertemplate='%{y:.2f} %', textfont=dict(color='black'),textposition='top center')
        else:
            selected_data = promedios.melt(id_vars='Periodo', var_name='Operadora', value_name='THP')
            
            # Crear el gráfico de líneas para promedios
            fig = px.line(selected_data, x='Periodo', y='THP', color='Operadora', 
                          labels={'THP': 'THP (MB)', 'Periodo': 'Mes'},
                          markers=True,
                          text='THP')
                        
            # Configurar el gráfico de líneas para mostrar los valores al pasar el mouse
            fig.update_traces(hovertemplate='%{y:.2f} MB', textfont=dict(color='black'),textposition='top center')
        # Personalizar el gráfico
        color_map = {
            'THP Claro': 'red',
            'THP Personal': 'blue',
            'THP Movistar': '#00BFFF'
        }

        for operadora, color in color_map.items():
            fig.update_traces(line=dict(color=color), selector=dict(name=operadora))


        # Mostrar el gráfico
        st.plotly_chart(fig)
        
      # Gráfico de líneas comparativo (THP Claro, THP Personal, THP Movistar)
        df_grouped_comparison = df_filtered.groupby(['Periodo', 'Provincia'])[['THP Claro', 'THP Personal', 'THP Movistar']].mean().round(2).reset_index()
        col1, col2 = st.columns(2)
       
        st.subheader(provincia_seleccionada)

        # Convertir a formato largo para Plotly Express
        df_melted = df_grouped_comparison.melt(id_vars=['Periodo', 'Provincia'], 
                                               value_vars=['THP Claro', 'THP Personal', 'THP Movistar'],
                                               var_name='Operador', value_name='THP')

        # Toggle para seleccionar entre promedios y variaciones porcentuales
        # Crear dos columnas
        col1, col2 = st.columns((2, 4))

        with col1:
        # No necesitas `st.empty()` aquí a menos que quieras un espacio vacío explícito
            st.markdown("<h2 style='padding: 10px; color: #537a9b'; >THP Provincias</h2>", unsafe_allow_html=True)

        with col2:
        # No necesitas `st.empty()` aquí a menos que quieras un espacio vacío explícito
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)  # Espacio vertical superior
            
            toggle_comparativo = st.toggle("Evolución Porcentual")

        if toggle_comparativo:
            # Crear un DataFrame para almacenar las variaciones porcentuales comparativas
            variaciones_comparativas = df_grouped_comparison.copy()
            for operadora in ['THP Claro', 'THP Personal', 'THP Movistar']:
                variaciones_comparativas[f'{operadora} (%)'] = variaciones_comparativas.groupby('Provincia')[operadora].pct_change() * 100

            # Convertir a formato largo para Plotly Express
            df_melted_comparativo = variaciones_comparativas.melt(id_vars=['Periodo', 'Provincia'], 
                                                                   value_vars=[f'{operadora} (%)' for operadora in ['THP Personal', 'THP Movistar', 'THP Claro']],
                                                                   var_name='Operador', value_name='THP')
            

            fig_comparison = px.line(df_melted_comparativo, x='Periodo', y='THP', color='Operador', line_group='Provincia',
                                     markers=True,
                                     labels={'THP': 'Variación (%)', 'Operador': 'Operador'},text='THP')
            color_map = {'THP Claro': 'red', 'THP Personal': 'blue', 'THP Movistar': '#00BFFF'}
            for operador, color in color_map.items():
                fig_comparison.update_traces(line=dict(color=color), selector=dict(name=operador))
                fig_comparison.update_traces(hovertemplate='%{y:.2f} %', texttemplate='%{text:.2f} ', textfont=dict(color='black'),textposition='top center')
        else:
            # Crear el gráfico de líneas para promedios comparativos
            fig_comparison = px.line(df_melted, x='Periodo', y='THP', color='Operador', line_group='Provincia', 
                                     markers=True, 
                                     labels={'THP': 'Promedio THP', 'Operador': 'Operador'},text='THP')
            color_map = {'THP Claro': 'red', 'THP Personal': 'blue', 'THP Movistar': '#00BFFF'}  # Asegúrate de definir los colores correctos
            for operador, color in color_map.items():
                fig_comparison.update_traces(line=dict(color=color), selector=dict(name=operador))
                fig_comparison.update_traces(hovertemplate='%{y:.2f} MB', textfont=dict(color='black'),textposition='top center')
        
        # Mostrar el gráfico de líneas comparativo en Streamlit
        st.plotly_chart(fig_comparison)

    # Dividir la página en dos columnas para colocar los gráficos lado a lado
    st.markdown("<h2 style='padding: 0px; color: #537a9b'; >THP Claro</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)

    # Colocar el gráfico de provincias en la primera columna
    if not df_filtered.empty:
        with col1:
            st.plotly_chart(fig_line_provincias_claro)

    # Colocar el gráfico de localidades en la segunda columna
    if localidad_seleccionada and not df_filtered_localidades.empty:
        with col2:
            st.plotly_chart(fig_line_localidades)

    # Crear la tabla interactiva    
    gb = GridOptionsBuilder.from_dataframe(df_filtered_localidades)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
    gridOptions = gb.build()

    st.markdown("<hr style='border: 1px solid darkred;'>", unsafe_allow_html=True)
    # Mostrar la tabla
    st.markdown("<h2 style='padding: 0px; color: #537a9b'; >TABLERO</h2>", unsafe_allow_html=True)
    AgGrid(df_filtered_localidades, gridOptions=gridOptions)

except FileNotFoundError:
    st.error(f"El archivo no fue encontrado en la ruta especificada: {file_path}")

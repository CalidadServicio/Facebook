import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos desde el archivo CSV
data_path = f'./assets/data.csv'
df = pd.read_csv(data_path, encoding='utf-8')
st.header("THP CLARO", divider='rainbow')

# Mapear valores de periodo a nombres de meses y ordenar
periodo_mapping = {
    32024: 'Marzo',
    42024: 'Abril',
    52024: 'Mayo'
}

# Aplicar el mapeo a la columna periodo
df['Periodo'] = df['Periodo'].map(periodo_mapping)

# Ordenar el DataFrame por el orden de los meses
df['Periodo'] = pd.Categorical(df['Periodo'], categories=['Marzo', 'Abril', 'Mayo'], ordered=True)
df = df.sort_values(by='Periodo')

# Crear un widget de selección múltiple para la provincia
provincia_seleccionada = st.sidebar.multiselect("Provincia", df["provincia"].unique())
if not provincia_seleccionada:
    df2 = df.copy()
else:
    df2 = df[df["provincia"].isin(provincia_seleccionada)]

# Crear un widget de selección múltiple para la localidad
localidad_seleccionada = st.sidebar.multiselect("Localidad", df2["localidad"].unique())
if not localidad_seleccionada:
    df3 = df2.copy()
else:
    df3 = df2[df2["localidad"].isin(localidad_seleccionada)]

# Filtrar el DataFrame basado en las selecciones de Provincia y Localidad
if not provincia_seleccionada and not localidad_seleccionada:
    filtered_df = df
elif not localidad_seleccionada:
    filtered_df = df[df["provincia"].isin(provincia_seleccionada)]
elif not provincia_seleccionada:
    filtered_df = df[df["localidad"].isin(localidad_seleccionada)]
else:
    filtered_df = df3[df3["provincia"].isin(provincia_seleccionada) & df3["localidad"].isin(localidad_seleccionada)]

# Crear el gráfico de líneas usando Plotly
if not localidad_seleccionada:
    # Agrupar por periodo y provincia, calcular la suma de THP Claro
    df_grouped_line = filtered_df.groupby(['Periodo', 'provincia'])['THP Claro'].mean().reset_index()
    
    fig_line = px.line(df_grouped_line, x='Periodo', y='THP Claro', color='provincia', markers=True,
                       labels={'THP Claro': 'Suma THP Claro'},
                       title='Suma del Promedio THP Claro por Provincia')
else:
    # Agrupar por periodo, provincia y localidad, calcular el promedio de THP Claro
    df_grouped_line = filtered_df.groupby(['Periodo', 'provincia', 'localidad'])['THP Claro'].mean().reset_index()
    
    fig_line = px.line(df_grouped_line, x='Periodo', y='THP Claro', color='localidad', markers=True,
                       labels={'THP Claro': 'Promedio THP Claro'},
                       title='Promedio THP Claro por Localidad')

# Configurar el gráfico de líneas para mostrar los valores al pasar el mouse
fig_line.update_traces(mode='lines+markers', hovertemplate='%{y}')
fig_line.update_layout(hovermode='closest')

# Mostrar el gráfico de líneas en Streamlit
st.plotly_chart(fig_line)

# Grafico Barra
if not localidad_seleccionada:
    df_grouped_bar = filtered_df.groupby(['Periodo', 'provincia'])['THP Claro'].mean().reset_index()
    fig_bar = px.bar(df_grouped_bar, x='provincia', y='THP Claro', color='Periodo',
                     barmode='group',  # Ajuste para mostrar las barras agrupadas
                     labels={'THP Claro': 'Promedio THP Claro'},
                     title='Promedio del THP Claro por Provincia y Periodo')

    # Configurar el gráfico de barras para mostrar los valores al pasar el mouse y separar las barras
    fig_bar.update_traces(hovertemplate='%{y}')
    fig_bar.update_layout(hovermode='closest', bargap=0.3, bargroupgap=0.1)  # Ajustar el espacio entre las barras

    # Mostrar el gráfico de barras en Streamlit
    st.plotly_chart(fig_bar)
else:
    df_grouped_bar = filtered_df.groupby(['Periodo', 'provincia', 'localidad'])['THP Claro'].mean().reset_index()
    if 'localidad' in df_grouped_bar.columns:
        fig_bar = px.bar(df_grouped_bar, x='provincia', y='THP Claro', color='localidad',
                         barmode='group',  # Ajuste para mostrar las barras agrupadas
                         labels={'THP Claro': 'Promedio THP Claro'},
                         title='Promedio del THP Claro por Provincia y Periodo')

        # Configurar el gráfico de barras para mostrar los valores al pasar el mouse y separar las barras
        fig_bar.update_traces(hovertemplate='%{y}')
        fig_bar.update_layout(hovermode='closest', bargap=0.3, bargroupgap=0.1)  # Ajustar el espacio entre las barras

        # Mostrar el gráfico de barras en Streamlit
        st.plotly_chart(fig_bar)

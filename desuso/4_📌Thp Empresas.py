import pandas as pd
import streamlit as st
import plotly.express as px

# Cargar el archivo CSV
file_path = f'./assets/data.csv'
data = pd.read_csv(file_path)

# Mapear los valores de Periodo a nombres de meses legibles
data['Periodo'] = data['Periodo'].map({
    32024: 'Marzo 2024',
    42024: 'Abril 2024',
    52024: 'Mayo 2024'
})

    
st.header("Promedio THP", divider='rainbow')    

# Calcular promedios THP para cada periodo y operador
promedios = data.groupby('Periodo')[['THP Claro', 'THP Personal', 'THP Movistar']].mean().reset_index()

# Asegurar que el periodo esté en el orden correcto
promedios['Periodo'] = pd.Categorical(promedios['Periodo'], categories=['Marzo 2024', 'Abril 2024', 'Mayo 2024'], ordered=True)
promedios = promedios.sort_values('Periodo')


# Columnas de THP
thp_columns = ['THP Claro', 'THP Personal', 'THP Movistar']

# Crear un filtro para seleccionar el mes
mes_seleccionado = st.selectbox("Mes", ['Marzo 2024', 'Abril 2024', 'Mayo 2024'])

# Función para obtener el valor del THP y la variación respecto al mes anterior
def obtener_valores(promedios, mes, columna):
    valor_mes = promedios.loc[promedios['Periodo'] == mes, columna].values[0]
    mes_anterior = {'Abril 2024': 'Marzo 2024', 'Mayo 2024': 'Abril 2024'}.get(mes, None)
    if mes_anterior:
        valor_anterior = promedios.loc[promedios['Periodo'] == mes_anterior, columna].values[0]
        variacion = (valor_mes - valor_anterior) / valor_anterior * 100
    else:
        variacion = None
    return valor_mes, variacion

# Mostrar las métricas en columnas
cols = st.columns(3)
for i, metrica in enumerate(thp_columns):
    with cols[i]:
        st.subheader(metrica)
        valor_mes, variacion = obtener_valores(promedios, mes_seleccionado, metrica)
        if variacion is not None:
            st.metric(label="", value=f'{valor_mes:.2f} GB', delta=f'{variacion:.2f}%')
        else:
            st.metric(label="", value=f'{valor_mes:.2f} GB')

# Crear un gráfico de líneas mejorado con colores específicos
st.header("Grafico THP", divider='rainbow')
fig = px.line(
    promedios,
    x='Periodo',
    y=thp_columns,
    title='',
    labels={'value': 'THP (GB)', 'Periodo': 'Periodo'},
    markers=True
)

# Asignar colores específicos a cada línea
fig.update_traces(line=dict(color='red'), selector=dict(name='THP Claro'))
fig.update_traces(line=dict(color='blue'), selector=dict(name='THP Personal'))
fig.update_traces(line=dict(color='lightblue'), selector=dict(name='THP Movistar'))

# Personalizar el gráfico
fig.update_layout(
    title='',
    xaxis_title='Periodo',
    yaxis_title='THP (GB)',
    legend_title='Operadores',
    template='plotly_dark'  # Cambiar el tema a oscuro
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)

## Filtrar las columnas deseadas (para mostrar en el checkbox)
df_filtered = data[['pais','provincia','localidad', 'Muestras Claro', 'THP Claro', 'THP Personal', 'Muestras Personal', 'THP Movistar', 'Muestras Movistar','Ranking']]


# Título principal del dashboard
st.header("Tablero THP", divider='rainbow')

# Checkbox para mostrar/ocultar datos filtrados
if st.checkbox('Mostrar/Ocultar Datos Filtrados'):
    st.dataframe(df_filtered)

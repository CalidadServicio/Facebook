import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos desde el archivo CSV
data_path = f'./assets/data.csv'
df = pd.read_csv(data_path, encoding='utf-8')
st.header("THP CLARO ", divider='rainbow')

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


# Agrupar por periodo, provincia y localidad, calcular el promedio de THP Claro
df_grouped = filtered_df.groupby(['Periodo', 'provincia', 'localidad'])['THP Claro'].mean().reset_index()


# Crear gráfico de líneas usando matplotlib
fig, ax = plt.subplots(figsize=(10, 6))

# Iterar sobre cada provincia seleccionada para graficar líneas separadas por localidad
for provincia in provincia_seleccionada:
    data_provincia = df_grouped[df_grouped['provincia'] == provincia]
    for localidad in data_provincia['localidad'].unique():
        data_localidad = data_provincia[data_provincia['localidad'] == localidad]
        ax.plot(data_localidad['Periodo'], data_localidad['THP Claro'], marker='o', label=f"{provincia} - {localidad}")

# Configurar etiquetas y título
ax.set_xlabel('Periodo')
ax.set_ylabel('Promedio THP Claro')
ax.set_title('')
ax.legend()

# Rotar etiquetas del eje x para mejor visuaslización
plt.xticks(rotation=45)

# Mostrar gráfico en Streamlit
st.pyplot(fig)

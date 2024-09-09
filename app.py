import streamlit as st
import pandas as pd

# Cargar el logo de Intelvet


st.title("Intelvet - Análisis de Sensibilidad de Flujo de Fondos")

# Lista de cursos predefinidos (con posibilidad de actualización)
cursos_predefinidos = {
    "Diagnóstico a Campo (Bovinos)": {"especie": "Bovinos", "clases": 10, "precio_usd": 230},
    "Odontología (Pequeños)": {"especie": "Pequeños", "clases": 4, "precio_usd": 60},
    "Técnicas Quirúrgicas (Pequeños)": {"especie": "Pequeños", "clases": 9, "precio_usd": 110},
    "Casos Clínicos de Dermatología (Pequeños)": {"especie": "Pequeños", "clases": 8, "precio_usd": 70},
    "Oftalmología (Pequeños)": {"especie": "Pequeños", "clases": 8, "precio_usd": 100},
    "Anestesia (Pequeños)": {"especie": "Pequeños", "clases": 9, "precio_usd": 110},
    "Ecografía Abdominal - Nivel Inicial (Pequeños)": {"especie": "Pequeños", "clases": 19, "precio_usd": 400},
    "Ecografía Abdominal - Nivel Intermedio (Pequeños)": {"especie": "Pequeños", "clases": 4, "precio_usd": 60},
}

# Permitir agregar cursos nuevos junto con el costo
st.sidebar.header("Agregar un Curso Nuevo")
nuevo_curso = st.sidebar.text_input("Nombre del Nuevo Curso")
if nuevo_curso:
    especie = st.sidebar.selectbox("Especie", ["Bovinos", "Pequeños"])
    cantidad_clases = st.sidebar.number_input("Cantidad de Clases", min_value=1, max_value=50)
    precio_usd = st.sidebar.number_input("Precio del Curso en USD", min_value=10, max_value=10000)
    
    if st.sidebar.button("Agregar Curso"):
        cursos_predefinidos[nuevo_curso] = {
            "especie": especie,
            "clases": cantidad_clases,
            "precio_usd": precio_usd
        }
        st.sidebar.success(f"Curso '{nuevo_curso}' agregado con éxito.")

# Mostrar y editar los costos de cursos existentes
st.sidebar.header("Editar Costos de Cursos Existentes")
for curso, info in cursos_predefinidos.items():
    nuevo_precio = st.sidebar.number_input(f"Modificar Precio de {curso} (USD)", value=info["precio_usd"], min_value=10, max_value=10000)
    cursos_predefinidos[curso]["precio_usd"] = nuevo_precio

# Selección de cursos por mes con posibilidad de múltiples cursos
st.header("Ingresos por Mes")
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
cursos_por_mes = {}
inscriptos_por_curso = {}

for mes in meses:
    st.subheader(f"Cursos en {mes}")
    selected_courses = st.multiselect(f"Seleccionar cursos para {mes}", list(cursos_predefinidos.keys()), key=f"multiselect_{mes}")
    if selected_courses:
        cursos_por_mes[mes] = selected_courses
        for curso in selected_courses:
            inscriptos_por_curso[curso] = st.number_input(f"Inscriptos para {curso} en {mes}", min_value=0, max_value=100, key=f"inscriptos_{mes}_{curso}")

# Inicializar total de ingresos en USD
total_ingresos_usd = 0

# Listas para almacenar los datos de cada mes
ingresos_por_mes = []
costos_variables_por_mes = []
costos_fijos_por_mes = []

# Detalles de costos fijos y variables
st.header("Costos Fijos")
publicidad = st.slider("Publicidad ($)", 0, 500, 200)
impuestos = st.slider("Impuestos ($)", 0, 200, 100)
honorarios = st.slider("Honorarios ($)", 0, 500, 200)
plataforma = st.slider("Plataforma ($)", 0, 500, 200)
otros_gastos = st.slider("Otros Gastos ($)", 0, 500, 200)
zoom = st.slider("Zoom ($)", 0, 50, 15)

st.header("Costos Variables")
costo_hora_curso = st.slider("Costo por Hora de Curso ($)", 50, 200, 100)
horas_primer_mes = st.slider("Horas Primer Mes", 1, 10, 4)
horas_segundo_mes = st.slider("Horas Segundo Mes", 1, 10, 4)
costo_por_referente = st.slider("Costo por Curso al Referente ($)", 100, 300, 200)
costo_por_zapata = st.slider("Costo por Curso a Zapata ($)", 100, 300, 200)

# Iterar sobre cada mes y calcular ingresos y costos
for mes in meses:
    ingresos_mes = 0
    costos_variables_mes = 0
    costos_fijos_mes = publicidad + impuestos + honorarios + plataforma + otros_gastos + zoom  # Costos fijos

    if mes in cursos_por_mes:
        cursos = cursos_por_mes[mes]
        for curso in cursos:
            info_curso = cursos_predefinidos[curso]
            inscriptos = inscriptos_por_curso.get(curso, 0)
            ingresos_mes += info_curso["precio_usd"] * inscriptos
            horas_curso = info_curso['clases']
            costos_variables_mes += (horas_curso * costo_hora_curso) + costo_por_referente + costo_por_zapata

    # Si no hay cursos para un mes, ingresos y costos variables se quedan en 0
    ingresos_por_mes.append(ingresos_mes)
    costos_variables_por_mes.append(costos_variables_mes)
    costos_fijos_por_mes.append(costos_fijos_mes)

# Crear DataFrame con los resultados por mes
df_flujo_fondos = pd.DataFrame({
    "Mes": meses,
    "Ingresos ($)": ingresos_por_mes,
    "Costos Variables ($)": costos_variables_por_mes,
    "Costos Fijos ($)": costos_fijos_por_mes
})

# Calcular el resultado mensual y acumulado
df_flujo_fondos["Resultado Mensual ($)"] = df_flujo_fondos["Ingresos ($)"] - (df_flujo_fondos["Costos Variables ($)"] + df_flujo_fondos["Costos Fijos ($)"])
df_flujo_fondos["Resultado Acumulado ($)"] = df_flujo_fondos["Resultado Mensual ($)"].cumsum()

# Mostrar tabla de resultados
st.dataframe(df_flujo_fondos)

# Mostrar gráficos
st.line_chart(df_flujo_fondos.set_index("Mes")[["Ingresos ($)", "Costos Variables ($)", "Costos Fijos ($)"]])
st.line_chart(df_flujo_fondos.set_index("Mes")[["Resultado Mensual ($)", "Resultado Acumulado ($)"]])

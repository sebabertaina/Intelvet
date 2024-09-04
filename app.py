import streamlit as st
import pandas as pd

st.title("Intelvet - Análisis de Sensibilidad de Flujo de Fondos")

# Variables de ingreso por curso en una sola línea
st.header("Ingresos por Curso")
cursos = {}
for mes in ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]:
    col1, col2, col3 = st.columns(3)
    with col1:
        cantidad = st.number_input(f"Cursos en {mes}", min_value=0, max_value=10, value=1, key=f"cantidad_{mes}")
    with col2:
        matriculados = st.number_input(f"Matriculados en {mes}", min_value=0, max_value=100, value=65, key=f"matriculados_{mes}")
    with col3:
        monto = st.number_input(f"Monto de Matrícula en {mes} ($)", min_value=0, max_value=1000, value=55, key=f"monto_{mes}")
    cursos[mes] = {
        "cantidad": cantidad,
        "matriculados": matriculados,
        "monto": monto
    }

# Variables de costos variables por curso con cálculo automático
st.header("Costos Variables")
costo_hora_curso = st.slider("Costo por Hora de Curso ($)", 50, 200, 100)
horas_primer_mes = st.slider("Horas Primer Mes", 1, 10, 4)
horas_segundo_mes = st.slider("Horas Segundo Mes", 1, 10, 4)
costo_por_referente = st.slider("Costo por Curso al Referente ($)", 100, 300, 200)
costo_por_zapata = st.slider("Costo por Curso a Zapata ($)", 100, 300, 200)

# Costos Fijos
st.header("Costos Fijos")
costos_fijos = {
    "publicidad": st.slider("Publicidad ($)", 0, 500, 200),
    "impuestos": st.slider("Impuestos ($)", 0, 200, 100),
    "honorarios": st.slider("Honorarios ($)", 0, 500, 200),
    "plataforma": st.slider("Plataforma ($)", 0, 500, 200),
    "otros_gastos": st.slider("Otros Gastos ($)", 0, 500, 200),
    "zoom": st.slider("Zoom ($)", 0, 50, 15)
}

# Calcular ingresos y costos mes a mes
meses = list(cursos.keys())
ingresos = []
costos_variables_totales = []
costos_fijos_totales = [sum(costos_fijos.values())] * 12

for i, mes in enumerate(meses):
    ingreso_mensual = cursos[mes]["cantidad"] * cursos[mes]["monto"] * cursos[mes]["matriculados"]
    ingresos.append(ingreso_mensual)
    
    if i == 0:
        costo_variable_mensual = (cursos[mes]["cantidad"] * (horas_primer_mes * costo_hora_curso)) + \
                                 (cursos[mes]["cantidad"] * (costo_por_referente + costo_por_zapata))
    elif i == 1:
        costo_variable_mensual = (cursos[mes]["cantidad"] * (horas_segundo_mes * costo_hora_curso)) + \
                                 (cursos[mes]["cantidad"] * (costo_por_referente + costo_por_zapata))
    else:
        costo_variable_mensual = cursos[mes]["cantidad"] * (costo_por_referente + costo_por_zapata)
    
    costos_variables_totales.append(costo_variable_mensual)

# Calcular resultados
resultados_mensuales = []
resultados_acumulados = []
resultado_acumulado = 0

for i in range(12):
    resultado_mensual = ingresos[i] - (costos_variables_totales[i] + costos_fijos_totales[i])
    resultados_mensuales.append(resultado_mensual)
    resultado_acumulado += resultado_mensual
    resultados_acumulados.append(resultado_acumulado)

# Crear DataFrame
data = {
    "Mes": meses,
    "Ingresos ($)": ingresos,
    "Costos Variables ($)": costos_variables_totales,
    "Costos Fijos ($)": costos_fijos_totales,
    "Resultado Mensual ($)": resultados_mensuales,
    "Resultado Acumulado ($)": resultados_acumulados
}

# Crear un índice categórico para mantener el orden correcto de los meses
meses_ordenados = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
df_flujo_fondos = pd.DataFrame(data)
df_flujo_fondos['Mes'] = pd.Categorical(df_flujo_fondos['Mes'], categories=meses_ordenados, ordered=True)
df_flujo_fondos = df_flujo_fondos.sort_values('Mes')  # Asegurar que el DataFrame esté ordenado correctamente

# Mostrar tabla
st.dataframe(df_flujo_fondos)

# Mostrar gráficos
st.line_chart(df_flujo_fondos.set_index("Mes")[["Ingresos ($)", "Costos Variables ($)", "Costos Fijos ($)"]])
st.line_chart(df_flujo_fondos.set_index("Mes")[["Resultado Mensual ($)", "Resultado Acumulado ($)"]])

import streamlit as st
from datetime import datetime
import pandas as pd


# Cargar los cursos predefinidos (como variable)
if "cursos_data" not in st.session_state:
    st.session_state.cursos_data = {
        "Nombre del Curso": [
            "Diagnóstico a Campo", "Odontología", "Técnicas quirurgicas",
            "Casos clínicos de dermatología", "Oftalmología", "Introducción a la Anestesia",
            "Ecografía Abdominal - Intermedio", "Ecografía Abdominal - Inicial"
        ],
        "Precio del Curso": [245, 75, 150, 79, 150, 150, 300, 300],
        "Duración del Curso (Semanas)": [9.5, 4, 4.5, 8, 9, 9, 16, 20],
        "Clases por Semana": [2, 1, 2, 1, 1, 1, 1, 1],
        "Tipo de Animales": ["Grandes - Bovinos", "Pequeños", "Pequeños", "Pequeños", "Pequeños", 
                             "Pequeños", "Pequeños", "Pequeños"]
    }

# Convertir a DataFrame para manejo en la aplicación
df_cursos = pd.DataFrame(st.session_state.cursos_data)

# Definir clases para los cursos y costos fijos
class Curso:
    def __init__(self, nombre, precio, duracion_semanas, clases_por_semana, inscripciones=0):
        self.nombre = nombre
        self.precio = precio
        self.duracion_semanas = duracion_semanas
        self.clases_por_semana = clases_por_semana
        self.inscripciones = inscripciones
        self.coordinador_costo = 200
        self.gustavo_zapata_costo = 200
        self.profesores_costo_por_clase = 100
    
    def clases_por_mes(self):
        clases_totales = self.duracion_semanas * self.clases_por_semana
        clases_por_mes = []
        semanas_restantes = self.duracion_semanas
        while semanas_restantes > 0:
            semanas_mes_actual = min(4, semanas_restantes)
            clases_mes_actual = semanas_mes_actual * self.clases_por_semana
            clases_por_mes.append(clases_mes_actual)
            semanas_restantes -= 4
        return clases_por_mes
    
    def calcular_costos_profesores_por_mes(self):
        clases_por_mes = self.clases_por_mes()
        costos_por_mes = [clases * self.profesores_costo_por_clase for clases in clases_por_mes]
        return costos_por_mes
    
    def calcular_costos_inicio(self):
        return self.coordinador_costo + self.gustavo_zapata_costo
    
    def calcular_ingresos(self):
        return self.inscripciones * self.precio


class CostosFijos:
    def __init__(self, publicidad=0, impuestos=0, plataforma=0, zoom=0, honorarios=0):
        self.publicidad = publicidad
        self.impuestos = impuestos
        self.plataforma = plataforma
        self.zoom = zoom
        self.honorarios = honorarios
    
    def total_mensual(self):
        return self.publicidad + self.impuestos + self.plataforma + self.zoom + self.honorarios


class FlujoDeCaja:
    def __init__(self, cursos_por_mes, costos_fijos):
        self.cursos_por_mes = cursos_por_mes
        self.costos_fijos = costos_fijos
    
    def calcular_flujo_mensual(self):
        flujo_mensual = {f'{i:02d}': {"ingresos": 0, "costos_inicio": 0, "costos_profesores": 0, "costos_fijos": 0, "neto": 0} for i in range(1, 13)}
        
        # Calcular ingresos y costos por curso
        for mes, cursos in self.cursos_por_mes.items():
            for curso, inscripciones in cursos.items():
                curso.inscripciones = inscripciones
                ingresos = curso.calcular_ingresos()
                costos_profesores_por_mes = curso.calcular_costos_profesores_por_mes()
                costos_inicio = curso.calcular_costos_inicio()
                
                # Calcular el mes de inicio
                mes_inicio = int(mes) - 1
                flujo_mensual[f'{mes_inicio + 1:02d}']["ingresos"] += ingresos
                flujo_mensual[f'{mes_inicio + 1:02d}']["costos_inicio"] += costos_inicio
                
                # Distribuir los costos de profesores mes a mes
                for i, costo in enumerate(costos_profesores_por_mes):
                    mes_distribucion = (mes_inicio + i) % 12 + 1
                    flujo_mensual[f'{mes_distribucion:02d}']["costos_profesores"] += costo

        # Agregar costos fijos mensuales
        for mes in flujo_mensual:
            flujo_mensual[mes]["costos_fijos"] = self.costos_fijos.total_mensual()
            flujo_mensual[mes]["neto"] = (
                flujo_mensual[mes]["ingresos"] 
                - flujo_mensual[mes]["costos_inicio"] 
                - flujo_mensual[mes]["costos_profesores"] 
                - flujo_mensual[mes]["costos_fijos"]
            )
        
        return flujo_mensual

# Iniciar Streamlit
st.title("Gestión de Cursos Online y Flujo de Caja")

# Sección para editar o eliminar cursos predefinidos
st.sidebar.header("Editar Cursos Predefinidos")
curso_seleccionado = st.sidebar.selectbox("Seleccionar curso para editar", df_cursos["Nombre del Curso"])

# Mostrar los detalles del curso seleccionado
curso_data = df_cursos[df_cursos["Nombre del Curso"] == curso_seleccionado].iloc[0]
nuevo_nombre = st.sidebar.text_input("Nombre del curso", value=curso_data["Nombre del Curso"], key="nombre_curso")
nuevo_precio = st.sidebar.number_input("Precio del curso", min_value=0, value=int(curso_data["Precio del Curso"]), key="precio_curso")
nueva_duracion = st.sidebar.number_input("Duración (semanas)", min_value=1, value=int(curso_data["Duración del Curso (Semanas)"]), key="duracion_curso")
nuevas_clases_por_semana = st.sidebar.number_input("Clases por semana", min_value=1, value=int(curso_data["Clases por Semana"]), key="clases_curso")
nuevo_tipo_animales = st.sidebar.selectbox("Tipo de Animales", ["Pequeños", "Grandes - Bovinos"], index=["Pequeños", "Grandes - Bovinos"].index(curso_data["Tipo de Animales"]), key="tipo_animales")

# Guardar cambios en el curso
if st.sidebar.button("Guardar cambios", key="guardar_cambios"):
    index = df_cursos[df_cursos["Nombre del Curso"] == curso_seleccionado].index[0]
    st.session_state.cursos_data["Nombre del Curso"][index] = nuevo_nombre
    st.session_state.cursos_data["Precio del Curso"][index] = nuevo_precio
    st.session_state.cursos_data["Duración del Curso (Semanas)"][index] = nueva_duracion
    st.session_state.cursos_data["Clases por Semana"][index] = nuevas_clases_por_semana
    st.session_state.cursos_data["Tipo de Animales"][index] = nuevo_tipo_animales
    st.success(f"Curso '{nuevo_nombre}' actualizado correctamente!")

# Eliminar curso
if st.sidebar.button("Eliminar curso", key="eliminar_curso"):
    index = df_cursos[df_cursos["Nombre del Curso"] == curso_seleccionado].index[0]
    for key in st.session_state.cursos_data:
        st.session_state.cursos_data[key].pop(index)
    st.success(f"Curso '{curso_seleccionado}' eliminado correctamente!")

# Permitir agregar nuevos cursos
st.sidebar.header("Agregar Nuevo Curso")
nombre_nuevo_curso = st.sidebar.text_input("Nombre del nuevo curso", key="nombre_nuevo_curso")
precio_nuevo_curso = st.sidebar.number_input("Precio del nuevo curso", min_value=0, value=100, key="precio_nuevo_curso")
duracion_nuevo_curso = st.sidebar.number_input("Duración (semanas)", min_value=1, value=4, key="duracion_nuevo_curso")
clases_por_semana_nuevo_curso = st.sidebar.number_input("Clases por semana", min_value=1, value=1, key="clases_nuevo_curso")
tipo_animales_nuevo_curso = st.sidebar.selectbox("Tipo de Animales", ["Pequeños", "Grandes - Bovinos"], key="tipo_animales_nuevo_curso")

# Botón para agregar curso
if st.sidebar.button("Agregar Curso", key="agregar_curso"):
    st.session_state.cursos_data["Nombre del Curso"].append(nombre_nuevo_curso)
    st.session_state.cursos_data["Precio del Curso"].append(precio_nuevo_curso)
    st.session_state.cursos_data["Duración del Curso (Semanas)"].append(duracion_nuevo_curso)
    st.session_state.cursos_data["Clases por Semana"].append(clases_por_semana_nuevo_curso)
    st.session_state.cursos_data["Tipo de Animales"].append(tipo_animales_nuevo_curso)
    st.sidebar.success(f"Curso '{nombre_nuevo_curso}' agregado con éxito!")
    df_cursos = pd.DataFrame(st.session_state.cursos_data)

# Entrada de datos para costos fijos
st.sidebar.header("Ingresar costos fijos")
publicidad = st.sidebar.number_input("Publicidad mensual", min_value=0.0, value=200.0, key="publicidad")
impuestos = st.sidebar.number_input("Impuestos mensuales", min_value=0.0, value=150.0, key="impuestos")
plataforma = st.sidebar.number_input("Costo de la plataforma mensual", min_value=0.0, value=100.0, key="plataforma")
zoom = st.sidebar.number_input("Costo de Zoom mensual", min_value=0.0, value=50.0, key="zoom")
honorarios = st.sidebar.number_input("Honorarios mensuales", min_value=0.0, value=300.0, key="honorarios")

# Crear instancia de costos fijos
costos_fijos = CostosFijos(
    publicidad=publicidad,
    impuestos=impuestos,
    plataforma=plataforma,
    zoom=zoom,
    honorarios=honorarios
)

# Mostrar los cursos en el panel central para asignar meses de inicio
st.header("Asignar Meses de Inicio y Inscripciones")

meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
cursos_por_mes = {f'{i:02d}': {} for i in range(1, 13)}

for i, mes in enumerate(meses):
    st.subheader(f"Cursos que inician en {mes}")
    cursos_seleccionados = st.multiselect(f"Seleccionar cursos que inician en {mes}", df_cursos["Nombre del Curso"], key=f"cursos_{mes}")
    
    for curso_seleccionado in cursos_seleccionados:
        inscripciones = st.number_input(f"Ingresiones para {curso_seleccionado} en {mes}", min_value=0, value=10, key=f"inscripciones_{curso_seleccionado}_{mes}")
        
        curso_data = df_cursos[df_cursos["Nombre del Curso"] == curso_seleccionado].iloc[0]
        curso = Curso(
            nombre=curso_data["Nombre del Curso"],
            precio=curso_data["Precio del Curso"],
            duracion_semanas=curso_data["Duración del Curso (Semanas)"],
            clases_por_semana=curso_data["Clases por Semana"]
        )
        
        mes_numero = i + 1
        cursos_por_mes[f'{mes_numero:02d}'][curso] = inscripciones

# Calcular el flujo de caja
flujo_caja = FlujoDeCaja(cursos_por_mes, costos_fijos)
resultados_flujo = flujo_caja.calcular_flujo_mensual()

# Convertir los resultados a un DataFrame para visualizar en una tabla
datos_flujo = {
    "Mes": [],
    "Ingresos": [],
    "Costos Variables": [],
    "Costos Fijos": [],
    "Resultado Mensual": [],
    "Resultado Acumulado": []
}

resultado_acumulado = 0
for mes, datos in resultados_flujo.items():
    resultado_acumulado += datos["neto"]
    datos_flujo["Mes"].append(mes)
    datos_flujo["Ingresos"].append(datos["ingresos"])
    datos_flujo["Costos Variables"].append(datos["costos_profesores"] + datos["costos_inicio"])
    datos_flujo["Costos Fijos"].append(datos["costos_fijos"])
    datos_flujo["Resultado Mensual"].append(datos["neto"])
    datos_flujo["Resultado Acumulado"].append(resultado_acumulado)

df_flujo = pd.DataFrame(datos_flujo)

# Mostrar la tabla
st.header("Tabla de Flujo de Caja")
st.dataframe(df_flujo)





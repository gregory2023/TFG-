import streamlit as st
import requests
import pandas as pd
import time

API_URL = "http://13.61.34.115:8000"

st.set_page_config(page_title="YOUFACE — Panel de Control", page_icon="👁", layout="wide")

st.markdown("""
<style>
    .metric-card { background: #1F3864; border-radius: 10px; padding: 20px; color: white; text-align: center; }
    .metric-value { font-size: 48px; font-weight: bold; color: #4FC3F7; }
    .metric-label { font-size: 14px; color: #ccc; margin-top: 5px; }
    .alumno-presente { background: #1B5E20; border-radius: 8px; padding: 8px 14px; color: #A5D6A7; margin: 4px 0; font-size: 14px; }
    .alumno-registrado { background: #1A237E; border-radius: 8px; padding: 8px 14px; color: #90CAF9; margin: 4px 0; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

st.title("YOUFACE — Panel de Control del Examen")
st.caption(f"Ultima actualizacion: {time.strftime('%H:%M:%S')}")

def cargar_alertas():
    try:
        r = requests.get(f"{API_URL}/alertas", timeout=5)
        return r.json()
    except:
        return []

def cargar_alumnos():
    try:
        r = requests.get(f"{API_URL}/alumnos", timeout=5)
        return r.json()
    except:
        return []

alertas = cargar_alertas()
alumnos = cargar_alumnos()

# ── Metricas principales ───────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

df_alertas = pd.DataFrame(alertas) if alertas else pd.DataFrame()

total_alertas = len(df_alertas)
total_alumnos = len(alumnos)

if not df_alertas.empty:
    df_alertas['timestamp'] = pd.to_datetime(df_alertas['timestamp'])
    infracciones = len(df_alertas[df_alertas['alert_type'].str.contains('infraccion', na=False)])
    accesos = df_alertas[df_alertas['alert_type'] == 'acceso_examen']['user_id'].nunique()
else:
    infracciones = 0
    accesos = 0

col1.metric("Total Alertas", total_alertas)
col2.metric("Alumnos Registrados", total_alumnos)
col3.metric("Alumnos Presentes", accesos)
col4.metric("Infracciones", infracciones)

st.divider()

# ── Alumnos registrados y presentes ───────────────────────────
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Alumnos Registrados")
    if alumnos:
        for a in alumnos:
            st.markdown(f'<div class="alumno-registrado">👤 {a["nombre"]} — DNI: {a["dni"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No hay alumnos registrados.")

with col_der:
    st.subheader("Alumnos Detectados en Examen")
    if not df_alertas.empty:
        presentes = df_alertas[df_alertas['alert_type'] == 'acceso_examen']['user_id'].unique()
        if len(presentes) > 0:
            for nombre in presentes:
                ultimo = df_alertas[
                    (df_alertas['user_id'] == nombre) &
                    (df_alertas['alert_type'] == 'acceso_examen')
                ]['timestamp'].max()
                st.markdown(f'<div class="alumno-presente">✅ {nombre} — Ultimo acceso: {ultimo.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
        else:
            st.info("Ningun alumno detectado aun.")
    else:
        st.info("Ningun alumno detectado aun.")

st.divider()

# ── Registro de alertas ────────────────────────────────────────
st.subheader("Registro de Alertas")
if not df_alertas.empty:
    df_mostrar = df_alertas[['timestamp', 'user_id', 'alert_type']].sort_values('timestamp', ascending=False).copy()
    df_mostrar.columns = ['Fecha y Hora', 'Alumno', 'Tipo de Alerta']
    st.dataframe(df_mostrar, use_container_width=True)
else:
    st.info("No hay alertas registradas aun.")

st.divider()

# ── Grafica ────────────────────────────────────────────────────
if not df_alertas.empty:
    st.subheader("Distribucion de Alertas por Tipo")
    st.bar_chart(df_alertas['alert_type'].value_counts())

# ── Infracciones detalle ───────────────────────────────────────
if not df_alertas.empty and infracciones > 0:
    st.subheader("Detalle de Infracciones")
    df_inf = df_alertas[df_alertas['alert_type'].str.contains('infraccion', na=False)][['timestamp', 'user_id', 'alert_type']].sort_values('timestamp', ascending=False)
    df_inf.columns = ['Fecha y Hora', 'Alumno', 'Tipo']
    st.dataframe(df_inf, use_container_width=True)

# Refresco automatico cada 10 segundos
time.sleep(10)
st.rerun()

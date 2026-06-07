
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Arca Continental - Churn Hunters", layout="wide")
st.title("🎯 Panel de Control Preventivo: Churn Hunters")
st.markdown("### Datos reales del modelo de Machine Learning aplicados al canal tradicional")
st.markdown("---")

# Cargamos directo sin funciones ni decoradores de caché para que no guarde memoria vieja
df = pd.read_csv("base_dashboard_final.csv")

# Buscamos la columna de tu compañera: si está 'target' la usa, si no, agarra la primera columna numérica
col_prob = 'target' if 'target' in df.columns else df.select_dtypes(include=['number']).columns[0]
df[col_prob] = pd.to_numeric(df[col_prob], errors='coerce').fillna(0.0)

# Tus cortes exactos
def clasificar_riesgo_porc(p):
    if p > 0.7: return 'Alto 🔴'
    elif p >= 0.4: return 'Medio 🟡'
    else: return 'Bajo 🟢'
        
df['Nivel de Riesgo'] = df[col_prob].apply(clasificar_riesgo_porc)
df['Probabilidad Churn'] = df[col_prob]

# --- INTERFAZ ---
st.sidebar.header("🎯 Filtros de Acción Comercial")
filtro_riesgo = st.sidebar.multiselect("Filtrar por Semáforo de Riesgo:", options=['Alto 🔴', 'Medio 🟡', 'Bajo 🟢'], default=['Alto 🔴', 'Medio 🟡', 'Bajo 🟢'])

df_filtrado = df[df['Nivel de Riesgo'].isin(filtro_riesgo)]

if 'territory_d' in df.columns:
    lista_territorios = ["Todos"] + list(df['territory_d'].dropna().unique())
    territorio_seleccionado = st.sidebar.selectbox("Filtrar por Región (Territorio):", lista_territorios)
    if territorio_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['territory_d'] == territorio_seleccionado]

# KPIs
col1, col2, col3 = st.columns(3)
df_alto_riesgo = df_filtrado[df_filtrado['Nivel de Riesgo'] == 'Alto 🔴']

with col1:
    st.metric(label="Clientes en Alerta Máxima", value=f"{df_alto_riesgo['customer_id'].nunique() if 'customer_id' in df_filtrado.columns else len(df_alto_riesgo):,}")
with col2:
    volumen = df_alto_riesgo['uni_boxes_sold_m'].sum() if 'uni_boxes_sold_m' in df_filtrado.columns else 0
    st.metric(label="Volumen de Cajas en Riesgo", value=f"{volumen:,.0f} u.")
with col3:
    st.metric(label="Total Clientes Filtrados", value=f"{df_filtrado['customer_id'].nunique() if 'customer_id' in df_filtrado.columns else len(df_filtrado):,}")

st.markdown("---")
col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown("### 🏢 Riesgo por Subcanal Comercial")
    if 'comercial_subchannel_d' in df_filtrado.columns:
        fig_canal = px.histogram(df_filtrado, x='comercial_subchannel_d', color='Nivel de Riesgo', color_discrete_map={'Alto 🔴': '#FF4B4B', 'Medio 🟡': '#FFD14B', 'Bajo 🟢': '#00CC96'}, barmode='stack').update_xaxes(categoryorder="total descending")
        st.plotly_chart(fig_canal, use_container_width=True)

with col_der:
    st.markdown("### 🧊 Impacto de Infraestructura")
    col_x = 'num_coolers' if 'num_coolers' in df_filtrado.columns else df_filtrado.columns[2]
    fig_coolers = px.histogram(df_filtrado, x=col_x, color='Nivel de Riesgo', color_discrete_map={'Alto 🔴': '#FF4B4B', 'Medio 🟡': '#FFD14B', 'Bajo 🟢': '#00CC96'}, barmode='group')
    st.plotly_chart(fig_coolers, use_container_width=True)

st.markdown("---")
st.subheader("📋 Matriz de Priorización de Visitas Comerciales")
columnas_vista = [c for c in ['customer_id', 'territory_d', 'comercial_subchannel_d', 'Nivel de Riesgo', 'Probabilidad Churn'] if c in df_filtrado.columns]
st.dataframe(df_filtrado[columnas_vista].sort_values(by='Probabilidad Churn', ascending=False), use_container_width=True, height=350)
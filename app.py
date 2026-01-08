import streamlit as st
import pandas as pd
import plotly_express as px

st.set_page_config(
    page_title="Gold and Silver vs Geopolitical Risk",
    page_icon=":dollar:",
    menu_items={
        'Get Help':'https://www.youtube.com/watch?v=xvFZjo5PgG0',
        'Report a bug':'https://www.youtube.com/watch?v=5B3JGUXSRJo',
        'About':'# Proyecto estudiantil'
    }
)



@st.cache_data
def load_data(path:str):
#NORMALIZAR DATOS COMO EN EL EDA: 
 df=pd.read_csv(path)
 df.columns=df.columns.str.lower()
 df['date']=df['date'].astype('datetime64[ns]')
 df=df.sort_values(by='date',ascending=True).reset_index(drop=True)

 #DATOS NUMERICOS:
 for col in ["gold_price", "silver_price",
                "gold_change_%", "silver_change_%",
                "gprd", "gprd_act", "gprd_threat"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
 
 #COLUMNAS SINTETICAS:
 df["gold_ret"] = df["gold_change_%"] / 100
 df["silver_ret"] = df["silver_change_%"] / 100
 df["gold_silver_ratio"] = df["gold_price"] / df["silver_price"]

 df["gprd_pct_change"] = df["gprd"].pct_change(fill_method=None) * 100
 df["gprd_act_pct_change"] = df["gprd_act"].pct_change(fill_method=None) * 100
 df["gprd_threat_pct_change"] = df["gprd_threat"].pct_change(fill_method=None) * 100

 return df

DATA_PATH = "Gold-Silver-GeopoliticalRisk_HistoricalData.csv"
df = load_data(DATA_PATH)

st.title("Gold & Silver vs Geopolitical Risk")

# ----- SLIDER DE AÑOS -----
min_year = int(df["date"].dt.year.min())
max_year = int(df["date"].dt.year.max())

end_year = st.slider(
    "Mostrar datos hasta el año:",
    min_value=min_year,
    max_value=max_year,
    value=max_year,      # valor inicial (todo el rango)
    step=1,
)

# Filtrar datos hasta ese año (acumulado)
df_year = df[df["date"].dt.year <= end_year]

st.write(f"Mostrando datos desde {min_year} hasta {end_year} (filas: {len(df_year)})")


# --------- Título ----------
st.title("Análisis de Oro, Plata y Riesgo Geopolítico")

st.markdown(
    "EDA interactivo del dataset de precios de oro/plata y el índice de riesgo geopolítico "
    "para explorar relaciones en el tiempo."
)

st.write("### Vista rápida de los datos filtrados")
st.dataframe(df_year.head())

# --------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Precios", "Riesgo vs Metales", "Distribución de retornos"])

# ===== TAB 1: PRECIOS =====
with tab1:
    st.subheader("Precios de oro y plata a lo largo del tiempo")

    df_prices = df_year.melt(
        id_vars="date",
        value_vars=["gold_price", "silver_price"],
        var_name="metal",
        value_name="price"
    )

    fig = px.line(
        df_prices,
        x="date",
        y="price",
        color="metal",
        title="Precios de oro y plata"
    )
    st.plotly_chart(fig, use_container_width=True)

# ===== TAB 2: RIESGO vs METALES =====
with tab2:
    st.subheader("Índices de riesgo geopolítico")

    risk_cols = [c for c in ["gprd", "gprd_act", "gprd_threat"] if c in df_year.columns]

    df_risk = df_year.melt(
        id_vars="date",
        value_vars=risk_cols,
        var_name="index",
        value_name="value"
    )

    fig_risk = px.line(
        df_risk,
        x="date",
        y="value",
        color="index",
        title="Evolución del riesgo geopolítico"
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    st.subheader("Cambios % en riesgo vs cambios % en metales")

    col1, col2 = st.columns(2)

    with col1:
        fig_sc_gold = px.scatter(
            df_year,
            x="gprd_pct_change",
            y="gold_change_%",
            title="Cambio % GPRD vs cambio % oro",
            labels={
                "gprd_pct_change": "Cambio % diario GPRD",
                "gold_change_%": "Cambio % diario oro"
            }
        )
        st.plotly_chart(fig_sc_gold, use_container_width=True)

    with col2:
        fig_sc_silver = px.scatter(
            df_year,
            x="gprd_pct_change",
            y="silver_change_%",
            title="Cambio % GPRD vs cambio % plata",
            labels={
                "gprd_pct_change": "Cambio % diario GPRD",
                "silver_change_%": "Cambio % diario plata"
            }
        )
        st.plotly_chart(fig_sc_silver, use_container_width=True)

# ===== TAB 3: DISTRIBUCIÓN =====
with tab3:
    st.subheader("Distribución de cambios porcentuales diarios")

    df_ret = df_year.melt(
        id_vars="date",
        value_vars=["gold_change_%", "silver_change_%"],
        var_name="metal",
        value_name="return_%"
    )

    fig_box = px.box(
        df_ret,
        x="metal",
        y="return_%",
        title="Distribución de cambios % diarios en oro y plata",
        points="all"  # muestra outliers
    )
    st.plotly_chart(fig_box, use_container_width=True)

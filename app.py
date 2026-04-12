# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import urllib.parse

from pricing_engine import (
    formato_pesos,
    calcular_precio_venta,
    obtener_reglas_iniciales
)

from proveedor_loader import obtener_productos_proveedor

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Valentín Pet Food",
    page_icon="🐾",
    layout="wide"
)

zona = pytz.timezone("America/Argentina/Buenos_Aires")

# =========================
# SESSION STATE
# =========================
if "productos_cacheados" not in st.session_state:
    st.session_state["productos_cacheados"] = []

if "precios_anteriores" not in st.session_state:
    st.session_state["precios_anteriores"] = {}

if "productos_mostrados" not in st.session_state:
    st.session_state["productos_mostrados"] = []

if "historial_aumentos" not in st.session_state:
    st.session_state["historial_aumentos"] = []

if "ver_historial" not in st.session_state:
    st.session_state["ver_historial"] = False

if "reglas" not in st.session_state:
    st.session_state["reglas"] = obtener_reglas_iniciales()

# =========================
# HEADER
# =========================
st.title("🐾 Valentín Pet Food")
st.caption("Sistema de precios automático")

# =========================
# BOTONES
# =========================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Actualizar"):

        # guardar precios anteriores
        precios_previos = {
            p["Producto"]: p["Venta"]
            for p in st.session_state["productos_cacheados"]
            if "Venta" in p
        }

        st.session_state["precios_anteriores"] = precios_previos

        # traer productos
        productos = obtener_productos_proveedor()

        productos_aumentados = []

        for p in productos:

            ganancia, venta = calcular_precio_venta(
                p["Costo"],
                p["Peso"],
                st.session_state["reglas"]
            )

            p["Ganancia"] = ganancia
            p["Venta"] = venta

            precio_anterior = precios_previos.get(p["Producto"])

            if precio_anterior and venta > precio_anterior:

                p["Aumento"] = True
                productos_aumentados.append(p)

                # 🔥 GUARDAR HISTORIAL
                porcentaje = ((venta - precio_anterior) / precio_anterior) * 100

                st.session_state["historial_aumentos"].append({
                    "fecha": datetime.now(zona).strftime("%d/%m/%Y %H:%M"),
                    "producto": p["Producto"],
                    "precio_anterior": precio_anterior,
                    "costo_anterior": p["Costo"],
                    "costo_actual": p["Costo"],
                    "porcentaje": round(porcentaje, 2)
                })

            else:
                p["Aumento"] = False

        # limpiar historial (5 días)
        historial_filtrado = []
        ahora = datetime.now(zona)

        for h in st.session_state["historial_aumentos"]:
            fecha_h = datetime.strptime(h["fecha"], "%d/%m/%Y %H:%M")
            fecha_h = zona.localize(fecha_h)

            if (ahora - fecha_h).days <= 5:
                historial_filtrado.append(h)

        st.session_state["historial_aumentos"] = historial_filtrado

        st.session_state["productos_cacheados"] = productos
        st.session_state["productos_mostrados"] = productos

        st.rerun()

with col3:
    if st.button("Historial de aumentos"):
        st.session_state["ver_historial"] = True
        st.rerun()

# =========================
# PANTALLA HISTORIAL
# =========================
if st.session_state["ver_historial"]:

    st.subheader("📊 Historial de aumentos (últimos 5 días)")

    historial = st.session_state["historial_aumentos"]

    if not historial:
        st.info("No hay aumentos registrados.")

    else:
        df_hist = pd.DataFrame(historial)

        df_hist = df_hist.sort_values("fecha")

        df_hist = df_hist.rename(columns={
            "fecha": "Fecha",
            "producto": "Producto",
            "precio_anterior": "Precio anterior",
            "costo_anterior": "Costo anterior",
            "costo_actual": "Costo actual",
            "porcentaje": "% Aumento"
        })

        st.dataframe(df_hist, use_container_width=True)

    if st.button("⬅️ Volver al catálogo"):
        st.session_state["ver_historial"] = False
        st.rerun()

    st.stop()

# =========================
# DATA
# =========================
df = pd.DataFrame(st.session_state["productos_mostrados"])

if not df.empty and busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False)]

# =========================
# MOSTRAR PRODUCTOS
# =========================
if df.empty:
    st.info("Presioná actualizar para cargar productos")

else:
    for _, row in df.iterrows():

        nombre = row["Producto"]

        if row.get("Aumento"):
            nombre += " 🔺"

        st.markdown(f"**{nombre}**")

        st.caption(f"Costo: {formato_pesos(row['Costo'])}")
        st.write(f"💰 Venta: {formato_pesos(row['Venta'])}")

        st.divider()

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

if "productos_aumentados" not in st.session_state:
    st.session_state["productos_aumentados"] = []

if "hubo_aumento" not in st.session_state:
    st.session_state["hubo_aumento"] = False

if "ultima_actualizacion" not in st.session_state:
    st.session_state["ultima_actualizacion"] = None

if "reglas" not in st.session_state:
    st.session_state["reglas"] = obtener_reglas_iniciales()

if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = []

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

# =========================
# FUNCIONES
# =========================
def agregar_al_carrito(producto, venta):
    for item in st.session_state["seleccionados"]:
        if item["Producto"] == producto:
            item["Cantidad"] += 1
            return

    st.session_state["seleccionados"].append({
        "Producto": producto,
        "Venta": int(venta),
        "Cantidad": 1
    })


def generar_mensaje_producto(producto, venta):
    mensaje = f"🐾 1 uni de {producto}\n💲 Precio: {formato_pesos(venta)}"
    return urllib.parse.quote(mensaje)

# =========================
# HEADER
# =========================
st.title("Valentín Pet Food")
st.caption("Sistema de precios")

# =========================
# BOTÓN ACTUALIZAR
# =========================
if st.button("🔄 Actualizar precios"):

    precios_previos = {
        p["Producto"]: p["Venta"]
        for p in st.session_state["productos_cacheados"]
        if "Producto" in p and "Venta" in p
    }

    nuevos_productos = obtener_productos_proveedor()
    productos_aumentados = []

    for p in nuevos_productos:
        ganancia, venta = calcular_precio_venta(
            p["Costo"],
            p["Peso"],
            st.session_state["reglas"]
        )

        p["Ganancia"] = ganancia
        p["Venta"] = venta

        anterior = precios_previos.get(p["Producto"])

        if anterior is not None and venta > anterior:
            p["Aumento"] = True
            productos_aumentados.append(p)
        else:
            p["Aumento"] = False

    st.session_state["productos_cacheados"] = nuevos_productos
    st.session_state["productos_aumentados"] = productos_aumentados
    st.session_state["hubo_aumento"] = len(productos_aumentados) > 0
    st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y %H:%M")

# =========================
# INFO
# =========================
if st.session_state["ultima_actualizacion"]:
    st.info(f"Última actualización: {st.session_state['ultima_actualizacion']}")

if st.session_state["hubo_aumento"]:
    st.warning("⚠️ Hubo aumentos en los precios")

# =========================
# DATA A MOSTRAR
# =========================
if st.session_state["productos_aumentados"]:
    df = pd.DataFrame(st.session_state["productos_aumentados"])
else:
    df = pd.DataFrame(st.session_state["productos_cacheados"])

# =========================
# LISTADO
# =========================
st.subheader("📦 Productos")

if df.empty:
    st.info("No hay productos para mostrar. Presioná actualizar.")
else:
    df = df.sort_values("Producto")

    for i, row in df.iterrows():

        if row.get("Aumento"):
            nombre = f"{row['Producto']} 🔺 AUMENTÓ"
        else:
            nombre = row["Producto"]

        st.markdown(f"**{nombre}**")
        st.caption(f"Costo: {formato_pesos(row['Costo'])} | Ganancia: {formato_pesos(row['Ganancia'])}")

        col1, col2 = st.columns(2)

        with col1:
            st.success(formato_pesos(row["Venta"]))

        with col2:
            if st.button("Agregar", key=f"add_{i}"):
                agregar_al_carrito(row["Producto"], row["Venta"])
                st.toast("Agregado")

        st.divider()

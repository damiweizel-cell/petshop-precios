import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

from pricing_engine import (
    formato_pesos,
    calcular_precio_venta,
    obtener_reglas_iniciales
)

from proveedor_loader import obtener_productos_proveedor

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Valentín Pet Food",
    page_icon="🐾",
    layout="wide"
)

# =========================
# ZONA HORARIA
# =========================
zona = pytz.timezone("America/Argentina/Buenos_Aires")

# =========================
# SESSION STATE
# =========================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = "carolinak"

if "password" not in st.session_state:
    st.session_state["password"] = "caro100"

if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if "productos_cacheados" not in st.session_state:
    st.session_state["productos_cacheados"] = []

if "ultima_actualizacion" not in st.session_state:
    st.session_state["ultima_actualizacion"] = None

if "reglas" not in st.session_state:
    st.session_state["reglas"] = obtener_reglas_iniciales()

if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = []

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

# =========================
# LOGIN
# =========================
def pantalla_login():
    st.markdown("## 🔐 Iniciar sesión")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario == st.session_state["usuario"] and password == st.session_state["password"]:
            st.session_state["logueado"] = True
            st.rerun()
        else:
            st.error("Datos incorrectos")

if not st.session_state["logueado"]:
    pantalla_login()
    st.stop()

# =========================
# CARGA DE PRODUCTOS
# =========================
if not st.session_state["productos_cacheados"]:
    productos = obtener_productos_proveedor()
    st.session_state["productos_cacheados"] = productos
    st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")

productos = st.session_state["productos_cacheados"]

# =========================
# CALCULAR PRECIOS
# =========================
for p in productos:
    ganancia, venta = calcular_precio_venta(
        p["Costo"],
        p["Peso"],
        st.session_state["reglas"]
    )
    p["Ganancia"] = ganancia
    p["Venta"] = venta

df = pd.DataFrame(productos)

# =========================
# HEADER
# =========================
st.title("🐾 Valentín Pet Food")
st.caption("Sistema de precios automático")

if st.session_state["ultima_actualizacion"]:
    st.info(f"Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# BUSCADOR + ACCIONES
# =========================
col1, col2, col3 = st.columns([2,1,1])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Actualizar"):
        st.cache_data.clear()
        st.session_state["productos_cacheados"] = []
        st.rerun()

with col3:
    if st.button(f"Carrito ({len(st.session_state['seleccionados'])})"):
        st.session_state["ver_carrito"] = True
        st.rerun()

# =========================
# FILTRO
# =========================
if busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False)]

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.header("🛒 Carrito")

    total = 0

    for item in st.session_state["seleccionados"]:
        st.write(item["Producto"], "-", formato_pesos(item["Venta"]))
        total += item["Venta"]

    st.success(f"TOTAL: {formato_pesos(total)}")

    if st.button("Volver"):
        st.session_state["ver_carrito"] = False
        st.rerun()

    st.stop()

# =========================
# CATÁLOGO
# =========================
st.header("📦 Productos")

for i, row in df.iterrows():

    col1, col2, col3, col4 = st.columns([4,1,1,1])

    with col1:
        st.write(row["Producto"])

    with col2:
        st.write(f"{row['Peso']} kg")

    with col3:
        st.write(formato_pesos(row["Costo"]))

    with col4:
        st.write(formato_pesos(row["Venta"]))

    if st.button("Agregar", key=i):
        st.session_state["seleccionados"].append({
            "Producto": row["Producto"],
            "Venta": row["Venta"]
        })
        st.toast("Agregado al carrito")

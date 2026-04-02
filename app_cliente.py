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

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0F172A 0%, #020617 100%);
    color: white;
}

.titulo {
    font-size: 40px;
    font-weight: 900;
}

.subtitulo {
    font-size: 18px;
    color: #cbd5e1;
}

.card {
    background: #111827;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 12px;
}

.precio {
    background: #22c55e;
    color: black;
    padding: 10px;
    border-radius: 12px;
    font-weight: 900;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION
# =========================
if "productos" not in st.session_state:
    st.session_state["productos"] = obtener_productos_proveedor()

if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

zona = pytz.timezone("America/Argentina/Buenos_Aires")

# =========================
# FUNCIONES
# =========================
def agregar(nombre, precio, cant):
    for item in st.session_state["carrito"]:
        if item["Producto"] == nombre:
            item["Cantidad"] += cant
            return

    st.session_state["carrito"].append({
        "Producto": nombre,
        "Precio": precio,
        "Cantidad": cant
    })

def total_items():
    return sum(x["Cantidad"] for x in st.session_state["carrito"])

def mensaje():
    lineas = ["Hola, necesito hacer un pedido:", ""]
    total = 0

    for item in st.session_state["carrito"]:
        sub = item["Cantidad"] * item["Precio"]
        total += sub
        lineas.append(f"{item['Cantidad']} x {item['Producto']} = {formato_pesos(sub)}")

    lineas.append("")
    lineas.append(f"TOTAL: {formato_pesos(total)}")

    return urllib.parse.quote("\n".join(lineas))

# =========================
# PRECIOS
# =========================
reglas = obtener_reglas_iniciales()

productos = st.session_state["productos"]

for p in productos:
    _, venta = calcular_precio_venta(p["Costo"], p["Peso"], reglas)
    p["Venta"] = venta

df = pd.DataFrame(productos)

# =========================
# FILTRO DESTACADOS
# =========================
def es_destacado(nombre):
    nombre = nombre.lower()
    return (
        "biopet" in nombre or
        "old prince" in nombre or
        "maintenance" in nombre or
        "excellent" in nombre or
        "royal canin" in nombre
    )

df = df[df["Producto"].apply(es_destacado)]

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1,4])

with col1:
    st.image("assets/logo.png", width=180)

with col2:
    st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

# =========================
# BOTON CONSULTA
# =========================
st.link_button(
    "💬 Consulta por WhatsApp",
    f"https://wa.me/5491141645510?text={urllib.parse.quote('Hola, necesito hacerte una consulta.')}"
)

# =========================
# INFO
# =========================
st.info("Compra simple • Atención rápida • Pedido por WhatsApp")

# =========================
# BUSCADOR
# =========================
busqueda = st.text_input("Buscar producto")

if busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False)]

# =========================
# CARRITO BOTON
# =========================
if st.button(f"Carrito ({total_items()})"):
    st.session_state["ver_carrito"] = True

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.subheader("🛒 Tu carrito")

    total = 0

    for i, item in enumerate(st.session_state["carrito"]):
        sub = item["Cantidad"] * item["Precio"]
        total += sub

        col1, col2, col3 = st.columns([4,1,1])

        with col1:
            st.write(item["Producto"])

        with col2:
            cant = st.number_input("Cant", value=item["Cantidad"], key=i)
            item["Cantidad"] = cant

        with col3:
            st.write(formato_pesos(sub))

    st.markdown(f"### TOTAL: {formato_pesos(total)}")

    st.link_button(
        "Enviar pedido",
        f"https://wa.me/5491141645510?text={mensaje()}"
    )

    st.stop()

# =========================
# PRODUCTOS
# =========================
st.subheader("Productos destacados")

for i, row in df.iterrows():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([4,1,1])

    with col1:
        st.write(f"**{row['Producto']}**")

    with col2:
        st.markdown(f"<div class='precio'>{formato_pesos(row['Venta'])}</div>", unsafe_allow_html=True)

    with col3:
        cant = st.number_input("Cant", 1, 20, 1, key=f"c{i}")

        if st.button("Agregar", key=f"a{i}"):
            agregar(row["Producto"], row["Venta"], cant)
            st.success("Agregado")

    st.markdown('</div>', unsafe_allow_html=True)

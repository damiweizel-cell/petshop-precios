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
    page_title="Valentín Pet Food - Tienda Online",
    page_icon="🐾",
    layout="wide"
)

# =========================
# ESTILOS
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0F172A 0%, #111827 100%);
    color: #F8FAFC;
}

.header-card {
    background: #111827;
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 15px;
}

.section-title {
    font-size: 32px;
    font-weight: 900;
}

.section-subtitle {
    font-size: 16px;
    color: #CBD5E1;
}

.delivery-banner {
    background: linear-gradient(135deg, #F59E0B, #FB923C);
    border-radius: 16px;
    padding: 12px;
    text-align: center;
    font-weight: 900;
    margin-bottom: 10px;
    color: black;
}

.info-banner {
    background: #2563EB;
    border-radius: 14px;
    padding: 10px;
    margin-bottom: 12px;
    font-weight: 700;
}

.producto-card {
    background: #1F2937;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

.producto-nombre {
    font-size: 18px;
    font-weight: 900;
}

.precio {
    font-size: 22px;
    font-weight: 900;
    background: #22C55E;
    padding: 6px 12px;
    border-radius: 10px;
    color: black;
}

.carrito-total {
    background: #166534;
    border-radius: 16px;
    padding: 15px;
    text-align: center;
}

button {
    border-radius: 12px !important;
    background: #F3F4F6 !important;
    color: #111827 !important;
    font-weight: 800 !important;
}

input {
    color: black !important;
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
def agregar(producto, precio, cantidad):
    for item in st.session_state["carrito"]:
        if item["Producto"] == producto:
            item["Cantidad"] += cantidad
            return

    st.session_state["carrito"].append({
        "Producto": producto,
        "Precio": precio,
        "Cantidad": cantidad
    })

def quitar(producto):
    st.session_state["carrito"] = [
        x for x in st.session_state["carrito"] if x["Producto"] != producto
    ]

def total_items():
    return sum(x["Cantidad"] for x in st.session_state["carrito"])

def mensaje_whatsapp():
    lineas = ["Hola, necesito hacer un pedido:", ""]
    total = 0

    for item in st.session_state["carrito"]:
        sub = item["Cantidad"] * item["Precio"]
        total += sub
        lineas.append(f"- {item['Cantidad']} x {item['Producto']} = {formato_pesos(sub)}")

    lineas.append("")
    lineas.append(f"TOTAL: {formato_pesos(total)}")

    return urllib.parse.quote("\n".join(lineas))

# =========================
# PRECIOS
# =========================
reglas = obtener_reglas_iniciales()

for p in st.session_state["productos"]:
    _, venta = calcular_precio_venta(p["Costo"], p["Peso"], reglas)
    p["Venta"] = venta

df = pd.DataFrame(st.session_state["productos"])

# =========================
# HEADER
# =========================
st.markdown('<div class="header-card">', unsafe_allow_html=True)

col1, col2 = st.columns([1,4])
with col1:
    st.image("assets/logo.png", width=90)
with col2:
    st.markdown('<div class="section-title">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Tienda Online</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="delivery-banner">🚚 Consultar tiempo de entrega</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="info-banner">🕒 {datetime.now(zona).strftime("%d/%m/%Y %H:%M hs")}</div>',
    unsafe_allow_html=True
)

# =========================
# BUSCAR + BOTONES
# =========================
col1, col2, col3 = st.columns([3,1,1])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Actualizar"):
        st.session_state["productos"] = obtener_productos_proveedor()
        st.rerun()

with col3:
    if st.button(f"Carrito ({total_items()})"):
        st.session_state["ver_carrito"] = True
        st.rerun()

# =========================
# FILTRO
# =========================
if busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False)]

df = df.head(20)

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:

    st.header("🛒 Carrito")

    total = 0

    for i, item in enumerate(st.session_state["carrito"]):
        sub = item["Cantidad"] * item["Precio"]
        total += sub

        st.markdown('<div class="producto-card">', unsafe_allow_html=True)

        st.write(item["Producto"])
        st.write(f"Subtotal: {formato_pesos(sub)}")

        col1, col2 = st.columns(2)

        with col1:
            cant = st.number_input(
                "Cantidad",
                min_value=1,
                value=item["Cantidad"],
                key=f"cant{i}"
            )
            item["Cantidad"] = cant

        with col2:
            if st.button("Eliminar", key=f"del{i}"):
                quitar(item["Producto"])
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="carrito-total">TOTAL {formato_pesos(total)}</div>', unsafe_allow_html=True)

    url = f"https://wa.me/5491141645510?text={mensaje_whatsapp()}"

    st.link_button("📲 Enviar pedido", url)

    if st.button("Volver"):
        st.session_state["ver_carrito"] = False
        st.rerun()

    st.stop()

# =========================
# PRODUCTOS
# =========================
st.subheader("🐶🐱 Productos")

for i, row in df.iterrows():

    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='precio'>{formato_pesos(row['Venta'])}</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        cantidad = st.number_input(
            "Cant.",
            min_value=1,
            value=1,
            key=f"prod{i}"
        )

    with col2:
        if st.button("Agregar", key=f"add{i}"):
            agregar(row["Producto"], row["Venta"], cantidad)
            st.success("Agregado")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

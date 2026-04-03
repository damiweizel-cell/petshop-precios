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
# ESTILOS
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #020617 100%);
        color: #F8FAFC;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #F8FAFC;
    }

    /* LIMPIAR CONTENEDORES RAROS */
    div[data-testid="stVerticalBlock"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* HEADER */
    .header-clean {
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 18px;
    }

    .titulo {
        font-size: 46px;
        font-weight: 900;
    }

    .subtitulo {
        font-size: 20px;
        color: #CBD5E1;
    }

    /* BUSCADOR */
    .busqueda-box {
        margin-top: 18px;
        margin-bottom: 12px;
    }

    /* INFO */
    .info-banner {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 20px;
        font-weight: 800;
    }

    /* HERO */
    .hero-box {
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        border: 1px solid rgba(147,197,253,0.10);
    }

    .hero-title {
        font-size: 42px;
        font-weight: 900;
    }

    .hero-text {
        font-size: 20px;
        margin-bottom: 20px;
    }

    /* BLOQUE INFO */
    .info-box-unico {
        background: rgba(30,41,59,0.6);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 26px;
    }

    .info-item-title {
        font-size: 22px;
        font-weight: 900;
    }

    .info-item-text {
        font-size: 16px;
        color: #CBD5E1;
    }

    /* PRODUCTOS */
    .producto-card {
        padding: 18px 0 22px 0;
    }

    .producto-nombre {
        font-size: 24px;
        font-weight: 900;
        margin-bottom: 10px;
    }

    .precio-cliente {
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(135deg, #86EFAC, #22C55E);
        padding: 10px 14px;
        border-radius: 14px;
        text-align: center;
    }

    /* INPUT CANTIDAD */
    div[data-testid="stNumberInput"] input {
        font-size: 20px !important;
        font-weight: 900 !important;
        text-align: center !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border-radius: 12px !important;
    }

    /* BOTONES */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 900 !important;
        min-height: 50px !important;
        background: #E5E7EB !important;
        color: #111827 !important;
    }

    /* SEPARADOR */
    hr {
        border: none;
        height: 1px;
        background: rgba(148,163,184,0.3);
        margin: 20px 0;
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

def total_items():
    return sum(x["Cantidad"] for x in st.session_state["carrito"])

def mensaje_whatsapp_pedido():
    lineas = ["Hola, necesito hacer un pedido:", ""]
    total = 0

    for item in st.session_state["carrito"]:
        sub = item["Cantidad"] * item["Precio"]
        total += sub
        lineas.append(f"- {item['Cantidad']} x {item['Producto']} = {formato_pesos(sub)}")

    lineas.append("")
    lineas.append(f"TOTAL: {formato_pesos(total)}")

    return urllib.parse.quote("\\n".join(lineas))

def mensaje_whatsapp_consulta():
    return urllib.parse.quote("Hola, necesito hacerte una consulta.")

# =========================
# DATOS
# =========================
reglas = obtener_reglas_iniciales()

for p in st.session_state["productos"]:
    _, venta = calcular_precio_venta(p["Costo"], p["Peso"], reglas)
    p["Venta"] = venta

df = pd.DataFrame(st.session_state["productos"])

# =========================
# HEADER
# =========================
st.markdown('<div class="header-clean">', unsafe_allow_html=True)

c1, c2 = st.columns([1.4, 5])

with c1:
    st.image("assets/logo.png", width=260)

with c2:
    st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# BUSCADOR
# =========================
col1, col2, col3 = st.columns([4,1,1])

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
# INFO
# =========================
st.markdown(
    f'<div class="info-banner">🕒 Última actualización: {datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")}</div>',
    unsafe_allow_html=True
)

# =========================
# HERO
# =========================
h1, h2 = st.columns([1,1.2])

with h1:
    st.markdown('<div class="hero-title">Todo para perros y gatos</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-text">Comprá fácil y rápido por WhatsApp</div>', unsafe_allow_html=True)

    st.link_button(
        "Consultar",
        f"https://wa.me/5491141645510?text={mensaje_whatsapp_consulta()}"
    )

with h2:
    st.image("assets/nuestra_manada.jpeg", use_container_width=True)

# =========================
# BLOQUE INFO
# =========================
st.markdown('<div class="info-box-unico">', unsafe_allow_html=True)

i1, i2, i3 = st.columns(3)

with i1:
    st.markdown("<div class='info-item-title'>🐾 Productos seleccionados</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-item-text'>Alimentos y artículos destacados</div>", unsafe_allow_html=True)

with i2:
    st.markdown("<div class='info-item-title'>📦 Compra simple</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-item-text'>Armá tu pedido rápido</div>", unsafe_allow_html=True)

with i3:
    st.markdown("<div class='info-item-title'>💬 WhatsApp</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-item-text'>Atención directa</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FILTRO
# =========================
if busqueda:
    df_mostrar = df[df["Producto"].str.contains(busqueda, case=False)]
else:
    df_mostrar = df

# =========================
# PRODUCTOS
# =========================
st.markdown("## 🐶🐱 Productos")

for i, row in df_mostrar.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    t1, t2 = st.columns([4,2])

    with t1:
        st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)

    with t2:
        st.markdown(f"<div class='precio-cliente'>{formato_pesos(row['Venta'])}</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1,3])

    with c1:
        cantidad = st.number_input("", 1, 99, 1, key=f"prod{i}")

    with c2:
        if st.button("Agregar al carrito", key=f"btn{i}", use_container_width=True):
            agregar(row["Producto"], row["Venta"], cantidad)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

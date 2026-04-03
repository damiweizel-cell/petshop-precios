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
        font-size: 35px;
        font-weight: 900;
    }

    .subtitulo {
        font-size: 20px;
        color: #CBD5E1;
    }

    /* LABEL BUSCADOR */
    .busqueda-label {
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .busqueda-ayuda {
        font-size: 14px;
        color: #CBD5E1;
        font-style: italic;
        font-weight: 500;
        margin-left: 10px;
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
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 10px;
    }

    .precio-cliente {
        font-size: 20px;
        font-weight: 900;
        background: linear-gradient(135deg, #86EFAC, #22C55E);
        padding: 10px 14px;
        border-radius: 14px;
        text-align: center;
        display: inline-block;
        min-width: 160px;
        color: #052E16 !important;
    }

    /* INPUT BUSCADOR */
    div.stTextInput > div > div > input {
        font-size: 18px !important;
        font-weight: 700 !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border-radius: 12px !important;
        min-height: 52px !important;
    }

    /* INPUT CANTIDAD */
    div[data-testid="stNumberInput"] input {
        font-size: 20px !important;
        font-weight: 900 !important;
        text-align: center !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border-radius: 12px !important;
        min-height: 52px !important;
    }

    /* BOTONES */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 900 !important;
        min-height: 52px !important;
        background: #E5E7EB !important;
        color: #111827 !important;
        font-size: 16px !important;
    }

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: #111827 !important;
    }

    div[data-testid="stLinkButton"] a {
        border-radius: 14px !important;
        font-weight: 900 !important;
        min-height: 52px !important;
        background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
        color: white !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* SEPARADOR */
    hr {
        border: none;
        height: 1px;
        background: rgba(148,163,184,0.3);
        margin: 20px 0;
    }

    /* MOBILE */
    @media (max-width: 768px) {
        .titulo {
            font-size: 28px;
        }

        .subtitulo {
            font-size: 16px;
        }

        .hero-title {
            font-size: 30px;
        }

        .hero-text {
            font-size: 17px;
        }

        .producto-nombre {
            font-size: 20px;
        }

        .precio-cliente {
            font-size: 18px;
            min-width: 140px;
            margin-top: 8px;
        }

        .info-item-title {
            font-size: 18px;
        }

        .info-item-text {
            font-size: 14px;
        }
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

if "buscar_click" not in st.session_state:
    st.session_state["buscar_click"] = False

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
# DESTACADOS PORTADA
# =========================
MARCAS_DESTACADAS = ["old prince", "biopet", "maintenance", "excellent"]

def es_destacado(nombre):
    nombre = str(nombre).lower()
    return any(marca in nombre for marca in MARCAS_DESTACADAS)

df_destacados = df[df["Producto"].apply(es_destacado)].copy()
df_destacados = df_destacados.sort_values("Producto")

# =========================
# HEADER
# =========================
st.markdown('<div class="header-clean">', unsafe_allow_html=True)

c1, c2 = st.columns([2.1, 4.4])

with c1:
    st.image("assets/logo.png", width=360)

with c2:
    st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# BUSCADOR
# =========================
st.markdown(
    '<div class="busqueda-label">Buscar producto <span class="busqueda-ayuda">escribí el nombre y presioná la lupa</span></div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([5, 0.8, 1.2])

with col1:
    busqueda = st.text_input("", placeholder="Ej: Old Prince, pipetas, piedras sanitarias...", label_visibility="collapsed")

with col2:
    if st.button("🔎", use_container_width=True):
        st.session_state["buscar_click"] = True

with col3:
    if st.button(f"Carrito ({total_items()})", use_container_width=True):
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
        "Consultas por WhatsApp",
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
    st.markdown("<div class='info-item-text'>Mostramos alimentos destacados para tu mascota.</div>", unsafe_allow_html=True)

with i2:
    st.markdown("<div class='info-item-title'>📦 Compra simple</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-item-text'>Elegí, agregá al carrito y enviá tu pedido.</div>", unsafe_allow_html=True)

with i3:
    st.markdown("<div class='info-item-title'>💬 WhatsApp</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-item-text'>Atención directa y pedidos rápidos.</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FILTRO
# =========================
mostrar_busqueda = st.session_state["buscar_click"] and busqueda.strip() != ""

if mostrar_busqueda:
    df_mostrar = df[df["Producto"].str.contains(busqueda, case=False, na=False)].copy()
    titulo_productos = "🔎 Resultados de búsqueda"
else:
    df_mostrar = df_destacados.copy()
    titulo_productos = "🐶🐱 Productos destacados"

# =========================
# PRODUCTOS
# =========================
st.markdown(f"## {titulo_productos}")

for i, row in df_mostrar.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    t1, t2 = st.columns([4,2])

    with t1:
        st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)

    with t2:
        st.markdown(f"<div class='precio-cliente'>{formato_pesos(row['Venta'])}</div>", unsafe_allow_html=True)

    # IMPORTANTE: en mobile Streamlit puede apilar columnas sí o sí.
    # Este reparto minimiza ese problema y lo deja mucho mejor.
    c1, c2 = st.columns([1.2, 2.8], vertical_alignment="bottom")

    with c1:
        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=99,
            value=1,
            step=1,
            key=f"prod{i}"
        )

    with c2:
        if st.button("Agregar al carrito", key=f"btn{i}", use_container_width=True):
            agregar(row["Producto"], row["Venta"], cantidad)
            st.toast("✅ Producto agregado")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

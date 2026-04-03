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
        padding-top: 0.4rem;
        padding-bottom: 1.2rem;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #F8FAFC;
    }

    div[data-testid="stVerticalBlock"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* =========================
       HEADER
    ========================= */
    .header-clean {
        padding: 0 0 10px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 12px;
    }

    .titulo {
        font-size: 35px;
        font-weight: 900;
        margin-top: -12px;
        margin-bottom: 2px;
        line-height: 1.05;
    }

    .subtitulo {
        font-size: 19px;
        color: #CBD5E1;
        margin-top: 0;
    }

    .logo-wrap {
        margin-bottom: -28px;
    }

    /* =========================
       BUSCADOR
    ========================= */
    .busqueda-label {
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .busqueda-ayuda {
        font-size: 14px;
        color: #CBD5E1;
        font-style: italic;
        font-weight: 500;
        margin-left: 8px;
    }

    div.stTextInput > div > div > input {
        font-size: 17px !important;
        font-weight: 700 !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border-radius: 12px !important;
        min-height: 48px !important;
        padding-right: 42px !important;
    }

    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 900 !important;
        min-height: 48px !important;
        background: #E5E7EB !important;
        color: #111827 !important;
        font-size: 15px !important;
        padding: 0.3rem 0.7rem !important;
    }

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: #111827 !important;
    }

    /* =========================
       INFO
    ========================= */
    .info-banner {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 18px;
        font-weight: 800;
    }

    /* =========================
       HERO
    ========================= */
    .hero-title {
        font-size: 38px;
        font-weight: 900;
        line-height: 1.05;
    }

    .hero-text {
        font-size: 19px;
        margin-bottom: 18px;
    }

    /* =========================
       BLOQUE INFO
    ========================= */
    .info-box-unico {
        background: rgba(30,41,59,0.6);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 18px;
    }

    .info-item-title {
        font-size: 20px;
        font-weight: 900;
    }

    .info-item-text {
        font-size: 15px;
        color: #CBD5E1;
    }

    /* =========================
       PRODUCTOS
    ========================= */
    .producto-card {
        padding: 10px 0 10px 0;
    }

    .producto-nombre {
        font-size: 20px;
        font-weight: 900;
        margin-bottom: 8px;
        line-height: 1.25;
    }

    .precio-cliente {
        font-size: 18px;
        font-weight: 900;
        background: linear-gradient(135deg, #86EFAC, #22C55E);
        padding: 10px 14px;
        border-radius: 14px;
        text-align: center;
        display: inline-block;
        min-width: 150px;
        color: #052E16 !important;
        margin-bottom: 8px;
    }

    div[data-testid="stNumberInput"] input {
        font-size: 18px !important;
        font-weight: 900 !important;
        text-align: center !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border-radius: 12px !important;
        min-height: 48px !important;
    }

    label {
        margin-bottom: 2px !important;
    }

    hr {
        border: none;
        height: 1px;
        background: rgba(148,163,184,0.22);
        margin: 10px 0 12px 0;
    }

    div[data-testid="stLinkButton"] a {
        border-radius: 12px !important;
        font-weight: 900 !important;
        min-height: 48px !important;
        background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
        color: white !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* =========================
       MOBILE
    ========================= */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.2rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-bottom: 1rem;
        }

        .logo-wrap {
            margin-bottom: -38px;
        }

        .titulo {
            font-size: 27px;
            margin-top: -18px;
        }

        .subtitulo {
            font-size: 15px;
        }

        .hero-title {
            font-size: 26px;
        }

        .hero-text {
            font-size: 16px;
        }

        .producto-nombre {
            font-size: 18px;
        }

        .precio-cliente {
            font-size: 17px;
            min-width: 130px;
            padding: 9px 12px;
        }

        .info-item-title {
            font-size: 17px;
        }

        .info-item-text {
            font-size: 13px;
        }

        .busqueda-label {
            font-size: 16px;
        }

        .busqueda-ayuda {
            font-size: 12px;
        }

        div.stButton > button {
            min-height: 46px !important;
            font-size: 14px !important;
        }

        div[data-testid="stNumberInput"] input {
            min-height: 46px !important;
            font-size: 17px !important;
        }

        div.stTextInput > div > div > input {
            min-height: 46px !important;
            font-size: 16px !important;
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

c1, c2 = st.columns([1.7, 4.3])

with c1:
    st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
    st.image("assets/logo.png", width=300)
    st.markdown('</div>', unsafe_allow_html=True)

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

col1, col2, col3 = st.columns([4.8, 0.8, 1.4])

with col1:
    busqueda = st.text_input(
        "",
        placeholder="Ej: Old Prince, pipetas, piedras sanitarias...",
        label_visibility="collapsed"
    )

with col2:
    if st.button("🔎", use_container_width=True):
        st.session_state["buscar_click"] = True

with col3:
    if st.button(f"🛒 {total_items()}", use_container_width=True):
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

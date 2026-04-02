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
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #F8FAFC;
    }

    .top-box {
        background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.98) 100%);
        border-radius: 26px;
        padding: 22px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 16px 34px rgba(0,0,0,0.28);
    }

    .titulo {
        font-size: 42px;
        font-weight: 900;
        line-height: 1.05;
        margin-bottom: 6px;
        color: #F8FAFC;
    }

    .subtitulo {
        font-size: 20px;
        color: #CBD5E1;
        font-weight: 600;
    }

    .hero-box {
        background:
            radial-gradient(circle at top right, rgba(59,130,246,0.25) 0%, rgba(0,0,0,0) 35%),
            linear-gradient(135deg, rgba(37,99,235,0.16) 0%, rgba(15,23,42,0.95) 45%, rgba(30,41,59,0.96) 100%);
        border-radius: 30px;
        padding: 28px;
        margin-bottom: 20px;
        border: 1px solid rgba(147,197,253,0.18);
        box-shadow: 0 18px 40px rgba(0,0,0,0.30);
    }

    .hero-mini {
        font-size: 17px;
        color: #93C5FD;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 46px;
        font-weight: 900;
        line-height: 1.05;
        margin-bottom: 14px;
        color: #F8FAFC;
    }

    .hero-text {
        font-size: 22px;
        line-height: 1.5;
        color: #E2E8F0;
        margin-bottom: 24px;
    }

    .hero-img-box {
        background: rgba(255,255,255,0.03);
        border-radius: 26px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .info-banner {
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
        border-radius: 18px;
        padding: 15px 18px;
        margin-bottom: 18px;
        font-size: 17px;
        font-weight: 800;
        color: white;
        box-shadow: 0 10px 24px rgba(37,99,235,0.22);
    }

    .mini-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.96) 0%, rgba(15,23,42,0.98) 100%);
        border-radius: 22px;
        padding: 18px;
        min-height: 120px;
        border: 1px solid rgba(147,197,253,0.10);
        box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }

    .mini-card-title {
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 6px;
        color: #F8FAFC;
    }

    .mini-card-text {
        font-size: 16px;
        line-height: 1.45;
        color: #CBD5E1;
    }

    .titulo-seccion {
        font-size: 28px;
        font-weight: 900;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .producto-card {
        background: linear-gradient(180deg, #1F2937 0%, #111827 100%);
        border-radius: 24px;
        padding: 18px;
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 12px 30px rgba(0,0,0,0.28);
    }

    .producto-nombre {
        font-size: 24px;
        font-weight: 900;
        color: #F9FAFB;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    .precio-cliente {
        font-size: 30px;
        font-weight: 900;
        color: #052E16;
        background: linear-gradient(135deg, #86EFAC 0%, #22C55E 100%);
        padding: 12px 16px;
        border-radius: 18px;
        text-align: center;
        display: inline-block;
        min-width: 150px;
        box-shadow: 0 8px 18px rgba(34,197,94,0.25);
    }

    .carrito-item {
        background: linear-gradient(180deg, #1F2937 0%, #111827 100%);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 22px rgba(0,0,0,0.24);
    }

    .carrito-total {
        background: linear-gradient(135deg, #14532D 0%, #166534 100%);
        border-radius: 24px;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 12px 26px rgba(22,101,52,0.30);
    }

    .carrito-total-label {
        font-size: 15px;
        font-weight: 800;
        color: #DCFCE7;
    }

    .carrito-total-value {
        font-size: 42px;
        font-weight: 900;
        color: #F0FDF4;
    }

    div.stTextInput > div > div > input {
        border-radius: 18px !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border: none !important;
        min-height: 54px;
        font-size: 17px !important;
    }

    div[data-testid="stNumberInput"] input {
        border-radius: 16px !important;
        min-height: 50px !important;
        font-size: 16px !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border: none !important;
    }

    div.stButton > button {
        border-radius: 18px !important;
        font-weight: 900 !important;
        padding: 0.85rem 1rem !important;
        border: none !important;
        min-height: 54px !important;
        font-size: 17px !important;
        background: linear-gradient(135deg, #F8FAFC 0%, #E5E7EB 100%) !important;
        color: #111827 !important;
        box-shadow: 0 8px 18px rgba(0,0,0,0.16) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #FFFFFF 0%, #D1D5DB 100%) !important;
        color: #111827 !important;
    }

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: #111827 !important;
    }

    div[data-testid="stLinkButton"] a {
        border-radius: 18px !important;
        font-weight: 900 !important;
        min-height: 56px !important;
        font-size: 17px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
        color: white !important;
        box-shadow: 0 12px 24px rgba(34,197,94,0.28) !important;
        text-decoration: none !important;
    }

    label, .stTextInput label {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #E2E8F0 !important;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.7rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-bottom: 2rem;
        }

        .titulo {
            font-size: 30px;
        }

        .subtitulo {
            font-size: 16px;
        }

        .hero-title {
            font-size: 32px;
        }

        .hero-text {
            font-size: 18px;
        }

        .producto-nombre {
            font-size: 20px;
        }

        .precio-cliente {
            font-size: 25px;
            min-width: 135px;
        }

        .titulo-seccion {
            font-size: 24px;
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

def mensaje_whatsapp_pedido():
    lineas = ["Hola, necesito hacer un pedido:", ""]
    total = 0

    for item in st.session_state["carrito"]:
        sub = item["Cantidad"] * item["Precio"]
        total += sub
        lineas.append(f"- {item['Cantidad']} x {item['Producto']} = {formato_pesos(sub)}")

    lineas.append("")
    lineas.append(f"TOTAL: {formato_pesos(total)}")

    return urllib.parse.quote("\n".join(lineas))

def mensaje_whatsapp_consulta():
    return urllib.parse.quote("Hola, necesito hacerte una consulta.")

# =========================
# PRECIOS
# =========================
reglas = obtener_reglas_iniciales()

for p in st.session_state["productos"]:
    _, venta = calcular_precio_venta(p["Costo"], p["Peso"], reglas)
    p["Venta"] = venta

df = pd.DataFrame(st.session_state["productos"])

# =========================
# DESTACADOS
# =========================
PRIORIDADES = [
    "biopet",
    "old prince",
    "maintenance",
    "excellent urinary gato",
    "royal canin"
]

def es_destacado(nombre):
    nombre = str(nombre).lower()
    return any(p in nombre for p in PRIORIDADES)

df_destacados = df[df["Producto"].apply(es_destacado)].copy()

if df_destacados.empty:
    df_destacados = df.copy()

df_destacados = df_destacados.sort_values("Producto").head(20)

# =========================
# HEADER
# =========================
st.markdown('<div class="top-box">', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 4.5])

with col1:
    st.image("assets/logo.png", width=180)

with col2:
    st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown('<div class="hero-box">', unsafe_allow_html=True)

hero1, hero2 = st.columns([1.25, 1])

with hero1:
    st.markdown('<div class="hero-mini">🐾 Tienda online • Pedidos simples • Atención rápida</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Todo para perros y gatos</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-text">Encontrá alimentos y productos seleccionados para tu mascota, con pedidos simples y atención directa por WhatsApp.</div>',
        unsafe_allow_html=True
    )

    st.link_button(
        "💬 Consulta",
        f"https://wa.me/5491141645510?text={mensaje_whatsapp_consulta()}",
        use_container_width=False
    )

with hero2:
    st.markdown('<div class="hero-img-box">', unsafe_allow_html=True)
    st.image(
        "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1200&q=80",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# INFO
# =========================
st.markdown(
    f'<div class="info-banner">🕒 Última actualización: {datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")}</div>',
    unsafe_allow_html=True
)

# =========================
# BLOQUES INFO
# =========================
mc1, mc2, mc3 = st.columns(3)

with mc1:
    st.markdown("""
        <div class="mini-card">
            <div class="mini-card-title">🐾 Productos seleccionados</div>
            <div class="mini-card-text">Mostramos alimentos y artículos destacados para perros y gatos.</div>
        </div>
    """, unsafe_allow_html=True)

with mc2:
    st.markdown("""
        <div class="mini-card">
            <div class="mini-card-title">📦 Compra simple</div>
            <div class="mini-card-text">Elegí productos, sumalos al carrito y armá tu pedido fácil.</div>
        </div>
    """, unsafe_allow_html=True)

with mc3:
    st.markdown("""
        <div class="mini-card">
            <div class="mini-card-title">💬 Atención por WhatsApp</div>
            <div class="mini-card-text">Consultas y pedidos directos desde la tienda online.</div>
        </div>
    """, unsafe_allow_html=True)

# =========================
# BUSCADOR
# =========================
st.markdown('<div class="titulo-seccion">🔎 Buscar y comprar</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,1,1])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Actualizar", use_container_width=True):
        st.session_state["productos"] = obtener_productos_proveedor()
        st.rerun()

with col3:
    cantidad_total = total_items()

    if st.button(f"Carrito ({cantidad_total})", use_container_width=True):
        st.session_state["ver_carrito"] = True
        st.rerun()

# =========================
# FILTRO
# =========================
if busqueda:
    df_mostrar = df[df["Producto"].str.contains(busqueda, case=False, na=False)].copy()
    df_mostrar = df_mostrar.sort_values("Producto")
else:
    df_mostrar = df_destacados.copy()

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.markdown('<div class="titulo-seccion">🛒 Mi carrito</div>', unsafe_allow_html=True)

    if not st.session_state["carrito"]:
        st.info("Todavía no agregaste productos.")

    else:
        total = 0

        for i, item in enumerate(st.session_state["carrito"]):
            sub = item["Cantidad"] * item["Precio"]
            total += sub

            st.markdown('<div class="carrito-item">', unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns([4.4, 1.2, 1.4, 1])

            with c1:
                st.write(f"**{item['Producto']}**")
                st.caption(f"Precio unitario: {formato_pesos(item['Precio'])}")
                st.write(f"Subtotal: **{formato_pesos(sub)}**")

            with c2:
                cant = st.number_input(
                    "Cant.",
                    min_value=1,
                    value=item["Cantidad"],
                    key=f"cant{i}"
                )
                item["Cantidad"] = cant

            with c3:
                st.write("")
                st.write("")
                st.write(f"**{formato_pesos(sub)}**")

            with c4:
                st.write("")
                st.write("")
                if st.button("❌", key=f"del{i}"):
                    quitar(item["Producto"])
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="carrito-total">
                <div class="carrito-total-label">TOTAL DEL PEDIDO</div>
                <div class="carrito-total-value">{formato_pesos(total)}</div>
            </div>
        """, unsafe_allow_html=True)

        url = f"https://wa.me/5491141645510?text={mensaje_whatsapp_pedido()}"
        st.link_button("📲 Enviar pedido", url, use_container_width=True)

    colv1, colv2 = st.columns(2)

    with colv1:
        if st.button("⬅️ Volver al catálogo", use_container_width=True):
            st.session_state["ver_carrito"] = False
            st.rerun()

    with colv2:
        if st.button("🗑 Vaciar carrito", use_container_width=True):
            st.session_state["carrito"] = []
            st.rerun()

    st.stop()

# =========================
# PRODUCTOS
# =========================
st.markdown('<div class="titulo-seccion">🐶🐱 Productos destacados</div>', unsafe_allow_html=True)

for i, row in df_mostrar.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([4.3, 1.8, 1.6])

    with col1:
        st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"<div class='precio-cliente'>{formato_pesos(row['Venta'])}</div>",
            unsafe_allow_html=True
        )

    with col3:
        cantidad = st.number_input(
            "Cant.",
            min_value=1,
            max_value=99,
            step=1,
            value=1,
            key=f"prod{i}"
        )

        if st.button("Agregar", key=f"add{i}", use_container_width=True):
            agregar(row["Producto"], row["Venta"], cantidad)
            st.toast("✅ Producto agregado")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

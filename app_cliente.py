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

    /* Eliminar espacios/containers raros de Streamlit */
    div[data-testid="stVerticalBlock"] > div:has(> div.stMarkdown) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .header-clean {
        padding: 8px 0 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 18px;
    }

    .titulo {
        font-size: 46px;
        font-weight: 900;
        line-height: 1.05;
        margin-bottom: 6px;
        color: #F8FAFC;
    }

    .subtitulo {
        font-size: 21px;
        color: #CBD5E1;
        font-weight: 600;
    }

    .busqueda-box {
        margin-top: 18px;
        margin-bottom: 12px;
    }

    .info-banner {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 20px;
        font-size: 17px;
        font-weight: 800;
        color: white;
        box-shadow: 0 10px 24px rgba(37,99,235,0.22);
    }

    .hero-box {
        background:
            radial-gradient(circle at top right, rgba(59,130,246,0.18) 0%, rgba(0,0,0,0) 35%),
            linear-gradient(135deg, rgba(37,99,235,0.10) 0%, rgba(15,23,42,0.96) 45%, rgba(30,41,59,0.96) 100%);
        border-radius: 28px;
        padding: 30px;
        margin-bottom: 24px;
        border: 1px solid rgba(147,197,253,0.10);
        box-shadow: 0 18px 40px rgba(0,0,0,0.28);
    }

    .hero-mini {
        font-size: 16px;
        color: #93C5FD;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .hero-title {
        font-size: 44px;
        font-weight: 900;
        line-height: 1.05;
        margin-bottom: 14px;
        color: #F8FAFC;
    }

    .hero-text {
        font-size: 21px;
        line-height: 1.5;
        color: #E2E8F0;
        margin-bottom: 24px;
    }

    .hero-img-box {
        background: transparent;
        border-radius: 22px;
        padding: 0;
        border: none;
    }

    .info-box-unico {
        background: linear-gradient(180deg, rgba(30,41,59,0.96) 0%, rgba(15,23,42,0.98) 100%);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 26px;
        border: 1px solid rgba(147,197,253,0.10);
        box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }

    .info-item {
        padding: 10px 6px;
    }

    .info-item-title {
        font-size: 24px;
        font-weight: 900;
        margin-bottom: 6px;
        color: #F8FAFC;
    }

    .info-item-text {
        font-size: 17px;
        line-height: 1.5;
        color: #CBD5E1;
    }

    .titulo-seccion {
        font-size: 28px;
        font-weight: 900;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 14px;
    }

    .producto-card {
        background: linear-gradient(180deg, #1F2937 0%, #111827 100%);
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 12px 30px rgba(0,0,0,0.28);
    }

    .producto-nombre {
        font-size: 24px;
        font-weight: 900;
        color: #F9FAFB;
        line-height: 1.2;
        margin-bottom: 12px;
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
        min-width: 170px;
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
        min-height: 56px;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding-left: 14px !important;
    }

    div[data-testid="stNumberInput"] input {
        border-radius: 16px !important;
        min-height: 54px !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border: none !important;
        text-align: center !important;
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
            font-size: 32px;
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
            font-size: 24px;
            min-width: 140px;
        }

        .titulo-seccion {
            font-size: 24px;
        }

        .info-item-title {
            font-size: 20px;
        }

        .info-item-text {
            font-size: 15px;
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
st.markdown('<div class="header-clean">', unsafe_allow_html=True)

col1, col2 = st.columns([1.4, 5])

with col1:
    st.image("assets/logo.png", width=240)

with col2:
    st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# BUSCADOR ARRIBA
# =========================
st.markdown('<div class="busqueda-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 1, 1])

with col1:
    busqueda = st.text_input("Buscar producto", placeholder="Ej: Old Prince, pipetas, piedras sanitarias...")

with col2:
    if st.button("Actualizar", use_container_width=True):
        st.session_state["productos"] = obtener_productos_proveedor()
        st.rerun()

with col3:
    cantidad_total = total_items()

    if st.button(f"Carrito ({cantidad_total})", use_container_width=True):
        st.session_state["ver_carrito"] = True
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# INFO ARRIBA
# =========================
st.markdown(
    f'<div class="info-banner">🕒 Última actualización: {datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")}</div>',
    unsafe_allow_html=True
)

# =========================
# HERO
# =========================
st.markdown('<div class="hero-box">', unsafe_allow_html=True)

hero1, hero2 = st.columns([1.05, 1.25])

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
        "assets/nuestra_manada.jpeg",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# BLOQUE INFO ÚNICO
# =========================
st.markdown('<div class="info-box-unico">', unsafe_allow_html=True)

ic1, ic2, ic3 = st.columns(3)

with ic1:
    st.markdown("""
        <div class="info-item">
            <div class="info-item-title">🐾 Productos seleccionados</div>
            <div class="info-item-text">Mostramos alimentos y artículos destacados para perros y gatos.</div>
        </div>
    """, unsafe_allow_html=True)

with ic2:
    st.markdown("""
        <div class="info-item">
            <div class="info-item-title">📦 Compra simple</div>
            <div class="info-item-text">Elegí productos, sumalos al carrito y armá tu pedido fácil.</div>
        </div>
    """, unsafe_allow_html=True)

with ic3:
    st.markdown("""
        <div class="info-item">
            <div class="info-item-title">💬 Atención por WhatsApp</div>
            <div class="info-item-text">Consultas y pedidos directos desde la tienda online.</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

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

    top1, top2 = st.columns([4.5, 2])

    with top1:
        st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)

    with top2:
        st.markdown(
            f"<div class='precio-cliente'>{formato_pesos(row['Venta'])}</div>",
            unsafe_allow_html=True
        )

    c1, c2 = st.columns([1.1, 2.4])

    with c1:
        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=99,
            step=1,
            value=1,
            key=f"prod{i}"
        )

    with c2:
        st.write("")
        if st.button("Agregar al carrito", key=f"add{i}", use_container_width=True):
            agregar(row["Producto"], row["Venta"], cantidad)
            st.toast("✅ Producto agregado")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

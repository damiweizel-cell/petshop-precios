import streamlit as st
import pandas as pd
import pytz
import urllib.parse
from datetime import datetime

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
# CSS MOBILE FIRST
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #020617 100%);
        color: #F8FAFC;
    }

    .main .block-container {
        max-width: 1100px;
        padding-top: 0.4rem;
        padding-bottom: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
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
       HEADER / BANNER
    ========================= */
    .banner-wrap {
        margin-bottom: 10px;
    }

    .titulo {
        font-size: 24px;
        font-weight: 900;
        line-height: 1.05;
        margin-top: 4px;
        margin-bottom: 2px;
        text-align: left;
    }

    .subtitulo {
        font-size: 14px;
        color: #CBD5E1;
        margin-top: 0;
        margin-bottom: 10px;
        text-align: left;
    }

    /* =========================
       BUSCADOR
    ========================= */
    .busqueda-label {
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .busqueda-ayuda {
        font-size: 12px;
        color: #CBD5E1;
        font-style: italic;
        font-weight: 500;
        margin-left: 8px;
    }

    div.stTextInput > div > div > input {
        font-size: 14px !important;
        font-weight: 700 !important;
        background: #F8FAFC !important;
        color: #111827 !important;
        border-radius: 10px !important;
        min-height: 40px !important;
        padding-right: 8px !important;
    }

    /* =========================
       BOTONES
    ========================= */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 900 !important;
        min-height: 38px !important;
        background: #E5E7EB !important;
        color: #111827 !important;
        font-size: 12px !important;
        padding: 0.15rem 0.45rem !important;
        border: none !important;
        width: auto !important;
    }

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: #111827 !important;
    }

    div[data-testid="stLinkButton"] a {
        border-radius: 12px !important;
        font-weight: 900 !important;
        min-height: 42px !important;
        background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%) !important;
        color: white !important;
        text-decoration: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-size: 14px !important;
    }

    /* =========================
       INFO
    ========================= */
    .info-banner {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        border-radius: 14px;
        padding: 12px 14px;
        margin-bottom: 14px;
        font-weight: 800;
        font-size: 14px;
    }

    /* =========================
       PRODUCTOS
    ========================= */
    .titulo-productos {
        font-size: 18px;
        font-weight: 900;
        margin-top: 6px;
        margin-bottom: 8px;
    }

    .producto-card {
        padding: 4px 0 6px 0;
    }

    .producto-nombre {
        font-size: 17px;
        font-weight: 900;
        margin-bottom: 8px;
        line-height: 1.25;
    }

    .precio-cliente {
        font-size: 16px;
        font-weight: 900;
        background: linear-gradient(135deg, #86EFAC, #22C55E);
        padding: 9px 12px;
        border-radius: 12px;
        text-align: center;
        display: inline-block;
        min-width: 125px;
        color: #052E16 !important;
        margin-bottom: 6px;
    }

    .qty-box {
        background:#F8FAFC;
        color:#111827;
        border-radius:10px;
        text-align:center;
        padding:7px 6px;
        font-weight:900;
        font-size:15px;
        min-height: 38px;
        display:flex;
        align-items:center;
        justify-content:center;
    }

    hr {
        border: none;
        height: 1px;
        background: rgba(148,163,184,0.16);
        margin: 6px 0 8px 0;
    }

    /* =========================
       DESKTOP
    ========================= */
    @media (min-width: 769px) {
        .main .block-container {
            padding-top: 0.6rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
            padding-bottom: 1.5rem;
        }

        .titulo {
            font-size: 34px;
        }

        .subtitulo {
            font-size: 18px;
        }

        .busqueda-label {
            font-size: 18px;
        }

        .busqueda-ayuda {
            font-size: 13px;
        }

        div.stTextInput > div > div > input {
            min-height: 46px !important;
            font-size: 16px !important;
        }

        div.stButton > button {
            min-height: 44px !important;
            font-size: 14px !important;
        }

        .info-banner {
            font-size: 16px;
        }

        .titulo-productos {
            font-size: 28px;
            margin-bottom: 14px;
        }

        .producto-nombre {
            font-size: 22px;
        }

        .precio-cliente {
            font-size: 20px;
            min-width: 160px;
            padding: 10px 14px;
        }

        .qty-box {
            font-size: 17px;
            min-height: 44px;
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

    return urllib.parse.quote("\\n".join(lineas))

def mensaje_whatsapp_consulta():
    return urllib.parse.quote("Hola, quiero consultar precios y productos.")

# =========================
# DATOS
# =========================
reglas = obtener_reglas_iniciales()

for p in st.session_state["productos"]:
    _, venta = calcular_precio_venta(p["Costo"], p["Peso"], reglas)
    p["Venta"] = venta

df = pd.DataFrame(st.session_state["productos"])

MARCAS_DESTACADAS = ["old prince", "biopet", "maintenance", "excellent"]

def es_destacado(nombre):
    nombre = str(nombre).lower()
    return any(marca in nombre for marca in MARCAS_DESTACADAS)

df_destacados = df[df["Producto"].apply(es_destacado)].copy()
df_destacados = df_destacados.sort_values("Producto")

# =========================
# HEADER (LOGO FULL WIDTH + TITULO ABAJO)
# =========================
st.markdown('<div class="banner-wrap">', unsafe_allow_html=True)
st.image("assets/logo.png", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

# =========================
# BUSCADOR
# =========================
st.markdown(
    '<div class="busqueda-label">Buscar producto <span class="busqueda-ayuda">escribí el nombre y presioná la lupa</span></div>',
    unsafe_allow_html=True
)

b1, b2, b3 = st.columns([4.0, 0.8, 1.0], gap="small")

with b1:
    busqueda = st.text_input(
        "",
        placeholder="Ej: Old Prince, pipetas...",
        label_visibility="collapsed"
    )

with b2:
    buscar = st.button("🔎", key="btn_buscar", use_container_width=True)

with b3:
    if st.button(f"🛒 {total_items()}", key="btn_carrito", use_container_width=True):
        st.session_state["ver_carrito"] = True
        st.rerun()

if buscar:
    st.session_state["buscar_click"] = True

# =========================
# INFO
# =========================
st.markdown(
    f'<div class="info-banner">🕒 Última actualización: {datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")}</div>',
    unsafe_allow_html=True
)

# =========================
# CONSULTA WHATSAPP
# =========================
st.link_button(
    "Consultar por WhatsApp",
    f"https://wa.me/5491141645510?text={mensaje_whatsapp_consulta()}",
    use_container_width=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# FILTRO
# =========================
mostrar_busqueda = st.session_state["buscar_click"] and busqueda.strip() != ""

if mostrar_busqueda:
    df_mostrar = df[df["Producto"].str.contains(busqueda, case=False, na=False)].copy()
    titulo_productos = "🔎 Resultados de búsqueda"
    st.success(f"Mostrando resultados para: {busqueda}")
else:
    df_mostrar = df_destacados.copy()
    titulo_productos = "🐶🐱 Productos destacados"

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.markdown('<div class="titulo-productos">🛒 Mi carrito</div>', unsafe_allow_html=True)

    if not st.session_state["carrito"]:
        st.info("Todavía no agregaste productos.")

    else:
        total = 0

        for i, item in enumerate(st.session_state["carrito"]):
            sub = item["Cantidad"] * item["Precio"]
            total += sub

            st.markdown('<div class="producto-card">', unsafe_allow_html=True)

            c1, c2 = st.columns([3.4, 1.6], gap="small")

            with c1:
                st.markdown(f"<div class='producto-nombre'>{item['Producto']}</div>", unsafe_allow_html=True)
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

                if st.button("❌", key=f"del{i}", use_container_width=True):
                    quitar(item["Producto"])
                    st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #14532D 0%, #166534 100%);
                border-radius: 18px;
                padding: 18px;
                text-align: center;
                margin-top: 14px;
                margin-bottom: 16px;
            ">
                <div style="font-size: 13px; font-weight: 800; color: #DCFCE7;">TOTAL DEL PEDIDO</div>
                <div style="font-size: 30px; font-weight: 900; color: #F0FDF4;">{formato_pesos(total)}</div>
            </div>
        """, unsafe_allow_html=True)

        url = f"https://wa.me/5491141645510?text={mensaje_whatsapp_pedido()}"
        st.link_button("📲 Enviar pedido", url, use_container_width=True)

    cv1, cv2 = st.columns(2, gap="small")

    with cv1:
        if st.button("⬅️ Volver", use_container_width=True):
            st.session_state["ver_carrito"] = False
            st.rerun()

    with cv2:
        if st.button("🗑 Vaciar", use_container_width=True):
            st.session_state["carrito"] = []
            st.rerun()

    st.stop()

# =========================
# PRODUCTOS
# =========================
st.markdown(f'<div class="titulo-productos">{titulo_productos}</div>', unsafe_allow_html=True)

for i, row in df_mostrar.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='precio-cliente'>{formato_pesos(row['Venta'])}</div>",
        unsafe_allow_html=True
    )

    key_qty = f"qty_{i}"
    if key_qty not in st.session_state:
        st.session_state[key_qty] = 1

    # Fila compacta REAL
    c1, c2, c3, c4 = st.columns([0.7, 1.0, 0.7, 2.0], gap="small")

    with c1:
        if st.button("➖", key=f"menos_{i}"):
            if st.session_state[key_qty] > 1:
                st.session_state[key_qty] -= 1

    with c2:
        st.markdown(
            f"<div class='qty-box'>{st.session_state[key_qty]}</div>",
            unsafe_allow_html=True
        )

    with c3:
        if st.button("➕", key=f"mas_{i}"):
            st.session_state[key_qty] += 1

    with c4:
        if st.button("Agregar", key=f"btn{i}"):
            agregar(row["Producto"], row["Venta"], st.session_state[key_qty])
            st.toast("✅ Agregado", icon="🛒")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

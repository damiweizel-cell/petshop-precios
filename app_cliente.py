import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import urllib.parse
import base64

# =========================
# ICONO / FAVICON / PWA
# =========================
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

icono_base64 = get_base64_image("assets/icono_app.png")

st.markdown(f"""
    <link rel="icon" type="image/png" href="data:image/png;base64,{icono_base64}">
    <link rel="apple-touch-icon" href="data:image/png;base64,{icono_base64}">
    <meta name="theme-color" content="#0F172A">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Valentín Pet Food">
""", unsafe_allow_html=True)

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
    page_icon="assets/logo.png",
    layout="wide"
)

# =========================
# IMÁGENES LOCALES PRODUCTOS
# =========================
IMAGENES_PRODUCTOS = {
    "Dog Selection Criadores Adulto X 21 Kg (+3 De Regalo)": "assets/productos/dog_selection_adulto_21.jpg",
    "Dog Selection Criadores Cachorro X 21 Kg (+3 De Regalo)": "assets/productos/dog_selection_cachorro_21.jpg",
    "Ken-L Perro X 22 + 3 Kg De Regalo": "assets/productos/kenl_22_3.jpg",
    "Matute X 20 Kg +2kg De Regalo": "assets/productos/matute_20_2.jpg",
    "Nutribon Plus Perro X 20 Kg (+2 De Regalo)": "assets/productos/nutribon_plus_20.jpg",
    "Top Nutrition Ad Mediano X 15kg (+3 De Regalo)": "assets/productos/top_nutrition_15.jpg",
    "Old Prince Equilibrium Ad Med Y Large X 20 Kg +3kg De Regalo": "assets/productos/old_prince_equilibrium_20.jpg",
    "Voraz Ad X 22kg (+3 De Regalo)": "assets/productos/voraz_22.jpg",
    "Pedigree Cachorro X 21 Kg (+3 De Regalo)": "assets/productos/pedigree_cachorro_21.jpg",
    "Cat Chow Ad Pescado X 15 Kg +3kg Gratis": "assets/productos/cat_chow_pescado_15.jpg",
    "Pro Plan Cat Adulto X 15 Kg": "assets/productos/proplan_cat_15.jpg",
    "Royal Canin Medium Adulto X 15 Kg": "assets/productos/royal_canin_medium_15.jpg",
    "Vital Can Balanced Ad Medium B X 20 Kg +2kg De Regalo": "assets/productos/vital_can_balanced_20.jpg",
    "Vital Can Premium Ad X 20 Kg + 2 Kg Gratis": "assets/productos/vital_can_premium_20.jpg",
    "Spinomax (Pastilla) De 2 A 4 Kg": "assets/productos/spinomax_2_4.jpg",
    "Pets Protector 2 A 4 Kg": "assets/productos/pets_protector_2_4.jpg",
}

# =========================
# ESTILOS
# =========================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top center, rgba(59,130,246,0.18) 0%, rgba(15,23,42,0) 40%),
            linear-gradient(180deg, #0B1120 0%, #0F172A 45%, #111827 100%);
        color: #F8FAFC;
    }

    .main .block-container {
        max-width: 1220px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #F8FAFC;
    }

    /* HEADER SUPERIOR */
    .top-header {
        background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.96) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 16px 38px rgba(0,0,0,0.32);
    }

    .brand-title {
        font-size: 42px;
        font-weight: 900;
        line-height: 1.05;
        color: #F8FAFC;
        margin-bottom: 6px;
    }

    .brand-subtitle {
        font-size: 20px;
        font-weight: 600;
        color: #CBD5E1;
    }

    /* HERO */
    .hero-box {
        background:
            radial-gradient(circle at top right, rgba(96,165,250,0.28) 0%, rgba(0,0,0,0) 35%),
            linear-gradient(135deg, rgba(37,99,235,0.18) 0%, rgba(15,23,42,0.95) 40%, rgba(30,41,59,0.96) 100%);
        border: 1px solid rgba(147,197,253,0.25);
        border-radius: 34px;
        padding: 28px;
        margin-bottom: 18px;
        box-shadow: 0 20px 44px rgba(0,0,0,0.34);
    }

    .hero-title {
        font-size: 46px;
        font-weight: 900;
        line-height: 1.05;
        color: #F8FAFC;
        margin-bottom: 14px;
    }

    .hero-text {
        font-size: 23px;
        line-height: 1.45;
        color: #E2E8F0;
        margin-bottom: 24px;
    }

    .hero-mini {
        font-size: 17px;
        color: #93C5FD;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .hero-img-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 28px;
        padding: 14px;
    }

    /* BANNER INFO */
    .info-banner {
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
        border-radius: 20px;
        padding: 16px 18px;
        margin-bottom: 18px;
        font-size: 17px;
        font-weight: 800;
        color: white;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
    }

    /* CARDS PEQUEÑAS */
    .mini-card {
        background: linear-gradient(180deg, rgba(30,41,59,0.96) 0%, rgba(15,23,42,0.98) 100%);
        border: 1px solid rgba(147,197,253,0.12);
        border-radius: 22px;
        padding: 18px 18px;
        box-shadow: 0 12px 28px rgba(0,0,0,0.24);
        min-height: 110px;
    }

    .mini-card-title {
        font-size: 24px;
        font-weight: 900;
        color: #F8FAFC;
        margin-bottom: 6px;
    }

    .mini-card-text {
        font-size: 16px;
        color: #CBD5E1;
        line-height: 1.4;
    }

    /* TÍTULOS */
    .titulo-seccion {
        font-size: 28px;
        font-weight: 900;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    /* PRODUCTOS */
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

    /* CARRITO */
    .carrito-item {
        background: linear-gradient(180deg, #1F2937 0%, #111827 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.24);
    }

    .carrito-total {
        background: linear-gradient(135deg, #14532D 0%, #166534 100%);
        border-radius: 24px;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        box-shadow: 0 12px 26px rgba(22, 101, 52, 0.30);
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

    /* INPUTS */
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

    /* BOTONES */
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
        background: linear-gradient(135deg, #F59E0B 0%, #FB923C 100%) !important;
        color: #111827 !important;
        box-shadow: 0 12px 24px rgba(245,158,11,0.28) !important;
        text-decoration: none !important;
    }

    /* LABELS */
    label, .stTextInput label {
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #E2E8F0 !important;
    }

    /* RESPONSIVE */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.7rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-bottom: 2rem;
        }

        .brand-title {
            font-size: 28px;
        }

        .brand-subtitle {
            font-size: 16px;
        }

        .hero-title {
            font-size: 30px;
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
# HEADER SUPERIOR
# =========================
st.markdown('<div class="top-header">', unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 4.5])

with col1:
    try:
        st.image("assets/logo.png", width=120)
    except:
        st.write("🐾")

with col2:
    st.markdown('<div class="brand-title">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HERO PRINCIPAL
# =========================
st.markdown('<div class="hero-box">', unsafe_allow_html=True)

hero1, hero2 = st.columns([1.25, 1])

with hero1:
    st.markdown('<div class="hero-mini">🐾 Tienda online • Pedidos simples • Atención rápida</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Todo para perros y gatos</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-text">Alimentos, accesorios, higiene y más, con atención rápida y pedidos simples por WhatsApp.</div>',
        unsafe_allow_html=True
    )

    st.link_button(
        "🚚 Consultar entrega",
        f"https://wa.me/5491141645510?text={mensaje_whatsapp_consulta()}",
        use_container_width=False
    )

with hero2:
    st.markdown('<div class="hero-img-box">', unsafe_allow_html=True)
    st.image(
        "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=1200&q=80",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# INFO ACTUALIZACIÓN
# =========================
st.markdown(
    f'<div class="info-banner">🕒 Última actualización: {datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")}</div>',
    unsafe_allow_html=True
)

# =========================
# MINI CARDS
# =========================
mc1, mc2, mc3 = st.columns(3)

with mc1:
    st.markdown("""
        <div class="mini-card">
            <div class="mini-card-title">🐾 Productos</div>
            <div class="mini-card-text">Encontrá alimentos y artículos para perros y gatos.</div>
        </div>
    """, unsafe_allow_html=True)

with mc2:
    st.markdown("""
        <div class="mini-card">
            <div class="mini-card-title">🚚 Entrega</div>
            <div class="mini-card-text">Consultanos disponibilidad y tiempos de entrega.</div>
        </div>
    """, unsafe_allow_html=True)

with mc3:
    st.markdown("""
        <div class="mini-card">
            <div class="mini-card-title">💬 WhatsApp</div>
            <div class="mini-card-text">Armá tu carrito y enviá tu pedido en segundos.</div>
        </div>
    """, unsafe_allow_html=True)

# =========================
# BUSCAR + BOTONES
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

    if cantidad_total > 0:
        st.markdown("""
            <style>
                div[data-testid="column"]:nth-of-type(3) div.stButton > button {
                    background: linear-gradient(135deg, #86EFAC 0%, #22C55E 100%) !important;
                    color: #052E16 !important;
                    border: none !important;
                    box-shadow: 0 10px 22px rgba(34,197,94,0.28) !important;
                }
                div[data-testid="column"]:nth-of-type(3) div.stButton > button p,
                div[data-testid="column"]:nth-of-type(3) div.stButton > button span,
                div[data-testid="column"]:nth-of-type(3) div.stButton > button div {
                    color: #052E16 !important;
                    font-weight: 900 !important;
                }
            </style>
        """, unsafe_allow_html=True)

    if st.button(f"Carrito ({cantidad_total})", use_container_width=True):
        st.session_state["ver_carrito"] = True
        st.rerun()

# =========================
# FILTRO
# =========================
if busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False, na=False)]

df = df.sort_values("Producto")

if not busqueda:
    df = df.head(20)

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

for i, row in df.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    col_img, col1, col2, col3 = st.columns([1.2, 4.3, 1.8, 1.6])

    with col_img:
        ruta_imagen = IMAGENES_PRODUCTOS.get(row["Producto"], "")
        if ruta_imagen:
            try:
                st.image(ruta_imagen, width=95)
            except:
                st.image("https://placehold.co/100x100?text=Pet", width=95)
        else:
            st.image("https://placehold.co/100x100?text=Pet", width=95)

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

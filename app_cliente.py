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
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Valentín Pet Food - Tienda Online",
    page_icon="🐾",
    layout="wide"
)

# =========================
# MAPA DE IMÁGENES LOCALES
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
# ESTILOS MOBILE-FIRST
# =========================
st.markdown("""
    <style>
        /* ===== Fondo general ===== */
        .stApp {
            background: linear-gradient(180deg, #0F172A 0%, #111827 45%, #1E293B 100%);
            color: #F8FAFC;
        }

        .main .block-container {
            max-width: 1200px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        /* ===== Tipografía general ===== */
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: #F8FAFC;
        }

        /* ===== Header ===== */
        .header-card {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border-radius: 28px;
            padding: 22px 22px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.28);
            margin-bottom: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            position: relative;
            overflow: hidden;
        }

        .header-card::before {
            content: "🐾";
            position: absolute;
            right: 22px;
            top: 10px;
            font-size: 90px;
            opacity: 0.06;
        }

        .section-title {
            font-size: 42px;
            font-weight: 900;
            color: #F8FAFC;
            margin-bottom: 2px;
            line-height: 1.05;
        }

        .section-subtitle {
            font-size: 18px;
            color: #CBD5E1;
            font-weight: 700;
        }

        /* ===== Banner entrega ===== */
        .delivery-banner {
            background: linear-gradient(135deg, #F59E0B 0%, #FB923C 100%);
            border-radius: 22px;
            padding: 16px 18px;
            font-size: 20px;
            font-weight: 900;
            color: #111827;
            text-align: center;
            margin-bottom: 16px;
            box-shadow: 0 10px 24px rgba(245, 158, 11, 0.25);
        }

        /* ===== Banner info ===== */
        .info-banner {
            background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 18px;
            font-size: 17px;
            font-weight: 800;
            color: white;
            box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
        }

        /* ===== Títulos secciones ===== */
        .titulo-seccion {
            font-size: 20px;
            font-weight: 900;
            color: #F8FAFC;
            margin-top: 12px;
            margin-bottom: 10px;
        }

        /* ===== Cards producto ===== */
        .producto-card {
            background: linear-gradient(180deg, #1F2937 0%, #111827 100%);
            border-radius: 24px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 28px rgba(0,0,0,0.28);
        }

        .producto-nombre {
            font-size: 22px;
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

        /* ===== Carrito ===== */
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

        /* ===== Inputs ===== */
        div.stTextInput > div > div > input {
            border-radius: 18px !important;
            background: #F8FAFC !important;
            color: #111827 !important;
            border: none !important;
            min-height: 52px;
            font-size: 17px !important;
        }

        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 16px !important;
            min-height: 50px !important;
            font-size: 16px !important;
        }

        /* ===== Botones ===== */
        div.stButton > button {
            border-radius: 18px !important;
            font-weight: 900 !important;
            padding: 0.80rem 1rem !important;
            border: none !important;
            min-height: 52px !important;
            font-size: 16px !important;
        }

        div[data-testid="stLinkButton"] a {
            border-radius: 18px !important;
            font-weight: 900 !important;
            min-height: 54px !important;
            font-size: 17px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* ===== Labels ===== */
        label, .stSelectbox label, .stTextInput label {
            font-size: 16px !important;
            font-weight: 800 !important;
            color: #E2E8F0 !important;
        }

        /* ===== Responsive móvil ===== */
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 0.8rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
                padding-bottom: 2rem;
            }

            .section-title {
                font-size: 32px;
            }

            .section-subtitle {
                font-size: 16px;
            }

            .producto-nombre {
                font-size: 20px;
            }

            .precio-cliente {
                font-size: 26px;
                min-width: 135px;
            }

            .delivery-banner {
                font-size: 18px;
                padding: 14px 16px;
            }

            .info-banner {
                font-size: 15px;
            }

            .carrito-total-value {
                font-size: 34px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# ZONA HORARIA
# =========================
zona = pytz.timezone("America/Argentina/Buenos_Aires")

# =========================
# SESSION STATE
# =========================
if "cliente_productos_cacheados" not in st.session_state:
    st.session_state["cliente_productos_cacheados"] = []

if "cliente_ultima_actualizacion" not in st.session_state:
    st.session_state["cliente_ultima_actualizacion"] = None

if "cliente_reglas" not in st.session_state:
    st.session_state["cliente_reglas"] = obtener_reglas_iniciales()

if "cliente_seleccionados" not in st.session_state:
    st.session_state["cliente_seleccionados"] = []

if "cliente_ver_carrito" not in st.session_state:
    st.session_state["cliente_ver_carrito"] = False

# =========================
# FUNCIONES CARRITO
# =========================
def agregar_al_carrito(producto, venta, cantidad):
    cantidad = int(cantidad)

    for item in st.session_state["cliente_seleccionados"]:
        if item["Producto"] == producto:
            item["Cantidad"] += cantidad
            return

    st.session_state["cliente_seleccionados"].append({
        "Producto": producto,
        "Venta": int(venta),
        "Cantidad": cantidad
    })


def quitar_del_carrito(producto):
    st.session_state["cliente_seleccionados"] = [
        x for x in st.session_state["cliente_seleccionados"] if x["Producto"] != producto
    ]


def total_items_carrito():
    return sum(item["Cantidad"] for item in st.session_state["cliente_seleccionados"])


def generar_mensaje_whatsapp(items):
    if not items:
        return ""

    lineas = ["Hola, necesito hacer un pedido:", ""]
    total = 0

    for item in items:
        subtotal = item["Cantidad"] * item["Venta"]
        total += subtotal
        lineas.append(
            f"- {item['Cantidad']} x {item['Producto']} = {formato_pesos(subtotal)}"
        )

    lineas.append("")
    lineas.append(f"TOTAL DEL PEDIDO: {formato_pesos(total)}")

    return "\n".join(lineas)

# =========================
# CARGA DE PRODUCTOS
# =========================
if not st.session_state["cliente_productos_cacheados"]:
    productos = obtener_productos_proveedor()
    st.session_state["cliente_productos_cacheados"] = productos
    st.session_state["cliente_ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")

productos = st.session_state["cliente_productos_cacheados"]

# =========================
# CALCULAR PRECIOS
# =========================
for p in productos:
    _, venta = calcular_precio_venta(
        p["Costo"],
        p["Peso"],
        st.session_state["cliente_reglas"]
    )
    p["Venta"] = venta

df = pd.DataFrame(productos)

# =========================
# HEADER
# =========================
st.markdown('<div class="header-card">', unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    try:
        st.image("assets/logo.png", width=120)
    except:
        st.write("🐾")

with col_titulo:
    st.markdown('<div class="section-title">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Tienda Online</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="delivery-banner">🚚 Consultar tiempo de entrega</div>', unsafe_allow_html=True)

if st.session_state["cliente_ultima_actualizacion"]:
    st.markdown(
        f'<div class="info-banner">🕒 Última actualización: {st.session_state["cliente_ultima_actualizacion"]}</div>',
        unsafe_allow_html=True
    )

# =========================
# BUSCADOR + ACCIONES
# =========================
col1, col2, col3 = st.columns([3.2, 1.1, 1.1])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.session_state["cliente_productos_cacheados"] = []
        st.rerun()

with col3:
    cantidad_total = total_items_carrito()

    if cantidad_total > 0:
        st.markdown("""
            <style>
                div[data-testid="column"]:nth-of-type(3) div.stButton > button {
                    background: linear-gradient(135deg, #86EFAC 0%, #22C55E 100%) !important;
                    color: #052E16 !important;
                    border: none !important;
                    box-shadow: 0 10px 22px rgba(34,197,94,0.28) !important;
                }
            </style>
        """, unsafe_allow_html=True)

    if st.button(f"Carrito ({cantidad_total})", use_container_width=True):
        st.session_state["cliente_ver_carrito"] = True
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
if st.session_state["cliente_ver_carrito"]:
    st.markdown('<div class="titulo-seccion">🛒 Mi carrito</div>', unsafe_allow_html=True)

    if not st.session_state["cliente_seleccionados"]:
        st.info("Todavía no agregaste productos.")

    else:
        total_general = 0

        for idx, item in enumerate(st.session_state["cliente_seleccionados"]):
            subtotal = item["Cantidad"] * item["Venta"]
            total_general += subtotal

            st.markdown('<div class="carrito-item">', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([4.5, 1.3, 1.5, 1])

            with col1:
                st.write(f"**{item['Producto']}**")
                st.caption(f"Precio unitario: {formato_pesos(item['Venta'])}")
                st.write(f"Subtotal: **{formato_pesos(subtotal)}**")

            with col2:
                nueva_cantidad = st.number_input(
                    "Cant.",
                    min_value=1,
                    step=1,
                    value=item["Cantidad"],
                    key=f"cliente_cant_{idx}"
                )
                item["Cantidad"] = nueva_cantidad

            with col3:
                st.write("")
                st.write("")
                st.write(f"**{formato_pesos(subtotal)}**")

            with col4:
                st.write("")
                st.write("")
                if st.button("❌", key=f"cliente_del_{idx}"):
                    quitar_del_carrito(item["Producto"])
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="carrito-total">
                <div class="carrito-total-label">TOTAL DEL PEDIDO</div>
                <div class="carrito-total-value">{formato_pesos(total_general)}</div>
            </div>
        """, unsafe_allow_html=True)

        mensaje = generar_mensaje_whatsapp(st.session_state["cliente_seleccionados"])
        mensaje_codificado = urllib.parse.quote(mensaje)

        whatsapp_url = f"https://wa.me/5491141645510?text={mensaje_codificado}"
        st.link_button("📲 Enviar pedido", whatsapp_url, use_container_width=True)

    colv1, colv2 = st.columns(2)

    with colv1:
        if st.button("⬅️ Volver al catálogo", use_container_width=True):
            st.session_state["cliente_ver_carrito"] = False
            st.rerun()

    with colv2:
        if st.button("🗑 Vaciar carrito", use_container_width=True):
            st.session_state["cliente_seleccionados"] = []
            st.rerun()

    st.stop()

# =========================
# CATÁLOGO CLIENTE
# =========================
st.markdown('<div class="titulo-seccion">🐶🐱 Productos destacados</div>', unsafe_allow_html=True)

for i, row in df.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    col_img, col1, col2, col3 = st.columns([1.2, 4.2, 1.8, 1.6])

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
        cantidad = st.selectbox(
            "Cant.",
            options=[1, 2, 3, 4, 5, 6],
            index=0,
            key=f"cantidad_producto_{i}"
        )

        if st.button("Agregar", key=f"agregar_cliente_{i}", use_container_width=True):
            agregar_al_carrito(row["Producto"], row["Venta"], cantidad)
            st.toast("✅ Producto agregado")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

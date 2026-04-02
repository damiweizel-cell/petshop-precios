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
# ESTILOS VISUALES
# =========================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #F8FAFC 0%, #EEF6FF 45%, #F1F5F9 100%);
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        .header-card {
            background: linear-gradient(135deg, #DBEAFE 0%, #EFF6FF 100%);
            border-radius: 30px;
            padding: 26px 30px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.06);
            margin-bottom: 20px;
            border: 1px solid #BFDBFE;
            position: relative;
            overflow: hidden;
        }

        .header-card::before {
            content: "🐾 🐾 🐾";
            position: absolute;
            right: 26px;
            top: 18px;
            font-size: 34px;
            opacity: 0.10;
        }

        .section-title {
            font-size: 46px;
            font-weight: 900;
            color: #0F172A;
            margin-bottom: 2px;
            line-height: 1.1;
        }

        .section-subtitle {
            font-size: 20px;
            color: #475569;
            font-weight: 700;
        }

        .delivery-banner {
            background: linear-gradient(135deg, #FEF3C7 0%, #FFF7ED 100%);
            border: 1px solid #FCD34D;
            border-radius: 22px;
            padding: 16px 22px;
            font-size: 22px;
            font-weight: 900;
            color: #92400E;
            text-align: center;
            margin-bottom: 18px;
            box-shadow: 0 8px 20px rgba(245, 158, 11, 0.10);
        }

        .info-banner {
            background: linear-gradient(135deg, #DBEAFE 0%, #EAF3FF 100%);
            border-radius: 20px;
            padding: 18px 22px;
            border: 1px solid #BFDBFE;
            margin-bottom: 18px;
            font-size: 18px;
            font-weight: 700;
            color: #1D4ED8;
        }

        .producto-card {
            background: white;
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 18px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 10px 24px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }

        .producto-nombre {
            font-size: 24px;
            font-weight: 900;
            color: #111827;
            line-height: 1.25;
            margin-bottom: 8px;
        }

        .precio-cliente {
            font-size: 32px;
            font-weight: 900;
            color: #15803D;
            background-color: #DCFCE7;
            padding: 12px 18px;
            border-radius: 18px;
            text-align: center;
            display: inline-block;
            min-width: 160px;
            box-shadow: 0 6px 16px rgba(34,197,94,0.18);
        }

        .carrito-item {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        }

        .carrito-total {
            background: #ECFDF5;
            border: 2px solid #22C55E;
            border-radius: 22px;
            padding: 22px;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 24px rgba(34,197,94,0.12);
        }

        .carrito-total-label {
            font-size: 15px;
            font-weight: 800;
            color: #166534;
        }

        .carrito-total-value {
            font-size: 42px;
            font-weight: 900;
            color: #14532D;
        }

        .carrito-destacado {
            background: linear-gradient(135deg, #DCFCE7 0%, #F0FDF4 100%);
            border: 2px solid #22C55E;
            color: #166534 !important;
            font-weight: 900 !important;
            box-shadow: 0 8px 18px rgba(34,197,94,0.15);
        }

        .subtle-label {
            font-size: 15px;
            font-weight: 700;
            color: #64748B;
            margin-bottom: 4px;
        }

        div.stButton > button {
            border-radius: 16px;
            font-weight: 800;
            padding: 0.75rem 1rem;
            border: none;
        }

        div.stTextInput > div > div > input {
            border-radius: 16px;
            background: white;
            color: #111827 !important;
            border: 1px solid #CBD5E1;
        }

        div[data-testid="stNumberInput"] input {
            border-radius: 14px !important;
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

if "cliente_nombre" not in st.session_state:
    st.session_state["cliente_nombre"] = ""

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


def generar_mensaje_whatsapp(items, nombre_cliente):
    if not items:
        return ""

    lineas = [f"Hola soy {nombre_cliente} y necesito hacerte el siguiente pedido:", ""]
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

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        st.image("assets/logo.png", width=155)
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
col1, col2, col3 = st.columns([3.2, 1, 1])

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
                    background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%) !important;
                    color: #166534 !important;
                    border: 2px solid #22C55E !important;
                    font-weight: 900 !important;
                    box-shadow: 0 8px 18px rgba(34,197,94,0.15) !important;
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
    st.header("🛒 Mi carrito")

    if not st.session_state["cliente_seleccionados"]:
        st.info("Todavía no agregaste productos.")

    else:
        total_general = 0

        st.markdown("### 👤 Tus datos")
        nombre_cliente = st.text_input(
            "Nombre",
            value=st.session_state["cliente_nombre"],
            placeholder="Escribí tu nombre",
            key="nombre_cliente_input"
        )
        st.session_state["cliente_nombre"] = nombre_cliente

        st.markdown("### 📦 Resumen del pedido")

        for idx, item in enumerate(st.session_state["cliente_seleccionados"]):
            subtotal = item["Cantidad"] * item["Venta"]
            total_general += subtotal

            st.markdown('<div class="carrito-item">', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([5, 1.3, 1.6, 1])

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

        nombre_valido = nombre_cliente.strip() != ""

        if not nombre_valido:
            st.warning("⚠️ Para enviar el pedido, primero completá tu nombre.")

        mensaje = generar_mensaje_whatsapp(
            st.session_state["cliente_seleccionados"],
            nombre_cliente.strip()
        )
        mensaje_codificado = urllib.parse.quote(mensaje)

        # Tu número de WhatsApp
        whatsapp_url = f"https://wa.me/5491141645510?text={mensaje_codificado}"

        if nombre_valido:
            st.link_button("📲 Enviar pedido", whatsapp_url, use_container_width=True)
        else:
            st.button("📲 Enviar pedido", disabled=True, use_container_width=True)

    colv1, colv2 = st.columns(2)

    with colv1:
        if st.button("⬅️ Volver al catálogo", use_container_width=True):
            st.session_state["cliente_ver_carrito"] = False
            st.rerun()

    with colv2:
        if st.button("🗑 Vaciar carrito", use_container_width=True):
            st.session_state["cliente_seleccionados"] = []
            st.session_state["cliente_nombre"] = ""
            st.rerun()

    st.stop()

# =========================
# CATÁLOGO CLIENTE
# =========================
st.header("🐶🐱 Productos destacados")

for i, row in df.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    col_img, col1, col2, col3 = st.columns([1.3, 4.6, 1.9, 1.5])

    with col_img:
        ruta_imagen = IMAGENES_PRODUCTOS.get(row["Producto"], "")
        if ruta_imagen:
            try:
                st.image(ruta_imagen, width=100)
            except:
                st.image("https://placehold.co/100x100?text=Pet", width=100)
        else:
            st.image("https://placehold.co/100x100?text=Pet", width=100)

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
            st.toast(f"✅ {row['Producto']} agregado al carrito")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

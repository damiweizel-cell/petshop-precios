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
    page_title="Valentín Pet Food",
    page_icon="🐾",
    layout="wide"
)

# =========================
# ESTILOS VISUALES
# =========================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #F0F9FF 0%, #F8FAFC 35%, #F3F4F6 100%);
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        .header-card {
            background: linear-gradient(135deg, #E0F2FE 0%, #F8FAFC 100%);
            border-radius: 28px;
            padding: 28px 32px;
            box-shadow: 0 10px 28px rgba(0,0,0,0.06);
            margin-bottom: 24px;
            border: 1px solid #DBEAFE;
            position: relative;
            overflow: hidden;
        }

        .header-card::before {
            content: "🐾 🐾 🐾";
            position: absolute;
            right: 28px;
            top: 18px;
            font-size: 34px;
            opacity: 0.10;
        }

        .section-title {
            font-size: 46px;
            font-weight: 900;
            color: #0F172A;
            margin-bottom: 6px;
            line-height: 1.1;
        }

        .section-subtitle {
            font-size: 18px;
            color: #475569;
            font-weight: 500;
        }

        .venta-destacada {
            font-size: 30px;
            font-weight: 900;
            color: #15803D;
            background-color: #DCFCE7;
            padding: 12px 16px;
            border-radius: 16px;
            text-align: center;
            display: inline-block;
            min-width: 140px;
            box-shadow: 0 4px 12px rgba(34,197,94,0.18);
        }

        .dato-secundario {
            font-size: 15px;
            color: #6B7280;
            font-weight: 600;
            text-align: center;
        }

        .producto-nombre {
            font-size: 20px;
            font-weight: 800;
            color: #111827;
            line-height: 1.3;
        }

        .producto-card {
            background: white;
            border-radius: 20px;
            padding: 18px 20px;
            margin-bottom: 16px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        }

        .carrito-item {
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 14px;
        }

        div.stButton > button {
            border-radius: 14px;
            font-weight: 700;
            padding: 0.65rem 1rem;
            border: none;
        }

        div.stTextInput > div > div > input {
            border-radius: 16px;
            background: white;
            color: #111827 !important;
            border: 1px solid #D1D5DB;
        }

        .bloque-reglas {
            background: white;
            border-radius: 20px;
            padding: 20px;
            border: 1px solid #E5E7EB;
            margin-bottom: 24px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        }

        .carrito-total {
            background: #ECFDF5;
            border: 2px solid #22C55E;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        .carrito-total-label {
            font-size: 15px;
            font-weight: 700;
            color: #166534;
        }

        .carrito-total-value {
            font-size: 38px;
            font-weight: 900;
            color: #14532D;
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
if "usuario" not in st.session_state:
    st.session_state["usuario"] = "carolinak"

if "password" not in st.session_state:
    st.session_state["password"] = "caro100"

if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if "productos_cacheados" not in st.session_state:
    st.session_state["productos_cacheados"] = []

if "ultima_actualizacion" not in st.session_state:
    st.session_state["ultima_actualizacion"] = None

if "reglas" not in st.session_state:
    st.session_state["reglas"] = obtener_reglas_iniciales()

if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = []

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

if "mostrar_reglas" not in st.session_state:
    st.session_state["mostrar_reglas"] = False

# =========================
# LOGIN
# =========================
def pantalla_login():
    st.markdown("## 🔐 Iniciar sesión")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if usuario == st.session_state["usuario"] and password == st.session_state["password"]:
            st.session_state["logueado"] = True
            st.rerun()
        else:
            st.error("Datos incorrectos")

if not st.session_state["logueado"]:
    pantalla_login()
    st.stop()

# =========================
# FUNCIONES CARRITO
# =========================
def agregar_al_carrito(producto, venta):
    for item in st.session_state["seleccionados"]:
        if item["Producto"] == producto:
            item["Cantidad"] += 1
            return

    st.session_state["seleccionados"].append({
        "Producto": producto,
        "Venta": int(venta),
        "Cantidad": 1
    })


def quitar_del_carrito(producto):
    st.session_state["seleccionados"] = [
        x for x in st.session_state["seleccionados"] if x["Producto"] != producto
    ]


def generar_mensaje_whatsapp(items):
    if not items:
        return ""

    lineas = []
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
if not st.session_state["productos_cacheados"]:
    productos = obtener_productos_proveedor()
    st.session_state["productos_cacheados"] = productos
    st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")

productos = st.session_state["productos_cacheados"]

# =========================
# CALCULAR PRECIOS
# =========================
for p in productos:
    ganancia, venta = calcular_precio_venta(
        p["Costo"],
        p["Peso"],
        st.session_state["reglas"]
    )
    p["Ganancia"] = ganancia
    p["Venta"] = venta

df = pd.DataFrame(productos)

# =========================
# HEADER
# =========================
st.markdown('<div class="header-card">', unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        st.image("assets/logo.png", width=150)
    except:
        st.write("🐾")

with col_titulo:
    st.markdown('<div class="section-title">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Sistema de precios automático</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["ultima_actualizacion"]:
    st.info(f"🕒 Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# BUSCADOR + ACCIONES
# =========================
col1, col2, col3, col4 = st.columns([2.5, 1, 1, 1])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Actualizar"):
        st.cache_data.clear()
        st.session_state["productos_cacheados"] = []
        st.rerun()

with col3:
    if st.button("Reglas"):
        st.session_state["mostrar_reglas"] = not st.session_state["mostrar_reglas"]

with col4:
    if st.button(f"Carrito ({len(st.session_state['seleccionados'])})"):
        st.session_state["ver_carrito"] = True
        st.rerun()

# =========================
# SECCIÓN REGLAS
# =========================
if st.session_state["mostrar_reglas"]:
    st.markdown('<div class="bloque-reglas">', unsafe_allow_html=True)
    st.subheader("⚙️ Reglas de cálculo de venta")

    reglas_editadas = st.data_editor(
        st.session_state["reglas"],
        num_rows="dynamic",
        use_container_width=True
    )

    if st.button("Guardar reglas"):
        st.session_state["reglas"] = reglas_editadas.copy()
        st.success("Reglas guardadas correctamente")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FILTRO
# =========================
if busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False, na=False)]

df = df.sort_values("Producto")

# Mostrar solo 20 si no hay búsqueda
if not busqueda:
    df = df.head(20)

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.header("🛒 Carrito")

    if not st.session_state["seleccionados"]:
        st.info("El carrito está vacío.")

    else:
        total_general = 0

        for idx, item in enumerate(st.session_state["seleccionados"]):
            subtotal = item["Cantidad"] * item["Venta"]
            total_general += subtotal

            st.markdown('<div class="carrito-item">', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([5, 1.2, 1.5, 1])

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
                    key=f"cant_{idx}"
                )
                item["Cantidad"] = nueva_cantidad

            with col3:
                st.write("")
                st.write("")
                st.write(f"**{formato_pesos(subtotal)}**")

            with col4:
                st.write("")
                st.write("")
                if st.button("❌", key=f"del_{idx}"):
                    quitar_del_carrito(item["Producto"])
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="carrito-total">
                <div class="carrito-total-label">TOTAL DEL PEDIDO</div>
                <div class="carrito-total-value">{formato_pesos(total_general)}</div>
            </div>
        """, unsafe_allow_html=True)

        mensaje = generar_mensaje_whatsapp(st.session_state["seleccionados"])
        mensaje_codificado = urllib.parse.quote(mensaje)
        whatsapp_url = f"https://wa.me/?text={mensaje_codificado}"

        st.link_button("📲 Enviar mensaje por WhatsApp", whatsapp_url, use_container_width=True)

    colv1, colv2 = st.columns(2)

    with colv1:
        if st.button("⬅️ Volver al catálogo", use_container_width=True):
            st.session_state["ver_carrito"] = False
            st.rerun()

    with colv2:
        if st.button("🗑 Vaciar carrito", use_container_width=True):
            st.session_state["seleccionados"] = []
            st.rerun()

    st.stop()

# =========================
# CATÁLOGO
# =========================
st.header("📦 Productos")

for i, row in df.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([5, 1, 1.3, 1.3, 1.8])

    with col1:
        st.markdown(f"<div class='producto-nombre'>{row['Producto']}</div>", unsafe_allow_html=True)

    with col2:
        st.write(f"{row['Peso']} kg")

    with col3:
        st.markdown(
            f"<div class='dato-secundario'>Costo<br><strong>{formato_pesos(row['Costo'])}</strong></div>",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"<div class='dato-secundario'>Ganancia<br><strong>{formato_pesos(row['Ganancia'])}</strong></div>",
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            f"<div class='venta-destacada'>{formato_pesos(row['Venta'])}</div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Agregar", key=i):
        agregar_al_carrito(row["Producto"], row["Venta"])
        st.toast("Agregado al carrito")

    st.markdown('</div>', unsafe_allow_html=True)

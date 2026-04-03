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
        /* =========================
           FONDO GENERAL
        ========================= */
        .stApp {
            background: linear-gradient(180deg, #0F172A 0%, #132238 35%, #1E293B 100%);
        }

        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 1320px;
        }

        /* =========================
           HEADER
        ========================= */
        .header-card {
            background: transparent;
            border-radius: 0;
            padding: 0;
            margin-bottom: 18px;
            border: none;
            box-shadow: none;
        }

        .section-title {
            font-size: 30px;
            font-weight: 800;
            color: #F8FAFC;
            margin-top: 8px;
            margin-bottom: 4px;
            line-height: 1.15;
            text-align: center;
        }

        .section-subtitle {
            font-size: 15px;
            color: #CBD5E1;
            font-weight: 500;
            text-align: center;
            margin-bottom: 8px;
        }

        /* =========================
           INFO Y TEXTOS
        ========================= */
        .stAlert {
            border-radius: 14px !important;
        }

        .stInfo {
            background-color: rgba(191, 219, 254, 0.18) !important;
            color: #E0F2FE !important;
            border: 1px solid rgba(147, 197, 253, 0.25) !important;
        }

        h1, h2, h3, h4, h5, h6, label, p {
        color: #F8FAFC;
        }

        /* Texto general */
        .stMarkdown, .stText, .stCaption {
        color: #F8FAFC !important;
        }

        /* =========================
           INPUTS / BOTONES
        ========================= */
        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            padding: 0.55rem 0.9rem;
            border: none;
            background-color: #F8FAFC;
            color: #0F172A;
        }

        div.stButton > button:hover {
            background-color: #E2E8F0;
            color: #0F172A;
        }

        div.stTextInput > div > div > input {
            border-radius: 14px;
            background: #F8FAFC;
            color: #111827 !important;
            border: 1px solid #CBD5E1;
        }

        /* =========================
   BOTONES - TEXTO VISIBLE
========================= */
div.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    padding: 0.55rem 0.9rem;
    border: none;
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}

div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: #0F172A !important;
}

div.stButton > button:hover {
    background-color: #E2E8F0 !important;
    color: #0F172A !important;
}

div.stButton > button:hover p,
div.stButton > button:hover span,
div.stButton > button:hover div {
    color: #0F172A !important;
}

/* LINK BUTTON (WhatsApp, etc.) */
a[data-testid="stLinkButton"] {
    background-color: #25D366 !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    text-align: center !important;
    padding: 0.75rem 1rem !important;
    text-decoration: none !important;
}

a[data-testid="stLinkButton"] * {
    color: white !important;
}

/* BOTONES DEL HEADER */
button[kind="secondary"] {
    color: #0F172A !important;
}

/* DATA EDITOR / INPUTS / CAMPOS */
input, textarea {
    color: #111827 !important;
}

/* NUMBER INPUT */
div[data-baseweb="input"] input {
    color: #111827 !important;
}

/* BOTONES CHICOS Y TEXTO INTERNO */
button * {
    color: inherit !important;
}

        /* =========================
           REGLAS
        ========================= */
        .bloque-reglas {
            background: rgba(255,255,255,0.06);
            border-radius: 18px;
            padding: 18px;
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }

        /* =========================
           CARRITO
        ========================= */
        .carrito-item {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 10px;
        }

        .carrito-total {
            background: #DCFCE7;
            border: 2px solid #22C55E;
            border-radius: 18px;
            padding: 18px;
            text-align: center;
            margin-top: 18px;
            margin-bottom: 18px;
        }

        .carrito-total-label {
            font-size: 14px;
            font-weight: 700;
            color: #166534;
        }

        .carrito-total-value {
            font-size: 34px;
            font-weight: 900;
            color: #14532D;
        }

        /* =========================
           PRODUCTOS TIPO LISTA
        ========================= */
        .producto-row {
    padding: 6px 0;
    display: flex;
    align-items: center;
}

.producto-nombre {
    font-size: 16px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.2;
    margin-bottom: 2px;
}

.dato-secundario {
    font-size: 13px;
    color: #CBD5E1;
    font-weight: 600;
    text-align: center;
    white-space: nowrap;
}

.venta-destacada {
    font-size: 17px;
    font-weight: 900;
    color: #166534;
    background-color: #DCFCE7;
    padding: 8px 12px;
    border-radius: 12px;
    text-align: center;
    display: inline-block;
    min-width: 95px;
    box-shadow: 0 4px 10px rgba(34,197,94,0.18);
    white-space: nowrap;
}

.linea-producto {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.12);
    margin: 4px 0 6px 0;
}

/* Encabezados mini tipo planilla */
.col-header {
    font-size: 12px;
    font-weight: 700;
    color: #93C5FD;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 8px;
}

/* Responsive celular */
@media (max-width: 768px) {
    .producto-nombre {
        font-size: 14px;
    }

    .dato-secundario {
        font-size: 12px;
    }

    .venta-destacada {
        font-size: 15px;
        min-width: 88px;
        padding: 7px 10px;
    }

    .col-header {
        font-size: 11px;
    }
}

        /* =========================
           RESPONSIVE CELULAR
        ========================= */
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 0.5rem;
                padding-bottom: 1rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            .section-title {
                font-size: 24px;
            }

            .section-subtitle {
                font-size: 13px;
            }

            .producto-nombre {
                font-size: 16px;
            }

            .dato-secundario {
                font-size: 12px;
            }

            .venta-destacada {
                font-size: 16px;
                min-width: 95px;
                padding: 8px 12px;
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
if "logueado" not in st.session_state:
    st.session_state["logueado"] = True

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

try:
    st.image("assets/logo.png", use_container_width=True)
except:
    st.write("🐾")

st.markdown('<div class="section-title">Valentín Pet Food</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Sistema de precios automático</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["ultima_actualizacion"]:
    st.info(f"🕒 Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# BUSCADOR + ACCIONES
# =========================
col1, col2, col3, col4 = st.columns([2.8, 1, 1, 1])

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

# Encabezado tipo lista / planilla
col1, col2, col3, col4, col5 = st.columns([5.5, 1.5, 1.5, 1.8, 1.4])

with col1:
    st.markdown("<div class='col-header'>Descripción</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='col-header'>Costo</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='col-header'>Ganancia</div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='col-header'>Venta</div>", unsafe_allow_html=True)
with col5:
    st.markdown("<div class='col-header'>Acción</div>", unsafe_allow_html=True)

st.markdown('<hr class="linea-producto">', unsafe_allow_html=True)

for i, row in df.iterrows():
    st.markdown('<div class="producto-row">', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([5.5, 1.5, 1.5, 1.8, 1.4])

    with col1:
        st.markdown(
            f"<div class='producto-nombre'>{row['Producto']}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='dato-secundario'>{row['Peso']} kg</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"<div class='dato-secundario'><strong>{formato_pesos(row['Costo'])}</strong></div>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"<div class='dato-secundario'><strong>{formato_pesos(row['Ganancia'])}</strong></div>",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"<div class='venta-destacada'>{formato_pesos(row['Venta'])}</div>",
            unsafe_allow_html=True
        )

    with col5:
        if st.button("Agregar", key=i):
            agregar_al_carrito(row["Producto"], row["Venta"])
            st.toast("Agregado al carrito")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="linea-producto">', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math
from datetime import datetime
import pytz

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Valentín Pet Food",
    page_icon="🐾",
    layout="wide"
)

# =========================
# ZONA HORARIA ARGENTINA
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

if "mostrar_cambio" not in st.session_state:
    st.session_state["mostrar_cambio"] = False

if "ultima_actualizacion" not in st.session_state:
    st.session_state["ultima_actualizacion"] = None

if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = []

if "mostrar_reglas" not in st.session_state:
    st.session_state["mostrar_reglas"] = False

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

if "mostrar_mensaje_final" not in st.session_state:
    st.session_state["mostrar_mensaje_final"] = False

# =========================
# LOGIN SIMPLE
# =========================
def pantalla_login():
    st.markdown("## 🔐 Iniciar sesión")
    st.write("Ingresá con tu usuario y contraseña para acceder a la app.")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    col_login1, col_login2 = st.columns([1, 4])

    with col_login1:
        if st.button("Ingresar", use_container_width=True):
            if usuario == st.session_state["usuario"] and password == st.session_state["password"]:
                st.session_state["logueado"] = True
                st.success("Ingreso correcto")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def pantalla_cambiar_password():
    st.markdown("### 🔑 Cambiar contraseña")

    actual = st.text_input("Contraseña actual", type="password", key="clave_actual")
    nueva = st.text_input("Nueva contraseña", type="password", key="clave_nueva")

    if st.button("Guardar nueva contraseña"):
        if actual == st.session_state["password"]:
            st.session_state["password"] = nueva
            st.success("Contraseña actualizada correctamente")
        else:
            st.error("La contraseña actual es incorrecta")

# =========================
# BLOQUEO DE ACCESO
# =========================
if not st.session_state["logueado"]:
    pantalla_login()
    st.stop()

# =========================
# FUNCIONES AUXILIARES
# =========================
def formato_pesos(valor):
    return f"$ {int(valor):,}".replace(",", ".")

def redondear_a_1000_superior(valor):
    return math.ceil(valor / 1000) * 1000

def obtener_margen(peso, reglas_df):
    for _, regla in reglas_df.iterrows():
        if peso >= regla["Desde kg"] and peso < regla["Hasta kg"]:
            return regla["Incremento"]
    return 0

def calcular_precio_venta(costo, peso, reglas_df):
    margen_regla = obtener_margen(peso, reglas_df)
    venta_base = costo + margen_regla
    venta_redondeada = redondear_a_1000_superior(venta_base)
    ganancia_real = venta_redondeada - costo
    return ganancia_real, venta_redondeada

def extraer_peso(nombre_producto):
    nombre = nombre_producto.lower().replace(",", ".")

    patrones = [
        r"x\s*(\d+(?:\.\d+)?)\s*kg",
        r"x\s*(\d+(?:\.\d+)?)\s*k",
        r"(\d+(?:\.\d+)?)\s*kg",
        r"(\d+(?:\.\d+)?)\s*k"
    ]

    for patron in patrones:
        match = re.search(patron, nombre)
        if match:
            try:
                return float(match.group(1))
            except:
                return 0.0

    return 0.0

@st.cache_data(ttl=3600)
def obtener_productos_proveedor():
    url = "https://animalshop.ennube.ar/lista/mayor/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    texto = soup.get_text("\n")

    lineas = [line.strip() for line in texto.split("\n") if line.strip()]

    productos = []
    i = 0

    while i < len(lineas) - 1:
        nombre = lineas[i]
        precio = lineas[i + 1]

        if re.match(r"^\$\s?\d[\d\.]*$", precio):
            nombre_limpio = nombre.strip()
            precio_limpio = precio.replace("$", "").replace(" ", "").replace(".", "")

            try:
                costo = int(precio_limpio)
                peso = extraer_peso(nombre_limpio)

                if len(nombre_limpio) > 5 and not nombre_limpio.upper() == nombre_limpio:
                    productos.append({
                        "Producto": nombre_limpio,
                        "Peso": peso,
                        "Costo": costo,
                        "Estado": "Actualizado"
                    })
            except:
                pass

            i += 2
        else:
            i += 1

    vistos = set()
    productos_unicos = []

    for p in productos:
        clave = (p["Producto"], p["Costo"])
        if clave not in vistos:
            vistos.add(clave)
            productos_unicos.append(p)

    return productos_unicos

def agregar_producto_seleccionado(producto, venta):
    item = {"Producto": producto, "Venta": int(venta)}
    if item not in st.session_state["seleccionados"]:
        st.session_state["seleccionados"].append(item)

def quitar_producto_seleccionado(producto):
    st.session_state["seleccionados"] = [
        x for x in st.session_state["seleccionados"] if x["Producto"] != producto
    ]

def generar_mensaje_multiple(items):
    if not items:
        return ""

    lineas = ["Hola 😊 Te paso los productos consultados:", ""]
    for item in items:
        lineas.append(f"🐾 {item['Producto']} - {formato_pesos(item['Venta'])}")

    return "\n".join(lineas)

# =========================
# ESTILOS PERSONALIZADOS
# =========================
st.markdown("""
    <style>
        .stApp {
            background-color: #F6F8FB;
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        .header-card {
            background: white;
            border-radius: 20px;
            padding: 24px 28px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.06);
            margin-bottom: 25px;
        }

        .producto-card {
            background: white;
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.05);
            margin-bottom: 16px;
            border: 1px solid #E5E7EB;
        }

        .producto-nombre {
            font-size: 22px;
            font-weight: 700;
            color: #1F2937;
            margin-bottom: 4px;
        }

        .producto-meta {
            font-size: 15px;
            color: #6B7280;
        }

        .badge-aumento {
            display: inline-block;
            background-color: #FEF3C7;
            color: #B45309;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 600;
        }

        .badge-normal {
            display: inline-block;
            background-color: #E5E7EB;
            color: #374151;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 600;
        }

        .mini-box {
            background: #F9FAFB;
            border-radius: 14px;
            padding: 12px 16px;
            text-align: center;
            border: 1px solid #E5E7EB;
            min-height: 92px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .mini-label {
            font-size: 13px;
            color: #6B7280;
            margin-bottom: 4px;
        }

        .mini-value {
            font-size: 20px;
            font-weight: 700;
            color: #1F2937;
        }

        .margen-box {
            background: #FFF7ED;
            border: 1px solid #FDBA74;
            border-radius: 14px;
            padding: 12px 16px;
            text-align: center;
            min-height: 92px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .margen-label {
            font-size: 13px;
            color: #9A3412;
            margin-bottom: 4px;
        }

        .margen-value {
            font-size: 20px;
            font-weight: 700;
            color: #9A3412;
        }

        .venta-box {
            background: #E8F5E9;
            border: 2px solid #4CAF50;
            border-radius: 16px;
            padding: 12px 16px;
            text-align: center;
            min-height: 92px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .venta-label {
            font-size: 13px;
            color: #2E7D32;
            margin-bottom: 4px;
        }

        .venta-value {
            font-size: 30px;
            font-weight: 800;
            color: #1B5E20;
        }

        .section-title {
            font-size: 48px;
            font-weight: 800;
            color: #1F2937;
            margin-bottom: 6px;
        }

        .section-subtitle {
            font-size: 20px;
            color: #6B7280;
        }

        .catalog-title {
            font-size: 30px;
            font-weight: 800;
            color: #1F2937;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .carrito-card {
            background: white;
            border-radius: 18px;
            padding: 22px 24px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid #E5E7EB;
        }

        .carrito-item {
            background: #F9FAFB;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 12px;
            border: 1px solid #E5E7EB;
        }

        .total-box {
            background: #E8F5E9;
            border: 2px solid #4CAF50;
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            margin-top: 15px;
            margin-bottom: 20px;
        }

        .total-label {
            font-size: 14px;
            color: #2E7D32;
            margin-bottom: 6px;
        }

        .total-value {
            font-size: 32px;
            font-weight: 800;
            color: #1B5E20;
        }

        div.stButton > button {
            border-radius: 14px;
            font-weight: 600;
            padding: 0.65rem 1rem;
        }

        div.stTextInput > div > div > input {
            border-radius: 14px;
        }

        textarea {
            border-radius: 14px !important;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# DATOS DEL PROVEEDOR
# =========================
try:
    productos = obtener_productos_proveedor()
    if productos and st.session_state.get("ultima_actualizacion") is None:
        st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")
except Exception as e:
    st.error(f"No se pudo cargar la lista del proveedor: {e}")
    productos = []

reglas_iniciales = pd.DataFrame([
    {"Desde kg": 1.0, "Hasta kg": 2.0, "Incremento": 2000},
    {"Desde kg": 3.0, "Hasta kg": 5.0, "Incremento": 3000},
    {"Desde kg": 7.5, "Hasta kg": 14.0, "Incremento": 4000},
    {"Desde kg": 15.0, "Hasta kg": 999.0, "Incremento": 6000},
])

if "reglas" not in st.session_state:
    st.session_state["reglas"] = reglas_iniciales.copy()

# =========================
# CALCULAR PRECIOS
# =========================
for p in productos:
    ganancia_real, venta = calcular_precio_venta(p["Costo"], p["Peso"], st.session_state["reglas"])
    p["Ganancia"] = ganancia_real
    p["Venta"] = venta

df_productos = pd.DataFrame(productos)

if df_productos.empty:
    st.warning("No se encontraron productos del proveedor.")

# =========================
# HEADER
# =========================
st.markdown('<div class="header-card">', unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        st.image("assets/logo.png", width=200)
    except:
        st.write("🐾")

with col_titulo:
    st.markdown('<div class="section-title">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Sistema de actualización automática de precios</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ÚLTIMA ACTUALIZACIÓN
# =========================
if st.session_state.get("ultima_actualizacion"):
    st.info(f"🕒 Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# ACCIONES PRINCIPALES
# =========================
col1, col2, col3, col4, col5, col6 = st.columns([1.2, 2.2, 1.2, 1.2, 1.2, 1.2])

with col1:
    if st.button("🔄 Actualizar precios", use_container_width=True):
        with st.spinner("Actualizando lista de precios..."):
            st.cache_data.clear()
            st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")
        st.success("Lista del proveedor actualizada correctamente")
        st.rerun()

with col2:
    busqueda = st.text_input("🔎 Buscar producto")

with col3:
    if st.button("⚙️ Reglas", use_container_width=True):
        st.session_state["mostrar_reglas"] = not st.session_state["mostrar_reglas"]

with col4:
    if st.button("🛒 Ver carrito", use_container_width=True):
        st.session_state["ver_carrito"] = True
        st.rerun()

with col5:
    if st.button("🔑 Cambiar clave", use_container_width=True):
        st.session_state["mostrar_cambio"] = True

with col6:
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state["logueado"] = False
        st.rerun()

if st.session_state.get("mostrar_cambio", False):
    pantalla_cambiar_password()

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# FILTRO DE BÚSQUEDA
# =========================
if busqueda:
    df_productos = df_productos[df_productos["Producto"].str.contains(busqueda, case=False, na=False)]

# =========================
# SECCIÓN REGLAS
# =========================
if st.session_state["mostrar_reglas"]:
    st.markdown("### ⚙️ Reglas de cálculo de venta")
    st.write("Editá los rangos de peso y el incremento fijo que querés aplicar.")

    reglas_editadas = st.data_editor(
        st.session_state["reglas"],
        num_rows="dynamic",
        use_container_width=True
    )

    if st.button("💾 Guardar reglas"):
        st.session_state["reglas"] = reglas_editadas.copy()
        st.success("Reglas guardadas correctamente")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

# =========================
# PANTALLA CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.markdown('<div class="carrito-card">', unsafe_allow_html=True)
    st.markdown("## 🛒 Carrito de productos")

    if st.session_state["seleccionados"]:
        total = sum([item["Venta"] for item in st.session_state["seleccionados"]])

        for idx, item in enumerate(st.session_state["seleccionados"]):
            st.markdown('<div class="carrito-item">', unsafe_allow_html=True)

            col_item1, col_item2 = st.columns([5, 1])

            with col_item1:
                st.write(f"**{item['Producto']}**")
                st.write(f"💲 {formato_pesos(item['Venta'])}")

            with col_item2:
                if st.button("❌", key=f"del_{idx}", use_container_width=True):
                    quitar_producto_seleccionado(item["Producto"])
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="total-box">
                <div class="total-label">TOTAL ESTIMADO</div>
                <div class="total-value">{formato_pesos(total)}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Generar mensaje", use_container_width=True):
            st.session_state["mostrar_mensaje_final"] = True

        if st.session_state["mostrar_mensaje_final"]:
            mensaje_final = generar_mensaje_multiple(st.session_state["seleccionados"])

            st.text_area(
                "Mensaje listo para WhatsApp:",
                value=mensaje_final,
                height=220,
                key="mensaje_final_area"
            )

            st.download_button(
                "📄 Descargar mensaje",
                data=mensaje_final,
                file_name="mensaje_whatsapp.txt",
                mime="text/plain",
                use_container_width=True
            )

    else:
        st.info("El carrito está vacío.")

    st.markdown("<br>", unsafe_allow_html=True)

    col_back1, col_back2 = st.columns(2)

    with col_back1:
        if st.button("⬅️ Volver al catálogo", use_container_width=True):
            st.session_state["ver_carrito"] = False
            st.session_state["mostrar_mensaje_final"] = False
            st.rerun()

    with col_back2:
        if st.button("🗑 Vaciar carrito", use_container_width=True):
            st.session_state["seleccionados"] = []
            st.session_state["mostrar_mensaje_final"] = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =========================
# CATÁLOGO
# =========================
st.markdown('<div class="catalog-title">📦 Catálogo</div>', unsafe_allow_html=True)

for i, row in df_productos.iterrows():
    badge_class = "badge-aumento" if row["Estado"] == "Aumentó" else "badge-normal"

    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3.2, 1.1, 1.4, 1.6, 1.6, 2.0])

    with col_a:
        st.markdown(f'<div class="producto-nombre">{row["Producto"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="producto-meta">Alimento balanceado</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
            <div class="mini-box">
                <div class="mini-label">Peso</div>
                <div class="mini-value">{row["Peso"]} kg</div>
            </div>
        """, unsafe_allow_html=True)

    with col_c:
        st.markdown(f"""
            <div style="text-align:center; padding-top:18px;">
                <span class="{badge_class}">{row["Estado"]}</span>
            </div>
        """, unsafe_allow_html=True)

    with col_d:
        st.markdown(f"""
            <div class="mini-box">
                <div class="mini-label">Costo</div>
                <div class="mini-value">{formato_pesos(row["Costo"])}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_e:
        st.markdown(f"""
            <div class="margen-box">
                <div class="margen-label">Ganancia</div>
                <div class="margen-value">{formato_pesos(row["Ganancia"])}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_f:
        st.markdown(f"""
            <div class="venta-box">
                <div class="venta-label">Venta</div>
                <div class="venta-value">{formato_pesos(row["Venta"])}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    mensaje = f"🐾 {row['Producto']}\n💲 Precio: {formato_pesos(row['Venta'])}"

    col_msg1, col_msg2, col_msg3 = st.columns([1.3, 1.3, 3.4])

    with col_msg1:
        if st.button("➕ Agregar", key=f"agregar_{i}", use_container_width=True):
            agregar_producto_seleccionado(row["Producto"], row["Venta"])
            st.toast(f"Agregado al carrito: {row['Producto']}")

    with col_msg2:
        if st.button("📋 Individual", key=f"copiar_{i}", use_container_width=True):
            st.session_state[f"mostrar_mensaje_{i}"] = True

    with col_msg3:
        if st.session_state.get(f"mostrar_mensaje_{i}", False):
            st.text_area(
                "Copiá este texto y pegalo en WhatsApp:",
                value=mensaje,
                height=85,
                key=f"mensaje_{i}"
            )

    st.markdown('</div>', unsafe_allow_html=True)

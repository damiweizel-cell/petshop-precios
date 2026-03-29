import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Valentín Pet Food",
    page_icon="🐾",
    layout="wide"
)
# =========================
# LOGIN SIMPLE
# =========================
if "usuario" not in st.session_state:
    st.session_state["usuario"] = "carolinak"

if "password" not in st.session_state:
    st.session_state["password"] = "caro100"

if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if "mostrar_cambio" not in st.session_state:
    st.session_state["mostrar_cambio"] = False

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
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Valentín Pet Food",
    page_icon="🐾",
    layout="wide"
)

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
    """
    Intenta detectar automáticamente el peso desde el nombre del producto.
    Ejemplos:
    - X 15 Kg
    - X15kg
    - X 7,5 Kg
    - X 1.5 Kg
    """
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

    response = requests.get(url, headers=headers, timeout=30)
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

        div.stButton > button {
            border-radius: 14px;
            font-weight: 600;
            padding: 0.65rem 1rem;
        }

        div.stTextInput > div > div > input {
            border-radius: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# DATOS REALES DEL PROVEEDOR
# =========================
try:
    productos = obtener_productos_proveedor()
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

if "mostrar_reglas" not in st.session_state:
    st.session_state["mostrar_reglas"] = False

# =========================
# CALCULAR VENTAS Y MÁRGENES
# =========================
for p in productos:
    ganancia_real, venta = calcular_precio_venta(p["Costo"], p["Peso"], st.session_state["reglas"])
    p["Ganancia"] = ganancia_real
    p["Venta"] = venta

df_productos = pd.DataFrame(productos)

if df_productos.empty:
    st.warning("No se encontraron productos del proveedor.")

# =========================
# HEADER CON LOGO
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
# ACCIONES PRINCIPALES
# =========================
col1, col2, col3, col4, col5 = st.columns([1.2, 2.4, 1.2, 1.2, 1.2])
with col4:
    if st.button("🔑 Cambiar clave", use_container_width=True):
        st.session_state["mostrar_cambio"] = True
if st.session_state.get("mostrar_cambio", False):
    pantalla_cambiar_password()

with col1:
    if st.button("🔄 Actualizar precios", use_container_width=True):
        st.cache_data.clear()
        st.success("Lista del proveedor actualizada correctamente")
        st.rerun()

with col2:
    busqueda = st.text_input("🔎 Buscar producto")

with col3:
    if st.button("⚙️ Reglas", use_container_width=True):
        st.session_state["mostrar_reglas"] = not st.session_state["mostrar_reglas"]

st.markdown("<br>", unsafe_allow_html=True)

with col5:
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state["logueado"] = False
        st.rerun()

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
# CATÁLOGO
# =========================
st.markdown('<div class="catalog-title">📦 Catálogo</div>', unsafe_allow_html=True)

for i, row in df_productos.iterrows():
    badge_class = "badge-aumento" if row["Estado"] == "Aumentó" else "badge-normal"

    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    # Ahora mostramos: producto + peso + estado + costo + margen + venta
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

    col_msg1, col_msg2 = st.columns([1.2, 4])

    with col_msg1:
        if st.button("📋 Preparar mensaje", key=f"copiar_{i}", use_container_width=True):
            st.session_state[f"mostrar_mensaje_{i}"] = True

    with col_msg2:
        if st.session_state.get(f"mostrar_mensaje_{i}", False):
            st.text_area(
                "Copiá este texto y pegalo en WhatsApp:",
                value=mensaje,
                height=85,
                key=f"mensaje_{i}"
            )

    st.markdown('</div>', unsafe_allow_html=True)
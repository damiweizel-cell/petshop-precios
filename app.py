import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import urllib.parse
import json
import os

from pricing_engine import (
    formato_pesos,
    calcular_precio_venta,
    obtener_reglas_iniciales,
    extraer_peso
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
# ARCHIVO DE PERSISTENCIA
# =========================
ARCHIVO_ESTADO = "estado_app.json"

def guardar_estado():
    estado = {
        "productos_cacheados": st.session_state.get("productos_cacheados", []),
        "precios_anteriores": st.session_state.get("precios_anteriores", {}),
        "ultima_actualizacion": st.session_state.get("ultima_actualizacion"),
        "productos_aumentados": st.session_state.get("productos_aumentados", []),
        "hubo_aumento": st.session_state.get("hubo_aumento", False),
        "productos_mostrados": st.session_state.get("productos_mostrados", []),
        "historial_aumentos": st.session_state.get("historial_aumentos", []),
        "reglas": st.session_state.get("reglas").to_dict(orient="records")
        if isinstance(st.session_state.get("reglas"), pd.DataFrame)
        else []
    }

    with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def cargar_estado():
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# =========================
# CACHE DE PRODUCTOS
# =========================
@st.cache_data(ttl=60)
def cargar_productos():
    return obtener_productos_proveedor()

# =========================
# ESTILOS VISUALES
# =========================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(180deg, #E5E7EB 0%, #D1D5DB 45%, #C7CDD4 100%);
        }

        .main .block-container {
            padding-top: 0.8rem;
            padding-bottom: 1rem;
            max-width: 1320px;
        }

        .header-card {
            background: transparent;
            border-radius: 0;
            padding: 0;
            margin-bottom: 18px;
            border: none;
            box-shadow: none;
        }

        .section-title {
            font-size: 42px;
            font-weight: 900;
            color: #111827;
            margin-top: 8px;
            margin-bottom: 4px;
            line-height: 1.1;
            text-align: center;
        }

        .section-subtitle {
            font-size: 16px;
            color: #374151;
            font-weight: 600;
            text-align: center;
            margin-bottom: 12px;
        }

        .stAlert {
            border-radius: 14px !important;
        }

        .stInfo {
            background-color: rgba(59, 130, 246, 0.10) !important;
            color: #1E3A8A !important;
            border: 1px solid rgba(59, 130, 246, 0.20) !important;
        }

        h1, h2, h3, h4, h5, h6, label, p {
            color: #111827;
        }

        .stMarkdown, .stText, .stCaption {
            color: #111827 !important;
        }

        div.stTextInput > div > div > input {
            border-radius: 14px;
            background: #FFFFFF;
            color: #111827 !important;
            border: 1px solid #9CA3AF;
        }

        input, textarea {
            color: #111827 !important;
        }

        div[data-baseweb="input"] input {
            color: #111827 !important;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            padding: 0.45rem 0.75rem;
            border: none;
            background-color: #1F2937 !important;
            color: #FFFFFF !important;
            width: auto !important;
            min-width: auto !important;
            white-space: nowrap;
        }

        div.stButton > button p,
        div.stButton > button span,
        div.stButton > button div {
            color: #FFFFFF !important;
        }

        div.stButton > button:hover {
            background-color: #374151 !important;
            color: #FFFFFF !important;
        }

        div.stButton > button:hover p,
        div.stButton > button:hover span,
        div.stButton > button:hover div {
            color: #FFFFFF !important;
        }

        button[kind="secondary"] {
            color: #FFFFFF !important;
        }

        button * {
            color: inherit !important;
        }

        a.boton-enviar-fijo,
        a.boton-enviar-fijo:visited,
        a.boton-enviar-fijo:hover,
        a.boton-enviar-fijo:active {
            background: #25D366 !important;
            color: #FFFFFF !important;
            text-decoration: none !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            padding: 8px 14px !important;
            border-radius: 10px !important;
            display: inline-block !important;
            text-align: center !important;
            min-width: 72px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.10) !important;
        }

        .bloque-reglas {
            background: rgba(255,255,255,0.65);
            border-radius: 18px;
            padding: 18px;
            border: 1px solid rgba(0,0,0,0.06);
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        .carrito-item {
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(0,0,0,0.06);
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

        .bloque-aumento {
            background: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 14px;
            padding: 12px 14px;
            margin-bottom: 14px;
        }

        .titulo-aumento {
            color: #B91C1C;
            font-weight: 900;
            font-size: 18px;
            margin-bottom: 4px;
        }

        .texto-aumento {
            color: #7F1D1D;
            font-size: 14px;
            font-weight: 600;
        }

        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 0.4rem;
                padding-bottom: 1rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            .section-title {
                font-size: 34px;
            }

            .section-subtitle {
                font-size: 14px;
            }    
/* =========================
   BOTÓN EXPORTAR (DOWNLOAD)
========================= */
div[data-testid="stDownloadButton"] button {
    color: #000000 !important;
}

div[data-testid="stDownloadButton"] button span {
    color: #000000 !important;
}

div[data-testid="stDownloadButton"] button p {
    color: #000000 !important;
}

        /* =========================
   NUMBER INPUT CARRITO
========================= */
div[data-baseweb="input"] input[type="number"] {
    color: #FFFFFF !important;
    background-color: #1F2937 !important;
    caret-color: #FFFFFF !important;
}

div[data-baseweb="input"] input {
    color: #FFFFFF !important;
    caret-color: #FFFFFF !important;
}

/* =========================
   TOAST / MENSAJE FLOTANTE
========================= */
[data-testid="stToast"] {
    background-color: #1F2937 !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
}

[data-testid="stToast"] * {
    color: #FFFFFF !important;
}
/* =========================
   FIX DEFINITIVO EXPORTAR
========================= */
div[data-testid="stDownloadButton"] button,
div[data-testid="stDownloadButton"] button *,
div[data-testid="stDownloadButton"] button span,
div[data-testid="stDownloadButton"] button p {
    color: #000000 !important;
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
if "estado_cargado" not in st.session_state:
    estado_guardado = cargar_estado()

    if estado_guardado:
        st.session_state["productos_cacheados"] = estado_guardado.get("productos_cacheados", [])
        st.session_state["precios_anteriores"] = estado_guardado.get("precios_anteriores", {})
        st.session_state["ultima_actualizacion"] = estado_guardado.get("ultima_actualizacion")
        st.session_state["productos_aumentados"] = estado_guardado.get("productos_aumentados", [])
        st.session_state["hubo_aumento"] = estado_guardado.get("hubo_aumento", False)
        st.session_state["productos_mostrados"] = estado_guardado.get("productos_mostrados", [])
        st.session_state["historial_aumentos"] = estado_guardado.get("historial_aumentos", [])

        reglas_guardadas = estado_guardado.get("reglas", [])
        if reglas_guardadas:
            st.session_state["reglas"] = pd.DataFrame(reglas_guardadas)
        else:
            st.session_state["reglas"] = obtener_reglas_iniciales()
    else:
        st.session_state["productos_cacheados"] = []
        st.session_state["precios_anteriores"] = {}
        st.session_state["ultima_actualizacion"] = None
        st.session_state["productos_aumentados"] = []
        st.session_state["hubo_aumento"] = False
        st.session_state["productos_mostrados"] = []
        st.session_state["reglas"] = obtener_reglas_iniciales()

    st.session_state["estado_cargado"] = True

if "logueado" not in st.session_state:
    st.session_state["logueado"] = True

if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = []

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

if "mostrar_reglas" not in st.session_state:
    st.session_state["mostrar_reglas"] = False

if "ver_historial" not in st.session_state:
    st.session_state["ver_historial"] = False

if "historial_aumentos" not in st.session_state:
    st.session_state["historial_aumentos"] = []

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
        lineas.append(f"{item['Cantidad']} uni de {item['Producto']}")
        lineas.append(f"Precio unitario: {formato_pesos(item['Venta'])}")
        lineas.append("")

    lineas.append(f"TOTAL DEL PEDIDO: {formato_pesos(total)}")

    return "\n".join(lineas)


def generar_mensaje_producto(producto, venta):
    mensaje = f"1 uni de {producto}\nPrecio unitario: {formato_pesos(venta)}"
    return urllib.parse.quote(mensaje)

def exportar_productos_csv(productos):
    if not productos:
        return None

    df_export = pd.DataFrame(productos).copy()

    columnas_deseadas = ["Producto", "Costo", "Ganancia", "Venta", "Aumento"]
    columnas_presentes = [c for c in columnas_deseadas if c in df_export.columns]
    df_export = df_export[columnas_presentes]

    df_export = df_export.rename(columns={
        "Producto": "Producto",
        "Costo": "Precio Costo",
        "Ganancia": "Margen / Ganancia",
        "Venta": "Precio Venta",
        "Aumento": "Aumentó"
    })

    return df_export.to_csv(
        index=False,
        sep=";",                 # 🔥 CLAVE
        encoding="utf-8-sig"     # 🔥 para Excel (acentos bien)
    ).encode("utf-8-sig")

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Productos")

        ws = writer.sheets["Productos"]

        # Ajustar ancho de columnas
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter

            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass

            ws.column_dimensions[col_letter].width = max_length + 3

    output.seek(0)
    return output
# =========================
# HEADER
# =========================
st.markdown('<div class="header-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Valentín Pet Food</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Sistema de precios automático</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["ultima_actualizacion"]:
    st.info(f"🕒 Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# BUSCADOR + ACCIONES
# =========================
col1, col2, col3, col4, col5, col6 = st.columns([3.2, 1, 1, 1, 1.2, 1.5])

with col1:
    busqueda = st.text_input("Buscar producto")

with col2:
    if st.button("Reglas"):
        st.session_state["mostrar_reglas"] = not st.session_state["mostrar_reglas"]

with col3:
    if st.button("Actualizar"):
        precios_previos = {}
        for p in st.session_state["productos_cacheados"]:
            if "Producto" in p and "Venta" in p:
                precios_previos[p["Producto"]] = p["Venta"]

        st.session_state["precios_anteriores"] = precios_previos

        cargar_productos.clear()
        productos = cargar_productos()

        productos_aumentados = []

        for p in productos:
            p["Aumento"] = False
        
            peso = extraer_peso(p["Producto"])
        
            ganancia, venta = calcular_precio_venta(
                p["Costo"],
                peso,
                st.session_state["reglas"]
            )
        
            # VALIDACIÓN ÚNICA Y CORRECTA
            if (
                peso < 1
                or venta is None
                or venta <= p["Costo"]
            ):
                p["Ganancia"] = "-"
                p["Venta"] = "A consultar"
            else:
                p["Ganancia"] = ganancia
                p["Venta"] = venta
        
                precio_anterior = st.session_state["precios_anteriores"].get(p["Producto"], None)
        
                if precio_anterior is not None and venta > precio_anterior:
                    p["Aumento"] = True
                    productos_aumentados.append(p)
        
                    porcentaje = ((venta - precio_anterior) / precio_anterior) * 100
        
                    st.session_state["historial_aumentos"].append({
                        "fecha": datetime.now(zona).strftime("%d/%m/%Y %H:%M"),
                        "producto": p["Producto"],
                        "costo_anterior": precio_anterior,
                        "costo_actual": venta,
                        "porcentaje": round(porcentaje, 2)
                    })

        st.session_state["productos_cacheados"] = productos
        st.session_state["productos_aumentados"] = productos_aumentados
        st.session_state["hubo_aumento"] = len(productos_aumentados) > 0
        st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")

        if len(productos_aumentados) > 0:
            st.session_state["productos_mostrados"] = productos_aumentados
        else:
            productos_old_prince = [
                p for p in productos
                if "OLD PRINCE" in str(p["Producto"]).upper()
            ]
            st.session_state["productos_mostrados"] = productos_old_prince

        guardar_estado()
        st.rerun()

with col4:
    if st.button(f"Carrito ({len(st.session_state['seleccionados'])})"):
        st.session_state["ver_carrito"] = True
        st.rerun()

with col5:
    archivo_csv = exportar_productos_csv(st.session_state["productos_cacheados"])

    if archivo_csv:
        st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] button {
            background-color: #E5E7EB !important;
        }
        div[data-testid="stDownloadButton"] button span {
            color: #000000 !important;
            font-weight: 700;
        }
        </style>
        """, unsafe_allow_html=True)

        st.download_button(
            label="📥 Exportar",
            data=archivo_csv,
            file_name="listado_productos_valentin_pet_food.csv",
            mime="text/csv"
        )

with col6:
    if st.button("Historial de aumentos"):
        st.session_state["ver_historial"] = True
        st.rerun()

# =========================
# ALERTA DE AUMENTOS
# =========================
if st.session_state["hubo_aumento"]:
    st.warning("⚠️ Hubo aumentos")

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
        guardar_estado()
        st.success("Reglas guardadas correctamente")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# HISTORIAL DE AUMENTOS
# =========================
if st.session_state["ver_historial"]:

    st.markdown(
        "<h2 style='color:#111827;'>📊 Historial de aumentos (últimos 5 días)</h2>",
        unsafe_allow_html=True
    )

    historial = st.session_state["historial_aumentos"]

    if not historial:
        st.info("No hay aumentos registrados.")

    else:
        df_hist = pd.DataFrame(historial)

        df_hist = df_hist.sort_values("fecha", ascending=True)

        df_hist = df_hist.rename(columns={
            "fecha": "Fecha",
            "producto": "Producto",
            "costo_anterior": "Costo Anterior",
            "costo_actual": "Nuevo Costo",
            "porcentaje": "% de Aumento"
        })

        st.dataframe(df_hist, use_container_width=True)

    if st.button("⬅️ Volver al catálogo", use_container_width=True):
        st.session_state["ver_historial"] = False
        st.rerun()

    st.stop()

# =========================
# DATAFRAME A MOSTRAR
# =========================
if busqueda and busqueda.strip() != "":
    df = pd.DataFrame(st.session_state["productos_cacheados"])
else:
    if st.session_state["productos_mostrados"]:
        df = pd.DataFrame(st.session_state["productos_mostrados"])
    else:
        df = pd.DataFrame()

# =========================
# FILTRO
# =========================
if not df.empty and busqueda:
    df = df[df["Producto"].str.contains(busqueda, case=False, na=False)]

# =========================
# ORDEN Y LIMITE
# =========================
if not df.empty:
    df = df.sort_values("Producto")
    df = df.head(30)

# =========================
# CARRITO
# =========================
if st.session_state["ver_carrito"]:
    st.markdown("<h2 style='color:#111827;'>🛒 Carrito</h2>", unsafe_allow_html=True)

    if not st.session_state["seleccionados"]:
        st.info("El carrito está vacío.")
    else:
        total_general = 0

        for idx, item in enumerate(st.session_state["seleccionados"]):
            subtotal = item["Cantidad"] * item["Venta"]
            total_general += subtotal

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
                st.write(f"**{formato_pesos(subtotal)}**")

            with col4:
                if st.button("❌", key=f"del_{item['Producto']}"):
                    quitar_del_carrito(item["Producto"])
                    st.rerun()

        st.write(f"### TOTAL: {formato_pesos(total_general)}")

        # ✅ BOTÓN WHATSAPP (SOLO SI HAY PRODUCTOS)
        mensaje = generar_mensaje_whatsapp(st.session_state["seleccionados"])
        mensaje_encoded = urllib.parse.quote(mensaje)

        link = f"https://wa.me/?text={mensaje_encoded}"

        st.markdown(
            f'<a href="{link}" target="_blank" class="boton-enviar-fijo">Enviar pedido por WhatsApp</a>',
            unsafe_allow_html=True
        )

    if st.button("Volver"):
        st.session_state["ver_carrito"] = False
        st.rerun()

    st.stop()
    
# =========================
# CATÁLOGO
# =========================
st.markdown("<h2 style='color:#111827;'>📦 Productos</h2>", unsafe_allow_html=True)

if df.empty:
    st.info("No hay productos para mostrar.")
else:
    for _, row in df.iterrows():
        st.write(f"**{row['Producto']}**")
        st.write(f"Costo: {formato_pesos(row['Costo'])}")
        venta = row["Venta"]

        if isinstance(venta, (int, float)):
            venta_mostrar = formato_pesos(venta)
        else:
            venta_mostrar = "A consultar"
        
        st.write(f"Venta: {venta_mostrar}")

        colA, colB = st.columns([1,1])

        with colA:
            if st.button("Agregar", key=f"add_{row['Producto']}"):
                agregar_al_carrito(row["Producto"], row["Venta"])
                st.success("Agregado al carrito")

        with colB:
            if isinstance(row["Venta"], (int, float)):
                mensaje = generar_mensaje_producto(row["Producto"], row["Venta"])
                link = f"https://wa.me/?text={mensaje}"
            
                st.markdown(
                    f'<a href="{link}" target="_blank" class="boton-enviar-fijo">Enviar</a>',
                    unsafe_allow_html=True
                )
            else:
                st.button("Enviar", disabled=True)
            
                st.markdown(
                    f'<a href="{link}" target="_blank" class="boton-enviar-fijo">Enviar</a>',
                    unsafe_allow_html=True
                )

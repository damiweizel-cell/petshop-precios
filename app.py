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
        "reglas": st.session_state.get("reglas").to_dict(orient="records")
        if isinstance(st.session_state.get("reglas"), pd.DataFrame)
        else [],
        # 🔥 NUEVO
        "historial_aumentos": st.session_state.get("historial_aumentos", [])
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
# 🔥 NUEVO SESSION STATE
# =========================
if "historial_aumentos" not in st.session_state:
    st.session_state["historial_aumentos"] = []

if "ver_historial" not in st.session_state:
    st.session_state["ver_historial"] = False

# =========================
# ESTILOS VISUALES
# =========================
st.markdown("""
<style>
button[data-testid="baseButton-secondary"] {
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ZONA HORARIA
# =========================
zona = pytz.timezone("America/Argentina/Buenos_Aires")

# =========================
# SESSION STATE ORIGINAL
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
        st.session_state["historial_aumentos"] = []
        st.session_state["reglas"] = obtener_reglas_iniciales()

    st.session_state["estado_cargado"] = True

# =========================
# HEADER
# =========================
st.title("Valentín Pet Food")

if st.session_state["ultima_actualizacion"]:
    st.info(f"🕒 Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# ACTUALIZAR
# =========================
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
        ganancia, venta = calcular_precio_venta(
            p["Costo"],
            p["Peso"],
            st.session_state["reglas"]
        )

        p["Ganancia"] = ganancia
        p["Venta"] = venta

        precio_anterior = st.session_state["precios_anteriores"].get(p["Producto"], None)

        if precio_anterior is not None and venta > precio_anterior:
            p["Aumento"] = True
            productos_aumentados.append(p)

            # 🔥 NUEVO HISTORIAL
            porcentaje = ((venta - precio_anterior) / precio_anterior) * 100 if precio_anterior > 0 else 0

            st.session_state["historial_aumentos"].append({
                "fecha": datetime.now(zona).strftime("%d/%m/%Y"),
                "producto": p["Producto"],
                "anterior": precio_anterior,
                "nuevo": venta,
                "porcentaje": round(porcentaje, 2)
            })

        else:
            p["Aumento"] = False

    # 🔥 FILTRO ÚLTIMOS 5 DÍAS
    fechas_validas = sorted(
        list(set([h["fecha"] for h in st.session_state["historial_aumentos"]])),
        reverse=True
    )[:5]

    st.session_state["historial_aumentos"] = [
        h for h in st.session_state["historial_aumentos"]
        if h["fecha"] in fechas_validas
    ]

    st.session_state["productos_cacheados"] = productos
    st.session_state["productos_aumentados"] = productos_aumentados
    st.session_state["hubo_aumento"] = len(productos_aumentados) > 0
    st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y - %H:%M hs")

    guardar_estado()
    st.rerun()

# =========================
# ALERTA + BOTÓN HISTORIAL
# =========================
if st.session_state["hubo_aumento"]:
    st.warning("⚠️ Hubo aumentos")

    if st.button("📊 Ver historial de aumentos"):
        st.session_state["ver_historial"] = True
        st.rerun()

# =========================
# HISTORIAL
# =========================
if st.session_state["ver_historial"]:

    st.subheader("📊 Historial de aumentos (últimos 5 días)")

    historial = st.session_state["historial_aumentos"]

    if not historial:
        st.info("No hay aumentos registrados.")
    else:
        df_hist = pd.DataFrame(historial).sort_values(
            by=["fecha", "producto"],
            ascending=[False, True]
        )

        st.dataframe(df_hist, use_container_width=True)

    if st.button("⬅️ Volver al catálogo"):
        st.session_state["ver_historial"] = False
        st.rerun()

    st.stop()

# =========================
# LISTADO
# =========================
df = pd.DataFrame(st.session_state["productos_cacheados"])

if df.empty:
    st.info("Presioná actualizar para ver productos")
else:
    st.dataframe(df, use_container_width=True)

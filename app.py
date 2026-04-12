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
        "historial_aumentos": st.session_state.get("historial_aumentos", []),  # 🔴 NUEVO
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
        st.session_state["historial_aumentos"] = estado_guardado.get("historial_aumentos", [])  # 🔴 NUEVO

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
        st.session_state["historial_aumentos"] = []  # 🔴 NUEVO
        st.session_state["reglas"] = obtener_reglas_iniciales()

    st.session_state["estado_cargado"] = True

# 🔴 NUEVOS FLAGS
if "historial_aumentos" not in st.session_state:
    st.session_state["historial_aumentos"] = []

if "ver_aumentos" not in st.session_state:
    st.session_state["ver_aumentos"] = False

if "logueado" not in st.session_state:
    st.session_state["logueado"] = True

if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = []

if "ver_carrito" not in st.session_state:
    st.session_state["ver_carrito"] = False

if "mostrar_reglas" not in st.session_state:
    st.session_state["mostrar_reglas"] = False

# =========================
# HEADER
# =========================
st.title("🐾 Valentín Pet Food")

if st.session_state["ultima_actualizacion"]:
    st.info(f"Última actualización: {st.session_state['ultima_actualizacion']}")

# =========================
# BOTONES
# =========================
col1, col2 = st.columns(2)

with col1:
    if st.button("Actualizar"):
        precios_previos = {
            p["Producto"]: p["Venta"]
            for p in st.session_state["productos_cacheados"]
            if "Producto" in p and "Venta" in p
        }

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

            precio_anterior = precios_previos.get(p["Producto"])

            if precio_anterior is not None and venta > precio_anterior:
                variacion = ((venta - precio_anterior) / precio_anterior) * 100

                aumento = {
                    "Producto": p["Producto"],
                    "Fecha": datetime.now(zona).strftime("%d/%m/%Y %H:%M"),
                    "Precio_Anterior": precio_anterior,
                    "Precio_Nuevo": venta,
                    "Variacion": round(variacion, 2)
                }

                st.session_state["historial_aumentos"].append(aumento)
                p["Aumento"] = True
                productos_aumentados.append(p)
            else:
                p["Aumento"] = False

        st.session_state["productos_cacheados"] = productos
        st.session_state["productos_aumentados"] = productos_aumentados
        st.session_state["hubo_aumento"] = len(productos_aumentados) > 0
        st.session_state["ultima_actualizacion"] = datetime.now(zona).strftime("%d/%m/%Y %H:%M")

        guardar_estado()
        st.rerun()

with col2:
    if st.session_state["hubo_aumento"]:
        if st.button("📈 Ver aumentos"):
            st.session_state["ver_aumentos"] = True
            st.rerun()

# =========================
# HISTORIAL DE AUMENTOS
# =========================
if st.session_state["ver_aumentos"]:

    st.subheader("📈 Historial de aumentos")

    historial = st.session_state["historial_aumentos"]

    if not historial:
        st.info("No hay aumentos registrados.")
    else:
        df = pd.DataFrame(historial)
        df["Fecha_dt"] = pd.to_datetime(df["Fecha"], format="%d/%m/%Y %H:%M")

        fecha_limite = datetime.now(zona) - pd.Timedelta(days=5)
        df = df[df["Fecha_dt"] >= fecha_limite]

        df = df.sort_values("Fecha_dt", ascending=False)

        st.dataframe(df[[
            "Producto",
            "Fecha",
            "Precio_Anterior",
            "Precio_Nuevo",
            "Variacion"
        ]])

    colA, colB = st.columns(2)

    with colA:
        if st.button("⬅️ Volver"):
            st.session_state["ver_aumentos"] = False
            st.rerun()

    with colB:
        if st.button("🗑 Limpiar historial"):
            st.session_state["historial_aumentos"] = []
            guardar_estado()
            st.success("Historial eliminado")
            st.rerun()

    st.stop()

# =========================
# PRODUCTOS
# =========================
st.subheader("📦 Productos")

df = pd.DataFrame(st.session_state["productos_cacheados"])

if df.empty:
    st.info("Presioná actualizar para cargar productos.")
else:
    for _, row in df.iterrows():
        nombre = row["Producto"]
        if row.get("Aumento"):
            nombre += " 🔺"

        st.write(f"**{nombre}**")
        st.write(f"Costo: {formato_pesos(row['Costo'])}")
        st.write(f"Venta: {formato_pesos(row['Venta'])}")
        st.write("---")

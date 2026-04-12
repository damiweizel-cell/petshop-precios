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

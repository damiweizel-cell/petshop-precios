import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import urllib.parse

from pricing_engine import formato_pesos, calcular_precio_venta, obtener_reglas_iniciales
from proveedor_loader import obtener_productos_proveedor

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Valentín Pet Food", page_icon="🐾", layout="wide")

# =========================
# CSS MOBILE FIRST
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0F172A 0%, #020617 100%);
    color: #F8FAFC;
}

.main .block-container {
    padding: 0.6rem 0.8rem;
}

.titulo { font-size: 24px; font-weight: 900; }
.subtitulo { font-size: 14px; color: #CBD5E1; }

.busqueda-label { font-size: 15px; font-weight: 900; }
.busqueda-ayuda { font-size: 12px; font-style: italic; color: #CBD5E1; }

div.stTextInput input {
    background: #F8FAFC !important;
    color: #111827 !important;
    border-radius: 10px !important;
    min-height: 40px !important;
}

div.stButton button {
    background: #E5E7EB !important;
    color: #111827 !important;
    border-radius: 10px !important;
    min-height: 36px !important;
    font-size: 13px !important;
    padding: 4px 6px !important;
}

.precio {
    background: linear-gradient(135deg,#86EFAC,#22C55E);
    padding: 8px 12px;
    border-radius: 12px;
    color:#052E16;
    font-weight:900;
    display:inline-block;
}

.producto-card {
    padding:6px 0;
}

hr {
    margin:6px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION
# =========================
if "productos" not in st.session_state:
    st.session_state["productos"] = obtener_productos_proveedor()

if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

if "buscar_click" not in st.session_state:
    st.session_state["buscar_click"] = False

# =========================
# FUNCIONES
# =========================
def agregar(prod, precio, cant):
    for i in st.session_state["carrito"]:
        if i["Producto"] == prod:
            i["Cantidad"] += cant
            return
    st.session_state["carrito"].append({
        "Producto": prod,
        "Precio": precio,
        "Cantidad": cant
    })

def total_items():
    return sum(i["Cantidad"] for i in st.session_state["carrito"])

# =========================
# DATOS
# =========================
reglas = obtener_reglas_iniciales()

for p in st.session_state["productos"]:
    _, venta = calcular_precio_venta(p["Costo"], p["Peso"], reglas)
    p["Venta"] = venta

df = pd.DataFrame(st.session_state["productos"])

MARCAS = ["old prince","biopet","maintenance","excellent"]

def destacado(x):
    return any(m in x.lower() for m in MARCAS)

df_dest = df[df["Producto"].apply(destacado)]

# =========================
# HEADER
# =========================
c1,c2 = st.columns([1,3])
with c1:
    st.image("assets/logo.png", width=200)
with c2:
    st.markdown('<div class="titulo">Valentín Pet Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Tu tienda online para perros y gatos</div>', unsafe_allow_html=True)

# =========================
# BUSCADOR
# =========================
st.markdown(
    '<div class="busqueda-label">Buscar producto <span class="busqueda-ayuda">escribí y tocá la lupa</span></div>',
    unsafe_allow_html=True
)

b1,b2,b3 = st.columns([4,0.8,1])

with b1:
    busqueda = st.text_input("", placeholder="Ej: Dog Chow")

with b2:
    buscar = st.button("🔎")

with b3:
    st.button(f"🛒 {total_items()}")

if buscar:
    st.session_state["buscar_click"] = True

# =========================
# RESULTADOS
# =========================
if st.session_state["buscar_click"] and busqueda:
    df_mostrar = df[df["Producto"].str.contains(busqueda, case=False)]
    st.success(f"Resultados para: {busqueda}")
else:
    df_mostrar = df_dest

# =========================
# PRODUCTOS
# =========================
for i,row in df_mostrar.iterrows():
    st.markdown('<div class="producto-card">', unsafe_allow_html=True)

    st.markdown(f"**{row['Producto']}**")
    st.markdown(f"<div class='precio'>{formato_pesos(row['Venta'])}</div>", unsafe_allow_html=True)

    key=f"q{i}"
    if key not in st.session_state:
        st.session_state[key]=1

    c1,c2,c3 = st.columns([0.7,1.2,2.1])

    with c1:
        if st.button("➖", key=f"m{i}"):
            if st.session_state[key]>1:
                st.session_state[key]-=1

    with c2:
        st.markdown(f"<div style='text-align:center;background:white;color:black;border-radius:8px'>{st.session_state[key]}</div>", unsafe_allow_html=True)

    with c3:
        sub1,sub2=st.columns([0.6,2.4])

        with sub1:
            if st.button("➕", key=f"p{i}"):
                st.session_state[key]+=1

        with sub2:
            if st.button("Agregar", key=f"a{i}"):
                agregar(row["Producto"], row["Venta"], st.session_state[key])
                st.toast("Agregado")

    st.markdown("<hr>", unsafe_allow_html=True)

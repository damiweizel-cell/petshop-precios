# =========================
# (TODO TU CÓDIGO ORIGINAL IGUAL HASTA CSS)
# =========================

st.markdown("""
<style>
/* TU CSS ORIGINAL + AGREGADO */

/* 🔴 FIX BOTÓN EXPORTAR */
div.stDownloadButton > button {
    color: #111827 !important;
    background-color: #E5E7EB !important;
    font-weight: 700;
}

div.stDownloadButton > button:hover {
    color: #111827 !important;
    background-color: #D1D5DB !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE (AGREGADO)
# =========================
if "historial_aumentos" not in st.session_state:
    st.session_state["historial_aumentos"] = []

if "ver_aumentos" not in st.session_state:
    st.session_state["ver_aumentos"] = False

# =========================
# ACTUALIZAR (MODIFICADO SOLO ESTA PARTE)
# =========================
if precio_anterior is not None and venta > precio_anterior:
    p["Aumento"] = True

    variacion = ((venta - precio_anterior) / precio_anterior) * 100

    st.session_state["historial_aumentos"].append({
        "Producto": p["Producto"],
        "Fecha": datetime.now(zona).strftime("%d/%m/%Y %H:%M"),
        "Precio_Anterior": precio_anterior,
        "Precio_Nuevo": venta,
        "Variacion": round(variacion, 2)
    })

    productos_aumentados.append(p)
else:
    p["Aumento"] = False

# =========================
# ALERTA + BOTÓN
# =========================
if st.session_state["hubo_aumento"]:
    colA, colB = st.columns([3,1])

    with colA:
        st.warning("⚠️ Hubo aumentos")

    with colB:
        if st.button("📈 Ver aumentos"):
            st.session_state["ver_aumentos"] = True
            st.rerun()

# =========================
# HISTORIAL (PANTALLA COMPLETA)
# =========================
if st.session_state["ver_aumentos"]:

    st.markdown("<h2>📈 Historial de aumentos</h2>", unsafe_allow_html=True)

    historial = st.session_state["historial_aumentos"]

    if historial:
        df = pd.DataFrame(historial)
        df["Fecha_dt"] = pd.to_datetime(df["Fecha"], format="%d/%m/%Y %H:%M")

        fecha_limite = datetime.now(zona) - pd.Timedelta(days=5)
        df = df[df["Fecha_dt"] >= fecha_limite]

        df = df.sort_values("Fecha_dt", ascending=False)

        st.dataframe(
            df[["Producto","Fecha","Precio_Anterior","Precio_Nuevo","Variacion"]],
            use_container_width=True
        )
    else:
        st.info("No hay aumentos registrados.")

    if st.button("⬅️ Volver"):
        st.session_state["ver_aumentos"] = False
        st.rerun()

    st.stop()

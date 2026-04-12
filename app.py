# =========================
# (TODO TU CÓDIGO ORIGINAL ARRIBA IGUAL)
# =========================

# 🔴 AGREGAR EN SESSION STATE (después de tus inicializaciones actuales)

if "historial_aumentos" not in st.session_state:
    st.session_state["historial_aumentos"] = []

if "ver_aumentos" not in st.session_state:
    st.session_state["ver_aumentos"] = False


# =========================
# 🔴 MODIFICAR guardar_estado()
# =========================

def guardar_estado():
    estado = {
        "productos_cacheados": st.session_state.get("productos_cacheados", []),
        "precios_anteriores": st.session_state.get("precios_anteriores", {}),
        "ultima_actualizacion": st.session_state.get("ultima_actualizacion"),
        "productos_aumentados": st.session_state.get("productos_aumentados", []),
        "hubo_aumento": st.session_state.get("hubo_aumento", False),
        "productos_mostrados": st.session_state.get("productos_mostrados", []),
        "historial_aumentos": st.session_state.get("historial_aumentos", []),  # 👈 NUEVO
        "reglas": st.session_state.get("reglas").to_dict(orient="records")
        if isinstance(st.session_state.get("reglas"), pd.DataFrame)
        else []
    }

    with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


# =========================
# 🔴 MODIFICAR cargar_estado()
# =========================

def cargar_estado():
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# 🔴 dentro del bloque donde cargás estado:

st.session_state["historial_aumentos"] = estado_guardado.get("historial_aumentos", [])


# 🔴 dentro del else (cuando no hay estado):

st.session_state["historial_aumentos"] = []


# =========================
# 🔴 MODIFICAR BLOQUE ACTUALIZAR (SOLO ESTA PARTE)
# =========================

if precio_anterior is not None and venta > precio_anterior:
    p["Aumento"] = True

    variacion = ((venta - precio_anterior) / precio_anterior) * 100

    aumento = {
        "Producto": p["Producto"],
        "Fecha": datetime.now(zona).strftime("%d/%m/%Y %H:%M"),
        "Precio_Anterior": precio_anterior,
        "Precio_Nuevo": venta,
        "Variacion": round(variacion, 2)
    }

    st.session_state["historial_aumentos"].append(aumento)
    productos_aumentados.append(p)
else:
    p["Aumento"] = False


# =========================
# 🔴 REEMPLAZAR ALERTA
# =========================

if st.session_state["hubo_aumento"]:
    colA, colB = st.columns([3,1])

    with colA:
        st.warning("⚠️ Hubo aumentos")

    with colB:
        if st.button("Ver aumentos"):
            st.session_state["ver_aumentos"] = True
            st.rerun()


# =========================
# 🔴 AGREGAR PANTALLA HISTORIAL (ANTES DEL CARRITO)
# =========================

if st.session_state.get("ver_aumentos", False):

    st.markdown(
        "<h2 style='color:#111827;'>📈 Historial de aumentos</h2>",
        unsafe_allow_html=True
    )

    historial = st.session_state.get("historial_aumentos", [])

    if not historial:
        st.info("No hay aumentos registrados.")
    else:
        df_hist = pd.DataFrame(historial)

        df_hist["Fecha_dt"] = pd.to_datetime(
            df_hist["Fecha"],
            format="%d/%m/%Y %H:%M"
        )

        fecha_limite = datetime.now(zona) - pd.Timedelta(days=5)
        df_hist = df_hist[df_hist["Fecha_dt"] >= fecha_limite]

        df_hist = df_hist.sort_values("Fecha_dt", ascending=False)

        st.dataframe(
            df_hist[
                ["Producto", "Fecha", "Precio_Anterior", "Precio_Nuevo", "Variacion"]
            ],
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Volver"):
            st.session_state["ver_aumentos"] = False
            st.rerun()

    with col2:
        if st.button("🗑 Limpiar historial"):
            st.session_state["historial_aumentos"] = []
            guardar_estado()
            st.success("Historial borrado")
            st.rerun()

    st.stop()

import math
import re
import pandas as pd


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
    venta_redondeada = redondear_a_1000_inferior(venta_base)
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


def obtener_reglas_iniciales():
    return pd.DataFrame([
        {"Desde kg": 1.0, "Hasta kg": 2.0, "Incremento": 2000},
        {"Desde kg": 3.0, "Hasta kg": 5.0, "Incremento": 3000},
        {"Desde kg": 7.5, "Hasta kg": 14.0, "Incremento": 4000},
        {"Desde kg": 15.0, "Hasta kg": 999.0, "Incremento": 6000},
    ])

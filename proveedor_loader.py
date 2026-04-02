import requests
from bs4 import BeautifulSoup
import re
from pricing_engine import extraer_peso


def obtener_productos_proveedor():
    url = "https://animalshop.ennube.ar/lista/mayor/"
    headers = {"User-Agent": "Mozilla/5.0"}

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

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from pricing_engine import extraer_peso


def obtener_productos_proveedor():
    url = "https://animalshop.ennube.ar/lista/mayor/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # =========================
    # 1) OBTENER PRODUCTOS DESDE TEXTO (más estable)
    # =========================
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

                if len(nombre_limpio) > 5:
                    productos.append({
                        "Producto": nombre_limpio,
                        "Peso": peso,
                        "Costo": costo,
                        "Estado": "Actualizado",
                        "Imagen": ""
                    })
            except:
                pass

            i += 2
        else:
            i += 1

    # =========================
    # 2) LIMPIAR DUPLICADOS
    # =========================
    vistos = set()
    productos_unicos = []

    for p in productos:
        clave = (p["Producto"], p["Costo"])
        if clave not in vistos:
            vistos.add(clave)
            productos_unicos.append(p)

    # =========================
    # 3) INTENTAR MAPEAR IMÁGENES
    # =========================
    imagenes_encontradas = []

    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-original")
            or ""
        ).strip()

        alt = (img.get("alt") or "").strip()

        if src:
            imagenes_encontradas.append({
                "src": urljoin(url, src),
                "alt": alt.lower()
            })

    # Intento simple de asociación por nombre
    for producto in productos_unicos:
        nombre_base = producto["Producto"].lower()

        mejor_imagen = ""

        for img in imagenes_encontradas:
            alt = img["alt"]

            if not alt:
                continue

            # Buscar coincidencia parcial razonable
            palabras_producto = [p for p in nombre_base.split() if len(p) > 3]
            coincidencias = sum(1 for palabra in palabras_producto if palabra in alt)

            if coincidencias >= 2:
                mejor_imagen = img["src"]
                break

        producto["Imagen"] = mejor_imagen

    return productos_unicos

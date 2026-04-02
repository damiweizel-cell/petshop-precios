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
    productos = []

    posibles_productos = soup.find_all(["div", "article", "li"])

    for bloque in posibles_productos:
        texto = bloque.get_text(" ", strip=True)

        precio_match = re.search(r"\$\s?([\d\.]+)", texto)
        if not precio_match:
            continue

        try:
            costo = int(precio_match.group(1).replace(".", ""))
        except:
            continue

        imagen_url = None
        img_tag = bloque.find("img")
        if img_tag:
            imagen_url = (
                img_tag.get("src")
                or img_tag.get("data-src")
                or img_tag.get("data-original")
                or img_tag.get("srcset")
            )

            if imagen_url:
                if "," in imagen_url:
                    imagen_url = imagen_url.split(",")[0].strip().split(" ")[0]

                imagen_url = urljoin(url, imagen_url)

        nombre = None

        for tag in bloque.find_all(["h1", "h2", "h3", "h4", "h5", "span", "p", "a"]):
            txt = tag.get_text(" ", strip=True)
            if txt and len(txt) > 8 and "$" not in txt:
                if not re.match(r"^[\d\W]+$", txt):
                    nombre = txt
                    break

        if not nombre:
            nombre = texto.replace(precio_match.group(0), "").strip()

        if not nombre or len(nombre) < 6:
            continue

        peso = extraer_peso(nombre)

        productos.append({
            "Producto": nombre,
            "Peso": peso,
            "Costo": costo,
            "Estado": "Actualizado",
            "Imagen": imagen_url if imagen_url else ""
        })

    vistos = set()
    productos_unicos = []

    for p in productos:
        clave = (p["Producto"], p["Costo"])
        if clave not in vistos:
            vistos.add(clave)
            productos_unicos.append(p)

    if not productos_unicos:
        texto = soup.get_text("\n")
        lineas = [line.strip() for line in texto.split("\n") if line.strip()]

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
                        productos_unicos.append({
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

    return productos_unicos

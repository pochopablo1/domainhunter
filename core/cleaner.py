import re

# Expresión regular robusta para dominios de Argentina e internacionales
PATRON_DOMINIOS = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com\.ar|net\.ar|org\.ar|gob\.ar|edu\.ar|tur\.ar|mil\.ar|co\.ar|ar|com|net|org|io|dev|co|xyz|info|biz|online|tech|store))'

def limpiar_y_extraer_dominios(texto_raw: str) -> list[str]:
    """
    Busca patrones de dominios válidos dentro de cualquier texto sucio,
    limpia caracteres raros (http, https, www, barras, etc.) y elimina duplicados
    manteniendo el orden de aparición.
    """
    if not texto_raw:
        return []
        
    texto_lower = texto_raw.lower()
    coincidencias = re.findall(PATRON_DOMINIOS, texto_lower)
    
    dominios_limpios = []
    vistos = set()
    
    for dom in coincidencias:
        # Limpieza adicional por si quedó algún caracter residual
        dom_clean = dom.strip(" /:?#@!$&'()*+,;=")
        if dom_clean and dom_clean not in vistos:
            vistos.add(dom_clean)
            dominios_limpios.append(dom_clean)
            
    return dominios_limpios

def analizar_estadisticas_extraccion(texto_raw: str) -> dict:
    """
    Proporciona un desglose detallado de la extracción.
    """
    dominios = limpiar_y_extraer_dominios(texto_raw)
    lineas = [l for l in texto_raw.splitlines() if l.strip()]
    
    # Conteo por TLD
    tlds = {}
    for d in dominios:
        partes = d.split('.')
        tld = ".".join(partes[1:])
        tlds[tld] = tlds.get(tld, 0) + 1

    return {
        "total_extraidos": len(dominios),
        "total_lineas_procesadas": len(lineas),
        "dominios": dominios,
        "desglose_tlds": tlds
    }

# Prueba directa
if __name__ == "__main__":
    texto_prueba = """
    Resultados del mercado:
    1. https://www.Homes.com.ar/seccion   - Creado en 1997 - Tráfico: 2.3M
    2. PAMPA.com.ar   (duplicado arriba o abajo)
    3. http://turismo-nqn.com.ar !!! 2010
    4. homes.com.ar  <- duplicado
    5. pagina-ejemplo.com
    6. mi-empresa.net.ar/contacto
    7. http://emprender.ar
    8. tech-hub.io
    """
    res = analizar_estadisticas_extraccion(texto_prueba)
    print("=== EXTRACCIÓN EXITOSA ===")
    print(f"Total dominios únicos: {res['total_extraidos']}")
    print(f"Desglose por TLD: {res['desglose_tlds']}")
    for i, d in enumerate(res['dominios'], 1):
        print(f"{i}. {d}")

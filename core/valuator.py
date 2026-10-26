import re

PALABRAS_ALTO_VALOR = {
    "casas", "autos", "auto", "motos", "moto", "propiedades", "remate", "remates",
    "abogado", "abogados", "contadores", "contador", "talleres", "taller", "clinicas",
    "tienda", "shop", "crypto", "bitcoin", "seguros", "salud", "medico", "turismo",
    "hotel", "hoteles", "pampa", "homes", "viajes", "credito", "creditos", "prestamo",
    "banco", "finanzas", "inversiones", "franquicias", "exportaciones", "importaciones",
    "cordoba", "rosario", "caba", "mendoza", "bienes", "raices", "tech", "digital",
    "market", "pyme", "barrio", "nordelta", "viviendas", "inmobiliaria", "vuelos",
    "club", "moda", "estilo", "ofertas", "descuentos", "envios", "express", "online",
    "vinos", "catering", "alquileres", "rent", "loan", "credit", "care", "realty", "miami", "dental", "insure"
}

PLANES_ADSENSE = [
    (
        ["auto", "autos", "moto", "motos", "talleres", "taller", "repuestos", "car", "spainauto"],
        {
            "nicho": "Automotor & Seguros Vehiculares",
            "cpc_adsense": "$0.80 - $3.20 USD / clic",
            "herramienta_estrella": "Valuador Oficial + Calculadora de Transferencia DNRPA y Patentes + Mapa de Talleres/VTV",
            "monetizacion_extra": "Leads CPA de Seguros Automotor / Motos (La Caja, Zurich, 123Seguros)"
        }
    ),
    (
        ["propiedades", "inmobiliaria", "alquileres", "casas", "homes", "realty", "miami", "rent"],
        {
            "nicho": "Real Estate, Alquileres & Créditos Hipotecarios",
            "cpc_adsense": "$1.50 - $6.00 USD / clic",
            "herramienta_estrella": "Calculadora de Ajuste de Alquiler (ICL/IPC) + Calculadora de Gastos de Escrituración e Hipoteca",
            "monetizacion_extra": "Anuncios AdSense de Bancos/Desarrolladoras + Destacados para Inmobiliarias"
        }
    ),
    (
        ["credito", "creditos", "prestamo", "finanzas", "inversiones", "franquicias", "contadores", "exportaciones", "credit", "loan"],
        {
            "nicho": "Finanzas, Impuestos, Franquicias & Comercio Exterior",
            "cpc_adsense": "$2.00 - $12.00 USD / clic",
            "herramienta_estrella": "Simulador de Cuotas / Calculadora de Monotributo e Impuestos de Importación/Exportación",
            "monetizacion_extra": "AdSense Finanzas (el CPC más alto de Google) + Afiliados de Fintechs/Bancos"
        }
    ),
    (
        ["salud", "clinicas", "medico", "dental", "care", "nutricionistas", "odontologos"],
        {
            "nicho": "Salud, Clínicas & Medicina Prepaga",
            "cpc_adsense": "$1.20 - $5.50 USD / clic",
            "herramienta_estrella": "Comparador de Planes de Prepagas / Cartilla Médica Interactiva + Turnero Guía",
            "monetizacion_extra": "Leads para Prepagas (OSDE, Swiss Medical, Galeno) y Clínicas Estéticas/Dentales"
        }
    ),
    (
        ["vinos", "catering", "eventos", "turismo", "viajes", "vuelos", "hotel"],
        {
            "nicho": "Turismo, Gastronomía & Eventos",
            "cpc_adsense": "$0.60 - $2.40 USD / clic",
            "herramienta_estrella": "Calculadora de Bebidas y Presupuesto para Eventos / Comparador de Escapadas y Bodegas",
            "monetizacion_extra": "AdSense + Comisiones de Reserva / Directorio de Proveedores de Eventos"
        }
    )
]

def obtener_plan_adsense(nombre: str) -> dict:
    for keywords, plan in PLANES_ADSENSE:
        for kw in keywords:
            if kw in nombre:
                return plan
    return {
        "nicho": "Portal de Servicios & Directorio SEO",
        "cpc_adsense": "$0.50 - $2.00 USD / clic",
        "herramienta_estrella": "Calculadora de Presupuestos Online + Comparador Interactivo + Guía de Trámites",
        "monetizacion_extra": "Google AdSense Display + Formulario de Presupuestos por WhatsApp"
    }

def calcular_valuacion_dominio(dominio: str) -> dict:
    """
    Calcula el Score de Valor comercial (0-100), Categoría, Estimación de Precio USD y Plan AdSense.
    """
    dom_clean = dominio.lower().strip()
    partes = dom_clean.split('.')
    nombre = partes[0]
    tld = ".".join(partes[1:])
    
    score = 50
    
    # 1. Evaluación de Longitud
    longitud = len(nombre)
    if longitud <= 5:
        score += 30
    elif longitud <= 8:
        score += 22
    elif longitud <= 12:
        score += 12
    elif longitud >= 16:
        score -= 15

    # 2. Evaluación por TLD
    if tld == "com":
        score += 18
    elif tld in ["com.ar", "ar"]:
        score += 14
    elif tld in ["io", "dev", "co", "ai"]:
        score += 12
    elif tld in ["net", "org", "net.ar"]:
        score += 6

    # 3. Presencia de Palabras Clave de Alto Valor
    coincidencias_kw = []
    for kw in PALABRAS_ALTO_VALOR:
        if kw in nombre:
            coincidencias_kw.append(kw)
            
    if coincidencias_kw:
        score += min(len(coincidencias_kw) * 15, 30)

    # 4. Penalización por guiones y números
    if "-" in nombre:
        score -= 20
    if re.search(r'\d', nombre):
        score -= 10

    score_final = max(10, min(99, score))
    
    if score_final >= 75:
        categoria = "🏆 PREMIUM"
        estimacion_usd = "$500 - $3,500+ USD"
        color = "#10b981"
    elif score_final >= 50:
        categoria = "⭐ OPORTUNIDAD"
        estimacion_usd = "$150 - $500 USD"
        color = "#f59e0b"
    else:
        categoria = "⚪ ESTÁNDAR"
        estimacion_usd = "$20 - $150 USD"
        color = "#9ca3af"

    plan_adsense = obtener_plan_adsense(nombre)

    return {
        "score": score_final,
        "categoria": categoria,
        "estimacion_usd": estimacion_usd,
        "keywords_detectadas": coincidencias_kw,
        "color": color,
        "adsense": plan_adsense
    }

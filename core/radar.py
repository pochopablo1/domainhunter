from core.cleaner import limpiar_y_extraer_dominios
from core.checker import analizar_lote_dominios
from core.valuator import calcular_valuacion_dominio

NICHOS_ESTRATÉGICOS = [
    "propiedades", "remates", "inmobiliaria", "autos", "creditos",
    "pampa", "salud", "turismo", "viajes", "tienda", "barrio", "seguros"
]

SUFIJOS_COMERCIALES = ["online", "express", "argentina", "hoy", "net", "hub"]

def ejecutar_radar_autopiloto() -> dict:
    """
    Escanea múltiples nichos estratégicos, encuentra dominios 100% DISPONIBLES,
    los clasifica y selecciona la MEJOR OPORTUNIDAD RECOMENDADA #1.
    """
    candidatos = []
    
    for nicho in NICHOS_ESTRATÉGICOS:
        candidatos.append(f"{nicho}.com.ar")
        candidatos.append(f"{nicho}.ar")
        for sufijo in SUFIJOS_COMERCIALES:
            candidatos.append(f"{nicho}{sufijo}.com.ar")

    dominios_unicos = list(dict.fromkeys(candidatos))
    resultados = analizar_lote_dominios(dominios_unicos)

    # Filtrar SOLAMENTE dominios disponibles
    disponibles = [r for r in resultados if r["estado"] in ["DISPONIBLE", "DISPONIBLE / INACTIVO"]]

    if not disponibles:
        return {"exito": False, "mensaje": "No se encontraron dominios disponibles en este momento."}

    # Ordenar por score de valuación descendente
    disponibles_ordenados = sorted(
        disponibles,
        key=lambda x: x.get("valuacion", {}).get("score", 0),
        reverse=True
    )

    # El #1 con mayor puntaje es la estrella
    mejor_opcion = disponibles_ordenados[0]
    val = mejor_opcion.get("valuacion", {})

    justificacion = (
        f"El dominio '{mejor_opcion['dominio']}' está 100% libre para registrar. "
        f"Posee un Score comercial de {val.get('score', 0)} pts y una estimación de mercado de {val.get('estimacion_usd', '$100-$300 USD')}. "
        f"Es un nombre corto, sin guiones ni números, altamente memorable en el mercado argentino."
    )

    return {
        "exito": True,
        "total_escaneados": len(resultados),
        "total_disponibles": len(disponibles),
        "mejor_oportunidad": mejor_opcion,
        "justificacion": justificacion,
        "otros_disponibles": disponibles_ordenados[1:10]
    }

if __name__ == "__main__":
    print("Ejecutando Radar Autopiloto...")
    res = ejecutar_radar_autopiloto()
    print(res)

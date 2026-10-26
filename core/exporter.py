import csv
import json
from datetime import datetime
import os

def exportar_a_csv(resultados: list[dict], filepath: str) -> str:
    """Guarda los resultados del análisis en formato CSV."""
    if not resultados:
        return ""
        
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    campos = ["dominio", "estado", "resuelve_dns", "fecha_creacion", "fecha_expiracion", "dias_restantes", "link_compra"]
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)
        
    return filepath

def exportar_a_json(resultados: list[dict], filepath: str) -> str:
    """Guarda los resultados del análisis en formato JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    payload = {
        "fecha_analisis": datetime.now().isoformat(),
        "total_dominios": len(resultados),
        "resultados": resultados
    }
    
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
        
    return filepath

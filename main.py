import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel
import uvicorn
import csv
import io

from core.cleaner import analizar_estadisticas_extraccion, limpiar_y_extraer_dominios
from core.checker import analizar_lote_dominios
from core.radar import ejecutar_radar_autopiloto

app = FastAPI(
    title="Analizador & Valuador de Dominios API",
    description="API REST para extracción, análisis, valuación comercial y radar autopiloto de dominios",
    version="1.2.0"
)

class ExtractRequest(BaseModel):
    texto_raw: str

class AnalyzeRequest(BaseModel):
    texto_raw: str | None = None
    dominios: list[str] | None = None

@app.post("/api/extract")
async def api_extraer_dominios(req: ExtractRequest):
    if not req.texto_raw:
        raise HTTPException(status_code=400, detail="Debe enviar texto para procesar.")
    res = analizar_estadisticas_extraccion(req.texto_raw)
    return res

@app.post("/api/analyze")
async def api_analizar_dominios(req: AnalyzeRequest):
    doms_a_procesar = []
    if req.dominios:
        doms_a_procesar = req.dominios
    elif req.texto_raw:
        doms_a_procesar = limpiar_y_extraer_dominios(req.texto_raw)
    else:
        raise HTTPException(status_code=400, detail="Debe proporcionar 'texto_raw' o lista de 'dominios'.")

    if not doms_a_procesar:
        return {"total": 0, "resultados": []}

    resultados = analizar_lote_dominios(doms_a_procesar)
    
    libres = sum(1 for r in resultados if r["estado"] in ["DISPONIBLE", "DISPONIBLE / INACTIVO"])
    vencidos = sum(1 for r in resultados if r["estado"] in ["EXPIRADO", "PROXIMO_A_VENCER"])
    registrados = sum(1 for r in resultados if r["estado"] == "REGISTRADO")
    premium = sum(1 for r in resultados if r.get("valuacion", {}).get("score", 0) >= 75)

    return {
        "total": len(resultados),
        "resumen": {
            "disponibles": libres,
            "proximos_vencer_o_expirados": vencidos,
            "registrados": registrados,
            "premium": premium
        },
        "resultados": resultados
    }

@app.post("/api/radar")
async def api_ejecutar_radar():
    res = ejecutar_radar_autopiloto()
    return res

@app.post("/api/export/csv")
async def api_exportar_csv(req: AnalyzeRequest):
    doms = req.dominios if req.dominios else limpiar_y_extraer_dominios(req.texto_raw or "")
    resultados = analizar_lote_dominios(doms) if doms else []
    
    output = io.StringIO()
    campos = ["dominio", "estado", "score_valuacion", "categoria_valor", "estimacion_usd", "resuelve_dns", "fecha_expiracion", "link_compra"]
    
    rows_para_csv = []
    for r in resultados:
        val = r.get("valuacion", {})
        rows_para_csv.append({
            "dominio": r["dominio"],
            "estado": r["estado"],
            "score_valuacion": val.get("score", 0),
            "categoria_valor": val.get("categoria", ""),
            "estimacion_usd": val.get("estimacion_usd", ""),
            "resuelve_dns": r["resuelve_dns"],
            "fecha_expiracion": r.get("fecha_expiracion") or "",
            "link_compra": r["link_compra"]
        })

    writer = csv.DictWriter(output, fieldnames=campos)
    writer.writeheader()
    writer.writerows(rows_para_csv)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analisis_dominios_valuados.csv"}
    )

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "API activa. Visita /docs para la documentación."}

if __name__ == "__main__":
    print("Iniciando servidor del Analizador de Dominios en http://localhost:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

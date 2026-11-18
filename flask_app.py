import os
import csv
import io
import json
from flask import Flask, request, jsonify, send_from_directory, Response
from core.cleaner import analizar_estadisticas_extraccion, limpiar_y_extraer_dominios
from core.checker import analizar_lote_dominios, analizar_dominio
from sniper_pythonanywhere import cargar_vip_persistente, seleccionar_lote_del_dia, ejecutar_sniper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")

@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/api/extract", methods=["POST"])
def api_extract():
    data = request.get_json(silent=True) or {}
    texto_raw = data.get("texto_raw", "")
    if not texto_raw:
        return jsonify({"error": "Debe enviar texto para procesar."}), 400
    return jsonify(analizar_estadisticas_extraccion(texto_raw))

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    doms = data.get("dominios") or limpiar_y_extraer_dominios(data.get("texto_raw", ""))
    if not doms:
        return jsonify({"total": 0, "resultados": []})

    resultados = analizar_lote_dominios(doms)
    libres = sum(1 for r in resultados if "DISPONIBLE" in r["estado"])
    vencidos = sum(1 for r in resultados if r["estado"] in ["EXPIRADO", "PROXIMO_A_VENCER", "REDEMPTION_PERIOD", "PENDING_DELETE"])
    registrados = sum(1 for r in resultados if r["estado"] == "REGISTRADO")
    premium = sum(1 for r in resultados if r.get("valuacion", {}).get("score", 0) >= 75)

    return jsonify({
        "total": len(resultados),
        "resumen": {
            "disponibles": libres,
            "proximos_vencer_o_expirados": vencidos,
            "registrados": registrados,
            "premium": premium
        },
        "resultados": resultados
    })

@app.route("/api/generate-niche", methods=["POST"])
def api_generate_niche():
    data = request.get_json(silent=True) or {}
    kw = (data.get("keyword") or "").lower().strip()
    if not kw:
        return jsonify({"total": 0, "resultados": []})

    sufijos = ["", "hoy", "online", "pro", "ya", "hub"]
    candidatos = []
    for s in sufijos:
        candidatos.append(f"{kw}{s}.com.ar")
        candidatos.append(f"{kw}{s}.com")

    resultados = analizar_lote_dominios(candidatos)
    return jsonify({"total": len(resultados), "resultados": resultados})

@app.route("/api/radar", methods=["POST"])
def api_radar():
    resultados = analizar_lote_dominios(seleccionar_lote_del_dia(full_scan=False))
    oportunidades = [
        r for r in resultados
        if r["estado"] in ["DISPONIBLE", "PENDING_DELETE", "REDEMPTION_PERIOD", "EXPIRADO", "PROXIMO_A_VENCER"]
    ]
    oportunidades.sort(key=lambda x: (0 if x["estado"] == "DISPONIBLE" else 1, -x.get("valuacion", {}).get("score", 0)))

    if not oportunidades:
        return jsonify({"exito": False, "mensaje": "No se encontraron oportunidades."})

    mejor = oportunidades[0]
    val = mejor.get("valuacion", {})
    ads = val.get("adsense", {})
    justificacion = (
        f"Estado: {mejor['estado']} | Nicho AdSense: {ads.get('nicho', '')} "
        f"(CPC estimado: {ads.get('cpc_adsense', '')}). "
        f"Idea de Portal: {ads.get('herramienta_estrella', '')}."
    )

    return jsonify({
        "exito": True,
        "total_escaneados": len(resultados),
        "total_disponibles": len(oportunidades),
        "mejor_oportunidad": mejor,
        "justificacion": justificacion,
        "otros_disponibles": resultados
    })

@app.route("/api/export/csv", methods=["POST"])
def api_export_csv():
    data = request.get_json(silent=True) or {}
    doms = data.get("dominios") or limpiar_y_extraer_dominios(data.get("texto_raw", ""))
    resultados = analizar_lote_dominios(doms) if doms else []

    output = io.StringIO()
    campos = ["dominio", "estado", "score_valuacion", "categoria_valor", "estimacion_usd", "cpc_adsense", "herramienta_portal", "fecha_expiracion", "link_compra"]
    writer = csv.DictWriter(output, fieldnames=campos)
    writer.writeheader()
    for r in resultados:
        val = r.get("valuacion", {})
        ads = val.get("adsense", {})
        writer.writerow({
            "dominio": r["dominio"],
            "estado": r["estado"],
            "score_valuacion": val.get("score", 0),
            "categoria_valor": val.get("categoria", ""),
            "estimacion_usd": val.get("estimacion_usd", ""),
            "cpc_adsense": ads.get("cpc_adsense", ""),
            "herramienta_portal": ads.get("herramienta_estrella", ""),
            "fecha_expiracion": r.get("fecha_expiracion") or "",
            "link_compra": r["link_compra"]
        })

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=dominios_adsense.csv"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

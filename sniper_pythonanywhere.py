import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from core.checker import analizar_dominio

# ==============================================================================
# CONFIGURACIÓN DE EMAIL GRATIS (GMAIL SMTP) - CARGA AUTOMÁTICA DESDE .env
# ==============================================================================
def cargar_env_local():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

cargar_env_local()

EMAIL_REMITENTE = os.environ.get("SNIPER_EMAIL_FROM", "pablo.santilli7@gmail.com")
EMAIL_APP_PASSWORD = os.environ.get("SNIPER_EMAIL_PASS", "")
EMAIL_DESTINO = os.environ.get("SNIPER_EMAIL_TO", "pablo.santilli7@gmail.com")

# ==============================================================================
# WATCHLIST VIP DE MÁXIMA GANANCIA (ARGENTINA & EXTERIOR)
# ==============================================================================
WATCHLIST_DOMINIOS = [
    # Argentina (.com.ar) - Alto Tráfico Orgánico + Alto CPC AdSense
    "propiedades.com.ar",
    "catering.com.ar",
    "vinos.com.ar",
    "franquicias.com.ar",
    "clinicas.com.ar",
    "talleres.com.ar",
    "contadores.com.ar",
    "exportaciones.com.ar",
    "motosusadas.com.ar",
    # Exterior (.com) - Alto CPC AdSense en USD
    "miamirealtyhub.com",
    "rentfast.com",
    "creditpro.com",
    "learnfast.com",
    "dentalcarepro.com"
]

def armar_html_email(alertas: list[dict], seguimiento: list[dict]) -> str:
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    bloques_alerta = ""
    for a in alertas:
        val = a.get("valuacion", {})
        ads = val.get("adsense", {})
        es_ar = a["dominio"].endswith(".ar")
        texto_boton = "🛒 ABRIR NIC.AR / TAD Y REGISTRAR ($8.500 ARS)" if es_ar else f"🛒 COMPRAR {a['dominio'].upper()} EN 1 CLIC ($10 USD)"
        
        bloques_alerta += f"""
        <div style="background:#ecfdf5; border:2px solid #10b981; border-radius:12px; padding:18px; margin-bottom:16px;">
            <div style="font-size:12px; font-weight:800; color:#047857; text-transform:uppercase;">
                🟢 ¡LISTO PARA COMPRAR AHORA MISMO! ({a['estado']})
            </div>
            <h2 style="margin:6px 0; color:#0f172a; font-size:22px;">{a['dominio']}</h2>
            <p style="margin:4px 0; font-size:14px; color:#334155;">
                💰 <strong>Valor Comercial:</strong> {val.get('estimacion_usd', '$500+ USD')} &nbsp;|&nbsp;
                📈 <strong>CPC AdSense:</strong> {ads.get('cpc_adsense', '$1.50+ USD/clic')}
            </p>
            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; margin:10px 0; font-size:13px; color:#1e293b;">
                <strong>⚡ Plan de Portal AdSense listo para armar:</strong><br>
                • <strong>Nicho:</strong> {ads.get('nicho', '')}<br>
                • <strong>Calculadora Estrella:</strong> {ads.get('herramienta_estrella', '')}<br>
                • <strong>Monetización Extra:</strong> {ads.get('monetizacion_extra', '')}
            </div>
            <a href="{a['link_compra']}" target="_blank"
               style="display:inline-block; background:#10b981; color:#ffffff; text-decoration:none; font-weight:800; padding:12px 20px; border-radius:8px; font-size:14px; margin-top:6px;">
               {texto_boton}
            </a>
        </div>
        """

    filas_tabla = ""
    for s in seguimiento:
        val = s.get("valuacion", {})
        ads = s.get("adsense_info") or val.get("adsense", {})
        dias = s.get("dias_restantes")
        dias_str = f"Hace {abs(dias)}d (En caída)" if (dias is not None and dias < 0) else (f"En {dias} días" if dias is not None else "LIBRE")
        
        filas_tabla += f"""
        <tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:10px; font-weight:700; color:#0f172a;">{s['dominio']}</td>
            <td style="padding:10px; font-size:13px;">{s['estado']}</td>
            <td style="padding:10px; font-size:13px;">{s.get('fecha_expiracion') or 'LIBRE'} ({dias_str})</td>
            <td style="padding:10px; font-size:13px; color:#047857; font-weight:700;">{ads.get('cpc_adsense', '')}</td>
            <td style="padding:10px;">
                <a href="{s['link_compra']}" style="color:#2563eb; font-weight:700; text-decoration:none; font-size:13px;">Ver / Comprar ➔</a>
            </td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px; color:#0f172a;">
        <div style="max-width:680px; margin:0 auto; background:#ffffff; border-radius:16px; padding:24px; border:1px solid #e2e8f0;">
            <h1 style="margin-top:0; color:#0f172a; font-size:22px;">🎯 DomainHunter Sniper — Reporte ({fecha_hoy})</h1>
            <p style="color:#64748b; font-size:14px;">Escaneo automático 24/7 en la nube (NIC Argentina & Verisign Exterior).</p>
            
            {bloques_alerta if bloques_alerta else '<p style="padding:12px; background:#f1f5f9; border-radius:8px;">No hay nuevos dominios liberados en este turno.</p>'}
            
            <h3 style="margin-top:24px; color:#0f172a;">⏳ Cuenta Regresiva de tu Watchlist VIP</h3>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f1f5f9; font-size:12px; color:#475569; text-transform:uppercase;">
                        <th style="padding:10px;">Dominio</th>
                        <th style="padding:10px;">Estado</th>
                        <th style="padding:10px;">Vencimiento</th>
                        <th style="padding:10px;">CPC AdSense</th>
                        <th style="padding:10px;">Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_tabla}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

def enviar_email_alerta(asunto: str, html_body: str) -> bool:
    if not EMAIL_REMITENTE or not EMAIL_APP_PASSWORD or not EMAIL_DESTINO:
        print("ℹ️ Email no configurado aún (completar EMAIL_REMITENTE / EMAIL_APP_PASSWORD / EMAIL_DESTINO).")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = f"DomainHunter Sniper <{EMAIL_REMITENTE}>"
        msg["To"] = EMAIL_DESTINO
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_REMITENTE, EMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_REMITENTE, [EMAIL_DESTINO], msg.as_string())

        print(f"📧 ¡Email enviado con éxito a {EMAIL_DESTINO}!")
        return True
    except Exception as e:
        print(f"⚠️ Error enviando email: {e}")
        return False

def ejecutar_sniper():
    print("====================================================")
    print("🐍 EJECUTANDO SNIPER PYTHON (APTO PYTHONANYWHERE)")
    print("====================================================")
    
    resultados = []
    alertas_compra = []

    for dom in WATCHLIST_DOMINIOS:
        info = analizar_dominio(dom)
        resultados.append(info)
        if info["estado"] in ["DISPONIBLE", "PENDING_DELETE"]:
            alertas_compra.append(info)
        print(f" -> {dom.ljust(22)} | {info['estado'].ljust(18)} | Vence: {str(info['fecha_expiracion']).ljust(10)} | CPC: {info['valuacion']['adsense']['cpc_adsense']}")
        time.sleep(0.25)

    out_file = os.path.join(os.path.dirname(__file__), "watchlist_status.json")
    payload = {
        "timestamp": datetime.now().isoformat(),
        "total_monitoreados": len(resultados),
        "alertas_compra_inmediata": alertas_compra,
        "resultados": resultados
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Estado guardado en {out_file}")

    if alertas_compra:
        nombres = ", ".join(a["dominio"] for a in alertas_compra)
        asunto = f"🚨 ¡DOMINIO LIBRE PARA COMPRAR YA!: {nombres}"
    else:
        asunto = "📊 Reporte Diario DomainHunter Sniper (.AR & .COM)"

    html_email = armar_html_email(alertas_compra, resultados)
    enviar_email_alerta(asunto, html_email)
    return payload

if __name__ == "__main__":
    ejecutar_sniper()

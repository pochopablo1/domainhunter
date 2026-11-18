import os
import sys
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
# DICCIONARIO MASIVO DE NICHOS RENTABLES PARA PORTALES GOOGLE ADSENSE (240+ DOMINIOS)
# ==============================================================================
POOL_ARGENTINA_AR = [
    # Motor, Vehículos & Servicios (Estilo AutosHoy / MotosUsadas)
    "camionetas.com.ar", "utilitarios.com.ar", "acoplados.com.ar", "tractores.com.ar",
    "cuatriciclos.com.ar", "repuestos.com.ar", "neumaticos.com.ar", "lubricentros.com.ar",
    "baterias.com.ar", "talleres.com.ar", "chapistas.com.ar", "cerrajeria.com.ar",
    "remises.com.ar", "fletes.com.ar", "mudanzas.com.ar", "logistica.com.ar",
    "autoelevadores.com.ar", "concesionarias.com.ar", "planahorro.com.ar", "multas.com.ar",
    "transferencias.com.ar", "patentes.com.ar", "autopartes.com.ar", "gomeria.com.ar",
    "gomerias.com.ar", "mecanicos.com.ar", "inyeccion.com.ar", "polarizados.com.ar",
    "llantas.com.ar", "amortiguadores.com.ar", "frenos.com.ar", "embragues.com.ar",
    "radiadores.com.ar", "escapes.com.ar", "parabrisas.com.ar", "autoescuelas.com.ar",
    "camionesusados.com.ar", "autosclasicos.com.ar", "lanchas.com.ar", "nautica.com.ar",

    # Finanzas, Seguros, Impuestos & Legal (CPC Más Alto de AdSense)
    "prestamos.com.ar", "creditos.com.ar", "hipotecas.com.ar", "seguros.com.ar",
    "aseguradoras.com.ar", "jubilaciones.com.ar", "sueldos.com.ar", "aguinaldo.com.ar",
    "monotributo.com.ar", "impuestos.com.ar", "contadores.com.ar", "abogados.com.ar",
    "escribanos.com.ar", "escribanias.com.ar", "sucesiones.com.ar", "divorcios.com.ar",
    "franquicias.com.ar", "inversiones.com.ar", "plazofijo.com.ar", "cotizaciones.com.ar",
    "licitaciones.com.ar", "subastas.com.ar", "remates.com.ar", "importaciones.com.ar",
    "exportaciones.com.ar", "aduana.com.ar", "despachantes.com.ar", "finanzas.com.ar",
    "auditoria.com.ar", "consultoras.com.ar", "pymes.com.ar", "facturacion.com.ar",
    "indemnizaciones.com.ar", "accidentes.com.ar", "gestoria.com.ar", "gestores.com.ar",

    # Inmobiliaria, Hogar & Construcción
    "propiedades.com.ar", "inmobiliarias.com.ar", "alquileres.com.ar", "departamentos.com.ar",
    "terrenos.com.ar", "lotes.com.ar", "loteos.com.ar", "campos.com.ar",
    "estancias.com.ar", "galpones.com.ar", "oficinas.com.ar", "cocheras.com.ar",
    "countries.com.ar", "cabanas.com.ar", "temporarios.com.ar", "arquitectos.com.ar",
    "constructoras.com.ar", "corralones.com.ar", "ferreterias.com.ar", "pinturerias.com.ar",
    "madereras.com.ar", "aberturas.com.ar", "piletas.com.ar", "climatizacion.com.ar",
    "plomeros.com.ar", "electricistas.com.ar", "gasistas.com.ar", "techistas.com.ar",
    "alambrados.com.ar", "pisos.com.ar", "revestimientos.com.ar", "amoblamientos.com.ar",
    "mudanzasyfletes.com.ar", "administracionconsorcios.com.ar", "expensas.com.ar",

    # Salud, Medicina & Profesionales
    "clinicas.com.ar", "sanatorios.com.ar", "prepagas.com.ar", "obrasocial.com.ar",
    "odontologos.com.ar", "implantes.com.ar", "ortodoncia.com.ar", "psicologos.com.ar",
    "nutricionistas.com.ar", "kinesiologos.com.ar", "oftalmologos.com.ar", "dermatologos.com.ar",
    "pediatras.com.ar", "veterinarias.com.ar", "mascotas.com.ar", "farmacias.com.ar",
    "opticas.com.ar", "geriatricos.com.ar", "enfermeria.com.ar", "laboratorios.com.ar",
    "estetica.com.ar", "gimnasios.com.ar", "suplementos.com.ar", "ortopedias.com.ar",

    # Educación, Eventos, Turismo & Agro
    "cursos.com.ar", "universidades.com.ar", "colegios.com.ar", "idiomas.com.ar",
    "catering.com.ar", "eventos.com.ar", "salones.com.ar", "casamientos.com.ar",
    "vinos.com.ar", "bodegas.com.ar", "cervecerias.com.ar", "hoteles.com.ar",
    "vuelos.com.ar", "cruceros.com.ar", "excursiones.com.ar", "glamping.com.ar",
    "semillas.com.ar", "fertilizantes.com.ar", "ganaderia.com.ar", "forrajes.com.ar",
    "agroquimicos.com.ar", "cosechadoras.com.ar", "fumigaciones.com.ar", "silos.com.ar"
]

POOL_EXTERIOR_COM = [
    # High-CPC US / Global Niches (Real Estate, Finance, Auto, Legal, Health)
    "miamirealtyhub.com", "orlandorealtyhub.com", "austinrealtyhub.com", "dallasrealtyhub.com",
    "rentfast.com", "creditpro.com", "learnfast.com", "dentalcarepro.com",
    "carvaluehub.com", "insurequoteai.com", "spainautohub.com", "madridhomespro.com",
    "texasautohub.com", "floridaloanpro.com", "solarquotepro.com", "injuryclaimpro.com",
    "roofingquotepro.com", "hvacrepairpro.com", "medspahub.com", "mortgageratepro.com",
    "autoloancalc.com", "debtreliefhub.com", "taxrefundpro.com", "homewarrantypro.com",
    "movingcosthub.com", "plumberquotepro.com", "vetcarepro.com", "seniorcarehub.com",
    "cryptotaxcalc.com", "freelancetaxhub.com", "smallbizloanpro.com", "refinancecalcpro.com",
    "usedcarvaluepro.com", "motovaluehub.com", "truckloanpro.com", "boatinsurehub.com"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIP_FILE = os.path.join(BASE_DIR, "watchlist_vip.json")
STATUS_FILE = os.path.join(BASE_DIR, "watchlist_status.json")

# Semilla inicial VIP (los que ya sabemos que están libres, vencidos en caída o por vencer pronto)
SEMILLA_VIP = [
    "transferencias.com.ar", "lubricentros.com.ar", "catering.com.ar", "talleres.com.ar",
    "contadores.com.ar", "multas.com.ar", "chapistas.com.ar", "acoplados.com.ar",
    "remises.com.ar", "propiedades.com.ar", "vinos.com.ar", "franquicias.com.ar",
    "clinicas.com.ar", "exportaciones.com.ar", "nutricionistas.com.ar",
    "miamirealtyhub.com", "rentfast.com", "creditpro.com", "learnfast.com", "dentalcarepro.com"
]

def cargar_vip_persistente() -> list[str]:
    if os.path.exists(VIP_FILE):
        try:
            with open(VIP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return list(dict.fromkeys(SEMILLA_VIP + data))
        except Exception:
            pass
    return list(SEMILLA_VIP)

def guardar_vip_persistente(dominios: list[str]):
    unicos = list(dict.fromkeys(dominios))
    with open(VIP_FILE, "w", encoding="utf-8") as f:
        json.dump(unicos, f, ensure_ascii=False, indent=2)

def seleccionar_lote_del_dia(full_scan: bool = False) -> list[str]:
    """
    Combina SIEMPRE toda la lista VIP (dominios vencidos o por vencer en <60 días)
    + un lote rotativo amplio del Diccionario Masivo (o todo el diccionario si se pasa --full).
    """
    vip_actual = cargar_vip_persistente()
    todos_diccionario = POOL_ARGENTINA_AR + POOL_EXTERIOR_COM
    resto = [d for d in todos_diccionario if d not in vip_actual]

    if full_scan:
        return vip_actual + resto

    # Rotación automática diaria: escanea 70 dominios nuevos del diccionario por día + todos los VIP
    tamano_lote = 70
    dia_del_anio = datetime.now().timetuple().tm_yday
    inicio = (dia_del_anio * tamano_lote) % max(1, len(resto))
    lote_rotativo = resto[inicio:inicio + tamano_lote]
    if len(lote_rotativo) < tamano_lote:
        lote_rotativo += resto[:tamano_lote - len(lote_rotativo)]

    return list(dict.fromkeys(vip_actual + lote_rotativo))

def armar_html_email(libres: list[dict], vencidos_en_caida: list[dict], proximos: list[dict], total_escaneados: int) -> str:
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    bloques_alerta = ""
    for a in libres:
        val = a.get("valuacion", {})
        ads = val.get("adsense", {})
        es_ar = a["dominio"].endswith(".ar")
        texto_boton = "🛒 ABRIR NIC.AR / TAD Y REGISTRAR ($8.500 ARS)" if es_ar else f"🛒 COMPRAR {a['dominio'].upper()} EN 1 CLIC ($10 USD)"
        
        bloques_alerta += f"""
        <div style="background:#ecfdf5; border:2px solid #10b981; border-radius:12px; padding:18px; margin-bottom:16px;">
            <div style="font-size:12px; font-weight:800; color:#047857; text-transform:uppercase;">
                🟢 ¡100% LIBRE PARA REGISTRAR HOY MISMO! ({a['estado']})
            </div>
            <h2 style="margin:6px 0; color:#0f172a; font-size:22px;">{a['dominio']}</h2>
            <p style="margin:4px 0; font-size:14px; color:#334155;">
                💰 <strong>Valor Comercial:</strong> {val.get('estimacion_usd', '$500+ USD')} &nbsp;|&nbsp;
                📈 <strong>CPC AdSense:</strong> {ads.get('cpc_adsense', '$1.50+ USD/clic')}
            </p>
            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; margin:10px 0; font-size:13px; color:#1e293b;">
                <strong>⚡ Plan de Portal AdSense listo para armar:</strong><br>
                • <strong>Nicho:</strong> {ads.get('nicho', '')}<br>
                • <strong>Calculadora Estrella:</strong> {ads.get('herramienta_estrella', '')}
            </div>
            <a href="{a['link_compra']}" target="_blank"
               style="display:inline-block; background:#10b981; color:#ffffff; text-decoration:none; font-weight:800; padding:12px 20px; border-radius:8px; font-size:14px; margin-top:6px;">
               {texto_boton}
            </a>
        </div>
        """

    def render_filas(lista: list[dict]) -> str:
        html = ""
        for s in lista:
            val = s.get("valuacion", {})
            ads = val.get("adsense", {})
            dias = s.get("dias_restantes")
            if dias is not None and dias < 0:
                dias_str = f"🔥 Venció hace {abs(dias)}d (En período de caída)"
            elif dias is not None:
                dias_str = f"⏳ Vence en {dias} días"
            else:
                dias_str = "🟢 LIBRE"
            dns_str = "🔴 Sin Web" if not s.get("resuelve_dns") else "🟢 Con Web"
            
            html += f"""
            <tr style="border-bottom:1px solid #e2e8f0;">
                <td style="padding:10px; font-weight:700; color:#0f172a;">
                    {s['dominio']}
                    <div style="font-size:11px; color:#64748b; font-weight:400;">💡 {ads.get('herramienta_estrella', '')}</div>
                </td>
                <td style="padding:10px; font-size:12px;">{s['estado']}<br><span style="color:#64748b;">{dns_str}</span></td>
                <td style="padding:10px; font-size:12px;"><strong>{s.get('fecha_expiracion') or 'LIBRE'}</strong><br>{dias_str}</td>
                <td style="padding:10px; font-size:12px; color:#047857; font-weight:700;">{ads.get('cpc_adsense', '')}</td>
                <td style="padding:10px;">
                    <a href="{s['link_compra']}" style="color:#2563eb; font-weight:700; text-decoration:none; font-size:12px;">Ir a Registro ➔</a>
                </td>
            </tr>
            """
        return html

    filas_caida = render_filas(vencidos_en_caida)
    filas_proximos = render_filas(proximos)

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px; color:#0f172a;">
        <div style="max-width:720px; margin:0 auto; background:#ffffff; border-radius:16px; padding:24px; border:1px solid #e2e8f0;">
            <h1 style="margin-top:0; color:#0f172a; font-size:22px;">🎯 DomainHunter Sniper — Escaneo Ampliado ({fecha_hoy})</h1>
            <p style="color:#64748b; font-size:14px;">
                Se escanearon <strong>{total_escaneados} dominios comerciales</strong> en NIC Argentina (<code>.com.ar</code>) y Verisign (<code>.com</code>).
            </p>
            
            {bloques_alerta if bloques_alerta else '<p style="padding:12px; background:#f1f5f9; border-radius:8px; font-size:13px;">No se liberaron dominios en este turno. Abajo tenés los que están en etapa de caída.</p>'}
            
            <h3 style="margin-top:24px; color:#dc2626;">🔥 1. Dominios VENCIDOS / EN REDENCIÓN (A punto de caer libres)</h3>
            <table style="width:100%; border-collapse:collapse; text-align:left; margin-bottom:24px;">
                <thead>
                    <tr style="background:#fef2f2; font-size:11px; color:#991b1b; text-transform:uppercase;">
                        <th style="padding:10px;">Dominio & Portal AdSense</th>
                        <th style="padding:10px;">Estado & Web</th>
                        <th style="padding:10px;">Vencimiento</th>
                        <th style="padding:10px;">CPC AdSense</th>
                        <th style="padding:10px;">Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_caida if filas_caida else '<tr><td colspan="5" style="padding:12px; color:#64748b;">Ninguno en período post-vencimiento hoy.</td></tr>'}
                </tbody>
            </table>

            <h3 style="margin-top:24px; color:#0f172a;">🟡 2. Próximos a Vencer (Ordenados por fecha más cercana)</h3>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f1f5f9; font-size:11px; color:#475569; text-transform:uppercase;">
                        <th style="padding:10px;">Dominio & Portal AdSense</th>
                        <th style="padding:10px;">Estado & Web</th>
                        <th style="padding:10px;">Vencimiento</th>
                        <th style="padding:10px;">CPC AdSense</th>
                        <th style="padding:10px;">Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_proximos}
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

def ejecutar_sniper(full_scan: bool = False):
    candidatos = seleccionar_lote_del_dia(full_scan=full_scan)
    print("=========================================================")
    print(f"🐍 SNIPER AMPLIADO - ESCANEANDO {len(candidatos)} DOMINIOS RENTABLES")
    print("=========================================================")
    
    resultados = []
    libres = []
    vencidos_en_caida = []
    proximos = []
    nuevos_vip = []

    for idx, dom in enumerate(candidatos, 1):
        info = analizar_dominio(dom)
        resultados.append(info)
        est = info["estado"]
        dias = info.get("dias_restantes")

        if est in ["DISPONIBLE", "PENDING_DELETE"]:
            libres.append(info)
            nuevos_vip.append(dom)
        elif est in ["EXPIRADO", "REDEMPTION_PERIOD"] or (dias is not None and dias < 0):
            vencidos_en_caida.append(info)
            nuevos_vip.append(dom)
        elif est == "PROXIMO_A_VENCER" or (dias is not None and 0 <= dias <= 75):
            proximos.append(info)
            nuevos_vip.append(dom)

        if est != "REGISTRADO" or (dias is not None and dias <= 75):
            print(f" [{idx}/{len(candidatos)}] 🎯 {dom.ljust(24)} | {est.ljust(18)} | Vence: {str(info['fecha_expiracion']).ljust(10)} ({dias}d)")
        
        # Pausa de 1.2s para dominios .ar así NIC.ar nunca aplica rate-limit en lotes grandes
        time.sleep(1.2 if dom.endswith(".ar") else 0.25)

    # Ordenar por cercanía de vencimiento
    vencidos_en_caida.sort(key=lambda x: x.get("dias_restantes") if x.get("dias_restantes") is not None else 0)
    proximos.sort(key=lambda x: x.get("dias_restantes") if x.get("dias_restantes") is not None else 9999)

    # Guardar lista VIP actualizada automáticamente (descarta los que ya renovaron por 1 año)
    guardar_vip_persistente(nuevos_vip)

    payload = {
        "timestamp": datetime.now().isoformat(),
        "total_monitoreados": len(resultados),
        "alertas_compra_inmediata": libres,
        "vencidos_en_caida": vencidos_en_caida,
        "proximos_a_vencer": proximos[:35],
        "resultados": libres + vencidos_en_caida + proximos[:40]
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Escaneo completado: {len(libres)} LIBRES | {len(vencidos_en_caida)} VENCIDOS EN CAÍDA | {len(proximos)} PRÓXIMOS A VENCER")
    print(f"✅ Estado guardado en {STATUS_FILE}")

    if libres:
        nombres = ", ".join(a["dominio"] for a in libres[:4])
        asunto = f"🚨 ¡{len(libres)} DOMINIOS LIBRES PARA COMPRAR YA!: {nombres}"
    elif vencidos_en_caida:
        nombres = ", ".join(a["dominio"] for a in vencidos_en_caida[:3])
        asunto = f"🔥 {len(vencidos_en_caida)} Dominios en Caída ({nombres}) + {len(proximos)} por Vencer"
    else:
        asunto = f"📊 Reporte Diario DomainHunter ({len(proximos)} dominios por vencer)"

    html_email = armar_html_email(libres, vencidos_en_caida, proximos[:30], len(resultados))
    enviar_email_alerta(asunto, html_email)
    return payload

if __name__ == "__main__":
    full = "--full" in sys.argv
    ejecutar_sniper(full_scan=full)

import socket
import urllib.request
import urllib.error
import json
import re
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from core.valuator import calcular_valuacion_dominio

def obtener_link_registro(dominio: str) -> str:
    if dominio.endswith(".ar"):
        return "https://nic.ar"
    else:
        return f"https://porkbun.com/checkout/search?q={dominio}"

def obtener_link_backorder(dominio: str) -> str:
    if dominio.endswith(".ar"):
        return "https://nic.ar"
    else:
        return f"https://www.dynadot.com/market/backorder?domain={dominio}"

def chequear_resolucion_dns(dominio: str) -> bool:
    """Verifica si el dominio resuelve a alguna dirección IP (registrado y activo)."""
    try:
        socket.gethostbyname(dominio)
        return True
    except socket.gaierror:
        return False

def consultar_whois_ar(dominio: str) -> dict:
    """
    Consulta directamente el servidor WHOIS de NIC Argentina (whois.nic.ar:43)
    para obtener fecha exacta de vencimiento, creación y titular sin bloqueos HTTP.
    """
    try:
        with socket.create_connection(("whois.nic.ar", 43), timeout=5) as s:
            s.sendall(f"{dominio}\r\n".encode("utf-8"))
            chunks = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data.decode("utf-8", errors="ignore"))
            raw_text = "".join(chunks)

        if "El dominio no se encuentra registrado" in raw_text:
            return {"exito": True, "disponible": True}

        reg_match = re.search(r"registered:\s*([0-9-]+)", raw_text)
        exp_match = re.search(r"expire:\s*([0-9-]+)", raw_text)
        name_match = re.search(r"name:\s*(.+)", raw_text)
        ns_matches = re.findall(r"nserver:\s*(.+)", raw_text)

        return {
            "exito": True,
            "disponible": False,
            "creacion": reg_match.group(1) if reg_match else None,
            "expiracion": exp_match.group(1) if exp_match else None,
            "titular": name_match.group(1).strip() if name_match else None,
            "nameservers": len(ns_matches)
        }
    except Exception:
        return {"exito": False}

def consultar_rdap(dominio: str) -> dict:
    """
    Consulta datos del dominio:
    - Para .ar usa socket directo a whois.nic.ar:43
    - Para .com / .net usa rdap.verisign.com directo
    - Para el resto usa rdap.org
    """
    if dominio.endswith(".ar"):
        return consultar_whois_ar(dominio)

    if dominio.endswith(".com"):
        url = f"https://rdap.verisign.com/com/v1/domain/{dominio}"
    elif dominio.endswith(".net"):
        url = f"https://rdap.verisign.com/net/v1/domain/{dominio}"
    else:
        url = f"https://rdap.org/domain/{dominio}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DomainHunter/2.0"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                events = data.get("events", [])
                statuses = data.get("status", [])
                
                expiracion = None
                creacion = None
                
                for event in events:
                    action = event.get("eventAction")
                    date_str = event.get("eventDate")
                    if action == "expiration" and date_str:
                        expiracion = date_str
                    elif action == "registration" and date_str:
                        creacion = date_str
                        
                return {
                    "exito": True,
                    "disponible": False,
                    "creacion": creacion,
                    "expiracion": expiracion,
                    "statuses": statuses
                }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"exito": True, "disponible": True}
    except Exception:
        pass
        
    return {"exito": False}

def analizar_dominio(dominio: str) -> dict:
    """
    Analiza un dominio individual combinando resolución DNS, WHOIS/RDAP y Valuación AdSense.
    """
    resuelve_dns = chequear_resolucion_dns(dominio)
    rdap_res = consultar_rdap(dominio)
    valuacion = calcular_valuacion_dominio(dominio)
    
    estado = "DESCONOCIDO"
    fecha_expiracion = None
    fecha_creacion = None
    dias_restantes = None
    statuses = rdap_res.get("statuses", [])
    status_str = ", ".join(statuses).lower()
    
    if rdap_res.get("disponible"):
        estado = "DISPONIBLE"
    elif "pending delete" in status_str:
        estado = "PENDING_DELETE"
    elif "redemption" in status_str:
        estado = "REDEMPTION_PERIOD"
    elif resuelve_dns:
        estado = "REGISTRADO"
    else:
        estado = "DISPONIBLE / INACTIVO"

    if rdap_res.get("expiracion"):
        try:
            exp_raw = rdap_res["expiracion"]
            if "T" in exp_raw:
                exp_str = exp_raw.replace("Z", "+00:00")
                dt_exp = datetime.fromisoformat(exp_str)
            else:
                dt_exp = datetime.strptime(exp_raw[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            fecha_expiracion = dt_exp.strftime("%Y-%m-%d")
            
            now = datetime.now(timezone.utc)
            dias_restantes = (dt_exp - now).days
            
            if estado not in ["PENDING_DELETE", "REDEMPTION_PERIOD"]:
                if dias_restantes < 0:
                    estado = "EXPIRADO"
                elif dias_restantes <= 60:
                    estado = "PROXIMO_A_VENCER"
                elif estado != "DISPONIBLE":
                    estado = "REGISTRADO"
        except Exception:
            pass

    if rdap_res.get("creacion"):
        try:
            cre_raw = rdap_res["creacion"]
            fecha_creacion = cre_raw[:10]
        except Exception:
            pass

    return {
        "dominio": dominio,
        "estado": estado,
        "resuelve_dns": resuelve_dns,
        "fecha_creacion": fecha_creacion,
        "fecha_expiracion": fecha_expiracion,
        "dias_restantes": dias_restantes,
        "titular": rdap_res.get("titular"),
        "valuacion": valuacion,
        "link_compra": obtener_link_registro(dominio),
        "link_backorder": obtener_link_backorder(dominio)
    }

def analizar_lote_dominios(dominios: list[str], max_workers: int = 4) -> list[dict]:
    """
    Procesa una lista de dominios respetando los límites de tasa de NIC.ar y Verisign.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        resultados = list(executor.map(analizar_dominio, dominios))
    return resultados

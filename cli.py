import sys
import os
import argparse
from core.cleaner import limpiar_y_extraer_dominios, analizar_estadisticas_extraccion
from core.checker import analizar_lote_dominios
from core.exporter import exportar_a_csv, exportar_a_json

def main():
    parser = argparse.ArgumentParser(description="Analizador y Verificador de Dominios Vencidos y Disponibles")
    parser.add_argument("-i", "--input", help="Ruta a un archivo .txt o .csv con texto sucio o lista de dominios.")
    parser.add_argument("-t", "--texto", help="Cadena de texto directa a analizar.")
    parser.add_argument("-o", "--output", help="Ruta base para guardar el resultado (ej. resultado.csv)")
    parser.add_argument("--json", action="store_true", help="Guardar también en formato JSON")
    
    args = parser.parse_args()
    
    texto_raw = ""
    if args.input:
        if os.path.exists(args.input):
            with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
                texto_raw = f.read()
        else:
            print(f"[!] Error: El archivo '{args.input}' no existe.")
            sys.exit(1)
    elif args.texto:
        texto_raw = args.texto
    else:
        print("==================================================")
        print("   ANALIZADOR DE DOMINIOS VENCIDOS & DISPONIBLES  ")
        print("==================================================")
        print("Pega el texto sucio o lista de dominios (presiona Ctrl+Z o Ctrl+D en una línea vacía al terminar):")
        try:
            texto_raw = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nOperación cancelada.")
            sys.exit(0)

    if not texto_raw.strip():
        print("[!] No se proporcionó texto para analizar.")
        sys.exit(0)

    print("\n[1/3] Extrayendo y limpiando dominios...")
    stats = analizar_estadisticas_extraccion(texto_raw)
    dominios = stats["dominios"]
    
    print(f" -> Se encontraron {len(dominios)} dominios únicos de {stats['total_lineas_procesadas']} líneas procesadas.")
    print(" -> Desglose por extensión:", stats["desglose_tlds"])
    
    if not dominios:
        print("[!] No se encontraron dominios válidos.")
        sys.exit(0)

    print("\n[2/3] Verificando estado y vencimientos en red (RDAP/DNS)...")
    resultados = analizar_lote_dominios(dominios)
    
    print("\n" + "="*80)
    print(f"{'DOMINIO':<30} | {'ESTADO':<22} | {'EXPIRACIÓN':<12} | {'DNS'}")
    print("="*80)
    
    for r in resultados:
        exp = r['fecha_expiracion'] if r['fecha_expiracion'] else "N/D"
        dns = "OK" if r['resuelve_dns'] else "NO"
        print(f"{r['dominio']:<30} | {r['estado']:<22} | {exp:<12} | {dns}")
    print("="*80)

    if args.output:
        print("\n[3/3] Guardando reportes...")
        csv_file = exportar_a_csv(resultados, args.output)
        print(f" -> Guardado CSV en: {csv_file}")
        if args.json:
            json_path = os.path.splitext(args.output)[0] + ".json"
            json_file = exportar_a_json(resultados, json_path)
            print(f" -> Guardado JSON en: {json_file}")
            
    print("\n¡Análisis finalizado con éxito!")

if __name__ == "__main__":
    main()

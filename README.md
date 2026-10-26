# 🌐 Analizador de Dominios Vencidos & Disponibles (`DomainHunter`)

Herramienta completa para la extracción, limpieza, verificación WHOIS/RDAP/DNS y análisis de vencimiento de dominios web (especialmente orientada a dominios de Argentina `.com.ar`, `.net.ar`, `.org.ar`, `.ar` y gTLDs globales como `.com`, `.net`, `.io`, etc.).

---

## 🚀 Características

- **Limpiador & Extractor Avanzado**: Extrae automáticamente dominios válidos a partir de textos sucios (logs, listas, notas, HTML copiado), elimina duplicados y normaliza URLs (quita `http://`, `https://`, `www.`, rutas y sufijos).
- **Verificación en Red**: Consulta registros RDAP públicos y resolución de nombres DNS para determinar si un dominio está:
  - 🟢 **DISPONIBLE / LIBRE**
  - 🟡 **VENCIDO / PROXIMO A VENCER**
  - 🔴 **REGISTRADO / ACTIVO**
- **Interfaz Web Interactiva**: Dashboard visual en modo oscuro con métricas en tiempo real, filtros por estado, cuadro de búsqueda instantáneo y enlaces directos a registrar (NIC Argentina / registradores globales).
- **Consola CLI**: Script interactivo para ejecutar desde la terminal sin abrir navegador.
- **Exportación de Reportes**: Guarda resultados en **CSV** y **JSON**.

---

## 🛠️ Instalación y Requisitos

### Requisitos
- **Python 3.9+**

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

---

## 💻 Uso de la Aplicación Web (Dashboard)

Para iniciar el Dashboard interactivo en tu navegador:

```bash
python main.py
```

Luego abre tu navegador en:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🖥️ Uso por Consola (CLI)

### 1. Analizar texto pegado directamente:
```bash
python cli.py
```

### 2. Analizar un archivo `.txt` o `.csv` y guardar en CSV:
```bash
python cli.py -i input_ejemplo.txt -o reporte.csv --json
```

---

## 📁 Estructura del Proyecto

```text
analizador-dominios/
├── core/
│   ├── __init__.py
│   ├── cleaner.py      # Extractor y limpiador regex
│   ├── checker.py      # Verificador de vencimiento (RDAP / DNS)
│   └── exporter.py     # Generador de CSV / JSON
├── static/
│   ├── index.html      # UI Dashboard Web
│   ├── styles.css      # Estilos visuales Glassmorphism
│   └── app.js          # Lógica frontend interactiva
├── main.py             # Servidor API FastAPI
├── cli.py              # Herramienta interactiva por consola
├── requirements.txt    # Dependencias del proyecto
├── input_ejemplo.txt   # Texto de prueba
└── README.md           # Documentación del proyecto
```

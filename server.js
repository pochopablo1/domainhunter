const http = require('http');
const fs = require('fs');
const path = require('path');
const dns = require('dns').promises;
const https = require('https');
const net = require('net');

const PORT = process.env.PORT || 8000;
const DOMAIN_REGEX = /(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com\.ar|net\.ar|org\.ar|gob\.ar|edu\.ar|tur\.ar|mil\.ar|co\.ar|ar|com|net|org|io|dev|co|xyz|info|biz|online|tech|store|es|us|ai))/gi;

const PALABRAS_ALTO_VALOR = [
    "casas", "autos", "auto", "propiedades", "remate", "remates", "abogado", "abogados",
    "tienda", "shop", "crypto", "bitcoin", "seguros", "salud", "medico", "turismo",
    "hotel", "hoteles", "pampa", "homes", "viajes", "credito", "creditos", "prestamo", "banco", "finanzas",
    "cordoba", "rosario", "caba", "mendoza", "bienes", "raices", "tech", "digital",
    "market", "pyme", "barrio", "nordelta", "viviendas", "inmobiliaria", "vuelos",
    "club", "moda", "estilo", "ofertas", "descuentos", "envios", "express", "online",
    "vinos", "catering", "talleres", "contadores", "motos", "alquileres", "rent", "loan", "care", "realty"
];

function calcularValuacion(dominio) {
    const partes = dominio.toLowerCase().trim().split('.');
    const nombre = partes[0];
    const tld = partes.slice(1).join('.');

    let score = 50;

    const len = nombre.length;
    if (len <= 5) score += 30;
    else if (len <= 8) score += 22;
    else if (len <= 12) score += 12;
    else if (len >= 16) score -= 15;

    if (tld === 'com') score += 18;
    else if (tld === 'com.ar' || tld === 'ar') score += 14;
    else if (['io', 'ai', 'co', 'es'].includes(tld)) score += 12;
    else if (['net', 'org', 'net.ar'].includes(tld)) score += 6;

    const kwsEncontradas = PALABRAS_ALTO_VALOR.filter(kw => nombre.includes(kw));
    if (kwsEncontradas.length > 0) score += Math.min(kwsEncontradas.length * 15, 30);

    if (nombre.includes('-')) score -= 20;
    if (/\d/.test(nombre)) score -= 10;

    const finalScore = Math.max(10, Math.min(99, score));

    let categoria = "⚪ ESTÁNDAR";
    let estimacionUsd = "$20 - $150 USD";
    let color = "#9ca3af";

    if (finalScore >= 75) {
        categoria = "🏆 PREMIUM";
        estimacionUsd = "$500 - $3,500+ USD";
        color = "#10b981";
    } else if (finalScore >= 50) {
        categoria = "⭐ OPORTUNIDAD";
        estimacionUsd = "$150 - $500 USD";
        color = "#f59e0b";
    }

    let adsense = {
        nicho: "Portal de Servicios & Directorio SEO",
        cpc_adsense: "$0.50 - $2.00 USD / clic",
        herramienta_estrella: "Calculadora de Presupuestos Online + Comparador Interactivo"
    };
    if (/auto|moto|taller|car/.test(nombre)) {
        adsense = {
            nicho: "Automotor & Seguros Vehiculares",
            cpc_adsense: "$0.80 - $3.20 USD / clic",
            herramienta_estrella: "Valuador Oficial + Calculadora DNRPA y Patentes + Mapa de Talleres/VTV"
        };
    } else if (/propiedad|inmobiliaria|alquiler|casa|home|realty|miami|rent/.test(nombre)) {
        adsense = {
            nicho: "Real Estate, Alquileres & Hipotecas",
            cpc_adsense: "$1.50 - $6.00 USD / clic",
            herramienta_estrella: "Calculadora de Alquiler (ICL/IPC) + Gastos de Escrituración e Hipoteca"
        };
    } else if (/credit|prestamo|finanza|inversion|franquicia|contador|exportacion|loan/.test(nombre)) {
        adsense = {
            nicho: "Finanzas, Impuestos & Comercio Exterior",
            cpc_adsense: "$2.00 - $12.00 USD / clic",
            herramienta_estrella: "Simulador de Cuotas / Calculadora de Monotributo e Impuestos de Aduana"
        };
    } else if (/salud|clinica|medic|dental|care|nutricion/.test(nombre)) {
        adsense = {
            nicho: "Salud, Clínicas & Medicina Prepaga",
            cpc_adsense: "$1.20 - $5.50 USD / clic",
            herramienta_estrella: "Comparador de Planes de Prepagas + Cartilla Interactiva"
        };
    } else if (/vino|catering|evento|turismo|viaje|vuelo|hotel/.test(nombre)) {
        adsense = {
            nicho: "Turismo, Gastronomía & Eventos",
            cpc_adsense: "$0.60 - $2.40 USD / clic",
            herramienta_estrella: "Calculadora de Bebidas y Presupuesto para Eventos / Directorio"
        };
    }

    return {
        score: finalScore,
        categoria,
        estimacion_usd: estimacionUsd,
        keywords_detectadas: kwsEncontradas,
        color,
        adsense
    };
}

function extraerDominios(textoRaw) {
    if (!textoRaw) return [];
    const matches = textoRaw.toLowerCase().match(DOMAIN_REGEX) || [];
    const limpios = [];
    const vistos = new Set();

    for (let rawMatch of matches) {
        let dom = rawMatch.replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('/')[0].split('?')[0].trim();
        dom = dom.replace(/[^\w.-]/g, '');
        if (dom && !vistos.has(dom)) {
            vistos.add(dom);
            limpios.push(dom);
        }
    }
    return limpios;
}

// Consulta directa WHOIS puerto 43 para NIC Argentina (.ar)
function consultarWhoisAr(dominio) {
    return new Promise((resolve) => {
        let data = '';
        const socket = net.createConnection(43, 'whois.nic.ar', () => {
            socket.write(dominio + '\r\n');
        });
        socket.on('data', chunk => data += chunk);
        socket.on('end', () => {
            if (data.includes('El dominio no se encuentra registrado')) {
                return resolve({ exito: true, disponible: true });
            }
            const regMatch = data.match(/registered:\s*([0-9-]+)/);
            const expMatch = data.match(/expire:\s*([0-9-]+)/);
            const nameMatch = data.match(/name:\s*(.+)/);
            if (expMatch || regMatch) {
                resolve({
                    exito: true,
                    disponible: false,
                    creacion: regMatch ? regMatch[1] : null,
                    expiracion: expMatch ? expMatch[1] : null,
                    titular: nameMatch ? nameMatch[1].trim() : null
                });
            } else {
                resolve({ exito: false });
            }
        });
        socket.on('error', () => resolve({ exito: false }));
        socket.setTimeout(4500, () => {
            socket.destroy();
            resolve({ exito: false });
        });
    });
}

// Consulta RDAP con soporte de redirecciones y Verisign directo para Exterior (.com / .net / global)
function consultarRDAP(dominio) {
    if (dominio.endsWith('.ar')) {
        return consultarWhoisAr(dominio);
    }

    let initialUrl = `https://rdap.org/domain/${dominio}`;
    if (dominio.endsWith('.com')) {
        initialUrl = `https://rdap.verisign.com/com/v1/domain/${dominio}`;
    } else if (dominio.endsWith('.net')) {
        initialUrl = `https://rdap.verisign.com/net/v1/domain/${dominio}`;
    }

    return new Promise((resolve) => {
        const fetchUrl = (url, redirects = 0) => {
            if (redirects > 3) return resolve({ exito: false });
            const req = https.get(url, { headers: { 'User-Agent': 'DomainHunter/2.0' } }, (res) => {
                if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                    return fetchUrl(res.headers.location, redirects + 1);
                }
                let body = '';
                res.on('data', chunk => body += chunk);
                res.on('end', () => {
                    if (res.statusCode === 200) {
                        try {
                            const data = JSON.parse(body);
                            let expiracion = null;
                            let creacion = null;
                            if (data.events) {
                                for (let evt of data.events) {
                                    if (evt.eventAction === 'expiration') expiracion = evt.eventDate;
                                    if (evt.eventAction === 'registration') creacion = evt.eventDate;
                                }
                            }
                            resolve({ exito: true, expiracion, creacion, statusList: data.status || [] });
                        } catch (e) {
                            resolve({ exito: false });
                        }
                    } else if (res.statusCode === 404) {
                        resolve({ exito: true, disponible: true });
                    } else {
                        resolve({ exito: false });
                    }
                });
            });
            req.on('error', () => resolve({ exito: false }));
            req.setTimeout(4500, () => {
                req.destroy();
                resolve({ exito: false });
            });
        };
        fetchUrl(initialUrl);
    });
}

async function analizarDominio(dominio) {
    let resuelveDNS = false;
    try {
        await dns.lookup(dominio);
        resuelveDNS = true;
    } catch (e) {
        resuelveDNS = false;
    }

    const rdap = await consultarRDAP(dominio);
    const valuacion = calcularValuacion(dominio);

    let estado = "DESCONOCIDO";
    let fechaExpiracion = null;
    let fechaCreacion = null;
    let diasRestantes = null;

    if (rdap.disponible) {
        estado = "DISPONIBLE";
    } else if (resuelveDNS) {
        estado = "REGISTRADO";
    } else {
        estado = "DISPONIBLE / INACTIVO";
    }

    if (rdap.expiracion) {
        try {
            const expDate = new Date(rdap.expiracion);
            fechaExpiracion = expDate.toISOString().split('T')[0];
            diasRestantes = Math.ceil((expDate - new Date()) / (1000 * 60 * 60 * 24));
            if (diasRestantes < 0) estado = "EXPIRADO";
            else if (diasRestantes <= 60) estado = "PROXIMO_A_VENCER";
            else if (estado !== "DISPONIBLE") estado = "REGISTRADO";
        } catch (e) {}
    }

    if (rdap.creacion) {
        try {
            fechaCreacion = new Date(rdap.creacion).toISOString().split('T')[0];
        } catch (e) {}
    }

    const linkCompra = dominio.endsWith(".ar")
        ? `https://nic.ar`
        : `https://www.godaddy.com/domainsearch/find?domainToCheck=${dominio}`;

    return {
        dominio,
        estado,
        resuelve_dns: resuelveDNS,
        fecha_creacion: fechaCreacion,
        fecha_expiracion: fechaExpiracion,
        dias_restantes: diasRestantes,
        titular: rdap.titular || null,
        valuacion,
        link_compra: linkCompra
    };
}

async function ejecutarRadarAutopiloto() {
    const candidatos = [
        // Argentina (.com.ar)
        "propiedades.com.ar", "catering.com.ar", "vinos.com.ar", "talleres.com.ar",
        "contadores.com.ar", "motosusadas.com.ar", "inversiones.com.ar", "remates.com.ar",
        "autosusados.com.ar", "alquileres.com.ar", "inmobiliariaexpress.com.ar",
        // Exterior (.com)
        "miamirealtyhub.com", "rentfast.com", "creditpro.com", "petcare.com",
        "learnfast.com", "cryptopulse.com", "carvaluehub.com", "insurequoteai.com",
        "madridhomespro.com", "spainautohub.com"
    ];

    const domsUnicos = Array.from(new Set(candidatos));
    const resultados = [];
    for (const d of domsUnicos) {
        resultados.push(await analizarDominio(d));
    }

    const oportunidades = resultados.filter(r =>
        r.estado === "EXPIRADO" || r.estado === "PROXIMO_A_VENCER" || r.estado.includes("DISPONIBLE")
    );

    if (oportunidades.length === 0) {
        return { exito: false, mensaje: "No se encontraron dominios por vencer o disponibles." };
    }

    oportunidades.sort((a, b) => (b.valuacion?.score || 0) - (a.valuacion?.score || 0));

    const mejorOpcion = oportunidades[0];
    const val = mejorOpcion.valuacion || {};

    const justificacion = `El dominio '${mejorOpcion.dominio}' se encuentra en estado ${mejorOpcion.estado} (Vencimiento: ${mejorOpcion.fecha_expiracion || 'Libre hoy'}). Tiene un Score Comercial de ${val.score || 0} pts y un valor estimado de mercado de ${val.estimacion_usd || '$300 - $2,500+ USD'}.`;

    return {
        exito: true,
        total_escaneados: resultados.length,
        total_disponibles: oportunidades.length,
        mejor_oportunidad: mejorOpcion,
        justificacion,
        otros_disponibles: resultados
    };
}

const server = http.createServer(async (req, res) => {
    if (req.method === 'POST' && req.url === '/api/extract') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const { texto_raw } = JSON.parse(body || '{}');
                const dominios = extraerDominios(texto_raw || '');
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    total_extraidos: dominios.length,
                    total_lineas_procesadas: (texto_raw || '').split('\n').length,
                    dominios
                }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'JSON inválido' }));
            }
        });
    } else if (req.method === 'POST' && req.url === '/api/analyze') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const payload = JSON.parse(body || '{}');
                const doms = payload.dominios || extraerDominios(payload.texto_raw || '');
                const resultados = [];
                for (const d of doms) {
                    resultados.push(await analizarDominio(d));
                }

                const libres = resultados.filter(r => r.estado.includes("DISPONIBLE")).length;
                const vencidos = resultados.filter(r => r.estado === "EXPIRADO" || r.estado === "PROXIMO_A_VENCER").length;
                const registrados = resultados.filter(r => r.estado === "REGISTRADO").length;
                const premium = resultados.filter(r => r.valuacion.score >= 75).length;

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    total: resultados.length,
                    resumen: { disponibles: libres, proximos_vencer_o_expirados: vencidos, registrados, premium },
                    resultados
                }));
            } catch (e) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
    } else if (req.method === 'POST' && req.url === '/api/generate-niche') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const { keyword } = JSON.parse(body || '{}');
                const kw = (keyword || '').toLowerCase().replace(/[^a-z0-9]/g, '');
                const sufijos = ['', 'hoy', 'online', 'pro', 'ya', 'hub'];
                const candidatos = [];
                sufijos.forEach(s => {
                    candidatos.push(`${kw}${s}.com.ar`);
                    candidatos.push(`${kw}${s}.com`);
                });
                const resultados = [];
                for (const d of candidatos) {
                    resultados.push(await analizarDominio(d));
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ total: resultados.length, resultados }));
            } catch (e) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
    } else if (req.method === 'POST' && req.url === '/api/radar') {
        try {
            const resRadar = await ejecutarRadarAutopiloto();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(resRadar));
        } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
    } else if (req.method === 'POST' && req.url === '/api/export/csv') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const payload = JSON.parse(body || '{}');
                const doms = payload.dominios || extraerDominios(payload.texto_raw || '');
                const resultados = [];
                for (const d of doms) {
                    resultados.push(await analizarDominio(d));
                }

                let csvContent = "dominio,estado,score_valuacion,categoria_valor,estimacion_usd,resuelve_dns,fecha_expiracion,link_compra\n";
                resultados.forEach(r => {
                    csvContent += `"${r.dominio}","${r.estado}","${r.valuacion.score}","${r.valuacion.categoria}","${r.valuacion.estimacion_usd}","${r.resuelve_dns}","${r.fecha_expiracion || ''}","${r.link_compra}"\n`;
                });

                res.writeHead(200, {
                    'Content-Type': 'text/csv',
                    'Content-Disposition': 'attachment; filename=analisis_dominios_valuados.csv'
                });
                res.end(csvContent);
            } catch (e) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
    } else {
        let filePath = req.url === '/' ? '/static/index.html' : req.url;
        filePath = path.join(__dirname, filePath);

        const ext = path.extname(filePath);
        const mimeTypes = { '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript' };

        fs.readFile(filePath, (err, content) => {
            if (err) {
                res.writeHead(404);
                res.end('Archivo no encontrado');
            } else {
                res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
                res.end(content, 'utf-8');
            }
        });
    }
});

server.listen(PORT, () => {
    console.log(`\n==================================================`);
    console.log(`🌐 Servidor iniciado con éxito en http://localhost:${PORT}`);
    console.log(`==================================================\n`);
});

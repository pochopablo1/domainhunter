const net = require('net');
const tls = require('tls');
const https = require('https');
const fs = require('fs');
const path = require('path');

const sleep = ms => new Promise(r => setTimeout(r, ms));

// Cargar .env local
function loadEnv() {
    const envPath = path.join(__dirname, '.env');
    if (fs.existsSync(envPath)) {
        const lines = fs.readFileSync(envPath, 'utf-8').split(/\r?\n/);
        for (const l of lines) {
            const trimmed = l.trim();
            if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
                const idx = trimmed.indexOf('=');
                const k = trimmed.slice(0, idx).trim();
                const v = trimmed.slice(idx + 1).trim();
                if (!process.env[k]) process.env[k] = v;
            }
        }
    }
}
loadEnv();

const EMAIL_FROM = process.env.SNIPER_EMAIL_FROM || 'pablo.santilli7@gmail.com';
const EMAIL_PASS = (process.env.SNIPER_EMAIL_PASS || '').replace(/\s+/g, '');
const EMAIL_TO = process.env.SNIPER_EMAIL_TO || 'pablo.santilli7@gmail.com';

// Lista VIP de seguimiento (Watchlist de máxima ganancia + Plan AdSense)
const WATCHLIST_AR = [
    {
        domain: 'propiedades.com.ar',
        estUsd: '$3,000 - $8,000 USD',
        cpc: '$1.50 - $6.00 USD/clic',
        portal: 'Calculadora de Alquiler (ICL/IPC) + Gastos de Escrituración e Hipoteca',
        nota: 'Venció 14/10/2026 - Ventana de caída: 13/11 al 28/11'
    },
    {
        domain: 'catering.com.ar',
        estUsd: '$1,000 - $2,000 USD',
        cpc: '$0.80 - $2.50 USD/clic',
        portal: 'Calculadora de Bebidas y Presupuesto para Eventos / Directorio de Catering',
        nota: 'Venció 24/10/2026 - Ventana de caída: 23/11 al 08/12'
    },
    {
        domain: 'vinos.com.ar',
        estUsd: '$1,500 - $3,000 USD',
        cpc: '$0.70 - $2.20 USD/clic',
        portal: 'Guía de Bodegas, Catas & Comparador de Precios de Vinos Argentinos',
        nota: 'Vence 07/11/2026 - Sin web activa'
    },
    {
        domain: 'franquicias.com.ar',
        estUsd: '$1,500 - $3,500 USD',
        cpc: '$2.00 - $7.00 USD/clic',
        portal: 'Calculadora de Retorno de Inversión (ROI) + Catálogo de Franquicias Argentinas',
        nota: 'Vence 28/11/2026 - Creado en 1997, sin web activa'
    },
    {
        domain: 'clinicas.com.ar',
        estUsd: '$1,200 - $2,500 USD',
        cpc: '$1.50 - $5.50 USD/clic',
        portal: 'Comparador de Prepagas (OSDE, Swiss Medical) + Cartilla de Clínicas y Guardia',
        nota: 'Vence 03/12/2026 - Sin web activa'
    },
    {
        domain: 'talleres.com.ar',
        estUsd: '$800 - $1,500 USD',
        cpc: '$0.90 - $3.00 USD/clic',
        portal: 'Estimador de Costo de Service y Chapa/Pintura + Mapa de Talleres y VTV',
        nota: 'Vence 04/12/2026 - NS: 0 (Abandonado)'
    },
    {
        domain: 'contadores.com.ar',
        estUsd: '$900 - $2,000 USD',
        cpc: '$2.00 - $8.00 USD/clic',
        portal: 'Calculadora de Monotributo, Ganancias y Honorarios Contables',
        nota: 'Vence 09/12/2026 - NS: 0 (Abandonado)'
    },
    {
        domain: 'exportaciones.com.ar',
        estUsd: '$600 - $1,500 USD',
        cpc: '$1.80 - $6.50 USD/clic',
        portal: 'Calculadora de Retenciones, Dólar Blend y Aranceles de Comercio Exterior',
        nota: 'Monitoreo de disponibilidad inmediata'
    },
    {
        domain: 'motosusadas.com.ar',
        estUsd: '$400 - $900 USD',
        cpc: '$0.80 - $2.80 USD/clic',
        portal: 'Valuador Oficial de Motos + Calculadora de Transferencia DNRPA y Seguros de Moto',
        nota: 'Monitoreo de disponibilidad inmediata'
    }
];

const WATCHLIST_COM = [
    {
        domain: 'miamirealtyhub.com',
        estUsd: '$500 - $1,800 USD',
        cpc: '$3.50 - $14.00 USD/clic',
        portal: 'Miami Mortgage & HOA Calculator + Investment ROI Finder',
        nota: 'En Redemption Period (Venció 28/08/2026) - A días de caer libre'
    },
    {
        domain: 'rentfast.com',
        estUsd: '$3,000 - $8,000 USD',
        cpc: '$2.50 - $9.00 USD/clic',
        portal: 'Rent Affordability Calculator + Tenant Screening & Lease Guide',
        nota: 'Vence 06/12/2026 - Creado en 1999, sin DNS activo'
    },
    {
        domain: 'creditpro.com',
        estUsd: '$5,000 - $15,000 USD',
        cpc: '$6.00 - $25.00 USD/clic',
        portal: 'Credit Score Simulator + Debt Payoff & Loan APR Calculator',
        nota: 'Vence 21/12/2026 - Creado en 1998, estado active simple, sin DNS'
    },
    {
        domain: 'learnfast.com',
        estUsd: '$2,500 - $6,000 USD',
        cpc: '$2.00 - $8.00 USD/clic',
        portal: 'AI Certification & Online Degree ROI Calculator',
        nota: 'Vence 26/12/2026 - Creado en 2003, sin DNS'
    },
    {
        domain: 'dentalcarepro.com',
        estUsd: '$600 - $1,500 USD',
        cpc: '$3.00 - $12.00 USD/clic',
        portal: 'Dental Implant & Invisalign Cost Estimator + Insurance Finder',
        nota: 'Vence 31/12/2026 - 1 año de antigüedad, sin DNS'
    }
];

function whoisAr(domain) {
    return new Promise((resolve) => {
        let data = '';
        const socket = net.createConnection(43, 'whois.nic.ar', () => {
            socket.write(domain + '\r\n');
        });
        socket.on('data', chunk => data += chunk);
        socket.on('end', () => {
            if (data.includes('El dominio no se encuentra registrado')) {
                return resolve({ domain, available: true, status: 'DISPONIBLE_YA' });
            }
            const regMatch = data.match(/registered:\s*([0-9-]+)/);
            const expMatch = data.match(/expire:\s*([0-9-]+)/);
            const nameMatch = data.match(/name:\s*(.+)/);
            resolve({
                domain,
                available: false,
                reg: regMatch ? regMatch[1] : null,
                exp: expMatch ? expMatch[1] : null,
                holder: nameMatch ? nameMatch[1].trim() : null
            });
        });
        socket.on('error', () => resolve({ domain, error: true }));
        socket.setTimeout(4500, () => { socket.destroy(); resolve({ domain, error: true }); });
    });
}

function rdapCom(domain) {
    return new Promise((resolve) => {
        const url = `https://rdap.verisign.com/com/v1/domain/${domain}`;
        const req = https.get(url, { headers: { 'User-Agent': 'DomainHunterSniper/2.0' } }, (res) => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        const data = JSON.parse(body);
                        let exp = null, reg = null;
                        for (const ev of (data.events || [])) {
                            if (ev.eventAction === 'expiration') exp = ev.eventDate.split('T')[0];
                            if (ev.eventAction === 'registration') reg = ev.eventDate.split('T')[0];
                        }
                        resolve({
                            domain,
                            available: false,
                            reg,
                            exp,
                            statuses: data.status || []
                        });
                    } catch (e) { resolve({ domain, error: true }); }
                } else if (res.statusCode === 404) {
                    resolve({ domain, available: true, status: 'DISPONIBLE_YA' });
                } else {
                    resolve({ domain, error: true });
                }
            });
        });
        req.on('error', () => resolve({ domain, error: true }));
        req.setTimeout(4500, () => { req.destroy(); resolve({ domain, error: true }); });
    });
}

function sendGmailSmtp(from, pass, to, subject, htmlBody) {
    return new Promise((resolve) => {
        if (!from || !pass || !to) {
            console.log('ℹ️ Faltan credenciales de email en .env');
            return resolve(false);
        }
        const socket = tls.connect(465, 'smtp.gmail.com', { rejectUnauthorized: false });
        let step = 0;
        const authB64 = Buffer.from(`\0${from}\0${pass}`).toString('base64');

        socket.on('data', (chunk) => {
            const resp = chunk.toString();
            if (step === 0 && resp.startsWith('220')) {
                step = 1;
                socket.write(`EHLO domainhunter.local\r\n`);
            } else if (step === 1 && resp.includes('250 ')) {
                step = 2;
                socket.write(`AUTH PLAIN ${authB64}\r\n`);
            } else if (step === 2 && resp.startsWith('235')) {
                step = 3;
                socket.write(`MAIL FROM:<${from}>\r\n`);
            } else if (step === 3 && resp.startsWith('250')) {
                step = 4;
                socket.write(`RCPT TO:<${to}>\r\n`);
            } else if (step === 4 && resp.startsWith('250')) {
                step = 5;
                socket.write(`DATA\r\n`);
            } else if (step === 5 && resp.startsWith('354')) {
                step = 6;
                const subjB64 = Buffer.from(subject, 'utf-8').toString('base64');
                const msg = [
                    `From: "DomainHunter Sniper" <${from}>`,
                    `To: <${to}>`,
                    `Subject: =?UTF-8?B?${subjB64}?=`,
                    `MIME-Version: 1.0`,
                    `Content-Type: text/html; charset=UTF-8`,
                    ``,
                    htmlBody,
                    `.`,
                    ``
                ].join('\r\n');
                socket.write(msg);
            } else if (step === 6 && resp.startsWith('250')) {
                step = 7;
                socket.write(`QUIT\r\n`);
                socket.end();
                console.log(`📧 ¡Email HTML enviado con éxito a ${to}!`);
                resolve(true);
            } else if (/^[45]\d\d/.test(resp)) {
                console.log('⚠️ Respuesta SMTP:', resp.trim());
                socket.end();
                resolve(false);
            }
        });
        socket.on('error', (err) => {
            console.log('⚠️ Error conexión SMTP:', err.message);
            resolve(false);
        });
    });
}

function buildEmailHtml(report) {
    const alertasHtml = report.alertas_compra_inmediata.map(a => `
        <div style="background:#ecfdf5; border:2px solid #10b981; border-radius:12px; padding:18px; margin-bottom:16px;">
            <div style="font-size:12px; font-weight:800; color:#047857; text-transform:uppercase;">
                🟢 ¡LISTO PARA COMPRAR AHORA MISMO! (${a.region})
            </div>
            <h2 style="margin:6px 0; color:#0f172a; font-size:22px;">${a.domain}</h2>
            <p style="margin:4px 0; font-size:14px; color:#334155;">
                💰 <strong>Valor Dominio:</strong> ${a.estUsd} &nbsp;|&nbsp;
                📈 <strong>CPC AdSense:</strong> ${a.cpc}
            </p>
            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; margin:10px 0; font-size:13px; color:#1e293b;">
                <strong>⚡ Plan de Portal AdSense listo para armar:</strong><br>
                ${a.portal}
            </div>
            <a href="${a.link}" target="_blank"
               style="display:inline-block; background:#10b981; color:#ffffff; text-decoration:none; font-weight:800; padding:12px 20px; border-radius:8px; font-size:14px; margin-top:6px;">
               🛒 REGISTRAR ${a.domain.toUpperCase()} AHORA ➔
            </a>
        </div>
    `).join('');

    const todos = [...report.argentina, ...report.exterior];
    const filas = todos.map(x => `
        <tr style="border-bottom:1px solid #e2e8f0;">
            <td style="padding:10px; font-weight:700; color:#0f172a;">
                ${x.domain}
                <div style="font-size:11px; color:#64748b; font-weight:400;">💡 ${x.portal}</div>
            </td>
            <td style="padding:10px; font-size:12px;">${x.estado}</td>
            <td style="padding:10px; font-size:12px;">${x.exp || 'LIBRE'}</td>
            <td style="padding:10px; font-size:12px; color:#047857; font-weight:700;">${x.cpc}</td>
        </tr>
    `).join('');

    return `
    <html>
    <body style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px; color:#0f172a;">
        <div style="max-width:680px; margin:0 auto; background:#ffffff; border-radius:16px; padding:24px; border:1px solid #e2e8f0;">
            <h1 style="margin-top:0; color:#0f172a; font-size:22px;">🎯 DomainHunter Sniper — Reporte en Vivo</h1>
            <p style="color:#64748b; font-size:14px;">Monitoreo automático de dominios de alto CPC para portales Google AdSense.</p>
            ${alertasHtml}
            <h3 style="margin-top:24px; color:#0f172a;">⏳ Cuenta Regresiva Watchlist (Argentina & Exterior)</h3>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f1f5f9; font-size:11px; color:#475569; text-transform:uppercase;">
                        <th style="padding:10px;">Dominio & Idea de Portal AdSense</th>
                        <th style="padding:10px;">Estado</th>
                        <th style="padding:10px;">Vence</th>
                        <th style="padding:10px;">CPC AdSense</th>
                    </tr>
                </thead>
                <tbody>
                    ${filas}
                </tbody>
            </table>
        </div>
    </body>
    </html>`;
}

async function runSniper() {
    const now = new Date();
    const report = {
        timestamp: now.toISOString(),
        alertas_compra_inmediata: [],
        argentina: [],
        exterior: []
    };

    console.log('====================================================');
    console.log('🎯 DOMAINHUNTER SNIPER - CHEQUEO AUTOMATICO EN VIVO');
    console.log('====================================================\n');

    console.log('🇦🇷 Verificando Watchlist Argentina (.com.ar)...');
    for (const item of WATCHLIST_AR) {
        const res = await whoisAr(item.domain);
        let dias = null;
        let estado = 'REGISTRADO';
        if (res.available) {
            estado = '🟢 LIBRE PARA COMPRAR YA';
            report.alertas_compra_inmediata.push({
                domain: item.domain,
                region: 'Argentina (NIC.ar - $8.500 ARS)',
                estUsd: item.estUsd,
                cpc: item.cpc,
                portal: item.portal,
                link: 'https://nic.ar'
            });
        } else if (res.exp) {
            dias = Math.ceil((new Date(res.exp) - now) / 86400000);
            if (dias < 0) estado = `🔥 VENCIDO HACE ${Math.abs(dias)} DÍAS (En Gracia/Caída)`;
            else if (dias <= 45) estado = `🟡 VENCE EN ${dias} DÍAS`;
        }
        const entry = { ...item, ...res, dias, estado };
        report.argentina.push(entry);
        console.log(` - ${item.domain.padEnd(22)} -> ${estado} | Vence: ${res.exp || 'LIBRE'} | CPC: ${item.cpc}`);
        await sleep(120);
    }

    console.log('\n🌍 Verificando Watchlist Exterior (.com)...');
    for (const item of WATCHLIST_COM) {
        const res = await rdapCom(item.domain);
        let dias = null;
        let estado = 'REGISTRADO';
        const stStr = (res.statuses || []).join(', ');
        if (res.available) {
            estado = '🟢 LIBRE PARA COMPRAR YA';
            report.alertas_compra_inmediata.push({
                domain: item.domain,
                region: 'Exterior (.com - $10 USD)',
                estUsd: item.estUsd,
                cpc: item.cpc,
                portal: item.portal,
                link: `https://porkbun.com/checkout/search?q=${item.domain}`
            });
        } else if (stStr.includes('pending delete')) {
            estado = '🚨 PENDING DELETE (Cae en <5 días a las 16:00 hs AR)';
            report.alertas_compra_inmediata.push({
                domain: item.domain,
                region: 'Exterior (.com) - PENDING DELETE',
                estUsd: item.estUsd,
                cpc: item.cpc,
                portal: item.portal,
                link: `https://www.dynadot.com/market/backorder?domain=${item.domain}`
            });
        } else if (stStr.includes('redemption')) {
            dias = res.exp ? Math.ceil((new Date(res.exp) - now) / 86400000) : null;
            estado = `🔥 REDEMPTION PERIOD (${Math.abs(dias || 0)}d post-exp)`;
        } else if (res.exp) {
            dias = Math.ceil((new Date(res.exp) - now) / 86400000);
            if (dias <= 60) estado = `🟡 VENCE EN ${dias} DÍAS`;
        }
        const entry = { ...item, ...res, dias, estado };
        report.exterior.push(entry);
        console.log(` - ${item.domain.padEnd(22)} -> ${estado} | Vence: ${res.exp || 'LIBRE'} | CPC: ${item.cpc}`);
        await sleep(120);
    }

    const outPath = path.join(__dirname, 'watchlist_status.json');
    fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf-8');
    console.log(`\n✅ Reporte guardado en: ${outPath}`);

    const subj = report.alertas_compra_inmediata.length > 0
        ? `🚨 ¡DOMINIO LIBRE PARA COMPRAR YA!: ${report.alertas_compra_inmediata.map(a => a.domain).join(', ')}`
        : `📊 Reporte Diario DomainHunter Sniper (.AR & .COM)`;

    await sendGmailSmtp(EMAIL_FROM, EMAIL_PASS, EMAIL_TO, subj, buildEmailHtml(report));
}

runSniper();

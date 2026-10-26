document.addEventListener('DOMContentLoaded', () => {
    const btnAutopilot = document.getElementById('btnAutopilot');
    const featuredOpportunityCard = document.getElementById('featuredOpportunityCard');
    const featDomain = document.getElementById('featDomain');
    const featScore = document.getElementById('featScore');
    const featPrice = document.getElementById('featPrice');
    const featJustification = document.getElementById('featJustification');
    const featBuyBtn = document.getElementById('featBuyBtn');

    const rawInput = document.getElementById('rawInput');
    const charCounter = document.getElementById('charCounter');
    const btnSample = document.getElementById('btnSample');
    const btnClean = document.getElementById('btnClean');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const btnClear = document.getElementById('btnClear');
    
    const nicheKeyword = document.getElementById('nicheKeyword');
    const btnGenerateNiche = document.getElementById('btnGenerateNiche');
    
    const loader = document.getElementById('loader');
    const loaderText = document.getElementById('loaderText');
    
    const metricsSection = document.getElementById('metricsSection');
    const metricTotal = document.getElementById('metricTotal');
    const metricFree = document.getElementById('metricFree');
    const metricExpiring = document.getElementById('metricExpiring');
    const metricTaken = document.getElementById('metricTaken');
    const metricPremium = document.getElementById('metricPremium');
    
    const resultsSection = document.getElementById('resultsSection');
    const resultsTbody = document.getElementById('resultsTbody');
    const tableSearch = document.getElementById('tableSearch');
    const btnExportCSV = document.getElementById('btnExportCSV');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const navTabs = document.querySelectorAll('.nav-tab');

    let currentResults = [];
    let currentFilter = 'ALL';

    const SAMPLE_TEXT = `Watchlist VIP Argentina & Exterior:
1. propiedades.com.ar
2. catering.com.ar
3. vinos.com.ar
4. talleres.com.ar
5. contadores.com.ar
6. exportaciones.com.ar
7. motosusadas.com.ar
8. miamirealtyhub.com
9. creditpro.com
10. rentfast.com`;

    // Función para copiar al portapapeles y abrir checkout directo
    window.copiarYComprar = function(dominio, url) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(dominio).catch(() => {});
        }
        window.open(url, '_blank');
    };

    // 0. Autopiloto Radar
    if (btnAutopilot) {
        btnAutopilot.addEventListener('click', async () => {
            showLoader('Ejecutando Radar Autopiloto... Escaneando Watchlist VIP y planes AdSense...');
            try {
                const res = await fetch('/api/radar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                hideLoader();

                if (!data.exito || !data.mejor_oportunidad) {
                    return alert(data.mensaje || 'No se encontraron oportunidades disponibles en este momento.');
                }

                const mejor = data.mejor_oportunidad;
                const val = mejor.valuacion || {};
                const ads = val.adsense || {};

                featDomain.textContent = mejor.dominio;
                featScore.textContent = `pts: ${val.score || 95} | ${val.categoria || '🏆 PREMIUM'}`;
                featPrice.textContent = `CPC AdSense: ${ads.cpc_adsense || '$1.50+ USD/clic'} | Valor: ${val.estimacion_usd || '$500+ USD'}`;
                featJustification.textContent = data.justificacion || 'Dominio ideal para armar portal con calculadoras y monetizar con Google AdSense.';
                featBuyBtn.href = mejor.link_compra;
                featBuyBtn.textContent = `🛒 COPIAR Y COMPRAR ${mejor.dominio.toUpperCase()} AHORA`;
                featBuyBtn.onclick = () => {
                    if (navigator.clipboard) navigator.clipboard.writeText(mejor.dominio).catch(() => {});
                };

                featuredOpportunityCard.classList.remove('hidden');

                const listaCompleta = data.otros_disponibles || [mejor];
                procesarRespuestaServidor({ resultados: listaCompleta });

                featuredOpportunityCard.scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                hideLoader();
                alert('Error al ejecutar el Radar Autopiloto.');
            }
        });
    }

    // Navegación por pestañas
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const targetId = tab.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.add('hidden'));
            document.getElementById(targetId).classList.remove('hidden');
        });
    });

    if (rawInput) {
        rawInput.addEventListener('input', () => {
            charCounter.textContent = `${rawInput.value.length} caracteres`;
        });
    }

    if (btnSample) {
        btnSample.addEventListener('click', () => {
            rawInput.value = SAMPLE_TEXT;
            charCounter.textContent = `${rawInput.value.length} caracteres`;
        });
    }

    if (btnClear) {
        btnClear.addEventListener('click', () => {
            rawInput.value = '';
            charCounter.textContent = '0 caracteres';
            metricsSection.classList.add('hidden');
            resultsSection.classList.add('hidden');
            featuredOpportunityCard.classList.add('hidden');
            currentResults = [];
        });
    }

    // 1. Extraer y Limpiar
    if (btnClean) {
        btnClean.addEventListener('click', async () => {
            const text = rawInput.value.trim();
            if (!text) return alert('Ingresa algún texto para extraer dominios.');

            showLoader('Extrayendo y limpiando dominios...');
            try {
                const res = await fetch('/api/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ texto_raw: text })
                });
                const data = await res.json();
                hideLoader();

                if (data.dominios && data.dominios.length > 0) {
                    alert(`✅ Extracción completada:\n- Se encontraron ${data.total_extraidos} dominios únicos.`);
                    rawInput.value = data.dominios.join('\n');
                    charCounter.textContent = `${rawInput.value.length} caracteres`;
                } else {
                    alert('⚠️ No se detectaron dominios válidos en el texto.');
                }
            } catch (err) {
                hideLoader();
                alert('Error al conectar con la API de extracción.');
            }
        });
    }

    // 2. Analizar Vencimientos & Valuar
    if (btnAnalyze) {
        btnAnalyze.addEventListener('click', async () => {
            const text = rawInput.value.trim();
            if (!text) return alert('Ingresa un texto o lista de dominios.');

            showLoader('Analizando WHOIS NIC.ar / Verisign y generando Plan de Portal AdSense...');
            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ texto_raw: text })
                });
                const data = await res.json();
                hideLoader();

                procesarRespuestaServidor(data);
            } catch (err) {
                hideLoader();
                alert('Error al procesar la verificación de dominios.');
            }
        });
    }

    // 3. Generar por Nicho
    if (btnGenerateNiche) {
        btnGenerateNiche.addEventListener('click', async () => {
            const kw = nicheKeyword.value.trim();
            if (!kw) return alert('Ingresa una palabra clave o rubro (ej: turismo, propiedades, autos, salud).');

            showLoader(`Generando y escaneando combinaciones de nicho para '${kw}'...`);
            try {
                const res = await fetch('/api/generate-niche', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ keyword: kw })
                });
                const data = await res.json();
                hideLoader();

                procesarRespuestaServidor(data);
            } catch (err) {
                hideLoader();
                alert('Error al generar combinación por nicho.');
            }
        });
    }

    function procesarRespuestaServidor(data) {
        currentResults = data.resultados || [];
        
        const libres = currentResults.filter(r => r.estado.includes("DISPONIBLE")).length;
        const vencidos = currentResults.filter(r => ["EXPIRADO", "PROXIMO_A_VENCER", "REDEMPTION_PERIOD", "PENDING_DELETE"].includes(r.estado)).length;
        const registrados = currentResults.filter(r => r.estado === "REGISTRADO").length;
        const premium = currentResults.filter(r => r.valuacion?.score >= 75).length;

        metricTotal.textContent = currentResults.length;
        metricFree.textContent = libres;
        metricExpiring.textContent = vencidos;
        metricTaken.textContent = registrados;
        metricPremium.textContent = premium;

        metricsSection.classList.remove('hidden');
        resultsSection.classList.remove('hidden');

        renderTable();
    }

    // Renderizar Tabla con Plan AdSense y Botón Copiar+Comprar en 1 Clic
    function renderTable() {
        resultsTbody.innerHTML = '';
        const search = tableSearch.value.toLowerCase();

        const filtered = currentResults.filter(item => {
            const matchesSearch = item.dominio.toLowerCase().includes(search);
            
            if (currentFilter === 'ALL') return matchesSearch;
            if (currentFilter === 'DISPONIBLE') return matchesSearch && (item.estado.includes('DISPONIBLE'));
            if (currentFilter === 'PREMIUM') return matchesSearch && (item.valuacion?.score >= 75);
            if (currentFilter === 'VENCIDO') return matchesSearch && (["EXPIRADO", "PROXIMO_A_VENCER", "REDEMPTION_PERIOD", "PENDING_DELETE"].includes(item.estado));
            if (currentFilter === 'REGISTRADO') return matchesSearch && (item.estado === 'REGISTRADO');
            return matchesSearch;
        });

        if (filtered.length === 0) {
            resultsTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2rem;">No hay dominios que coincidan con el filtro seleccionado.</td></tr>`;
            return;
        }

        filtered.forEach((item, idx) => {
            const tr = document.createElement('tr');
            const dias = item.dias_restantes;
            const diasTag = (dias !== null && dias !== undefined)
                ? (dias < 0 ? ` (hace ${Math.abs(dias)}d)` : ` (${dias}d)`)
                : '';
            const expDate = item.fecha_expiracion ? `${item.fecha_expiracion}${diasTag}` : '🟢 LIBRE HOY';
            const dnsStatus = item.resuelve_dns ? '🟢 Activo' : '🔴 Sin Web';
            const cleanBadgeClass = item.estado.replace(/ \/ /g, '-').replace(/ /g, '-');
            
            const val = item.valuacion || { score: 50, categoria: '⚪ ESTÁNDAR', estimacion_usd: '$15 - $100 USD', color: '#9ca3af' };
            const ads = val.adsense || {};

            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td>
                    <strong>${item.dominio}</strong>
                    ${ads.herramienta_estrella ? `<div style="font-size:0.75rem; color:#94a3b8; margin-top:3px;">💡 <strong>Portal AdSense:</strong> ${ads.herramienta_estrella}</div>` : ''}
                </td>
                <td><span class="badge badge-${cleanBadgeClass}">${item.estado}</span></td>
                <td>
                    <span class="badge-score" style="background: rgba(255,255,255,0.06); color: ${val.color}; border: 1px solid ${val.color};">
                        pts: ${val.score} | ${val.categoria}
                    </span>
                </td>
                <td>
                    <span class="val-est">${ads.cpc_adsense || val.estimacion_usd}</span>
                    <div style="font-size:0.72rem; color:#64748b;">Reventa: ${val.estimacion_usd}</div>
                </td>
                <td>${expDate}</td>
                <td>${dnsStatus}</td>
                <td>
                    <button onclick="copiarYComprar('${item.dominio}', '${item.link_compra}')" class="buy-link" style="cursor:pointer; border:none;">
                        📋 Copiar & Comprar
                    </button>
                </td>
            `;
            resultsTbody.appendChild(tr);
        });
    }

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderTable();
        });
    });

    if (tableSearch) tableSearch.addEventListener('input', renderTable);

    if (btnExportCSV) {
        btnExportCSV.addEventListener('click', async () => {
            if (currentResults.length === 0) return alert('No hay datos para exportar.');

            const res = await fetch('/api/export/csv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dominios: currentResults.map(r => r.dominio) })
            });
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dominios_adsense.csv';
            a.click();
        });
    }

    function showLoader(msg) {
        loaderText.textContent = msg;
        loader.classList.remove('hidden');
    }

    function hideLoader() {
        loader.classList.add('hidden');
    }
});

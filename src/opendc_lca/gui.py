"""Zero-dependency local browser interface for OpenDC-LCA."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import webbrowser

from .api import (
    analyze_practitioner_study,
    analyze_scenario,
    audit_scenario,
    new_practitioner_study,
    prepare_practitioner_study,
    summarize_performance_csv,
)
from .models import ValidationError

MAX_REQUEST_BYTES = 2_000_000

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenDC-LCA</title>
<style>
:root{--navy:#17324d;--blue:#0877a8;--pale:#eef5f8;--orange:#a84d00}
*{box-sizing:border-box}body{margin:0;font:16px system-ui;color:#17212b;background:#f7f9fb}
header{background:var(--navy);color:white;padding:22px 5vw}header h1{margin:0;font-size:1.8rem}
header p{margin:.35rem 0 0;color:#d8e6ef}.wrap{max-width:1200px;margin:28px auto;padding:0 24px}
.tabs{display:flex;gap:8px}.tabs button{background:#dce8ee;color:var(--navy)}
button{border:0;border-radius:5px;padding:10px 16px;font-weight:650;background:var(--blue);color:white;cursor:pointer}
button.active{background:var(--navy);color:white}.panel{background:white;padding:24px;border-radius:8px;
box-shadow:0 2px 10px #17212b16;margin-top:12px}.hidden{display:none!important}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:850px){.grid{grid-template-columns:1fr}}
textarea{width:100%;min-height:430px;font:13px ui-monospace,monospace;padding:12px;border:1px solid #bac8d1;border-radius:5px}
input[type=file]{display:block;margin:10px 0 16px}.notice{background:#fff4e5;color:#743800;padding:12px;border-left:4px solid #d97706}
label{display:block;font-weight:650;margin:10px 0 4px}input,select{width:100%;padding:9px;border:1px solid #bac8d1;border-radius:5px}
input[type=checkbox]{width:auto;margin-right:8px}.checklabel{font-weight:650;margin:18px 0 8px}
.formgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px 18px}@media(max-width:850px){.formgrid{grid-template-columns:1fr}}
pre{white-space:pre-wrap;word-break:break-word;background:#f3f6f8;padding:14px;min-height:200px;border-radius:5px}
details{margin-top:14px}summary{cursor:pointer;font-weight:650;color:var(--navy)}
.finding{padding:9px 11px;margin:7px 0;border-radius:4px;background:#edf3f6}.finding.blocker{background:#fde8e8;color:#821b1b}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.kpi{background:var(--pale);padding:14px;border-radius:5px}
.kpi b{display:block;font-size:1.3rem;margin-top:5px}.row{display:flex;gap:10px;margin:12px 0}
</style></head><body>
<header><h1>OpenDC-LCA</h1><p>Transparent life-cycle screening for data-center cooling</p></header>
<main class="wrap"><div class="tabs">
<button id="guidedTab" class="active" onclick="showTab('guided')">Guided study</button>
<button id="scenarioTab" onclick="showTab('scenario')">Advanced JSON</button>
<button id="performanceTab" onclick="showTab('performance')">Performance map</button></div>
<section id="guided" class="panel"><div class="notice">This guided workflow produces a screening result. It identifies missing evidence and does not automatically authorize a technology comparison.</div>
<h2>1. Describe the facility and cooling case</h2>
<div class="formgrid">
<div><label for="gName">Study name</label><input id="gName"></div>
<div><label for="gArchitecture">Cooling architecture</label><select id="gArchitecture"><option>air-cooled</option><option selected>direct-to-chip</option><option>one-phase immersion</option><option>two-phase immersion</option><option>other</option></select></div>
<div><label for="gGeography">Geography</label><input id="gGeography"></div>
<div><label for="gCapacity">IT capacity (kW)</label><input id="gCapacity" type="number" min="0" step="any"></div>
<div><label for="gUtilization">Average utilization (0–1)</label><input id="gUtilization" type="number" min="0" max="1" step="0.01"></div>
<div><label for="gPue">PUE</label><input id="gPue" type="number" min="1" step="0.01"></div>
<div><label for="gLife">Study life (years)</label><input id="gLife" type="number" min="0" step="any"></div>
<div><label for="gOnsiteWater">On-site water (L/kWh IT)</label><input id="gOnsiteWater" type="number" min="0" step="any"></div>
<div><label for="gYear">Reference year</label><input id="gYear" type="number" step="1"></div>
</div>
<h2>2. Enter electricity factors</h2>
<div class="formgrid">
<div><label for="gGridGhg">GHG (kg CO₂e/kWh)</label><input id="gGridGhg" type="number" min="0" step="any"></div>
<div><label for="gGridEnergy">Primary energy (MJ/kWh)</label><input id="gGridEnergy" type="number" min="0" step="any"></div>
<div><label for="gGridWater">Blue water (L/kWh)</label><input id="gGridWater" type="number" min="0" step="any"></div>
</div>
<h2>3. Identify the input source</h2>
<div class="formgrid">
<div><label for="gSourceTitle">Source title</label><input id="gSourceTitle"></div>
<div><label for="gSourceCitation">Citation, URL, or internal record</label><input id="gSourceCitation"></div>
<div><label for="gSourceId">Source ID</label><input id="gSourceId"></div>
</div>
<label class="checklabel"><input id="gEquipmentInclude" type="checkbox" onchange="toggleEquipment()">Include aggregate cooling-equipment lifecycle data</label>
<div id="equipmentFields" class="formgrid hidden">
<div><label for="gEquipmentName">Equipment name</label><input id="gEquipmentName" value="Cooling-system equipment"></div>
<div><label for="gEquipmentQuantity">Quantity</label><input id="gEquipmentQuantity" type="number" min="0" step="any" value="1"></div>
<div><label for="gEquipmentLife">Service life (years)</label><input id="gEquipmentLife" type="number" min="0" step="any" value="15"></div>
<div><label for="gEquipmentGhg">Production GHG (kg CO₂e/unit)</label><input id="gEquipmentGhg" type="number" min="0" step="any" value="0"></div>
<div><label for="gEquipmentEnergy">Production primary energy (MJ/unit)</label><input id="gEquipmentEnergy" type="number" min="0" step="any" value="0"></div>
<div><label for="gEquipmentWater">Production blue water (L/unit)</label><input id="gEquipmentWater" type="number" min="0" step="any" value="0"></div>
</div>
<div class="row"><button onclick="runGuided()">Run screening</button><button onclick="downloadPrepared()">Download governed scenario</button></div>
<div class="grid"><div><h2>Decision status</h2><div id="guidedStatus">Complete the fields to begin.</div><div id="guidedKpis" class="kpis"></div></div>
<div><h2>Data needed next</h2><div id="guidedNext"></div></div></div>
<details><summary>Machine-readable practitioner result</summary><pre id="guidedOutput"></pre></details></section>
<section id="scenario" class="panel hidden"><div class="notice">Screening output does not by itself authorize a public comparative claim. Audit findings are shown with every result.</div>
<div class="grid"><div><h2>Scenario JSON</h2><input id="scenarioFile" type="file" accept=".json,application/json">
<textarea id="scenarioText" aria-label="Scenario JSON"></textarea>
<div class="row"><button onclick="runScenario('analyze')">Analyze</button><button onclick="runScenario('audit')">Audit only</button><button onclick="downloadResult()">Export JSON</button></div></div>
<div><h2>Result</h2><div id="kpis" class="kpis"></div><div id="auditSummary"></div>
<details><summary>Raw JSON result</summary><pre id="scenarioOutput">Load a scenario to begin.</pre></details></div></div></section>
<section id="performance" class="panel hidden"><div class="notice">Performance-map summaries require provenance and evidence review before use in comparative LCA.</div>
<div class="grid"><div><h2>Performance-map CSV</h2><input id="performanceFile" type="file" accept=".csv,text/csv">
<textarea id="performanceText" aria-label="Performance CSV"></textarea><button onclick="runPerformance()">Summarize</button></div>
<div><h2>Summary</h2><pre id="performanceOutput">Load a performance map to begin.</pre></div></div></section></main>
<script>
let lastResult=null;
let preparedScenario=null;
function showTab(name){for(const x of ['guided','scenario','performance']){document.getElementById(x).classList.toggle('hidden',x!==name);document.getElementById(x+'Tab').classList.toggle('active',x===name)}}
function loadFile(input, target){input.addEventListener('change',async()=>{if(input.files[0])target.value=await input.files[0].text()})}
loadFile(document.getElementById('scenarioFile'),document.getElementById('scenarioText'));
loadFile(document.getElementById('performanceFile'),document.getElementById('performanceText'));
async function post(path,body){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw new Error(data.error||'Request failed');return data}
function setValue(id,value){document.getElementById(id).value=value}
function toggleEquipment(){document.getElementById('equipmentFields').classList.toggle('hidden',!document.getElementById('gEquipmentInclude').checked)}
async function loadGuidedTemplate(){const t=await post('/api/practitioner-template',{});setValue('gName',t.study_name);setValue('gArchitecture',t.cooling_architecture);setValue('gGeography',t.geography);setValue('gCapacity',t.it_capacity_kw);setValue('gUtilization',t.capacity_factor);setValue('gPue',t.pue);setValue('gLife',t.facility_lifetime_years);setValue('gOnsiteWater',t.onsite_water_l_per_kwh_it);setValue('gYear',t.reference_year);setValue('gGridGhg',t.grid_ghg_kgco2e_per_kwh);setValue('gGridEnergy',t.grid_primary_energy_mj_per_kwh);setValue('gGridWater',t.grid_blue_water_l_per_kwh);setValue('gSourceTitle',t.source.title);setValue('gSourceCitation',t.source.citation);setValue('gSourceId',t.source.id)}
function guidedInput(){return {study_name:document.getElementById('gName').value,cooling_architecture:document.getElementById('gArchitecture').value,geography:document.getElementById('gGeography').value,reference_year:Number(document.getElementById('gYear').value),it_capacity_kw:Number(document.getElementById('gCapacity').value),capacity_factor:Number(document.getElementById('gUtilization').value),pue:Number(document.getElementById('gPue').value),facility_lifetime_years:Number(document.getElementById('gLife').value),onsite_water_l_per_kwh_it:Number(document.getElementById('gOnsiteWater').value),grid_ghg_kgco2e_per_kwh:Number(document.getElementById('gGridGhg').value),grid_primary_energy_mj_per_kwh:Number(document.getElementById('gGridEnergy').value),grid_blue_water_l_per_kwh:Number(document.getElementById('gGridWater').value),equipment:{include:document.getElementById('gEquipmentInclude').checked,name:document.getElementById('gEquipmentName').value,quantity:Number(document.getElementById('gEquipmentQuantity').value),service_life_years:Number(document.getElementById('gEquipmentLife').value),production_ghg_kgco2e:Number(document.getElementById('gEquipmentGhg').value),production_primary_energy_mj:Number(document.getElementById('gEquipmentEnergy').value),production_blue_water_l:Number(document.getElementById('gEquipmentWater').value),end_of_life_ghg_kgco2e:0,end_of_life_primary_energy_mj:0,end_of_life_blue_water_l:0},source:{id:document.getElementById('gSourceId').value,title:document.getElementById('gSourceTitle').value,citation:document.getElementById('gSourceCitation').value,license:'not assessed',quality:'screening; practitioner supplied',uncertainty:'not_quantified',review_status:'unreviewed',confidentiality:'public'}}}
async function runGuided(){try{preparedScenario=await post('/api/practitioner-prepare',guidedInput());lastResult=await post('/api/practitioner-analyze',preparedScenario);document.getElementById('guidedOutput').textContent=JSON.stringify(lastResult,null,2);const k=lastResult.key_outputs;document.getElementById('guidedStatus').innerHTML=`<div class="finding"><b>${lastResult.evidence_level.toUpperCase()}</b><br>${lastResult.interpretation_scope}<br>Declared comparison-metadata gate: ${lastResult.declared_metadata_gate_passed?'no blockers':'blocked'}<br>${lastResult.claim_gate_notice}</div>`;document.getElementById('guidedKpis').innerHTML=`<div class="kpi">GHG<b>${k.ghg_kgco2e_per_it_mwh.toFixed(2)}</b>kg CO₂e/IT MWh</div><div class="kpi">Energy<b>${k.primary_energy_mj_per_it_mwh.toFixed(2)}</b>MJ/IT MWh</div><div class="kpi">Water<b>${k.blue_water_l_per_it_mwh.toFixed(2)}</b>L/IT MWh</div>`;document.getElementById('guidedNext').innerHTML=lastResult.next_data_required.map(x=>`<div class="finding">${x}</div>`).join('')}catch(e){document.getElementById('guidedStatus').innerHTML=`<div class="finding blocker">Error: ${e.message}</div>`}}
function downloadPrepared(){if(!preparedScenario)return;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(preparedScenario,null,2)],{type:'application/json'}));a.download='opendc-lca-scenario.json';a.click();URL.revokeObjectURL(a.href)}
async function runScenario(action){const out=document.getElementById('scenarioOutput');try{const scenario=JSON.parse(document.getElementById('scenarioText').value);lastResult=await post('/api/'+action,scenario);out.textContent=JSON.stringify(lastResult,null,2);const p=lastResult.result?.per_it_mwh;document.getElementById('kpis').innerHTML=p?`<div class="kpi">GHG<b>${p.ghg_kgco2e.toFixed(2)}</b>kg CO2e/IT MWh</div><div class="kpi">Energy<b>${p.primary_energy_mj.toFixed(2)}</b>MJ/IT MWh</div><div class="kpi">Water<b>${p.blue_water_l.toFixed(2)}</b>L/IT MWh</div>`:'';const findings=lastResult.audit||lastResult.findings||[];document.getElementById('auditSummary').innerHTML=`<h3>Scientific audit</h3>${findings.length?findings.map(f=>`<div class="finding ${f.severity}"><b>${f.severity.toUpperCase()}</b> — ${f.message}</div>`).join(''):'<div class="finding">No automated findings.</div>'}`}catch(e){out.textContent='Error: '+e.message}}
async function runPerformance(){const out=document.getElementById('performanceOutput');try{lastResult=await post('/api/performance-summary',{csv:document.getElementById('performanceText').value});out.textContent=JSON.stringify(lastResult,null,2)}catch(e){out.textContent='Error: '+e.message}}
function downloadResult(){if(!lastResult)return;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(lastResult,null,2)],{type:'application/json'}));a.download='opendc-lca-result.json';a.click();URL.revokeObjectURL(a.href)}
loadGuidedTemplate();
</script></body></html>"""


class GuiHandler(BaseHTTPRequestHandler):
    server_version = "OpenDC-LCA/1.1"

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/":
            self.send_error(404)
            return
        body = HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
                self._json(415, {"error": "Content-Type must be application/json"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_REQUEST_BYTES:
                self._json(413, {"error": "Request must be between 1 byte and 2 MB"})
                return
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/analyze":
                result = analyze_scenario(payload)
            elif self.path == "/api/audit":
                result = audit_scenario(payload)
            elif self.path == "/api/performance-summary":
                if not isinstance(payload, dict) or not isinstance(payload.get("csv"), str):
                    raise ValidationError("Request requires a CSV text field")
                result = summarize_performance_csv(payload["csv"])
            elif self.path == "/api/practitioner-template":
                result = new_practitioner_study()
            elif self.path == "/api/practitioner-prepare":
                result = prepare_practitioner_study(payload)
            elif self.path == "/api/practitioner-analyze":
                result = analyze_practitioner_study(payload)
            else:
                self._json(404, {"error": "Unknown endpoint"})
                return
            self._json(200, result)
        except (ValidationError, ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        return


def serve_gui(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    open_browser: bool = True,
    allow_remote: bool = False,
) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"} and not allow_remote:
        raise ValueError("Remote GUI binding requires explicit allow_remote=True")
    server = ThreadingHTTPServer((host, port), GuiHandler)
    url = f"http://{host}:{server.server_port}/"
    print(f"OpenDC-LCA GUI: {url}")
    if open_browser:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carregar apenas a malha (eventos NÃO serão embutidos)
with open(os.path.join(BASE_DIR, "dados", "malha_cia.geojson"), "r", encoding="utf-8") as f:
    malha_cia = json.load(f)

malha_json = json.dumps(malha_cia)

html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Dashboard Operacional</title>

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

<style>
body {
    margin:0;
    font-family:'Segoe UI', sans-serif;
    background:#f4f6f9;
}

.topbar {
    display:flex;
    gap:20px;
    padding:15px 20px;
}

.kpi {
    flex:1;
    background:white;
    padding:15px;
    border-radius:10px;
    box-shadow:0 4px 10px rgba(0,0,0,0.05);
}

.kpi h3 {
    margin:0;
    font-size:14px;
    color:#666;
}

.kpi span {
    font-size:22px;
    font-weight:bold;
}

.container {
    display:flex;
}

.sidebar {
    width:280px;
    background:white;
    padding:20px;
    height:calc(100vh - 90px);
    overflow:auto;
    box-shadow:4px 0 10px rgba(0,0,0,0.05);
}

.sidebar label {
    font-weight:bold;
    font-size:13px;
}

.sidebar select,
.sidebar input {
    width:100%;
    margin-bottom:10px;
    padding:5px;
}

#map {
    flex:1;
    height:calc(100vh - 90px);
}

button {
    width:100%;
    padding:8px;
    margin-top:5px;
    border:none;
    border-radius:6px;
    cursor:pointer;
}

.btn-primary {
    background:#007bff;
    color:white;
}

.btn-secondary {
    background:#6c757d;
    color:white;
}
</style>
</head>

<body>

<div class="topbar">
    <div class="kpi">
        <h3>Total Ocorrências</h3>
        <span id="kpiTotal">0</span>
    </div>
    <div class="kpi">
        <h3>Vítimas Fatais</h3>
        <span id="kpiFatal">0</span>
    </div>
    <div class="kpi">
        <h3>Vítimas Graves</h3>
        <span id="kpiGrave">0</span>
    </div>
    <div class="kpi">
        <h3>Vítimas Leves</h3>
        <span id="kpiLeve">0</span>
    </div>
</div>

<div class="container">

<div class="sidebar">

<label>CIA</label>
<select id="filtroCia" multiple></select>

<label>Pelotão</label>
<select id="filtroPelotao" multiple></select>

<label>Ano</label>
<select id="filtroAno" multiple></select>

<label>Data Inicial</label>
<input type="date" id="dataInicio"/>

<label>Data Final</label>
<input type="date" id="dataFim"/>

<label>Natureza</label>
<select id="filtroNatureza" multiple></select>

<label>Vítimas</label>
<div>
    <input type="checkbox" id="checkFatal"/> Fatal<br>
    <input type="checkbox" id="checkGrave"/> Grave<br>
    <input type="checkbox" id="checkLeve"/> Leve<br>
    <input type="checkbox" id="checkSem"/> Sem vítimas
</div>

<button class="btn-primary" onclick="aplicarFiltro()">Aplicar Filtro</button>
<button class="btn-secondary" onclick="limparFiltro()">Limpar</button>

</div>

<div id="map"></div>

</div>

<script>

var map = L.map('map').setView([-21.7, -48.2], 8);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

var malha = ___MALHA___;

L.geoJSON(malha, {
    style:function(){
        return {
            fillColor:"#cccccc",
            fillOpacity:0.2,
            color:"#333",
            weight:2
        };
    }
}).addTo(map);

var eventos = [];
var markersLayer = L.layerGroup().addTo(map);

// 🔥 CARREGAMENTO PROFISSIONAL DO JSON
fetch("dados/eventos_processados_atualizado.json")
    .then(response => response.json())
    .then(data => {
        eventos = data;
        popularFiltros();
    });

function corVitima(e){
    if(e.TEM_FATAL) return "#E31A1C";
    if(e.TEM_GRAVE) return "#FF7F00";
    if(e.TEM_LEVE) return "#FDBF00";
    return "#33A02C";
}

function popularFiltros(){
    preencherSelect("filtroCia", [...new Set(eventos.map(e=>e.Cia))]);
    preencherSelect("filtroPelotao", [...new Set(eventos.map(e=>e.Pelotao))]);
    preencherSelect("filtroAno", [...new Set(eventos.map(e=>e.ANO))]);
    preencherSelect("filtroNatureza", [...new Set(eventos.map(e=>e.Natureza))]);
}

function preencherSelect(id, valores){
    var select = document.getElementById(id);
    valores.sort().forEach(v=>{
        var opt = document.createElement("option");
        opt.value = v;
        opt.text = v;
        select.appendChild(opt);
    });
}

function getSelecionados(id){
    return Array.from(document.getElementById(id).selectedOptions).map(o=>o.value);
}

function aplicarFiltro(){

    markersLayer.clearLayers();

    var ciaSel = getSelecionados("filtroCia");
    var pelSel = getSelecionados("filtroPelotao");
    var anoSel = getSelecionados("filtroAno");
    var natSel = getSelecionados("filtroNatureza");

    var dataInicio = document.getElementById("dataInicio").value;
    var dataFim = document.getElementById("dataFim").value;

    var chkFatal = document.getElementById("checkFatal").checked;
    var chkGrave = document.getElementById("checkGrave").checked;
    var chkLeve = document.getElementById("checkLeve").checked;
    var chkSem = document.getElementById("checkSem").checked;

    var total=0, fatal=0, grave=0, leve=0;

    eventos.forEach(e=>{

        if(!e.LATITUDE || !e.LONGITUDE) return;

        if(ciaSel.length && !ciaSel.includes(e.Cia)) return;
        if(pelSel.length && !pelSel.includes(e.Pelotao)) return;
        if(anoSel.length && !anoSel.includes(String(e.ANO))) return;
        if(natSel.length && !natSel.includes(e.Natureza)) return;

        if(dataInicio && e.Data < dataInicio) return;
        if(dataFim && e.Data > dataFim) return;

        var passaVitima =
            (chkFatal && e.TEM_FATAL) ||
            (chkGrave && e.TEM_GRAVE) ||
            (chkLeve && e.TEM_LEVE) ||
            (chkSem && !e.TEM_FATAL && !e.TEM_GRAVE && !e.TEM_LEVE);

        if((chkFatal||chkGrave||chkLeve||chkSem) && !passaVitima) return;

        var marker = L.circleMarker(
            [e.LATITUDE, e.LONGITUDE],
            {
                radius:4,
                color:corVitima(e),
                fillColor:corVitima(e),
                fillOpacity:0.9
            }
        );

        markersLayer.addLayer(marker);

        total++;
        fatal += e.TOTAL_FATAL;
        grave += e.TOTAL_GRAVE;
        leve += e.TOTAL_LEVE;
    });

    document.getElementById("kpiTotal").innerText = total;
    document.getElementById("kpiFatal").innerText = fatal;
    document.getElementById("kpiGrave").innerText = grave;
    document.getElementById("kpiLeve").innerText = leve;
}

function limparFiltro(){
    document.querySelectorAll("select").forEach(s=>s.selectedIndex=-1);
    document.querySelectorAll("input[type=date]").forEach(i=>i.value="");
    document.querySelectorAll("input[type=checkbox]").forEach(c=>c.checked=false);
    markersLayer.clearLayers();
}

</script>

</body>
</html>
""".replace("___MALHA___", malha_json)

with open(os.path.join(BASE_DIR, "Dashboard_Operacional_V2.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard_Operacional_V2.html criado com sucesso!")
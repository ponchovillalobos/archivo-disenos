"""Genera `sitio/estudio.html`: la mesa de trabajo visual.

Por qué una página y no un formulario cualquiera: elegir una paleta leyendo
«teal-naranja» es imposible; elegirla viendo la franja de color es inmediato.
Lo mismo con los ánimos y las disposiciones. La interfaz existe para que las
decisiones que hoy se toman escribiendo YAML se tomen mirando.

Reglas heredadas de lo que ya nos costó una vez:
  · Fuentes y datos INCRUSTADOS, no enlazados: en `file://` el navegador
    bloquea `fetch()` y las fuentes externas, y la página sale en blanco o con
    la tipografía de respaldo sin avisar.
  · La página no inventa nada: todo lo que ofrece sale de `estudio_datos.py`,
    que a su vez lo lee de la voz y del código. Si mañana cambia una paleta,
    la interfaz cambia sola.
  · Guardar escribe el YAML por el servidor local, y el servidor solo acepta
    rutas dentro de `pedidos/`.
"""
import base64
import json
import os
import sys

S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
PROY = os.path.dirname(S)
FUENTES = os.path.join(PROY, "fuentes")

sys.path.insert(0, S)
import estudio_datos                                # noqa: E402


def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()


CSS = """
:root{
  --papel:#faf7f6; --tarjeta:#fffdfd; --tinta:#171214; --media:#6d6165;
  --leve:#9c9095; --filete:#e9e1e0; --sangre:#a81d26; --hueso:#efe7e5;
}
@media (prefers-color-scheme:dark){:root:not([data-tema="claro"]){
  --papel:#100c0d; --tarjeta:#191314; --tinta:#f6f1f0; --media:#a89ea1;
  --leve:#786e71; --filete:#2b2223; --sangre:#e85159; --hueso:#241c1d;
}}
:root[data-tema="oscuro"]{
  --papel:#100c0d; --tarjeta:#191314; --tinta:#f6f1f0; --media:#a89ea1;
  --leve:#786e71; --filete:#2b2223; --sangre:#e85159; --hueso:#241c1d;
}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--papel);color:var(--tinta);
  font-family:Newsreader,Georgia,serif;font-size:17px;line-height:1.5;
  -webkit-font-smoothing:antialiased}
.env{max-width:1380px;margin:0 auto;padding:34px 30px 90px}
h1{font-family:Fraunces,serif;font-weight:900;font-size:46px;line-height:.94;
  font-variation-settings:"opsz" 144,"WONK" 1;letter-spacing:-.02em}
h2{font-family:Fraunces,serif;font-weight:800;font-size:23px;
  font-variation-settings:"opsz" 60,"WONK" 1;letter-spacing:-.01em;
  margin-bottom:12px}
.eyebrow{font-family:Recursive,monospace;font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--sangre);font-weight:600}
.sub{color:var(--media);font-style:italic;margin-top:8px}
.regla{height:1px;background:var(--filete);margin:26px 0}

.mesa{display:grid;grid-template-columns:250px 1fr 330px;gap:24px;
  align-items:start}
@media(max-width:1180px){.mesa{grid-template-columns:1fr}}

.panel{background:var(--tarjeta);border:1px solid var(--filete);
  border-radius:3px;padding:18px}
.panel + .panel{margin-top:16px}

/* lista de pedidos */
.ped{display:block;width:100%;text-align:left;background:none;border:0;
  border-left:3px solid transparent;padding:9px 12px;cursor:pointer;
  font-family:inherit;font-size:15px;color:var(--tinta);border-radius:2px}
.ped:hover{background:var(--hueso)}
.ped[aria-current="true"]{border-left-color:var(--sangre);background:var(--hueso);
  font-weight:600}
.ped small{display:block;font-family:Recursive,monospace;font-size:10.5px;
  color:var(--leve);letter-spacing:.04em;margin-top:2px}

label{display:block;font-family:Recursive,monospace;font-size:11px;
  letter-spacing:.14em;text-transform:uppercase;color:var(--media);
  margin:16px 0 6px;font-weight:600}
input[type=text],textarea,select{width:100%;background:var(--papel);
  border:1px solid var(--filete);border-radius:2px;padding:9px 11px;
  font-family:inherit;font-size:16px;color:var(--tinta)}
textarea{resize:vertical;min-height:64px;line-height:1.45}
input:focus,textarea:focus,select:focus{outline:2px solid var(--sangre);
  outline-offset:1px}

/* paletas: se eligen mirando, no leyendo */
.paletas{display:grid;grid-template-columns:repeat(auto-fill,minmax(74px,1fr));
  gap:9px}
.pal{border:2px solid transparent;border-radius:3px;padding:0;cursor:pointer;
  background:none;overflow:hidden;position:relative;display:block}
.pal img{display:block;width:100%;height:88px;object-fit:cover;border-radius:2px}
.pal span{display:block;font-family:Recursive,monospace;font-size:10px;
  color:var(--media);padding:4px 2px 2px;letter-spacing:.02em;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pal[aria-pressed="true"]{border-color:var(--sangre)}
.pal.fuera span{color:var(--leve);font-style:italic}

.animos{display:flex;flex-wrap:wrap;gap:7px}
.an{border:1px solid var(--filete);background:var(--papel);border-radius:20px;
  padding:5px 13px;cursor:pointer;font-family:Recursive,monospace;font-size:12px;
  color:var(--tinta)}
.an.claro{border-color:#d9c98a}
.an[aria-pressed="true"]{background:var(--sangre);color:#fff;border-color:var(--sangre)}

/* láminas */
.lam{border:1px solid var(--filete);border-radius:3px;padding:14px;
  margin-bottom:11px;background:var(--papel)}
.lam .cab{display:flex;justify-content:space-between;align-items:center;
  font-family:Recursive,monospace;font-size:11px;color:var(--leve);
  letter-spacing:.14em;text-transform:uppercase}
.lam label{margin:11px 0 4px}
.quitar{background:none;border:0;color:var(--leve);cursor:pointer;font-size:17px;
  line-height:1;padding:0 4px}
.quitar:hover{color:var(--sangre)}

/* salidas */
.sal{display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:8px;
  align-items:center;margin-bottom:8px}
.sal select{font-size:14px;padding:7px 9px}

.btn{font-family:Recursive,monospace;font-size:12.5px;letter-spacing:.05em;
  border:1px solid var(--filete);background:var(--papel);color:var(--tinta);
  border-radius:2px;padding:9px 15px;cursor:pointer}
.btn:hover{border-color:var(--media)}
.btn.fuerte{background:var(--sangre);color:#fff;border-color:var(--sangre);
  font-weight:600}
.btn.fuerte:hover{filter:brightness(1.08)}
.acciones{display:flex;gap:9px;flex-wrap:wrap;margin-top:20px}

/* plan */
.plan dt{font-family:Recursive,monospace;font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--leve);margin-top:12px}
.plan dd{font-size:15.5px}
.huella{font-family:Recursive,monospace;font-size:12px;color:var(--media);
  letter-spacing:.04em}
.chip{display:inline-block;font-family:Recursive,monospace;font-size:11px;
  border:1px solid var(--filete);border-radius:20px;padding:2px 9px;
  margin:3px 3px 0 0;color:var(--media)}
.err{background:#fdecec;border:1px solid #e9b8b8;color:#8a1f22;padding:11px 13px;
  border-radius:3px;font-size:14.5px;margin-top:10px}
@media (prefers-color-scheme:dark){:root:not([data-tema="claro"]) .err{
  background:#2a1415;border-color:#5a2a2c;color:#f0b8ba}}
.ok{color:#2a7a45;font-family:Recursive,monospace;font-size:12px}
.aviso{font-size:13.5px;color:var(--media);font-style:italic;margin-top:8px}
.acento{display:inline-block;width:13px;height:13px;border-radius:50%;
  vertical-align:-2px;margin-right:6px;border:1px solid rgba(0,0,0,.15)}
.prohibido{font-size:13px;color:var(--media);margin-top:6px}
.prohibido b{color:var(--sangre);font-weight:600}
"""


JS = r"""
const D = JSON.parse(document.getElementById("datos").textContent);
const $ = s => document.querySelector(s);
const esc = t => (t ?? "").toString()
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
  .replace(/"/g,"&quot;");

let actual = null;      // el pedido en edición (objeto crudo)
let archivo = null;

/* ---------- lista de pedidos ---------- */
function pintarLista(){
  $("#lista").innerHTML = D.pedidos.map(p => `
    <button class="ped" data-a="${esc(p.archivo)}"
      aria-current="${p.archivo===archivo}">
      ${esc(p.crudo.pieza?.titulo || p.archivo)}
      <small>${esc(p.paleta||"?")} · ${esc(p.salidas.length)} salida${p.salidas.length===1?"":"s"}</small>
    </button>`).join("");
  document.querySelectorAll(".ped").forEach(b =>
    b.onclick = () => abrir(b.dataset.a));
}

function abrir(a){
  const p = D.pedidos.find(x => x.archivo === a);
  if(!p) return;
  archivo = a;
  actual = JSON.parse(JSON.stringify(p.crudo));
  pintarLista(); pintarEditor(); recalcular();
}

/* ---------- editor ---------- */
function pintarEditor(){
  const pz = actual.pieza ||= {}, en = actual.entrada ||= {tipo:"guion"},
        es = actual.estilo ||= {}, sal = actual.salidas ||= [];

  $("#ed").innerHTML = `
  <div class="panel">
    <h2>La pieza</h2>
    <label for="f-tit">Título</label>
    <input type="text" id="f-tit" value="${esc(pz.titulo)}">
    <label for="f-id">Identificador</label>
    <input type="text" id="f-id" value="${esc(pz.id)}">
    <label for="f-res">Resumen</label>
    <input type="text" id="f-res" value="${esc(pz.resumen)}">
  </div>

  <div class="panel">
    <h2>Color</h2>
    <p class="aviso">Sin elegir, la paleta sale del identificador: el mismo
      tema da siempre el mismo color y se puede regenerar idéntico.</p>
    <div class="paletas" id="paletas"></div>
    <label>Ánimo — la mitad clara está marcada</label>
    <div class="animos" id="animos"></div>
  </div>

  <div class="panel">
    <h2>Contenido</h2>
    <label for="f-tipo">De qué parte</label>
    <select id="f-tipo">${D.tipos_entrada.map(t =>
      `<option value="${t}" ${en.tipo===t?"selected":""}>${t}</option>`).join("")}</select>
    <div id="contenido"></div>
  </div>

  <div class="panel">
    <h2>Qué quiero que salga</h2>
    <div id="salidas"></div>
    <button class="btn" id="mas-salida">+ otra salida</button>
  </div>

  <div class="acciones">
    <button class="btn fuerte" id="guardar">Guardar el pedido</button>
    <button class="btn" id="revalidar">Comprobar</button>
    <span id="estado"></span>
  </div>`;

  pintarPaletas(); pintarAnimos(); pintarContenido(); pintarSalidas();

  ["f-tit","f-id","f-res"].forEach(id => $("#"+id).oninput = e => {
    const k = {"f-tit":"titulo","f-id":"id","f-res":"resumen"}[id];
    actual.pieza[k] = e.target.value; recalcular();
  });
  $("#f-tipo").onchange = e => {
    actual.entrada.tipo = e.target.value; pintarContenido(); recalcular();
  };
  $("#mas-salida").onclick = () => {
    actual.salidas.push({tipo:"reel", lienzo:"reel-9-16", montaje:"texto-vivo"});
    pintarSalidas(); recalcular();
  };
  $("#guardar").onclick = guardar;
  $("#revalidar").onclick = recalcular;
}

function pintarPaletas(){
  const sel = actual.estilo.paleta;
  $("#paletas").innerHTML =
    `<button class="pal ${!sel?"":""}" data-p="" aria-pressed="${!sel}"
       style="display:grid;place-items:center;border:1px dashed var(--filete)">
       <span style="padding:30px 4px;font-style:italic">automática</span></button>` +
    D.paletas.map(p => `
      <button class="pal ${p.sorteo?"":"fuera"}" data-p="${p.nombre}"
        aria-pressed="${sel===p.nombre}" title="${esc(p.look)}">
        <img src="data:image/png;base64,${p.muestra}" alt="">
        <span>${esc(p.nombre)}</span>
      </button>`).join("");
  document.querySelectorAll(".pal").forEach(b => b.onclick = () => {
    const v = b.dataset.p;
    if(v) actual.estilo.paleta = v; else delete actual.estilo.paleta;
    pintarPaletas(); recalcular();
  });
}

function pintarAnimos(){
  const sel = actual.estilo.animo;
  $("#animos").innerHTML =
    `<button class="an" data-a="" aria-pressed="${!sel}">automático</button>` +
    D.animos.map(a => `<button class="an ${a.luminoso?"claro":""}" data-a="${a.nombre}"
       aria-pressed="${sel===a.nombre}" title="${esc(a.luz)}">${esc(a.nombre)}</button>`).join("");
  document.querySelectorAll(".an").forEach(b => b.onclick = () => {
    const v = b.dataset.a;
    if(v) actual.estilo.animo = v; else delete actual.estilo.animo;
    pintarAnimos(); recalcular();
  });
}

function pintarContenido(){
  const en = actual.entrada, c = $("#contenido");
  if(en.tipo === "audio"){
    c.innerHTML = `<label for="f-audio">Archivo de audio</label>
      <input type="text" id="f-audio" value="${esc(en.audio)}"
        placeholder="audio/procesados/…">`;
    $("#f-audio").oninput = e => { en.audio = e.target.value; recalcular(); };
    return;
  }
  if(en.tipo === "tema"){
    c.innerHTML = `<label for="f-tema">Tema</label>
      <input type="text" id="f-tema" value="${esc(en.tema)}">`;
    $("#f-tema").oninput = e => { en.tema = e.target.value; recalcular(); };
    return;
  }
  en.laminas ||= [];
  c.innerHTML = en.laminas.map((L,i) => `
    <div class="lam">
      <div class="cab"><span>lámina ${i+1}</span>
        <button class="quitar" data-i="${i}" title="quitar">×</button></div>
      <label>Titular <span class="cuenta" data-i="${i}"></span></label>
      <textarea data-k="titular" data-i="${i}">${esc(L.titular)}</textarea>
      <label>Escena — el prompt de la imagen, en inglés</label>
      <textarea data-k="escena" data-i="${i}">${esc(L.escena)}</textarea>
    </div>`).join("") +
    `<button class="btn" id="mas-lamina">+ otra lámina</button>`;

  c.querySelectorAll("textarea").forEach(t => t.oninput = e => {
    en.laminas[+e.target.dataset.i][e.target.dataset.k] = e.target.value;
    cuentas(); recalcular();
  });
  c.querySelectorAll(".quitar").forEach(b => b.onclick = () => {
    en.laminas.splice(+b.dataset.i,1); pintarContenido(); recalcular();
  });
  $("#mas-lamina").onclick = () => {
    en.laminas.push({titular:"", escena:""}); pintarContenido(); recalcular();
  };
  cuentas();
}

function cuentas(){
  // el tope real depende del destino: impreso 52, vídeo 96
  const impresa = (actual.salidas||[]).some(s =>
    ["carrusel_pdf","laminas","zip"].includes(s.tipo));
  const tope = impresa ? 52 : 96;
  document.querySelectorAll(".cuenta").forEach(sp => {
    const L = actual.entrada.laminas[+sp.dataset.i] || {};
    const n = (L.titular||"").trim().length;
    sp.textContent = ` ${n}/${tope}`;
    sp.style.color = n > tope ? "var(--sangre)" : "var(--leve)";
  });
}

function pintarSalidas(){
  $("#salidas").innerHTML = actual.salidas.map((s,i) => `
    <div class="sal">
      <select data-k="tipo" data-i="${i}">${D.tipos_salida.map(t =>
        `<option ${s.tipo===t?"selected":""}>${t}</option>`).join("")}</select>
      <select data-k="lienzo" data-i="${i}">${D.lienzos.map(l =>
        `<option value="${l.nombre}" ${s.lienzo===l.nombre?"selected":""}>${l.nombre}</option>`).join("")}</select>
      <select data-k="montaje" data-i="${i}" ${["reel","video"].includes(s.tipo)?"":"disabled"}>
        ${D.montajes.map(m => `<option ${s.montaje===m?"selected":""}>${m}</option>`).join("")}</select>
      <button class="quitar" data-i="${i}">×</button>
    </div>`).join("");
  $("#salidas").querySelectorAll("select").forEach(sl => sl.onchange = e => {
    actual.salidas[+e.target.dataset.i][e.target.dataset.k] = e.target.value;
    pintarSalidas(); cuentas(); recalcular();
  });
  $("#salidas").querySelectorAll(".quitar").forEach(b => b.onclick = () => {
    actual.salidas.splice(+b.dataset.i,1); pintarSalidas(); cuentas(); recalcular();
  });
}

/* ---------- el plan, calculado en la propia página ---------- */
async function sha1(txt){
  const b = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(txt));
  return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");
}
function bigMod(hex, n){          // el hash es de 160 bits: se reduce por trozos
  let r = 0;
  for(const c of hex) r = (r*16 + parseInt(c,16)) % n;
  return r;
}

async function recalcular(){
  const es = actual.estilo || {}, pz = actual.pieza || {};
  const clave = es.clave_estilo || pz.id || "";
  const activas = D.paletas.filter(p => p.sorteo);
  const luminosos = D.animos.filter(a => a.luminoso);
  const graves = D.animos.filter(a => !a.luminoso);

  let pal = es.paleta, ani = es.animo;
  if(!pal) pal = activas[bigMod(await sha1(clave), activas.length)].nombre;
  if(!ani){
    const claro = bigMod(await sha1("luz:"+clave), 100) < 60;
    const g = claro ? luminosos : graves;
    ani = g[bigMod(await sha1("cual:"+clave), g.length)].nombre;
  }
  const P = D.paletas.find(p => p.nombre === pal) || {};
  const A = D.animos.find(a => a.nombre === ani) || {};
  const ac = es.acento || P.acento || "#888";

  // avisos que se pueden comprobar aquí mismo
  const avisos = [];
  if(!pz.id) avisos.push("falta el identificador");
  if(!(actual.salidas||[]).length) avisos.push("no has pedido ninguna salida");
  (actual.salidas||[]).forEach((s,i) => {
    if(s.tipo === "carrusel_pdf" && s.lienzo === "apaisado-16-9")
      avisos.push(`salida ${i+1}: un carrusel PDF apaisado no tiene destino`);
  });
  const impresa = (actual.salidas||[]).some(s =>
    ["carrusel_pdf","laminas","zip"].includes(s.tipo));
  const tope = impresa ? 52 : 96;
  (actual.entrada?.laminas||[]).forEach((L,i) => {
    const n = (L.titular||"").trim().length;
    if(n > tope) avisos.push(`lámina ${i+1}: titular de ${n} caracteres, tope ${tope}`);
  });

  $("#plan").innerHTML = `
    <h2>Lo que se ejecutará</h2>
    <dl class="plan">
      <dt>Paleta</dt><dd><span class="acento" style="background:${ac}"></span>${esc(pal)}${es.paleta?"":" <span class='huella'>(automática)</span>"}</dd>
      <dt>Ánimo</dt><dd>${esc(ani)} ${A.luminoso?"<span class='ok'>luminoso</span>":""}</dd>
      <dt>Luz</dt><dd style="font-size:14px;color:var(--media)">${esc(A.luz)}</dd>
      <dt>Salidas</dt><dd>${(actual.salidas||[]).map(s =>
        `<span class="chip">${esc(s.tipo)} · ${esc(s.lienzo)}${s.montaje&&["reel","video"].includes(s.tipo)?" · "+esc(s.montaje):""}</span>`).join("") || "—"}</dd>
      <dt>Láminas</dt><dd>${(actual.entrada?.laminas||[]).length || (actual.entrada?.tipo==="audio"?"las que salgan del audio":"—")}</dd>
    </dl>
    ${avisos.length ? `<div class="err">${avisos.map(esc).join("<br>")}</div>` : ""}
    <p class="prohibido">Esta voz no permite:
      ${D.voz.prohibido.map(p=>`<b>${esc(p.replace(/_/g," "))}</b>`).join(" · ")}</p>`;
}

/* ---------- guardar ---------- */
async function guardar(){
  const est = $("#estado");
  try{
    const r = await fetch("/guardar-pedido", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({archivo, pedido: actual})
    });
    const j = await r.json();
    if(j.ok){
      est.innerHTML = `<span class="ok">guardado · huella ${esc(j.huella)}</span>`;
      const p = D.pedidos.find(x => x.archivo === archivo);
      if(p){ p.crudo = JSON.parse(JSON.stringify(actual)); p.huella = j.huella; }
      pintarLista();
    } else {
      est.innerHTML = `<span style="color:var(--sangre)">${esc(j.error)}</span>`;
    }
  }catch(e){
    est.innerHTML = `<span style="color:var(--sangre)">
      no hay servidor: abre el portal con «Abrir portal.command»</span>`;
  }
}

pintarLista();
if(D.pedidos.length) abrir(D.pedidos[0].archivo);
"""


def construir():
    datos = estudio_datos.volcar()
    tit = b64(os.path.join(FUENTES, "Fraunces.ttf"))
    txt = b64(os.path.join(FUENTES, "Newsreader.ttf"))
    ui = b64(os.path.join(FUENTES, "Recursive.ttf"))
    crudo = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")

    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Estudio · Fuente Primaria</title>
<style>
@font-face{{font-family:Fraunces;src:url(data:font/ttf;base64,{tit})format("truetype");
  font-weight:100 900;font-display:block}}
@font-face{{font-family:Newsreader;src:url(data:font/ttf;base64,{txt})format("truetype");
  font-weight:200 800;font-display:block}}
@font-face{{font-family:Recursive;src:url(data:font/ttf;base64,{ui})format("truetype");
  font-weight:300 1000;font-display:block}}
{CSS}
</style></head><body>
<div class="env">
  <p class="eyebrow">Mesa de trabajo</p>
  <h1>Estudio</h1>
  <p class="sub">Se elige mirando. Lo que aquí se decide se escribe en el pedido,
    y el pedido es lo que se ejecuta.</p>
  <div class="regla"></div>
  <div class="mesa">
    <div>
      <div class="panel"><h2>Pedidos</h2><div id="lista"></div></div>
      <div class="panel">
        <h2>Voz</h2>
        <p style="font-size:15px">{datos['voz']['titulo']}</p>
        <p class="aviso">{datos['voz']['lema']}</p>
      </div>
      <p style="margin-top:16px"><a href="index.html" class="btn"
        style="text-decoration:none;display:inline-block">← al catálogo</a></p>
    </div>
    <div id="ed"></div>
    <div><div class="panel" id="plan"></div></div>
  </div>
</div>
<script id="datos" type="application/json">{crudo}</script>
<script>{JS}</script>
</body></html>"""

    p = os.path.join(PROY, "sitio", "estudio.html")
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    return p, len(html)


if __name__ == "__main__":
    p, n = construir()
    print("  estudio.html · %.0f KB" % (n / 1024))

from flask import Flask, request, redirect, url_for, render_template_string, jsonify, make_response
from datetime import datetime
from zoneinfo import ZoneInfo
import os, json, textwrap

app = Flask(__name__)

# --- Mock DB (hardcoded) ---
CLIENTES = {
    "1001": {"nombre": "María", "apellido": "Gómez", "direccion": "Av. Siempre Viva 742", "medidor": "MD-742-ARG"},
    "1002": {"nombre": "Jorge", "apellido": "Pérez", "direccion": "Calle 12 #345", "medidor": "MD-12-345"},
    "1003": {"nombre": "Lucía", "apellido": "Fernández", "direccion": "Diagonal 80 1200", "medidor": "MD-80-1200"},
    "2001": {"nombre": "Carlos", "apellido": "Sosa", "direccion": "Matheu 150", "medidor": "MD-150-MLS"},
}

# --- Simple persistent counter (JSON file) ---
COUNTER_PATH = os.path.join(os.path.dirname(__file__), 'reclamos_counter.json')

def get_next_reclamo_id():
    data = {"seq": 0}
    if os.path.exists(COUNTER_PATH):
        try:
            with open(COUNTER_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {"seq": 0}
    data["seq"] = int(data.get("seq", 0)) + 1
    with open(COUNTER_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    # Formato: R-2025-000123 (año-corrido de 6 dígitos)
    year = datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).year
    return f"R-{year}-{data['seq']:06d}"

# --- Templates (Tailwind via CDN) ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ title or 'Reclamos' }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 min-h-screen">
  <div class="max-w-5xl mx-auto p-6">
    <header class="mb-6">
      <h1 class="text-3xl font-bold text-slate-800">📟 Sistema de Reclamos</h1>
      <p class="text-slate-500">Demo Flask + Ticket ZPL</p>
    </header>
    {% block content %}{% endblock %}
    <footer class="mt-10 text-center text-xs text-slate-400">v1 – Demo sin base de datos (hardcode)</footer>
  </div>
</body>
</html>
"""

FORM_HTML = """
{% extends 'base.html' %}
{% block content %}
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <form id="reclamoForm" action="{{ url_for('generar') }}" method="POST" class="lg:col-span-2 bg-white p-6 rounded-2xl shadow">
    <h2 class="text-xl font-semibold mb-4">Alta de Reclamo</h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm text-slate-600 mb-1">Agente (quien recibe)</label>
        <input required type="text" name="agente" class="w-full rounded-xl border-slate-300 focus:border-sky-400 focus:ring-sky-200" placeholder="Nombre y apellido" />
      </div>
      <div>
        <label class="block text-sm text-slate-600 mb-1">Nº de Cliente</label>
        <input required type="text" name="numero_cliente" id="numero_cliente" class="w-full rounded-xl border-slate-300 focus:border-sky-400 focus:ring-sky-200" placeholder="p.ej. 1001" />
      </div>
      <div>
        <label class="block text-sm text-slate-600 mb-1">Nombre</label>
        <input type="text" name="nombre" id="nombre" readonly class="w-full rounded-xl border-slate-200 bg-slate-100" />
      </div>
      <div>
        <label class="block text-sm text-slate-600 mb-1">Apellido</label>
        <input type="text" name="apellido" id="apellido" readonly class="w-full rounded-xl border-slate-200 bg-slate-100" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm text-slate-600 mb-1">Dirección</label>
        <input type="text" name="direccion" id="direccion" readonly class="w-full rounded-xl border-slate-200 bg-slate-100" />
      </div>
      <div>
        <label class="block text-sm text-slate-600 mb-1">Nº de Medidor</label>
        <input type="text" name="medidor" id="medidor" readonly class="w-full rounded-xl border-slate-200 bg-slate-100" />
      </div>
      <div>
        <label class="block text-sm text-slate-600 mb-1">Tipo de problema</label>
        <select name="tipo" id="tipo" class="w-full rounded-xl border-slate-300 focus:border-sky-400 focus:ring-sky-200">
          <option value="Baja tensión">Baja tensión</option>
          <option value="Alta tensión">Alta tensión</option>
          <option value="Sin luz">Sin luz</option>
          <option value="Otro">Otro</option>
        </select>
      </div>
      <div id="otro_wrapper" class="hidden">
        <label class="block text-sm text-slate-600 mb-1">Especifique otro problema</label>
        <input type="text" name="otro_detalle" id="otro_detalle" class="w-full rounded-xl border-slate-300 focus:border-sky-400 focus:ring-sky-200" placeholder="Describa el tipo de problema" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm text-slate-600 mb-1">Comentarios / Detalles del domicilio</label>
        <textarea name="comentarios" rows="4" class="w-full rounded-xl border-slate-300 focus:border-sky-400 focus:ring-sky-200" placeholder="Descripción detallada, referencias, entre calles, etc."></textarea>
      </div>
    </div>

    <div class="flex items-center justify-end gap-3 mt-6">
      <button type="reset" class="px-4 py-2 rounded-xl border text-slate-600">Limpiar</button>
      <button type="submit" class="px-5 py-2.5 rounded-xl bg-sky-600 text-white shadow hover:bg-sky-700">Generar ticket</button>
    </div>
  </form>

  <aside class="bg-white p-6 rounded-2xl shadow h-max">
    <h3 class="font-semibold mb-2">Ayuda</h3>
    <ul class="text-sm text-slate-600 list-disc pl-5 space-y-1">
      <li>Ingresá el Nº de cliente para autocompletar los datos (demo).</li>
      <li>Si el tipo es <em>Otro</em>, detallalo en el campo adicional.</li>
      <li>El número de reclamo y la hora se generan automáticamente.</li>
    </ul>
    <div class="mt-4 text-xs text-slate-500">Clientes demo: 1001, 1002, 1003, 2001.</div>
  </aside>
</div>

<script>
  const numeroCliente = document.getElementById('numero_cliente');
  const otroWrapper = document.getElementById('otro_wrapper');
  const tipoSel = document.getElementById('tipo');

  function toggleOtro() {
    if (tipoSel.value === 'Otro') {
      otroWrapper.classList.remove('hidden');
    } else {
      otroWrapper.classList.add('hidden');
      document.getElementById('otro_detalle').value = '';
    }
  }
  tipoSel.addEventListener('change', toggleOtro);
  toggleOtro();

  async function fetchCliente(nro) {
    if (!nro) return;
    const res = await fetch(`{{ url_for('buscar_cliente') }}?n=${encodeURIComponent(nro)}`);
    const data = await res.json();
    document.getElementById('nombre').value = data.nombre || '';
    document.getElementById('apellido').value = data.apellido || '';
    document.getElementById('direccion').value = data.direccion || '';
    document.getElementById('medidor').value = data.medidor || '';
  }

  numeroCliente.addEventListener('change', (e) => fetchCliente(e.target.value.trim()));
  numeroCliente.addEventListener('blur', (e) => fetchCliente(e.target.value.trim()));
</script>
{% endblock %}
"""

TICKET_HTML = """
{% extends 'base.html' %}
{% block content %}
<div class="bg-white p-6 rounded-2xl shadow">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-xl font-semibold">Ticket generado</h2>
    <div class="text-sm text-slate-500">{{ ts_local }}</div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
    <div class="space-y-1">
      <div><span class="font-semibold">Nº Reclamo:</span> {{ reclamo_id }}</div>
      <div><span class="font-semibold">Agente:</span> {{ agente }}</div>
      <div><span class="font-semibold">Fecha:</span> {{ fecha }}</div>
      <div><span class="font-semibold">Hora:</span> {{ hora }}</div>
    </div>
    <div class="space-y-1">
      <div><span class="font-semibold">Cliente:</span> {{ numero_cliente }} – {{ cliente.nombre }} {{ cliente.apellido }}</div>
      <div><span class="font-semibold">Dirección:</span> {{ cliente.direccion }}</div>
      <div><span class="font-semibold">Medidor:</span> {{ cliente.medidor }}</div>
    </div>
  </div>

  <hr class="my-4" />

  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
    <div><span class="font-semibold">Tipo de problema:</span> {{ tipo }}</div>
    {% if otro_detalle %}<div><span class="font-semibold">Otro:</span> {{ otro_detalle }}</div>{% endif %}
  </div>

  {% if comentarios %}
  <div class="mt-2 text-sm"><span class="font-semibold">Comentarios:</span> {{ comentarios }}</div>
  {% endif %}

  <div class="flex items-center gap-3 mt-6">
    <a href="{{ url_for('zpl', reclamo_id=reclamo_id) }}" class="px-4 py-2 rounded-xl border">Descargar ZPL</a>
    <a href="{{ url_for('index') }}" class="px-4 py-2 rounded-xl bg-slate-800 text-white">Cargar otro</a>
  </div>
</div>
{% endblock %}
"""

# --- Register templates with Flask loader ---
from jinja2 import DictLoader
app.jinja_loader = DictLoader({
    'base.html': BASE_HTML,
    'form.html': FORM_HTML,
    'ticket.html': TICKET_HTML,
})

# --- Routes ---
@app.get('/')
def index():
    return render_template_string(FORM_HTML, title='Alta de Reclamo')

@app.get('/buscar_cliente')
def buscar_cliente():
    n = request.args.get('n', '').strip()
    cli = CLIENTES.get(n, {})
    return jsonify(cli)

@app.post('/generar')
def generar():
    tz = ZoneInfo('America/Argentina/Buenos_Aires')
    now = datetime.now(tz)
    reclamo_id = get_next_reclamo_id()

    numero_cliente = request.form.get('numero_cliente', '').strip()
    cliente = CLIENTES.get(numero_cliente, {
        "nombre": "", "apellido": "", "direccion": "", "medidor": ""
    })

    tipo = request.form.get('tipo', 'Baja tensión')
    otro_detalle = request.form.get('otro_detalle', '').strip() if tipo == 'Otro' else ''
    comentarios = request.form.get('comentarios', '').strip()
    agente = request.form.get('agente', '').strip()

    # Guardar el ticket mínimo en memoria (en un archivo JSON simple por demo)
    store = {
        "reclamo_id": reclamo_id,
        "ts": now.isoformat(),
        "agente": agente,
        "numero_cliente": numero_cliente,
        "cliente": cliente,
        "tipo": tipo,
        "otro_detalle": otro_detalle,
        "comentarios": comentarios,
    }
    # Appends to a small log file (optional)
    try:
        log_path = os.path.join(os.path.dirname(__file__), 'reclamos_log.jsonl')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(store, ensure_ascii=False) + "\n")
    except Exception:
        pass

    fecha = now.strftime('%d/%m/%Y')
    hora = now.strftime('%H:%M:%S')

    ts_local = f"{fecha} {hora} (ART)"
    return render_template_string(
        TICKET_HTML,
        title='Ticket generado',
        ts_local=ts_local,
        reclamo_id=reclamo_id,
        fecha=fecha,
        hora=hora,
        agente=agente,
        numero_cliente=numero_cliente,
        cliente=cliente,
        tipo=tipo,
        otro_detalle=otro_detalle,
        comentarios=comentarios,
    )

# --- ZPL Generation ---

def zpl_escape(text: str) -> str:
    # Basic escaping for ^, ~, \\ characters in ZPL
    return text.replace('^', ' ').replace('~', ' ').replace('\\', '/')

@app.get('/zpl/<reclamo_id>')
def zpl(reclamo_id):
    # In a real app, you'd load by ID. For demo we take latest from log.
    last = None
    log_path = os.path.join(os.path.dirname(__file__), 'reclamos_log.jsonl')
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get('reclamo_id') == reclamo_id:
                        last = obj
                        break
                except Exception:
                    continue
    if not last:
        return make_response("No se encontró el reclamo", 404)

    # Build ZPL (100x150mm aprox – 800x1200 dots at 203dpi)
    # Simple layout
    tz = ZoneInfo('America/Argentina/Buenos_Aires')
    dt = datetime.fromisoformat(last['ts']).astimezone(tz)
    fecha = dt.strftime('%d/%m/%Y')
    hora = dt.strftime('%H:%M:%S')

    cli = last['cliente']

    line1 = f"Reclamo {reclamo_id}"
    line2 = f"Agente: {last['agente']}"
    line3 = f"Fecha: {fecha}  Hora: {hora}"
    line4 = f"Cliente: {last['numero_cliente']} - {cli.get('nombre','')} {cli.get('apellido','')}"
    line5 = f"Dir: {cli.get('direccion','')}"
    line6 = f"Medidor: {cli.get('medidor','')}"

    tipo = last.get('tipo','')
    otro = last.get('otro_detalle','')
    comentarios = last.get('comentarios','')

    if tipo == 'Otro' and otro:
        tipo_line = f"Tipo: {tipo} ({otro})"
    else:
        tipo_line = f"Tipo: {tipo}"

    # Wrap comments to avoid exceeding width
    wrapped = textwrap.wrap(comentarios, width=40)

    zpl = [
        '^XA',
        '^PW800',            # print width
        '^LL1200',           # label length
        '^CF0,40',
        '^FO40,40^FD' + zpl_escape(line1) + '^FS',
        '^CF0,28',
        '^FO40,90^FD' + zpl_escape(line2) + '^FS',
        '^FO40,130^FD' + zpl_escape(line3) + '^FS',
        '^FO40,170^FD' + zpl_escape(line4) + '^FS',
        '^FO40,210^FD' + zpl_escape(line5) + '^FS',
        '^FO40,250^FD' + zpl_escape(line6) + '^FS',
        '^FO40,300^FD' + zpl_escape(tipo_line) + '^FS',
        '^FO40,340^GB720,2,2^FS',  # divider
        '^CF0,26',
    ]

    y = 380
    for line in wrapped[:10]:  # limit lines
        zpl.append(f'^FO40,{y}^FD' + zpl_escape(line) + '^FS')
        y += 32

    # QR with ID for quick lookup
    zpl += [
        '^FO520,40^BQN,2,6',
        '^FDLA,' + zpl_escape(reclamo_id) + '^FS',
        '^XZ'
    ]

    zpl_str = "\n".join(zpl)
    resp = make_response(zpl_str)
    resp.headers['Content-Type'] = 'application/zpl'
    resp.headers['Content-Disposition'] = f'attachment; filename="ticket_{reclamo_id}.zpl"'
    return resp

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)


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
    "310788000360": {"nombre": "Gabriela", "apellido": "AGUILA", "direccion": "B° Santa Cruz mza 722 L-12 casa 11 Calle 11 E/ 50 y 43", "medidor": "5047990"},
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
    # Carga el ticket desde log (demo)
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

    # Datos base
    tz = ZoneInfo('America/Argentina/Buenos_Aires')
    dt = datetime.fromisoformat(last['ts']).astimezone(tz)
    fecha = dt.strftime('%d/%m/%Y')
    hora  = dt.strftime('%H:%M:%S')
    cli   = last['cliente']

    # Líneas
    titulo       = f"Reclamo {reclamo_id}"
    agente_line  = f"Agente: {last['agente']}"
    fechahora    = f"Fecha: {fecha}   Hora: {hora}"
    cliente_line = f"Cliente: {last['numero_cliente']} - {cli.get('nombre','')} {cli.get('apellido','')}"
    med_line     = f"Medidor: {cli.get('medidor','')}"
    tipo         = last.get('tipo','')
    otro         = last.get('otro_detalle','')
    tipo_line    = f"Motivo: {tipo} - {otro}" if (tipo == 'Otro' and otro) else f"Motivo: {tipo}"
    comentarios  = last.get('comentarios','')

    # Dirección multilínea (≈34 chars por línea en 80mm con CF0,26/24)
    direccion = cli.get('direccion','')
    dir_lines = textwrap.wrap("Dom.: " + direccion, width=34)

    # ZPL 80mm con logo encabezado
    zpl = [
        '^XA',
        '^PW576',         # ancho total (80mm @203dpi)
        '^LL900',         # alto de la etiqueta (ajustable)
        '^LH0,0',
        '^CI28',

        # --- LOGO encabezado ---
        "^FO90,10^GFA,6426,6426,34,N03hOFC,L01hSF,L0hTFE,K03hUF8,K0hVFE,J03hWF8,J0hXFC,I01hXFE,I03hYF8,I07hYFC,I0iFE,001KFChO07JFE,003JF8hQ03JF,007IFChS0JF8,00JFhT03IFC,00IFEhT01IFE,01IFChU07FFE,03IF8hU03IF,03IFhV01IF,07FFEhW0IF8,07FFChW0IF8,0IF8hW07FFC,0IFhX03FFC,0IFhX03FFE,1FFEL0hLFCK01FFE,1FFEK07hMF8J01FFE,3FFCJ01hNFEK0IF,3FFCJ07hOF8J0IF,3FF8J0hPFCJ07FF,3FF8I01hPFEJ07FF,7FF8I03hPFEJ07FF8,7FFJ07hQFJ03FF8,7FFJ07hQF8I03FF8,7FFJ0hRF8I03FF8,7FFJ0hRFCI03FF8,7FFI01IFChK0IFCI03FF8,7FFI01IFhL03FFCI01FFC,FFEI01FFEhL01FFCI01FFC,FFEI01FFChL01FFCI01FFC,:FFEI01FFChM0FFEI01FFC,FFEI01FFChL01FFCI01FFC,:FFEI01FFEhL01FFCI01FFC,FFEI01IFhL03FFCI01FFC,IFJ0JFhK0IFCI01FFC,7FFJ0WFEO07gJFCI03FF8,7FFJ0XFEN07gJF8I03FF8,7FFJ07XF8M07gJF8I03FF8,7FFJ03XFEM07gJFJ03FF8,7FFJ03YF8L07gIFEJ03FF8,7FF8I01YFEL07gIFEJ07FF8,3FF8J0gFL07gIFCJ07FF,3FF8J03YF8K07gIF8J07FF,3FFCJ01YFCK07gHFEK0IF,3FFCK03XFEK07gHF8K0IF,1FFCL03XFK07gGFCK01FFE,1FFEg07JF8J07FFgK01FFE,1FFEgG0JFCJ07FFgK03FFE,0IFgG01IFEJ07FFgK03FFC,0IF8gG0IFEJ07FFgK07FFC,07FF8gG03IFJ07FFgK0IF8,07FFCgG01IF8I07FFgK0IF8,03FFEgH0IF8I07FFgJ01IF,03IFgH07FFCI07FFgJ03IF,01IF8gG07FFCI07FFgJ07FFE,01IFCgG03FFEI07FFgI01IFE,00JFgG01FFEI07FFgI03IFC,007IFCg01IFI07FFgI0JF8,003JFgG0IFI07FFgH07JF,003KFg07FFI07FFgG07JFE,001gFCJ07FF8007FFJ0gHFE,I0gGF8I07FF8007FFJ0gHFC,I07gFEI03FF8007FFJ0gHF,I01gGFI03FFC007FFJ0gGFE,J0gGF8003FFC007FFJ0gGFC,J07gFC001FFC007FFJ0gGF,J01gFE001FFC007FFJ0gFE,K07YFE001FFC007FFJ0gF8,K01gF001FFE007FFJ0YFC,L03YFI0FFE007FFJ0XFE,M01XF800FFE007FFJ0WFC,gI0IF800FFE007FFJ0FFE,gI07FF800FFE007FFJ0FFE,gI03FF800FFE007FFJ0FFE,::::gI07FF800FFE007FFJ0FFE,gI0IF800FFE007FFJ0FFE,3gKF800FFE007FFJ0FFE,3gKFI0FFE007FFJ0FFE,:3gJFE001FFE007FFJ0FFE,3gJFE001FFC007FFJ0FFE,3gJFC001FFC007FFJ0FFE,3gJF8001FFC007FFJ0FFE,3gJFI03FFC007FFJ0FFE,3gIFEI03FF8007FFJ0FFE,3gIF8I03FF8007FFJ0FFE,3gHFCJ07FF8007FFJ0FFE,3FF8gJ07FF8007FFJ0FFE,3FF8gJ0IFI07FFJ0FFE,:3FF8gI01IFI07FFJ0FFE,3FF8gI01FFEI07FFJ0FFE,3FF8gI03FFEI07FFJ0FFE,3FF8gI07FFCI07FFJ0FFE,3FF8gI0IFCI07FFJ0FFE,3FF8gH01IF8I07FFJ0FFE,3FF8gH03IF8I07FFJ0FFE,3FF8gH07IFJ07FFJ0FFE,3FF8gG01IFEJ07FFJ0FFE,3FF8gG03IFEJ07FFJ0FFE,3FF8g01JFCJ07FFJ0FFE,3FF8Y01KF8J07FFJ0FFE,3gNFK07NFE,3gMFEK07NFE,3gMFCK07NFE,3gMF8K07NFE,3gLFEL07NFE,3gLFCL07NFE,3gLFM07NFE,3gKFCM07NFE,3gKFN07OF,3gJF8N07OF,3gIFP07NFE,,:::::::::::::::::J0FC07FF0FF83807380FC0E03F003FI07F80C070FF80E00700F801FC01F8,I01FF07FF1FFE380F383FE0E0FFC07FC007FE0C070FFE0E00703FE03FE03FE,I03CF87FF1IF3C0E387FF0E1FFE0F3E007FF0C070IF0E00707FE07FF079F,I038387001C071C0E387078E1E0F0C0E007078C070E070E0070E070F078707,I030387001C071C1C38E038E3C070C0E007038C070E070E0070E070E038707,I03C007001C071E1C38EI0E38038FJ07038C070E070E0071C001C01C78,I03F807001C0F0E1C38EI0E38038FEI07078C070E1E0E0071C001C01C7F,I01FE07FF1FFE0E3838EI0E380387F80073F0C070FFC0E0071C001C01C3FE,J07F87FF1FFC073838EI0E380381FE007FE0C070FFE0E0071C001C01C0FF,K0787001E78073838EI0E3803801E007FC0C070E070E0071C001C01C00F,K03C7001C3C073038E020E3803800E007I0E070E038E0071C001C01C0078,I0701C7001C1E03F038E038E3C071C07007I0E070E038E0071E071E03CE038,I0783C7001C0E03F0387078E1C0F1E0E007I0E070E078E0070E070F078F078,I03C7877F1C0F03E0387CF0E1F1E0F1E007I0F1E0EDF0EFC70F9F078F878F,I01FF07FF1C0781E0383FE0E0FFC0FFC007I07FE0IF0FFE707FE03FE03FF,J0FE07FF1C0381E0380FC0E03F803F8007I03F80FFC0FFE701F801FC01FC,^FS",

        # Título y QR (más abajo por el logo)
        '^CF0,32',
        '^FO20,215^FD' + zpl_escape(titulo) + '^FS',
        '^FO430,190^BQN,2,4',
        '^FDLA,' + zpl_escape(reclamo_id) + '^FS',

        # Separador
        #'^FO20,240^GB536,2,2^FS',

        # Datos principales
        '^CF0,26',
        '^FO20,260^FD' + zpl_escape(agente_line)  + '^FS',
        '^FO20,290^FD' + zpl_escape(fechahora)    + '^FS',
        '^FO20,320^FD' + zpl_escape(cliente_line) + '^FS',
    ]

    # Dirección multilínea
    y = 350
    for line in dir_lines:
        zpl.append(f'^FO20,{y}^FD' + zpl_escape(line) + '^FS')
        y += 28

    # Medidor + Motivo
    zpl += [
        f'^FO20,{y}^FD'     + zpl_escape(med_line)  + '^FS',
        f'^FO20,{y+30}^FD'  + zpl_escape(tipo_line) + '^FS',
        f'^FO20,{y+60}^GB536,2,2^FS',
        '^CF0,24',
        f'^FO20,{y+80}^FD'  + zpl_escape('Informe y observaciones:') + '^FS',
    ]

    # Comentarios multilínea
    wrapped = textwrap.wrap(comentarios, width=34)
    y_comments = y + 110
    for line in wrapped[:9]:
        zpl.append(f'^FO20,{y_comments}^FD' + zpl_escape(line) + '^FS')
        y_comments += 28

    # Pie (línea + Nº reclamo). Calculamos una Y segura.
    footer_y = max(y_comments + 20, 760)
    zpl += [
        f'^FO20,{footer_y}^GB536,2,2^FS',
        '^CF0,26',
        f'^FO20,{footer_y+20}^FD' + zpl_escape('N° de reclamo: ' + reclamo_id) + '^FS',
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


from flask import Blueprint, render_template, request, jsonify, make_response
from config import TZ
from repositories.clientes_repo import HardcodedClientesRepository
from repositories.tickets_repo import JsonlTicketsRepository
from services.tickets_service import TicketsService
from printers.zpl_builder import build_ticket_zpl


bp = Blueprint("reclamos", __name__)


_clientes_repo = HardcodedClientesRepository()
_tickets_repo = JsonlTicketsRepository()
_service = TicketsService(_clientes_repo, _tickets_repo)




@bp.get("/")
def index():
    return render_template("form.html", title="Alta de Reclamo")




@bp.get("/buscar_cliente")
def buscar_cliente():
    n = request.args.get("n", "").strip()
    cli = _clientes_repo.get_by_numero(n)
    if not cli:
        return jsonify({})
    return jsonify({
        "nombre": cli.nombre,
        "apellido": cli.apellido,
        "direccion": cli.direccion,
        "medidor": cli.medidor,
    })




@bp.post("/generar")
def generar():
    numero_cliente = request.form.get('numero_cliente', '').strip()
    tipo = request.form.get('tipo', 'Baja tensión')
    otro_detalle = request.form.get('otro_detalle', '').strip() if tipo == 'Otro' else ''
    comentarios = request.form.get('comentarios', '').strip()
    agente = request.form.get('agente', '').strip()


    ticket = _service.crear_ticket(agente, numero_cliente, tipo, otro_detalle, comentarios)


    fecha = ticket.ts.strftime('%d/%m/%Y')
    hora = ticket.ts.strftime('%H:%M:%S')


    return render_template(
        "ticket.html",
        title="Ticket generado",
        ts_local=f"{fecha} {hora} (ART)",
        reclamo_id=ticket.id,
        fecha=fecha,
        hora=hora,
        agente=ticket.agente,
        numero_cliente=ticket.cliente_numero,
        cliente={
            "nombre": ticket.cliente.nombre,
            "apellido": ticket.cliente.apellido,
            "direccion": ticket.cliente.direccion,
            "medidor": ticket.cliente.medidor,
        },
        tipo=tipo,
        otro_detalle=otro_detalle,
        comentarios=comentarios,
        )




@bp.get("/zpl/<reclamo_id>")
def zpl(reclamo_id):
    ticket = _tickets_repo.find_by_id(reclamo_id)
    if not ticket:
        return make_response("No se encontró el reclamo", 404)
    zpl_str = build_ticket_zpl(ticket)
    resp = make_response(zpl_str)
    resp.headers['Content-Type'] = 'application/zpl'
    resp.headers['Content-Disposition'] = f'attachment; filename="ticket_{reclamo_id}.zpl"'
    return resp

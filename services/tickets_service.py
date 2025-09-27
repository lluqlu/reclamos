# services/tickets_service.py
import json
from datetime import datetime
from typing import Optional
from config import COUNTER_PATH, TZ
from domain.models import Ticket, Cliente, ProblemaTipo
from repositories import ClientesRepository, TicketsRepository


def _next_reclamo_id(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(TZ)
    seq = 0
    if COUNTER_PATH.exists():
        try:
            data = json.loads(COUNTER_PATH.read_text("utf-8"))
            seq = int(data.get("seq", 0))
        except Exception:
            seq = 0
    seq += 1
    COUNTER_PATH.write_text(json.dumps({"seq": seq}), encoding="utf-8")
    return f"R-{now.year}-{seq:06d}"


class TicketsService:
    def __init__(self, clientes_repo: ClientesRepository, tickets_repo: TicketsRepository):
        self.clientes_repo = clientes_repo
        self.tickets_repo = tickets_repo

    def crear_ticket(self, agente: str, numero_cliente: str, tipo: str, otro_detalle: str, comentarios: str) -> Ticket:
        cliente = self.clientes_repo.get_by_numero(numero_cliente) or Cliente(
            numero=numero_cliente, nombre="", apellido="", direccion="", medidor=""
        )
        ticket = Ticket(
            id=_next_reclamo_id(),
            ts=datetime.now(TZ),
            agente=agente.strip(),
            cliente_numero=numero_cliente.strip(),
            cliente=cliente,
            tipo=ProblemaTipo(tipo),
            otro_detalle=otro_detalle.strip(),
            comentarios=comentarios.strip(),
        )
        self.tickets_repo.append(ticket)
        return ticket


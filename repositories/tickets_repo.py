import json
from datetime import datetime
from typing import Optional
from domain.models import Ticket, Cliente, ProblemaTipo
from config import LOG_PATH, TZ




class JsonlTicketsRepository:
    def append(self, ticket: Ticket) -> None:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            obj = {
                "id": ticket.id,
                "ts": ticket.ts.isoformat(),
                "agente": ticket.agente,
                "cliente_numero": ticket.cliente_numero,
                "cliente": {
                "numero": ticket.cliente.numero,
                "nombre": ticket.cliente.nombre,
                "apellido": ticket.cliente.apellido,
                "direccion": ticket.cliente.direccion,
                "medidor": ticket.cliente.medidor,
                },
                "tipo": ticket.tipo.value,
                "otro_detalle": ticket.otro_detalle,
                "comentarios": ticket.comentarios,
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        if not LOG_PATH.exists():
            return None
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("id") == ticket_id:
                        cli = obj["cliente"]
                        cliente = Cliente(
                            numero=cli["numero"],
                            nombre=cli["nombre"],
                            apellido=cli["apellido"],
                            direccion=cli["direccion"],
                            medidor=cli["medidor"],
                        )
                        return Ticket(
                            id=obj["id"],
                            ts=datetime.fromisoformat(obj["ts"]).astimezone(TZ),
                            agente=obj["agente"],
                            cliente_numero=obj["cliente_numero"],
                            cliente=cliente,
                            tipo=ProblemaTipo(obj["tipo"]),
                            otro_detalle=obj.get("otro_detalle", ""),
                            comentarios=obj.get("comentarios", ""),
                            )
                except Exception:
                    continue
            return None

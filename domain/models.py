from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional




class ProblemaTipo(str, Enum):
    BAJA_TENSION = "Baja tensión"
    ALTA_TENSION = "Alta tensión"
    SIN_LUZ = "Sin luz"
    OTRO = "Otro"




@dataclass
class Cliente:
    numero: str
    nombre: str
    apellido: str
    direccion: str
    medidor: str




@dataclass
class Ticket:
    id: str
    ts: datetime
    agente: str
    cliente_numero: str
    cliente: Cliente
    tipo: ProblemaTipo
    otro_detalle: str = ""
    comentarios: str = ""

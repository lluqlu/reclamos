from typing import Protocol, Optional
from domain.models import Cliente, Ticket

class ClientesRepository(Protocol):
    def get_by_numero(self, numero: str) -> Optional[Cliente]:
        ...

class TicketsRepository(Protocol):
    def append(self, ticket: Ticket) -> None:
        ...
    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        ...


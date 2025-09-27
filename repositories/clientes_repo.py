from typing import Dict, Optional
from domain.models import Cliente




class HardcodedClientesRepository:
    def __init__(self):
        self._data: Dict[str, Cliente] = {
            "1001": Cliente("1001", "María", "Gómez", "Av. Siempre Viva 742", "5047990"),
            "1002": Cliente("1002", "Jorge", "Pérez", "Calle 12 #345", "4256578"),
            "1003": Cliente("1003", "Carlos", "Monzón", "Elvira Rawson 129", "5631247"),
            "2001": Cliente("2001", "Carlos", "Sosa", "Matheu 150", "5237894"),
        }


    def get_by_numero(self, numero: str) -> Optional[Cliente]:
        return self._data.get(numero)

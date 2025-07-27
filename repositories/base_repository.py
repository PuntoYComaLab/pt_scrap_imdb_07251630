from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRepository(ABC):
    """Repositorio base siguiendo Clean Architecture"""
    
    @abstractmethod
    def save(self, data: List[Dict[str, Any]]) -> bool:
        """Guarda los datos en el repositorio"""
        pass
    
    @abstractmethod
    def delete_all(self) -> bool:
        """Elimina todos los datos del repositorio"""
        pass 
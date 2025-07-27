import csv
import os
from typing import List, Dict, Any
from repositories.base_repository import BaseRepository
from util import log_info, log_error

class CSVRepository(BaseRepository):
    """Repositorio que guarda datos en archivos CSV"""
    
    def __init__(self, filename: str, data_dir: str = "data"):
        self.filename = filename
        self.data_dir = data_dir
        self.filepath = os.path.join(data_dir, f"{filename}.csv")
        
        # Crear directorio si no existe
        os.makedirs(data_dir, exist_ok=True)
    
    def save(self, data: List[Dict[str, Any]]) -> bool:
        """Guarda los datos en un archivo CSV"""
        if not data:
            log_error("No hay datos para guardar")
            return False
        
        try:
            fieldnames = data[0].keys()
            
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            log_info(f"Datos guardados exitosamente en {self.filepath}")
            return True
            
        except Exception as e:
            log_error(f"Error guardando datos en CSV {self.filepath}: {e}")
            return False
    
    def delete_all(self) -> bool:
        """Elimina el archivo CSV"""
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
                log_info(f"Archivo {self.filepath} eliminado")
            return True
        except Exception as e:
            log_error(f"Error eliminando archivo {self.filepath}: {e}")
            return False 
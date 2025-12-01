from app.models import Especialidad
from app.repositories import EspecialidadRepository
from typing import Optional, List, Dict, Any
import math
import logging
from functools import wraps
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator para reintentar operaciones con delay exponencial"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logging.error(f"Error después de {max_attempts} intentos: {str(e)}")
                        raise
                    wait_time = delay * (2 ** (attempt - 1))
                    logging.warning(f"Intento {attempt} falló. Reintentando en {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                    attempt += 1
        return wrapper
    return decorator

class EspecialidadService:
    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def listar_especialidades(page: int = 1, per_page: int = 10, filters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        especialidades: List[Especialidad] = EspecialidadRepository.listar_especialidades(page, per_page, filters)
        total_elements: int = EspecialidadRepository.contar_especialidades(filters)

        if per_page > 0:
            total_pages = math.ceil(total_elements / per_page)
        else:
            total_pages = 0

        return {
            "content": especialidades,
            "page": page,
            "size": per_page,
            "total_elements": total_elements,
            "total_pages": total_pages
        }

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def crear_especialidad(especialidad: Especialidad):
        EspecialidadRepository.crear_especialidad(especialidad)
        return especialidad

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def buscar_especialidad(id: int):
        especialidad = EspecialidadRepository.buscar_especialidad(id)
        return especialidad

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def actualizar_especialidad(especialidad: Especialidad, id: int):
        EspecialidadRepository.actualizar_especialidad(especialidad, id)

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def eliminar_especialidad(id: int):
        EspecialidadRepository.eliminar_especialidad(id)

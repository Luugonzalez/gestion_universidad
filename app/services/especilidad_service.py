from app.models import Especialidad
from app.repositories import EspecialidadRepository
from typing import Optional
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
    def listar_especialidades(page: int = 1, per_page: int = 10, filters: Optional[list] = None):
        logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
        return EspecialidadRepository.listar_especialidades(page, per_page, filters)

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
    def actualizar_especialidad(id: int, especialidad: Especialidad):
        EspecialidadRepository.actualizar_especialidad(id, especialidad)
        return especialidad

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def eliminar_especialidad(id: int):
        EspecialidadRepository.eliminar_especialidad(id)

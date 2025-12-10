from app.repositories.especialidad_repository import EspecialidadRepository
from app.models import Especialidad
import logging
import math
from app.utils.retry import retry


class EspecialidadService:

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def listar_especialidades(page: int = 1, per_page: int = 10, filters: list = None):
        especialidades = EspecialidadRepository.listar_especialidades(page, per_page, filters)
        total_elements = EspecialidadRepository.contar_especialidades(filters)

        total_pages = math.ceil(total_elements / per_page) if per_page > 0 else 0

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
        creada = EspecialidadRepository.crear_especialidad(especialidad)
        logging.info(f"Especialidad creada con id {creada.id}")
        return creada

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def buscar_especialidad(id: int):
        return EspecialidadRepository.buscar_especialidad(id)

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def actualizar_especialidad(especialidad: Especialidad, id: int):
        actualizada = EspecialidadRepository.actualizar_especialidad(especialidad, id)
        if actualizada:
            logging.info(f"Especialidad {id} actualizada")
        else:
            logging.warning(f"Intento de actualizar especialidad inexistente {id}")
        return actualizada

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def eliminar_especialidad(id: int):
        EspecialidadRepository.eliminar_especialidad(id)
        logging.info(f"Especialidad {id} eliminada (si existía)")

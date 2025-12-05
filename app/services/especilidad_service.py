from app.models import Especialidad
from app.repositories import EspecialidadRepository
from typing import Optional, List, Dict, Any
import math
from app.utils.retry import retry

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
    def buscar_especialidad(id: int) -> Especialidad| None:
        especialidad = EspecialidadRepository.buscar_especialidad(id)
        return especialidad

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def actualizar_especialidad(especialidad: Especialidad, id: int) -> Especialidad| None:
        return EspecialidadRepository.actualizar_especialidad(especialidad, id)
        

    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    def eliminar_especialidad(id: int):
        EspecialidadRepository.eliminar_especialidad(id)

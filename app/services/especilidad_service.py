from app.models import Especialidad
from app.repositories import EspecialidadRepository
from typing import Optional
import logging

class EspecialidadService:
    @staticmethod
    def listar_especialidades(page: int = 1, per_page: int = 10, filters: Optional[list] = None):
        logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
        return EspecialidadRepository.listar_especialidades(page, per_page, filters)

    @staticmethod
    def crear_especialidad(especialidad: Especialidad):
        EspecialidadRepository.crear_especialidad(especialidad)
        return especialidad

    @staticmethod
    def buscar_especialidad(id: int):
        especialidad = EspecialidadRepository.buscar_especialidad(id)
        return especialidad

    @staticmethod
    def actualizar_especialidad(id: int, especialidad: Especialidad):
        EspecialidadRepository.actualizar_especialidad(id, especialidad)
        return especialidad

    @staticmethod
    def eliminar_especialidad(id: int):
        EspecialidadRepository.eliminar_especialidad(id)

from app.models import Facultad
from app.repositories import FacultadRepository
from typing import Optional
import requests
from app.utils.retry import retry
import logging

class FacultadService:
  @retry(max_attempts=3, delay=1)
  def obtener_especialidad(self, id):
        url = f"http://especialidad:5000/api/especialidades/{id}"

        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            raise Exception(f"Error HTTP {response.status_code} en Especialidad")

        return response.json()

  @staticmethod
  def crear_facultad(facultad: Facultad):
    FacultadRepository.crear_facultad(facultad)
    return facultad
  
  @staticmethod
  def listar_facultades(page: int = 1, per_page: int = 10, filters: Optional[list] = None):
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
    facultades = FacultadRepository.listar_facultades(page, per_page, filters)
    return facultades

  @staticmethod
  def buscar_facultad(id: int):
    facultad = FacultadRepository.buscar_facultad(id)
    return facultad
    
  @staticmethod
  def actualizar_facultad(facultad: Facultad, id: int):
    FacultadRepository.actualizar_facultad(facultad, id)
    return facultad
  
  @staticmethod
  def eliminar_facultad(id: int):
    facultad = FacultadRepository.eliminar_facultad(id)
    return facultad
    
    
    
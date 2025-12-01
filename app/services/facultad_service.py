from app.models import Facultad
from app.repositories import FacultadRepository
from typing import Optional, List, Dict, Any
import requests
from app.utils.retry import retry
import logging
import math

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
  def listar_facultades(page: int = 1, per_page: int = 10, filters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Lista facultades, aplica paginación, y devuelve los metadatos asociados.

    Args:
        page: Número de página (base 1).
        per_page: Cantidad de elementos por página.
        filters: Lista de diccionarios en formato sqlalchemy-filters.

    Returns:
        Un diccionario con la lista de facultades en 'content' y los metadatos de paginación.
    """
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
    facultades: List[Facultad] = FacultadRepository.listar_facultades(page, per_page, filters)
    total_elements: int = FacultadRepository.contar_facultades(filters)

    if per_page > 0:
        total_pages = math.ceil(total_elements / per_page)
    else:
        total_pages = 0

    return {
        'content': facultades,
        'page': page,
        'size': per_page,
        'total_elements': total_elements,
        'total_pages': total_pages
    }

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



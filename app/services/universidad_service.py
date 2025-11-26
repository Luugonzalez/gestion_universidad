from app.models import Universidad
from app.repositories import UniversidadRepository
from typing import Optional, List, Dict, Any
import math

class UniversidadService:

    @staticmethod
    def crear_universidad(universidad: Universidad) -> Universidad:
        UniversidadRepository.crear_universidad(universidad)
        return universidad

    @staticmethod
    def listar_universidades(page: int = 1, per_page: int = 10, filters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Lista universidades, aplica paginación, y devuelve los metadatos asociados.

        Args:
            page: Número de página (base 1).
            per_page: Cantidad de elementos por página.
            filters: Lista de diccionarios en formato sqlalchemy-filters.

        Returns:
            Un diccionario con la lista de universidades en 'content' y los metadatos de paginación.
        """
        universidades: List[Universidad] = UniversidadRepository.listar_universidades(page, per_page, filters)
        total_elements: int = UniversidadRepository.contar_universidades(filters)

        if per_page > 0:
            total_pages = math.ceil(total_elements / per_page)
        else:
            total_pages = 0

        return {
            'content': universidades,
            'page': page,
            'size': per_page,
            'total_elements': total_elements,
            'total_pages': total_pages
        }

    @staticmethod
    def buscar_universidad(universidad_id: int) -> Optional[Universidad]:
        return UniversidadRepository.buscar_universidad(universidad_id)

    @staticmethod
    def actualizar_universidad(universidad: Universidad, universidad_id: int) -> Optional[Universidad]:
        UniversidadRepository.actualizar_universidad(universidad, universidad_id)
        return universidad

    @staticmethod
    def eliminar_universidad(universidad_id: int) -> Optional[Universidad]:
        return UniversidadRepository.eliminar_universidad(universidad_id)
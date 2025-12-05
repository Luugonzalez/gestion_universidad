from flask import jsonify, Blueprint, request 
from app.mapping import UniversidadMapping
from app.services.universidad_service import UniversidadService
from markupsafe import escape
import json
import logging
from app.validators import validate_with
from app import cache

from typing import Dict, Any, List

universidad_bp = Blueprint('universidad', __name__)

universidad_mapping = UniversidadMapping()

def format_filters_for_sqlalchemy(filters_dict: Dict[str, Any]) -> List:
    """
    Convierte un diccionario simple (desde el header X-filters) 
    al formato de lista de diccionarios que espera sqlalchemy-filters.
    Por defecto, usa la operación de igualdad '=='.
    """
    filters_list = []
    if filters_dict:
        for key, value in filters_dict.items():
            filters_list.append({
                "field": key,
                "op": "==", 
                "value": value
            })
    return filters_list

@universidad_bp.route('/universidad/<hashid:id>', methods=['GET'])
@cache.cached(timeout=60)
def buscar_por_hashid(id):
    universidad = UniversidadService.buscar_universidad(id)
    if universidad is None:
        return jsonify({"error": "Universidad no encontrada"}), 404
    return universidad_mapping.dump(universidad), 200


@universidad_bp.route('/universidad', methods=['GET'])
def listar_universidades():
    page: int = request.headers.get('X-page', 1, type=int)
    per_page: int = request.headers.get('X-per-page', 10, type=int) 
    filters_str : str|None = request.headers.get('X-filters', None, type=str) 
    
    filters = []
    if filters_str:
        try:
            filters_dict = json.loads(filters_str)
            # 1. Aplicamos el formateo antes de pasar el filtro al servicio/repositorio
            filters = format_filters_for_sqlalchemy(filters_dict)
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar X-filters: {e}")
            return jsonify({"error": "Formato de filtros inválido en X-filters"}), 400
    
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))

    # 2. El servicio ahora devuelve un diccionario con 'content' y 'pageable'
    pagination_data = UniversidadService.listar_universidades(page=page, per_page=per_page, filters=filters)
    
    # 3. Serializar solo el contenido y construir la respuesta completa
    content = universidad_mapping.dump(pagination_data['content'], many=True)
    
    response = {
        "content": content,
        "pageable": {
            "page": pagination_data['page'],
            "size": pagination_data['size'],
            "total_elements": pagination_data['total_elements'],
            "total_pages": pagination_data['total_pages']
        }
    }
    
    return jsonify(response), 200

@universidad_bp.route('/universidad', methods=['POST']) 
@validate_with(UniversidadMapping)
def crear(universidad):
    UniversidadService.crear_universidad(universidad)
    return jsonify("Universidad creada exitosamente"), 201 

@universidad_bp.route('/universidad/<hashid:id>', methods=['PUT'])
@validate_with(UniversidadMapping)
def actualizar(universidad, id):
    UniversidadService.actualizar_universidad(universidad, id)
    return jsonify("Universidad actualizada exitosamente"), 200 

@universidad_bp.route('/universidad/<hashid:id>', methods=['DELETE'])
def borrar_por_hashid(id):
    UniversidadService.eliminar_universidad(id)
    return jsonify("Universidad borrada exitosamente"), 200 


def sanitizar_universidad_entrada(request):
    universidad = universidad_mapping.load(request.get_json())
    universidad.nombre = escape(universidad.nombre)
    universidad.sigla = escape(universidad.sigla)
    universidad.tipo = escape(universidad.tipo) 
    return universidad





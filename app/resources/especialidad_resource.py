from flask import jsonify, Blueprint, request
from app.mapping.especialidad_mapping import EspecialidadMapping            
from app.services.especilidad_service import EspecialidadService
from app.models.especialidad import Especialidad
from markupsafe import escape
import json
import logging
from app.validators import validate_with
from app import cache

from typing import Dict, Any, List

especialidad_bp = Blueprint('especialidad', __name__)
especialidad_mapping = EspecialidadMapping()    

def format_filters_for_sqlalchemy(filters_dict: Dict[str, Any]) -> List:
    filters_list = []
    if filters_dict:
        for key, value in filters_dict.items():
            filters_list.append({
                "field": key,
                "op": "==", 
                "value": value
            })
    return filters_list

@especialidad_bp.route('/especialidad', methods=['GET'])
def listar_especialidades():
    page: int = request.headers.get('X-page', 1, type=int)
    per_page: int = request.headers.get('X-per-page', 10, type=int) 
    filters_str : str|None = request.headers.get('X-filters', None, type=str) 

    filters = [] 
    if filters_str:
        try:
            filters_dict = json.loads(filters_str)
            filters = format_filters_for_sqlalchemy(filters_dict)
        
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar X-filters: {e}")
            return jsonify({"error": "Formato de filtros inválido en X-filters"}), 400
        
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
        
    pagination_data = EspecialidadService.listar_especialidades(page=page, per_page=per_page, filters=filters)
    content = especialidad_mapping.dump(pagination_data['content'], many=True)

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

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['GET'])
@cache.cached(timeout=60)
def buscar_por_hashid(id):
    especialidad = EspecialidadService.buscar_especialidad(id)
    return especialidad_mapping.dump(especialidad), 200 

@especialidad_bp.route('/especialidad', methods=['POST'])
@validate_with(EspecialidadMapping)
def crear(especialidad):
    especialidad = especialidad_mapping.load(request.get_json())
    especialidad = sanitizar_especialidad_entrada(especialidad)
    EspecialidadService.crear_especialidad(especialidad)
    return jsonify("Especialidad creada exitosamente"), 201

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['PUT'])
@validate_with(EspecialidadMapping)
def actualizar(especialidad, id):
    especialidad = especialidad_mapping.load(request.get_json())
    especialidad = sanitizar_especialidad_entrada(especialidad)
    EspecialidadService.actualizar_especialidad(especialidad, id)
    return jsonify("Especialidad actualizada exitosamente"), 200        

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['DELETE'])
def borrar_por_hashid(id):
    EspecialidadService.eliminar_especialidad(id)
    return jsonify("Especialidad borrada exitosamente"), 200    

def sanitizar_especialidad_entrada(especialidad: Especialidad):
    especialidad.nombre = escape(especialidad.nombre)
    especialidad.letra = escape(especialidad.letra)
    especialidad.observacion = escape(especialidad.observacion)
    return especialidad


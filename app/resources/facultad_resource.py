from flask import jsonify, Blueprint, request 
from app.mapping.facultad_mapping import FacultadMapping
from app.services.facultad_service import FacultadService
from app.models.facultad import Facultad
from markupsafe import escape
from app.validators import validate_with
import json
import logging
from app import cache

from typing import Dict, Any, List

facultad_bp = Blueprint('facultad', __name__)
facultad_mapping = FacultadMapping()

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

@facultad_bp.route('/facultad', methods=['GET'])
def listar_facultades():
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
    
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters_str))
    
    pagination_data = FacultadService.listar_facultades(page=page, per_page=per_page, filters=filters)
    content = facultad_mapping.dump(pagination_data['content'], many=True)
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
    
@facultad_bp.route('/facultad/<hashid:id>', methods=['GET']) 
@cache.cached(timeout=60)
def buscar_por_hashid(id):
    facultad = FacultadService.buscar_facultad(id)
    if facultad is None:
        return jsonify({"error": "Facultad no encontrada"}), 404
    return facultad_mapping.dump(facultad), 200

@facultad_bp.route('/facultad', methods=['POST']) 
@validate_with(FacultadMapping)
def crear(facultad):
    FacultadService.crear_facultad(facultad)
    return jsonify("Facultad creada exitosamente"), 201 

@facultad_bp.route('/facultad/<hashid:id>', methods=['PUT']) 
@validate_with(FacultadMapping)
def actualizar(facultad, id):
    FacultadService.actualizar_facultad(facultad, id)
    return jsonify("Facultad actualizada exitosamente"), 200 

@facultad_bp.route('/facultad/<hashid:id>', methods=['DELETE'])
def borrar_por_hashid(id):
    facultad = FacultadService.eliminar_facultad(id)
    return jsonify("Facultad borrada exitosamente"), 200 

def sanitizar_facultad_entrada(facultad):
    facultad.nombre = escape(facultad.nombre)
    facultad.sigla = escape(facultad.sigla) 
    return facultad 
    facultad.nombre = escape(facultad.nombre)
    facultad.sigla = escape(facultad.sigla)
    facultad.codigoPostal = escape(facultad.codigoPostal)
    facultad.abreviatura = escape(facultad.abreviatura)
    facultad.directorio = escape(facultad.directorio)
    facultad.ciudad = escape(facultad.ciudad)
    facultad.domicilio = escape(facultad.domicilio)
    facultad.telefono = escape(facultad.telefono)
    facultad.contacto = escape(facultad.contacto)
    facultad.email = escape(facultad.email)
    return facultad







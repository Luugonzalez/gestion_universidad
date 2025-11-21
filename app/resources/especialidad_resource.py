from flask import jsonify, Blueprint, request
from app.mapping.especialidad_mapping import EspecialidadMapping            
from app.services.especilidad_service import EspecialidadService
from markupsafe import escape
import json
import logging

especialidad_bp = Blueprint('especialidad', __name__)
especialidad_mapping = EspecialidadMapping()    

@especialidad_bp.route('/especialidad', methods=['GET'])
def listar_especialidades():
    page: int = request.headers.get('X-page', 1, type=int)
    per_page: int = request.headers.get('X-per-page', 10, type=int) 
    filters_str : str|None = request.headers.get('X-filters', None, type=str) 
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters_str))
    if filters_str:
        filters = json.loads(filters_str)
        especialidades = EspecialidadService.listar_especialidades(page=page, per_page=per_page, filters=filters)
    else:
        especialidades = EspecialidadService.listar_especialidades(page=page, per_page=per_page)
    return especialidad_mapping.dump(especialidades, many=True), 200

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['GET'])
def buscar_por_hashid(id):
    especialidad = EspecialidadService.buscar_especialidad(id)
    return especialidad_mapping.dump(especialidad), 200 

@especialidad_bp.route('/especialidad', methods=['POST'])
def crear():
    especialidad = especialidad_mapping.load(request.get_json())
    EspecialidadService.crear_especialidad(especialidad)
    return jsonify("Especialidad creada exitosamente"), 201

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['PUT'])
def actualizar(id):
    especialidad = especialidad_mapping.load(request.get_json())
    EspecialidadService.actualizar_especialidad(especialidad, id)
    return jsonify("Especialidad actualizada exitosamente"), 200        

@especialidad_bp.route('/especialidad/<hashid:id>', methods=['DELETE'])
def borrar_por_hashid(id):
    EspecialidadService.eliminar_especialidad(id)
    return jsonify("Especialidad borrada exitosamente"), 200    

def sanitizar_especialidad_entrada(request):
    especialidad = especialidad_mapping.load(request.get_json())
    especialidad.nombre = escape(especialidad.nombre)
    especialidad.letra = escape(especialidad.letra)
    especialidad.observacion = escape(especialidad.observacion)
    return especialidad 



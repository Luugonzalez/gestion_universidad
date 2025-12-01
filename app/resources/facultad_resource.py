from flask import jsonify, Blueprint, request 
from app.mapping.facultad_mapping import FacultadMapping
from app.services.facultad_service import FacultadService
from markupsafe import escape
from app.validators import validate_with
import json
import logging

facultad_bp = Blueprint('facultad', __name__)
service: FacultadService = FacultadService()
facultad_mapping = FacultadMapping()

@facultad_bp.get("/facultad/<hashid:id>/especialidad")
def get_especialidad(id):
    try:
        data = service.obtener_especialidad_por_id(id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@facultad_bp.route('/facultad/<hashid:id>', methods=['GET']) #Funciona
def buscar_por_hashid(id):
    facultad = FacultadService.buscar_facultad(id)
    return facultad_mapping.dump(facultad), 200

@facultad_bp.route('/facultad', methods=['GET'])
def listar_facultades():
    page: int = request.headers.get('X-page', 1, type=int)
    per_page: int = request.headers.get('X-per-page', 10, type=int) 
    filters_str : str|None = request.headers.get('X-filters', None, type=str) 
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters_str))
    if filters_str:
        filters = json.loads(filters_str)
        facultades = FacultadService.listar_facultades(page=page, per_page=per_page, filters=filters)
    else:
        facultades = FacultadService.listar_facultades(page=page, per_page=per_page)
    return facultad_mapping.dump(facultades, many=True), 200

@facultad_bp.route('/facultad', methods=['POST']) 
@validate_with(FacultadMapping)
def crear(facultad):
    facultad = facultad_mapping.load(request.get_json())
    FacultadService.crear_facultad(facultad)
    return jsonify("Facultad creada exitosamente"), 201 

@facultad_bp.route('/facultad/<hashid:id>', methods=['PUT']) 
@validate_with(FacultadMapping)
def actualizar(id):
    facultad = facultad_mapping.load(request.get_json()) 
    FacultadService.actualizar_facultad( facultad, id)
    return jsonify("Facultad actualizada exitosamente"), 200 

@facultad_bp.route('/facultad/<hashid:id>', methods=['DELETE'])
def borrar_por_hashid(id):
    facultad = FacultadService.eliminar_Facultad(id)
    return jsonify("Facultad borrada exitosamente"), 200 


def sanitizar_facultad_entrada(request):
  facultad= facultad_mapping.load(request.get_json())
  facultad.nombre = escape(facultad.nombre)
  facultad.sigla = escape(facultad.sigla)
  facultad.codigoPostal = escape(facultad.codigoPostal)
  facultad.abreviatura= escape(facultad.abreviatura)
  facultad.directorio= escape(facultad.directorio)
  facultad.ciudad= escape(facultad.ciudad)
  facultad.domicilio= escape(facultad.domicilio)
  facultad.telefono= escape(facultad.telefono)
  facultad.contacto= escape(facultad.contacto)
  facultad.email= escape(facultad.email)

  return facultad







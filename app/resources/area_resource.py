from flask import jsonify, Blueprint, request
from app.mapping.area_mapping import AreaMapping
from app.services.area_service import AreaService
from markupsafe import escape
from app.validators import validate_with

area_bp = Blueprint('area', __name__)

area_mapping = AreaMapping()

@area_bp.route('/area/<hashid:id>', methods=['GET'])
def buscar_por_id(id):
    area = AreaService.buscar_area_por_id(id)
    return area_mapping.dump(area), 200

@area_bp.route('/area', methods=['GET'])
def listar_areas():
    areas = AreaService.listar_area()
    return area_mapping.dump(areas, many=True), 200

@area_bp.route('/area', methods=['POST'])
@validate_with(AreaMapping)
def crear(area):
    AreaService.crear_area(area)
    return jsonify("Area creada exitosamente"), 201

@area_bp.route('/area/<hashid:id>', methods=['PUT'])
@validate_with(AreaMapping)
def actualizar(area, id):
    AreaService.actualizar_area(id, area)
    return jsonify("Area actualizada exitosamente"), 200

@area_bp.route('/area/<hashid:id>', methods=['DELETE'])
def borrar_por_id(id):
    AreaService.borrar_por_id(id)
    return jsonify("Area borrada exitosamente"), 200

def sanitizar_area_entrada(request):
    area = area_mapping.load(request.get_json())
    area.nombre = escape(area.nombre)
    return area

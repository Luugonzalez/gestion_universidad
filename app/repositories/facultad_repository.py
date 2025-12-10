from app.models import Facultad
from app import db
from sqlalchemy_filters import apply_filters
from typing import Optional
import logging
from app import redis_client
import json

class FacultadRepository:

  @staticmethod
  def crear_facultad(facultad: Facultad):
    db.session.add(facultad)
    db.session.commit()
    return facultad
  
  @staticmethod
  def listar_facultades(page: int, per_page: int, filters: Optional[list] = None) -> list[Facultad]:
    query = db.session.query(Facultad)
    if filters and isinstance(filters, list):
        query = apply_filters(query, filters)
    paginated_query = query.offset((page - 1) * per_page).limit(per_page)
    return paginated_query.all()
  
  @staticmethod
  def buscar_facultad(id: int) -> Facultad:
      key = f"facultad:{id}"

      logging.info(f"[CACHE] Buscando clave en Redis: {key}")

      if redis_client is not None:
          cached = redis_client.get(key)
          if cached:
              data = json.loads(cached)
              logging.info(f"[CACHE HIT] Facultad {id} encontrada en Redis.")
              return Facultad(**data)

      logging.info(f"[CACHE MISS] No se encontró la facultad {id} en Redis. Consultando DB...")

      facultad = db.session.query(Facultad).filter(Facultad.id == id).one_or_none()
      if not facultad:
          return None
       
      if redis_client is not None:
          data = {
              "id": facultad.id,
              "nombre": facultad.nombre,
              "abreviatura": facultad.abreviatura,
              "directorio": facultad.directorio,
              "sigla": facultad.sigla,
              "codigoPostal": facultad.codigoPostal,
              "ciudad": facultad.ciudad,
              "domicilio": facultad.domicilio,
              "telefono": facultad.telefono,
              "contacto": facultad.contacto,
              "email": facultad.email
          }
          redis_client.set(key, json.dumps(data)) 
      return facultad
    
  @staticmethod
  def actualizar_facultad(facultad: Facultad, id: int) -> Facultad:
    entity = FacultadRepository.buscar_facultad(id)
    entity.nombre = facultad.nombre
    entity.abreviatura = facultad.abreviatura
    entity.directorio = facultad.directorio
    entity.sigla = facultad.sigla
    entity.codigoPostal = facultad.codigoPostal
    entity.ciudad = facultad.ciudad
    entity.domicilio = facultad.domicilio
    entity.telefono = facultad.telefono
    entity.contacto = facultad.contacto
    entity.email = facultad.email
    db.session.commit()
    return entity
  
  @staticmethod
  def eliminar_facultad(id: int) -> None:
    entity = FacultadRepository.buscar_facultad(id)
    db.session.delete(entity)
    db.session.commit()

  @staticmethod
  def contar_facultades(filters: Optional[list] = None) -> int:
    query = db.session.query(db.func.count(Facultad.id))
    
    if filters and isinstance(filters, list):
        query = apply_filters(query, filters)
    return query.scalar() or 0
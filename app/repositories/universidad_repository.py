from app.models import Universidad
from app import db
from sqlalchemy_filters import apply_filters
import logging
from typing import Optional, List

class UniversidadRepository:

  @staticmethod
  def crear_universidad(universidad: Universidad) -> Universidad:
    db.session.add(universidad)
    db.session.commit()
    return universidad
  
  @staticmethod
  def listar_universidades(page: int, per_page: int, filters: Optional[list] = None) -> list[Universidad]:
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
    
    # 1. Asegurar la ordenación. Siempre es buena práctica ordenar para la paginación.
    query = db.session.query(Universidad).order_by(Universidad.id)
    
    if filters and isinstance(filters, list):
        # Aquí la lista de filtros debe venir formateada correctamente desde el Controlador
        query = apply_filters(query, filters)
        
    paginated_query = query.offset((page - 1) * per_page).limit(per_page)
    return paginated_query.all()

  # 2. FUNCIÓN DE CONTEO AÑADIDA
  @staticmethod
  def contar_universidades(filters: Optional[List] = None) -> int:
      """
      Cuenta el número total de universidades, aplicando los filtros, si existen.
      Esta función es CRUCIAL para calcular el total de páginas en el Servicio.
      """
      # Iniciar la consulta de conteo
      query = db.session.query(db.func.count(Universidad.id))
      
      # Aplicar filtros al conteo (usa el mismo formato de filtro que listar_universidades)
      if filters and isinstance(filters, list):
          query = apply_filters(query, filters)
          
      # Ejecutar la consulta de conteo y devolver el resultado
      return query.scalar() or 0

  
  
  
  @staticmethod
  def listar_universidades(page: int, per_page: int, filters: Optional[list] = None) -> list[Universidad]:
    logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))
    query = db.session.query(Universidad)
    if filters and isinstance(filters, list):
        query = apply_filters(query, filters)
    paginated_query = query.offset((page - 1) * per_page).limit(per_page)
    return paginated_query.all()
  
  @staticmethod
  def buscar_universidad(id: int) -> Universidad:
    return Universidad.query.get(id)
  
  @staticmethod
  def actualizar_universidad(universidad: Universidad, id: int) -> Universidad:
    entity = UniversidadRepository.buscar_universidad(id)
    entity.nombre = universidad.nombre
    entity.sigla = universidad.sigla
    entity.tipo = universidad.tipo
    db.session.commit()
    return entity
  
  @staticmethod
  def eliminar_universidad(id: int) -> None:
    entity = UniversidadRepository.buscar_universidad(id)
    db.session.delete(entity)
    db.session.commit()
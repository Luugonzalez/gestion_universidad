from app.models import Especialidad
from app import db
from sqlalchemy_filters import apply_filters
import logging
from typing import Optional, List

class EspecialidadRepository:
    @staticmethod
    def listar_especialidades(page: int, per_page: int, filters: Optional[list] = None) -> list[Especialidad]:
        logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))

        query = db.session.query(Especialidad).order_by(Especialidad.id)
    
        if filters and isinstance(filters, list):
            query = apply_filters(query, filters)
    
        paginated_query = query.offset((page - 1) * per_page).limit(per_page)
        return paginated_query.all()
    
    @staticmethod
    def contar_especialidades(filters: Optional[List] = None) -> int:
        query = db.session.query(db.func.count(Especialidad.id))
        
        if filters and isinstance(filters, list):
            query = apply_filters(query, filters)
        return query.scalar() or 0

    @staticmethod
    def crear_especialidad(especialidad: Especialidad) -> Especialidad:
        db.session.add(especialidad)
        db.session.commit()
        return especialidad 

    @staticmethod
    def buscar_especialidad(id: int) -> Especialidad:
        return db.session.query(Especialidad).filter(Especialidad.id == id).one_or_none()

    @staticmethod
    def actualizar_especialidad(especialidad: Especialidad, id: int) -> Especialidad| None:
        entity = EspecialidadRepository.buscar_especialidad(id)
        if not entity:
            return None  
        entity.nombre = especialidad.nombre
        entity.letra = especialidad.letra
        entity.observacion = especialidad.observacion
        db.session.commit()
        return entity

    @staticmethod
    def eliminar_especialidad(id: int) -> None:
        entity = EspecialidadRepository.buscar_especialidad(id)
        if entity:
            db.session.delete(entity)
            db.session.commit()

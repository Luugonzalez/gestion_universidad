from app.models import Especialidad
from app import db, redis_client
from sqlalchemy_filters import apply_filters
import logging
import json

CACHE_TTL = 60 #seg
CACHE_PREFIX = "especialidad:"


class EspecialidadRepository:

    @staticmethod
    def listar_especialidades(page: int, per_page: int, filters: list = None) -> list:
        logging.info("page: {}, per_page: {}, filters: {}".format(page, per_page, filters))

        query = db.session.query(Especialidad).order_by(Especialidad.id)

        if filters and isinstance(filters, list):
            query = apply_filters(query, filters)

        return query.offset((page - 1) * per_page).limit(per_page).all()

    @staticmethod
    def contar_especialidades(filters: list = None) -> int:
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
        key = f"especialidad:{id}"

        # 1. Buscar en cache
        if redis_client is not None:
            cached = redis_client.get(key)
            if cached:
                data = json.loads(cached)
                # reconstruir modelo
                return Especialidad(**data)

        # 2. Buscar en DB
        especialidad = db.session.query(Especialidad).filter_by(id=id).one_or_none()
        if not especialidad:
            return None
        if redis_client is not None:
            data = {
                "id": especialidad.id,
                "nombre": especialidad.nombre,
                "letra": especialidad.letra,
                "observacion": especialidad.observacion,
                "facultad_id": especialidad.facultad_id
            }
            redis_client.set(key, json.dumps(data))
        return especialidad


    @staticmethod
    def actualizar_especialidad(especialidad: Especialidad, id: int):
        """
        Actualiza sobre la entidad persistente (DB) y luego invalida cache.
        """
        entity = db.session.query(Especialidad).filter(Especialidad.id == id).one_or_none()
        if not entity:
            return None

        entity.nombre = especialidad.nombre
        entity.letra = especialidad.letra
        entity.observacion = especialidad.observacion

        db.session.commit()

        # invalidar cache
        if redis_client:
            try:
                redis_client.delete(f"{CACHE_PREFIX}{id}")
            except Exception as e:
                logging.warning(f"Error invalidando cache: {e}")

        return entity

    @staticmethod
    def eliminar_especialidad(id: int):
        entity = db.session.query(Especialidad).filter(Especialidad.id == id).one_or_none()
        if not entity:
            return

        db.session.delete(entity)
        db.session.commit()

        # invalidar cache
        if redis_client:
            try:
                redis_client.delete(f"{CACHE_PREFIX}{id}")
            except Exception as e:
                logging.warning(f"Error invalidando cache: {e}")

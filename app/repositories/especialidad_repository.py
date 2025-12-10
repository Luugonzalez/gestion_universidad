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
    def buscar_especialidad(id: int):
        """
        Siempre retorna:
         - un objeto Especialidad (ORM) si existe
         - None si no existe
        Maneja correctamente la ausencia de redis_client (tests).
        """
        key = f"{CACHE_PREFIX}{id}"

        # 1) Intentar desde cache solo si existe redis_client
        if redis_client:
            try:
                cached = redis_client.get(key)
                if cached:
                    data = json.loads(cached)

                    # Reconstruir objeto Especialidad (desacoplado de la session)
                    obj = Especialidad()
                    obj.id = data.get("id")
                    obj.nombre = data.get("nombre")
                    obj.letra = data.get("letra")
                    obj.observacion = data.get("observacion")
                    obj.facultad_id = data.get("facultad_id")

                    logging.info(f"Especialidad {id} obtenida desde cache")
                    return obj
            except Exception as e:
                logging.warning(f"Error leyendo Redis: {e}")

        # 2) Si no está en caché, ir a la DB
        entity = db.session.query(Especialidad).filter(Especialidad.id == id).one_or_none()
        if not entity:
            return None

        # 3) Guardar en caché (si hay redis)
        if redis_client:
            try:
                data = {
                    "id": entity.id,
                    "nombre": entity.nombre,
                    "letra": entity.letra,
                    "observacion": entity.observacion,
                    "facultad_id": entity.facultad_id,
                }
                redis_client.set(key, json.dumps(data), ex=CACHE_TTL)
            except Exception as e:
                logging.warning(f"Error guardando en Redis: {e}")

        return entity

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

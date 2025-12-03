import os
import unittest
from unittest.mock import patch, MagicMock

from app import db, create_app
from app.services.facultad_service import FacultadService
from app.models import Facultad


# ---------- FACTORY PARA CREAR FACULTADES VÁLIDAS ----------
def crear_facultad_valida(
    nombre="Facultad X",
    abreviatura="ABR",
    directorio="Dir X",
    sigla="SIG",
    codigoPostal="0000",
    ciudad="Ciudad",
    domicilio="Calle Falsa 123",
    telefono="123456",
    contacto="Juan Perez",
    email="facultad@uni.edu",
    universidad_id=None,
):
    return Facultad(
        nombre=nombre,
        abreviatura=abreviatura,
        directorio=directorio,
        sigla=sigla,
        codigoPostal=codigoPostal,
        ciudad=ciudad,
        domicilio=domicilio,
        telefono=telefono,
        contacto=contacto,
        email=email,
        universidad_id=universidad_id,
    )


class TestFacultadService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["FLASK_CONTEXT"] = "testing"

        cls.app = create_app()

        cls.app.config["CACHE_TYPE"] = "NullCache"
        cls.app.config["CACHE_NO_NULL_WARNING"] = True

        from app import cache
        cache.init_app(cls.app)

        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    # --------- TEST CREAR ---------
    def test_crear_facultad(self):
        fac = crear_facultad_valida(nombre="Ingeniería", sigla="ING")

        creado = FacultadService.crear_facultad(fac)

        self.assertIsNotNone(creado.id)
        self.assertEqual(creado.nombre, "Ingeniería")

    # --------- TEST OBTENER ESPECIALIDAD (MOCKS) ---------
    @patch("app.services.facultad_service.requests.get")
    def test_obtener_especialidad_ok(self, mock_get):
        service = FacultadService()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "nombre": "Ingeniería"}

        mock_get.return_value = mock_response

        data = service.obtener_especialidad(1)

        self.assertEqual(data["id"], 1)
        self.assertEqual(data["nombre"], "Ingeniería")
        mock_get.assert_called_once()

    @patch("app.services.facultad_service.requests.get")
    def test_obtener_especialidad_retry_success(self, mock_get):

        mock_fail = MagicMock()
        mock_fail.status_code = 500

        mock_ok = MagicMock()
        mock_ok.status_code = 200
        mock_ok.json.return_value = {"id": 2, "nombre": "Química"}

        mock_get.side_effect = [mock_fail, mock_ok]

        service = FacultadService()
        data = service.obtener_especialidad(2)

        self.assertEqual(data["id"], 2)
        self.assertEqual(data["nombre"], "Química")
        self.assertEqual(mock_get.call_count, 2)

    @patch("app.services.facultad_service.requests.get")
    def test_obtener_especialidad_retry_fail(self, mock_get):

        mock_fail = MagicMock()
        mock_fail.status_code = 500

        mock_get.side_effect = [mock_fail, mock_fail, mock_fail]

        service = FacultadService()

        with self.assertRaises(Exception):
            service.obtener_especialidad(99)

        self.assertEqual(mock_get.call_count, 3)

    # --------- TEST PAGINACIÓN + FILTROS ---------
    def test_listar_facultades_paginacion_filtrado(self):

        facultades = [
            crear_facultad_valida(nombre="Ingeniería", sigla="ING"),
            crear_facultad_valida(nombre="Medicina", sigla="MED"),
            crear_facultad_valida(nombre="Económicas", sigla="ECO"),
            crear_facultad_valida(nombre="Derecho", sigla="DER"),
        ]

        db.session.add_all(facultades)
        db.session.commit()

        filters = [{"field": "sigla", "op": "==", "value": "ECO"}]

        result = FacultadService.listar_facultades(
            page=1,
            per_page=2,
            filters=filters
        )

        content = result["content"]

        self.assertEqual(result["total_elements"], 1)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0].nombre, "Económicas")

    # --------- TEST ACTUALIZAR ---------
    def test_actualizar_facultad(self):

        fac = crear_facultad_valida(nombre="Arquitectura", sigla="ARQ")
        db.session.add(fac)
        db.session.commit()

        fac_edit = crear_facultad_valida(nombre="Arquitectura y Diseño", sigla="ADIS")

        updated = FacultadService.actualizar_facultad(fac_edit, fac.id)

        self.assertEqual(updated.nombre, "Arquitectura y Diseño")
        self.assertEqual(updated.sigla, "ADIS")

    # --------- TEST ELIMINAR ---------
    def test_eliminar_facultad(self):

        fac = crear_facultad_valida(nombre="Odontología", sigla="ODO")
        db.session.add(fac)
        db.session.commit()

        FacultadService.eliminar_facultad(fac.id)

        eliminado = Facultad.query.get(fac.id)
        self.assertIsNone(eliminado)


if __name__ == "__main__":
    unittest.main()

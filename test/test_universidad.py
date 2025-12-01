import unittest
from flask import current_app
from app import create_app, db
from app.models import Universidad, Facultad
from app.services import UniversidadService, FacultadService
import os
import json


class UniversidadTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # -----------------------------------------------------------------------
    # Utilidades
    # -----------------------------------------------------------------------

    def __crear_universidad(self, nombre=None, sigla=None, tipo=None):
        u = Universidad()
        u.nombre = nombre or "Universidad Tecnologica Nacional"
        u.sigla = sigla or "UTN"
        u.tipo = tipo or "publica"
        return u

    def __crear_universidades(self, count=1, tipos=None):
        universidades = []
        for i in range(count):
            u = Universidad(
                nombre=f"Universidad {i+1}",
                sigla=f"U{i+1}",
                tipo=(tipos[i] if tipos and i < len(tipos) else ("publica" if i % 2 == 0 else "privada"))
            )
            UniversidadService.crear_universidad(u)
            universidades.append(u)
        return universidades

    # -----------------------------------------------------------------------
    # Tests básicos del contexto
    # -----------------------------------------------------------------------

    def test_app(self):
        self.assertIsNotNone(current_app)

    def test_model_universidad(self):
        universidad = self.__crear_universidad()
        self.assertEqual(universidad.nombre, "Universidad Tecnologica Nacional")
        self.assertEqual(universidad.sigla, "UTN")
        self.assertEqual(universidad.tipo, "publica")

    # -----------------------------------------------------------------------
    # Tests de servicio
    # -----------------------------------------------------------------------

    def test_crear_universidad(self):
        universidad = self.__crear_universidad()
        guardada = UniversidadService.crear_universidad(universidad)

        self.assertIsNotNone(guardada.id)
        self.assertEqual(guardada.nombre, universidad.nombre)
        self.assertEqual(guardada.sigla, universidad.sigla)
        self.assertEqual(guardada.tipo, universidad.tipo)

    def test_listar_universidades(self):
        UniversidadService.crear_universidad(self.__crear_universidad())

        result = UniversidadService.listar_universidades()
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertGreaterEqual(len(result["content"]), 1)

    def test_buscar_universidad(self):
        universidad = self.__crear_universidad()
        guardada = UniversidadService.crear_universidad(universidad)

        encontrada = UniversidadService.buscar_universidad(guardada.id)

        self.assertIsNotNone(encontrada)
        self.assertEqual(encontrada.nombre, universidad.nombre)
        self.assertEqual(encontrada.sigla, universidad.sigla)
        self.assertEqual(encontrada.tipo, universidad.tipo)

    def test_actualizar_universidad(self):
        universidad = self.__crear_universidad()
        UniversidadService.crear_universidad(universidad)

        nuevos = Universidad(
            nombre="UTN Modificada",
            sigla="UTN-M",
            tipo="privada"
        )

        modificada = UniversidadService.actualizar_universidad(nuevos, universidad.id)
        encontrada = UniversidadService.buscar_universidad(universidad.id)

        self.assertEqual(encontrada.nombre, "UTN Modificada")
        self.assertEqual(encontrada.sigla, "UTN-M")
        self.assertEqual(encontrada.tipo, "privada")

    def test_eliminar_universidad(self):
        universidad = self.__crear_universidad()
        UniversidadService.crear_universidad(universidad)

        UniversidadService.eliminar_universidad(universidad.id)
        encontrada = UniversidadService.buscar_universidad(universidad.id)

        self.assertIsNone(encontrada)

    # -----------------------------------------------------------------------
    # Relación: Universidad con Facultades
    # -----------------------------------------------------------------------

    def test_universidad_con_facultades(self):
        universidad = self.__crear_universidad()
        UniversidadService.crear_universidad(universidad)

        facultad = Facultad(
            nombre='Facultad Regional Mendoza',
            abreviatura='FRM',
            directorio='dir',
            sigla='FRM',
            codigoPostal='5500',
            ciudad='Mendoza',
            domicilio='Calle Falsa 123',
            telefono='12345678',
            contacto='Juan Pérez',
            email='contacto@frm.utn.edu.ar',
            universidad_id=universidad.id
        )

        FacultadService.crear_facultad(facultad)

        encontrada = UniversidadService.buscar_universidad(universidad.id)

        self.assertEqual(len(encontrada.facultades), 1)
        self.assertEqual(encontrada.facultades[0].nombre, "Facultad Regional Mendoza")

    # -----------------------------------------------------------------------
    # Tests de ENDPOINTS
    # -----------------------------------------------------------------------

    def test_post_universidad_datos_validos(self):
        payload = {
            "nombre": "Universidad de Prueba",
            "sigla": "UDP",
            "tipo": "publica"
        }

        resp = self.client.post(
            "/api/v1/universidad",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, 201)

        # Verificar que la respuesta sea un JSON válido
        self.assertIn("creada", resp.get_data(as_text=True).lower())

    def test_post_universidad_datos_invalidos(self):
        payload = {"nombre": "Universidad Incompleta"}  # Falta sigla y tipo

        resp = self.client.post(
            "/api/v1/universidad",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()

        self.assertIn("sigla", data)
        self.assertIn("tipo", data)

    def test_listar_universidades_endpoint_paginacion(self):
        self.__crear_universidades(12)

        resp = self.client.get(
            "/api/v1/universidad",
            headers={"X-page": "2", "X-per-page": "5"}
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(len(data["content"]), 5)
        self.assertEqual(data["pageable"]["page"], 2) # nro de página
        self.assertEqual(data["pageable"]["size"], 5) # tamaño de página (en elementos)
        self.assertEqual(data["pageable"]["total_elements"], 12) # cant. total de elementos
        self.assertEqual(data["pageable"]["total_pages"], 3) # cant. total de páginas

    def test_listar_universidades_endpoint_filters(self):
        tipos = ["privada"] * 3 + ["publica"] * 2
        self.__crear_universidades(5, tipos=tipos)

        resp = self.client.get(
            "/api/v1/universidad",
            headers={"X-filters": json.dumps({"tipo": "privada"})}
        )

        self.assertEqual(resp.status_code, 200)

        data = resp.get_json()
        tipos_resultantes = [u["tipo"].lower() for u in data["content"]]

        self.assertTrue(all(t == "privada" for t in tipos_resultantes))


if __name__ == '__main__':
    unittest.main()

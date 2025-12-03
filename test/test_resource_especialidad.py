import unittest
import os
from app import db
from flask import current_app
from app import create_app
from app.models.facultad import Facultad
from app.models.especialidad import Especialidad
from app.mapping.especialidad_mapping import EspecialidadMapping
from hashids import Hashids
import json

class EspecialidadResourceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()

        # Desactivar cache en testing
        self.app.config["CACHE_TYPE"] = "NullCache"
        self.app.config["CACHE_NO_NULL_WARNING"] = True

        from app import cache
        cache.init_app(self.app)

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        salt = self.app.config.get('HASHIDS_SALT', 'especialidades')
        min_length = self.app.config.get('HASHIDS_MIN_LENGTH', 10)
        self.hashids = Hashids(min_length=min_length, salt=salt)

        self.facultad = Facultad(
            nombre="Ingeniería",
            abreviatura="ING",
            directorio="Directorio X",
            sigla="ING",
            codigoPostal="5000",
            ciudad="Córdoba",
            domicilio="Av Siempre Viva",
            telefono="123456",
            contacto="contacto@ing.com",
            email="ing@uni.com"
        )
        db.session.add(self.facultad)
        db.session.commit()

        self.esp1 = Especialidad(
            nombre="Especialidad A",
            letra="A",
            observacion="Observacion A",
            facultad_id=self.facultad.id
        )
        self.esp2 = Especialidad(
            nombre="Especialidad B",
            letra="B",
            observacion="Observacion B",
            facultad_id=self.facultad.id
        )

        db.session.add_all([self.esp1, self.esp2])
        db.session.commit()

        self.esp1_hash = self.hashids.encode(self.esp1.id)
        self.esp2_hash = self.hashids.encode(self.esp2.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_obtener_todos(self):
        response = self.client.get('/api/v1/especialidad')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("content", data)
        self.assertGreaterEqual(len(data["content"]), 2)

    def test_buscar_por_hashid(self):
        response = self.client.get(f'/api/v1/especialidad/{self.esp1_hash}')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["letra"], "A")

    def test_post_especialidad(self):
        payload = {
            "nombre": "Especialidad C",
            "letra": "C",
            "observacion": "Nueva Especialidad",
            "facultad_id": self.facultad.id
        }

        response = self.client.post('/api/v1/especialidad', json=payload)
        self.assertEqual(response.status_code, 201)

        especiales = Especialidad.query.all()
        self.assertEqual(len(especiales), 3)

    def test_actualizar_especialidad(self):
        payload = {
            "nombre": "Especialidad A1",
            "letra": "A1",
            "observacion": "Modificada",
            "facultad_id": self.facultad.id
        }

        response = self.client.put(
            f'/api/v1/especialidad/{self.esp1_hash}',
            json=payload
        )
        self.assertEqual(response.status_code, 200)

        refreshed = Especialidad.query.get(self.esp1.id)
        self.assertEqual(refreshed.letra, "A1")

    def test_borrar_especialidad(self):
        response = self.client.delete(f'/api/v1/especialidad/{self.esp2_hash}')
        self.assertEqual(response.status_code, 200)

        deleted = Especialidad.query.get(self.esp2.id)
        self.assertIsNone(deleted)

    def test_listar_con_filtros(self):
        headers = {
            "X-filters": json.dumps({"letra": "A"})
        }

        response = self.client.get('/api/v1/especialidad', headers=headers)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        content = data["content"]

        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["letra"], "A")

if __name__ == '__main__':
    unittest.main()

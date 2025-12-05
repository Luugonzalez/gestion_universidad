import unittest
import os
from app import db
from flask import current_app
from app import create_app
from app.models.universidad import Universidad
from app.mapping.universidad_mapping import UniversidadMapping
from hashids import Hashids
import json

class UniversidadResourceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()

        # DESACTIVAR CACHE EN TESTING
        self.app.config["CACHE_TYPE"] = "NullCache"
        self.app.config["CACHE_NO_NULL_WARNING"] = True
        
        # volver a inicializar cache con la config actual
        from app import cache
        cache.init_app(self.app)

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        salt = self.app.config.get('HASHIDS_SALT', 'universidades')
        min_length = self.app.config.get('HASHIDS_MIN_LENGTH', 10)
        self.hashids = Hashids(min_length=min_length, salt=salt)

        self.uni1 = Universidad(nombre="UTN", sigla="UTN", tipo="Publica")
        self.uni2 = Universidad(nombre="UBA", sigla="UBA", tipo="Publica")
        db.session.add_all([self.uni1, self.uni2])
        db.session.commit()

        self.uni1_hash = self.hashids.encode(self.uni1.id)
        self.uni2_hash = self.hashids.encode(self.uni2.id)


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_obtener_todos(self):
        response = self.client.get('/api/v1/universidad')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("content", data)
        self.assertIsInstance(data["content"], list)
        self.assertGreaterEqual(len(data["content"]), 2)

    def test_buscar_por_hashid(self):
        response = self.client.get(f'/api/v1/universidad/{self.uni1_hash}')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["nombre"], "UTN")

    def test_crear_universidad(self):
        payload = {
            "nombre": "UNC",
            "sigla": "UNC",
            "tipo": "Publica"
        }

        response = self.client.post('/api/v1/universidad',
                                    json=payload)
        self.assertEqual(response.status_code, 201)

        unis = Universidad.query.all()
        self.assertEqual(len(unis), 3)

    def test_actualizar_universidad(self):
        payload = {
            "nombre": "UTN Actualizada",
            "sigla": "UTN",
            "tipo": "Publica"
        }

        response = self.client.put(f'/api/v1/universidad/{self.uni1_hash}',
                                   json=payload)
        self.assertEqual(response.status_code, 200)

        refreshed = Universidad.query.get(self.uni1.id)
        self.assertEqual(refreshed.nombre, "UTN Actualizada")

    def test_borrar_universidad(self):
        response = self.client.delete(f'/api/v1/universidad/{self.uni2_hash}')
        self.assertEqual(response.status_code, 200)

        deleted = Universidad.query.get(self.uni2.id)
        self.assertIsNone(deleted)

    def test_listar_con_filtros(self):
        headers = {
            "X-filters": json.dumps({"nombre": "UTN"})
        }

        response = self.client.get('/api/v1/universidad', headers=headers)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        content = data["content"]

        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["nombre"], "UTN")

if __name__ == '__main__':
    unittest.main()
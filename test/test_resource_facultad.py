import unittest
import os
import json
from hashids import Hashids
from app import db, create_app
from app.models import Facultad, Universidad

class FacultadResourceTestCase(unittest.TestCase):

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

        salt = self.app.config.get('HASHIDS_SALT', 'facultades')
        min_length = self.app.config.get('HASHIDS_MIN_LENGTH', 10)
        self.hashids = Hashids(min_length=min_length, salt=salt)

        # Crear universidad primero
        self.universidad = Universidad(nombre="Universidad Test", sigla="UT", tipo="Nacional")
        db.session.add(self.universidad)
        db.session.commit()

        # Crear facultades
        self.fac1 = Facultad(
            nombre="Facultad de Ingeniería",
            sigla="FI",
            abreviatura="FI",
            directorio="Dir 1",
            codigoPostal="5000",
            ciudad="Córdoba",
            domicilio="Av. Vélez Sársfield 1611",
            telefono="351-5353700",
            contacto="contacto@fi.edu.ar",
            email="info@fi.edu.ar",
            universidad_id=self.universidad.id
        )
        self.fac2 = Facultad(
            nombre="Facultad de Ciencias",
            sigla="FC",
            abreviatura="FC",
            directorio="Dir 2",
            codigoPostal="5000",
            ciudad="Córdoba",
            domicilio="Av. Medina Allende",
            telefono="351-5353800",
            contacto="contacto@fc.edu.ar",
            email="info@fc.edu.ar",
            universidad_id=self.universidad.id
        )
        db.session.add_all([self.fac1, self.fac2])
        db.session.commit()

        self.fac1_hash = self.hashids.encode(self.fac1.id)
        self.fac2_hash = self.hashids.encode(self.fac2.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_obtener_todos(self):
        response = self.client.get('/api/v1/facultad')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("content", data)
        self.assertIsInstance(data["content"], list)
        self.assertGreaterEqual(len(data["content"]), 2)

    def test_buscar_por_hashid(self):
        response = self.client.get(f'/api/v1/facultad/{self.fac1_hash}')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["nombre"], "Facultad de Ingeniería")

    def test_crear_facultad(self):
        payload = {
            "nombre": "Facultad de Derecho",
            "sigla": "FD",
            "abreviatura": "FD",
            "directorio": "Dir Test",
            "codigoPostal": "5000",
            "ciudad": "Córdoba",
            "domicilio": "Calle Test 123",
            "telefono": "351-1234567",
            "contacto": "contacto@fd.edu.ar",
            "email": "info@fd.edu.ar",
            "universidad_id": self.universidad.id
        }

        response = self.client.post('/api/v1/facultad', json=payload)
        self.assertEqual(response.status_code, 201)

        facultades = Facultad.query.all()
        self.assertEqual(len(facultades), 3)

    def test_actualizar_facultad(self):
        payload = {
            "nombre": "Facultad de Ingeniería Actualizada",
            "sigla": "FI",
            "abreviatura": "FI",
            "directorio": "Dir Actualizado",
            "codigoPostal": "5000",
            "ciudad": "Córdoba",
            "domicilio": "Av. Vélez Sársfield 1611",
            "telefono": "351-5353700",
            "contacto": "contacto@fi.edu.ar",
            "email": "info@fi.edu.ar",
            "universidad_id": self.universidad.id
        }

        response = self.client.put(f'/api/v1/facultad/{self.fac1_hash}', json=payload)
        self.assertEqual(response.status_code, 200)

        refreshed = Facultad.query.get(self.fac1.id)
        self.assertEqual(refreshed.nombre, "Facultad de Ingeniería Actualizada")

    def test_borrar_facultad(self):
        response = self.client.delete(f'/api/v1/facultad/{self.fac2_hash}')
        self.assertEqual(response.status_code, 200)

        deleted = Facultad.query.get(self.fac2.id)
        self.assertIsNone(deleted)

    def test_listar_con_filtros(self):
        headers = {
            "X-filters": json.dumps({"nombre": "Facultad de Ingeniería"})
        }

        response = self.client.get('/api/v1/facultad', headers=headers)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        content = data["content"]

        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["nombre"], "Facultad de Ingeniería")

if __name__ == '__main__':
    unittest.main()


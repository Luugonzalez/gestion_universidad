import unittest
import os
import json
from hashids import Hashids
from unittest.mock import patch
from app import db, create_app
from app.models import Especialidad, Facultad, Universidad
from app.services import FacultadService, UniversidadService, EspecialidadService
from app.resources import especialidad_bp

class EspecialidadResourceTestCase(unittest.TestCase):
    
    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        self.client = self.app.test_client()
        self.facultad = self._crear_facultad()  # Facultad reusable para todos los tests

        self.hashids = Hashids(
            salt=os.getenv('HASHIDS_SALT', 'Sistemas de gestion academica'),
            min_length=int(os.getenv('HASHIDS_MIN_LENGTH', 16)),
            alphabet=os.getenv('HASHIDS_ALPHABET', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _crear_universidad(self, nombre="UTN", sigla="UTN", tipo="publica"):
        u = Universidad(nombre=nombre, sigla=sigla, tipo=tipo)
        return UniversidadService.crear_universidad(u)

    def _crear_facultad(self, nombre='Facultad de Prueba', abreviatura='FP'):
        uni = self._crear_universidad()
        f = Facultad(
            nombre=nombre,
            abreviatura=abreviatura,
            directorio='directorio',
            sigla=abreviatura,
            codigoPostal='1234',
            ciudad='Ciudad',
            domicilio='Domicilio',
            telefono='0000',
            contacto='Contacto',
            email='email@prueba.com',
            universidad_id=uni.id
        )
        return FacultadService.crear_facultad(f)

    def _crear_especialidades(self, count=1, nombres=None):
        especialidades = []
        for i in range(count):
            nombre = nombres[i] if nombres and i < len(nombres) else f'Especialidad {i}'
            e = Especialidad(
                nombre=nombre,
                letra=f"L{i}",
                observacion=f"Observación {i}",
                facultad_id=self.facultad.id
            )
            EspecialidadService.crear_especialidad(e)
            especialidades.append(e)
        return especialidades

    def test_get_especialidades(self):
        response = self.client.get('/api/v1/especialidad')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("content", data)
        self.assertIsInstance(data["content"], list)
        self.assertEqual(len(data["content"]), 0)

    def test_post_especialidad(self):
        payload = {
            "nombre": "Ingenieria civil",
            "letra": "C",
            "observacion": "Clase normal",
            "facultad_id": self.facultad.id
        }
        resp = self.client.post("/api/v1/especialidad",
                                data=json.dumps(payload),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("creada", resp.get_data(as_text=True).lower())

    def test_post_especialidad_invalida(self):
        payload = {"nombre": "Sin letra ni facultad"}
        resp = self.client.post("/api/v1/especialidad",
                                data=json.dumps(payload),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("letra", data)
        self.assertIn("facultad_id", data)

    def test_listar_especialidades_paginacion(self):
        self._crear_especialidades(12)
        resp = self.client.get("/api/v1/especialidad",
                               headers={"X-page": "2", "X-per-page": "5"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data["content"]), 5)
        self.assertEqual(data["pageable"]["page"], 2)
        self.assertEqual(data["pageable"]["size"], 5)
        self.assertEqual(data["pageable"]["total_elements"], 12)
        self.assertEqual(data["pageable"]["total_pages"], 3)

    def test_listar_especialidades_filters(self):
        nombres = ["Ingenieria civil", "Ingenieria Electro", "Ingenieria Sist", "Fisica", "Ingenieria ind"]
        self._crear_especialidades(5, nombres=nombres)
        resp = self.client.get("/api/v1/especialidad",
                               headers={"X-filters": json.dumps({"nombre": "Fisica"})})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        nombres_resultantes = [e["nombre"] for e in data["content"]]
        self.assertTrue(all("Yoga" in n for n in nombres_resultantes))

    def test_put_especialidad(self):
        especialidad = self._crear_especialidades(1)[0]
        hashid_id = self.hashids.encode(especialidad.id)  
        
        payload = {
            "nombre": "Ingenieria civil modificada",
            "letra": "CM",
            "observacion": "Clase avanzada",
            "facultad_id": self.facultad.id
        }

        resp = self.client.put(f"/api/v1/especialidad/{hashid_id}",
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("actualizada", resp.get_data(as_text=True).lower())

    def test_delete_especialidad(self):
        especialidad = self._crear_especialidades(1)[0]
        hashid_id = self.hashids.encode(especialidad.id)  # usar .id

        resp = self.client.delete(f"/api/v1/especialidad/{hashid_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("borrada", resp.get_data(as_text=True).lower())

        # Verificar que realmente no exista
        get_resp = self.client.get(f"/api/v1/especialidad/{hashid_id}")
        self.assertEqual(get_resp.status_code, 404)

if __name__ == '__main__':
    unittest.main()

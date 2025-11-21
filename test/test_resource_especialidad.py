import unittest
import os
import json
from app import db, create_app
from app.models.especialidad import Especialidad
from app.models.facultad import Facultad
from app.models.universidad import Universidad


class EspecialidadResourceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Crear universidad de prueba
        self.universidad = Universidad(nombre='Universidad Test')
        db.session.add(self.universidad)
        db.session.commit()
        
        # Crear facultad de prueba
        self.facultad = Facultad(
            nombre='Facultad de Ingeniería',
            abreviatura='FI',
            directorio='fi',
            sigla='FI',
            codigoPostal='28001',
            ciudad='Madrid',
            domicilio='Calle Test 123',
            telefono='123456789',
            contacto='contacto@fi.edu',
            email='fi@universidad.edu',
            universidad_id=self.universidad.id
        )
        db.session.add(self.facultad)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_listar_especialidades_vacio(self):
        """Test GET /especialidad cuando no hay especialidades"""
        response = self.client.get('/api/v1/especialidad')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_crear_especialidad(self):
        """Test POST /especialidad para crear una nueva especialidad"""
        especialidad_data = {
            'nombre': 'Ingeniería Civil',
            'letra': 'IC',
            'observacion': 'Especialidad en construcción',
            'facultad_id': self.facultad.id
        }
        response = self.client.post(
            '/api/v1/especialidad',
            data=json.dumps(especialidad_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_listar_especialidades_con_datos(self):
        """Test GET /especialidad cuando hay especialidades"""
        # Crear algunas especialidades
        especialidad1 = Especialidad(
            nombre='Ingeniería Civil',
            letra='IC',
            observacion='Construcción',
            facultad_id=self.facultad.id
        )
        especialidad2 = Especialidad(
            nombre='Ingeniería Informática',
            letra='II',
            observacion='Sistemas',
            facultad_id=self.facultad.id
        )
        db.session.add(especialidad1)
        db.session.add(especialidad2)
        db.session.commit()
        
        response = self.client.get('/api/v1/especialidad')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_buscar_especialidad_por_id(self):
        """Test GET /especialidad/<id> para obtener una especialidad específica"""
        especialidad = Especialidad(
            nombre='Ingeniería Mecánica',
            letra='IM',
            observacion='Mecánica industrial',
            facultad_id=self.facultad.id
        )
        db.session.add(especialidad)
        db.session.commit()
        
        response = self.client.get(f'/api/v1/especialidad/{especialidad.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['nombre'], 'Ingeniería Mecánica')

    def test_actualizar_especialidad(self):
        """Test PUT /especialidad/<id> para actualizar una especialidad"""
        especialidad = Especialidad(
            nombre='Ingeniería Eléctrica',
            letra='IE',
            observacion='Electricidad',
            facultad_id=self.facultad.id
        )
        db.session.add(especialidad)
        db.session.commit()
        
        actualizada_data = {
            'nombre': 'Ingeniería Eléctrica Actualizada',
            'letra': 'IEA',
            'observacion': 'Electricidad avanzada',
            'facultad_id': self.facultad.id
        }
        response = self.client.put(
            f'/api/v1/especialidad/{especialidad.id}',
            data=json.dumps(actualizada_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_eliminar_especialidad(self):
        """Test DELETE /especialidad/<id> para eliminar una especialidad"""
        especialidad = Especialidad(
            nombre='Ingeniería de Sistemas',
            letra='IS',
            observacion='Sistemas computacionales',
            facultad_id=self.facultad.id
        )
        db.session.add(especialidad)
        db.session.commit()
        especialidad_id = especialidad.id
        
        response = self.client.delete(f'/api/v1/especialidad/{especialidad_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que fue eliminada
        eliminada = Especialidad.query.get(especialidad_id)
        self.assertIsNone(eliminada)


if __name__ == '__main__':
    unittest.main()

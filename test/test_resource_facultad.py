import unittest
import os
import json
from app import db, create_app
from app.models.facultad import Facultad
from app.models.universidad import Universidad


class FacultadResourceTestCase(unittest.TestCase):

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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_listar_facultades_vacio(self):
        """Test GET /facultad cuando no hay facultades"""
        response = self.client.get('/api/v1/facultad')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_crear_facultad(self):
        """Test POST /facultad para crear una nueva facultad"""
        facultad_data = {
            'nombre': 'Facultad de Ciencias',
            'abreviatura': 'FC',
            'directorio': 'ciencias',
            'sigla': 'FC',
            'codigoPostal': '28040',
            'ciudad': 'Madrid',
            'domicilio': 'Avenida Complutense',
            'telefono': '987654321',
            'contacto': 'contacto@ciencias.edu',
            'email': 'ciencias@universidad.edu',
            'universidad_id': self.universidad.id
        }
        response = self.client.post(
            '/api/v1/facultad',
            data=json.dumps(facultad_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    def test_listar_facultades_con_datos(self):
        """Test GET /facultad cuando hay facultades"""
        # Crear algunas facultades
        facultad1 = Facultad(
            nombre='Facultad de Ingeniería',
            abreviatura='FI',
            directorio='ingenieria',
            sigla='FI',
            codigoPostal='28001',
            ciudad='Madrid',
            domicilio='Calle Test 123',
            telefono='123456789',
            contacto='contacto@fi.edu',
            email='fi@universidad.edu',
            universidad_id=self.universidad.id
        )
        facultad2 = Facultad(
            nombre='Facultad de Medicina',
            abreviatura='FM',
            directorio='medicina',
            sigla='FM',
            codigoPostal='28002',
            ciudad='Madrid',
            domicilio='Calle Medicina 456',
            telefono='987654321',
            contacto='contacto@medicina.edu',
            email='medicina@universidad.edu',
            universidad_id=self.universidad.id
        )
        db.session.add(facultad1)
        db.session.add(facultad2)
        db.session.commit()
        
        response = self.client.get('/api/v1/facultad')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_buscar_facultad_por_id(self):
        """Test GET /facultad/<id> para obtener una facultad específica"""
        facultad = Facultad(
            nombre='Facultad de Derecho',
            abreviatura='FD',
            directorio='derecho',
            sigla='FD',
            codigoPostal='28003',
            ciudad='Madrid',
            domicilio='Calle Derecho 789',
            telefono='555555555',
            contacto='contacto@derecho.edu',
            email='derecho@universidad.edu',
            universidad_id=self.universidad.id
        )
        db.session.add(facultad)
        db.session.commit()
        
        response = self.client.get(f'/api/v1/facultad/{facultad.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['nombre'], 'Facultad de Derecho')

    def test_actualizar_facultad(self):
        """Test PUT /facultad/<id> para actualizar una facultad"""
        facultad = Facultad(
            nombre='Facultad de Educación',
            abreviatura='FE',
            directorio='educacion',
            sigla='FE',
            codigoPostal='28004',
            ciudad='Madrid',
            domicilio='Calle Educación 111',
            telefono='444444444',
            contacto='contacto@educacion.edu',
            email='educacion@universidad.edu',
            universidad_id=self.universidad.id
        )
        db.session.add(facultad)
        db.session.commit()
        
        actualizada_data = {
            'nombre': 'Facultad de Educación Actualizada',
            'abreviatura': 'FEA',
            'directorio': 'educacion_act',
            'sigla': 'FEA',
            'codigoPostal': '28005',
            'ciudad': 'Madrid',
            'domicilio': 'Calle Educación 222',
            'telefono': '333333333',
            'contacto': 'contacto2@educacion.edu',
            'email': 'educacion2@universidad.edu',
            'universidad_id': self.universidad.id
        }
        response = self.client.put(
            f'/api/v1/facultad/{facultad.id}',
            data=json.dumps(actualizada_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_eliminar_facultad(self):
        """Test DELETE /facultad/<id> para eliminar una facultad"""
        facultad = Facultad(
            nombre='Facultad de Artes',
            abreviatura='FA',
            directorio='artes',
            sigla='FA',
            codigoPostal='28006',
            ciudad='Madrid',
            domicilio='Calle Artes 333',
            telefono='222222222',
            contacto='contacto@artes.edu',
            email='artes@universidad.edu',
            universidad_id=self.universidad.id
        )
        db.session.add(facultad)
        db.session.commit()
        facultad_id = facultad.id
        
        response = self.client.delete(f'/api/v1/facultad/{facultad_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que fue eliminada
        eliminada = Facultad.query.get(facultad_id)
        self.assertIsNone(eliminada)


if __name__ == '__main__':
    unittest.main()

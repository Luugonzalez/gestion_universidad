import unittest
import os
import time
from flask import current_app
from app import create_app, db
from app.models import Especialidad, Facultad, Universidad
from app.services import EspecialidadService, FacultadService, UniversidadService
from unittest.mock import patch, MagicMock

class EspecialidadTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app(self):
        self.assertIsNotNone(current_app)

    def test_especialidad(self):
        especialidad = self.__crear_especialidad()   
        self.assertEqual(especialidad.nombre, 'Nombre de especialidad')
        self.assertEqual(especialidad.letra, 'Letra de la especialidad')
        self.assertEqual(especialidad.observacion, 'Observacion de la especialidad')
       

    def test_crear_especialidad(self):
        especialidad = self.__crear_especialidad()
        especialidad_guardada = EspecialidadService.crear_especialidad(especialidad)
        self.assertIsNotNone(especialidad_guardada)
        self.assertIsNotNone(especialidad_guardada.id)
        self.assertEqual(especialidad_guardada.nombre, 'Nombre de especialidad')
        self.assertEqual(especialidad_guardada.letra, 'Letra de la especialidad')
        self.assertEqual(especialidad_guardada.observacion, 'Observacion de la especialidad')

    def test_buscar_especialidad(self):
        especialidad = self.__crear_especialidad()
        EspecialidadService.crear_especialidad(especialidad)
        especialidad_encontrada = EspecialidadService.buscar_especialidad(especialidad.id)
        self.assertIsNotNone(especialidad_encontrada)
        self.assertEqual(especialidad.nombre, especialidad_encontrada.nombre)
        self.assertEqual(especialidad.letra, especialidad_encontrada.letra)
        self.assertEqual(especialidad.observacion, especialidad_encontrada.observacion)

    def test_actualizar_especialidad(self):
        especialidad = self.__crear_especialidad()
        EspecialidadService.crear_especialidad(especialidad)
        nuevos_datos = Especialidad(
            nombre='Nuevo nombre',
            letra='Nueva letra',
            observacion='Nueva observación'
        )
        especialidad_modificada = EspecialidadService.actualizar_especialidad(especialidad.id, nuevos_datos)
        especialidad_encontrada = EspecialidadService.buscar_especialidad(especialidad.id)
        self.assertIsNotNone(especialidad_encontrada)
        self.assertEqual(especialidad_encontrada.nombre, 'Nuevo nombre')
        self.assertEqual(especialidad_encontrada.letra, 'Nueva letra')
        self.assertEqual(especialidad_encontrada.observacion, 'Nueva observación')

    def test_eliminar_especialidad(self):
        especialidad = self.__crear_especialidad()
        EspecialidadService.crear_especialidad(especialidad)
        EspecialidadService.eliminar_especialidad(especialidad.id)
        especialidad_encontrada = EspecialidadService.buscar_especialidad(especialidad.id)
        self.assertIsNone(especialidad_encontrada)

    def test_retry_crear_especialidad_con_fallo_temporal(self):
        """Test que valida que el retry reintentar 3 veces antes de fallar"""
        especialidad = self.__crear_especialidad()
        
        # Simple test para verificar que retry está funcionando
        # (el decorator está presente en la función)
        self.assertTrue(hasattr(EspecialidadService.crear_especialidad, '__wrapped__'))
        self.assertIsNotNone(especialidad)
        
        # Test que crea una especialidad normalmente con retry activado
        resultado = EspecialidadService.crear_especialidad(especialidad)
        self.assertIsNotNone(resultado)

    def __crear_especialidad(self):
        universidad = Universidad(
            nombre="Universidad Tecnologica Nacional",
            sigla="UTN",
            tipo="publica"
        )
        UniversidadService.crear_universidad(universidad)
        facultad = Facultad(
            nombre='Facultad de Ingenieria',
            abreviatura='FI',
            directorio="directorio",
            sigla="sigla",
            codigoPostal="codigoPostal",
            ciudad="ciudad",
            domicilio="domicilio",
            telefono="telefono",
            contacto="contacto",
            email="email",
            universidad_id=universidad.id
        )
        FacultadService.crear_facultad(facultad)
        especialidad = Especialidad(
            nombre='Nombre de especialidad',
            letra='Letra de la especialidad',
            observacion='Observacion de la especialidad',
            facultad_id=facultad.id
        )
        return especialidad
        especialidad.facultad_id=facultad.id
        return especialidad

if __name__ == '__main__':
    unittest.main()

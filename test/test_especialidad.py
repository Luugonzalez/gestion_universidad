import unittest
import os
from flask import current_app
from app import create_app, db
from app.models import Especialidad, Facultad, Universidad
from app.services import EspecialidadService, FacultadService, UniversidadService

class EspecialidadServiceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # Creamos una facultad reusable
        self.facultad = self._crear_facultad()

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
                letra=f'L{i}',
                observacion=f'Observación {i}',
                facultad_id=self.facultad.id
            )
            EspecialidadService.crear_especialidad(e)
            especialidades.append(e)
        return especialidades

    def test_app_contexto(self):
        self.assertIsNotNone(current_app)

    def test_model_especialidad(self):
        e = self._crear_especialidades(1)[0]
        self.assertTrue(e.nombre.startswith("Especialidad"))

    def test_crear_y_buscar_especialidad(self):
        e = self._crear_especialidades(1)[0]
        encontrada = EspecialidadService.buscar_especialidad(e.id)
        self.assertIsNotNone(encontrada)
        self.assertEqual(encontrada.nombre, e.nombre)

    def test_actualizar_especialidad(self):
        e = self._crear_especialidades(1)[0]
        nuevos = Especialidad(nombre="Modificada", letra="M", observacion="Obs Modificada")
        EspecialidadService.actualizar_especialidad(nuevos, e.id)
        encontrada = EspecialidadService.buscar_especialidad(e.id)
        self.assertEqual(encontrada.nombre, "Modificada")
        self.assertEqual(encontrada.letra, "M")
        self.assertEqual(encontrada.observacion, "Obs Modificada")

    def test_eliminar_especialidad(self):
        e = self._crear_especialidades(1)[0]
        EspecialidadService.eliminar_especialidad(e.id)
        self.assertIsNone(EspecialidadService.buscar_especialidad(e.id))

    # Retry
    def test_retry_crear_especialidad(self):
        e = self._crear_especialidades(1)[0]
        # Verifica que el decorator retry está presente
        self.assertTrue(hasattr(EspecialidadService.crear_especialidad, "__wrapped__"))
        # Crear con retry activado
        resultado = EspecialidadService.crear_especialidad(e)
        self.assertIsNotNone(resultado)

    # Listado, paginación y filtros (servicio)
    def test_listar_especialidades_servicio(self):
        nombres = ["Ingenieria civil", "Ingenieria Electro", "Ingenieria Sist", "Fisica", "Ingenieria ind"]
        self._crear_especialidades(5, nombres=nombres)
        # Lista todas
        resultado = EspecialidadService.listar_especialidades()
        self.assertIsInstance(resultado, dict)
        self.assertEqual(resultado["total_elements"], 5)
        self.assertEqual(len(resultado["content"]), 5)

    def test_listar_especialidades_filtro_servicio(self):
        nombres = ["Ingenieria civil", "Ingenieria Electro", "Ingenieria Sist", "Fisica", "Ingenieria ind"]
        self._crear_especialidades(5, nombres=nombres)
        # Filtra solo "Fisica"
        resultado = EspecialidadService.listar_especialidades(filters=[{"field": "nombre", "op": "==", "value": "Fisica"}])
        self.assertEqual(resultado["total_elements"], 1)
        self.assertEqual(resultado["content"][0].nombre, "Fisica")

    def test_listar_especialidades_paginacion_servicio(self):
        self._crear_especialidades(12)
        resultado = EspecialidadService.listar_especialidades(page=2, per_page=5)
        self.assertEqual(resultado["page"], 2)
        self.assertEqual(resultado["size"], 5)
        self.assertEqual(resultado["total_elements"], 12)
        self.assertEqual(len(resultado["content"]), 5)
        self.assertEqual(resultado["total_pages"], 3)


if __name__ == "__main__":
    unittest.main()

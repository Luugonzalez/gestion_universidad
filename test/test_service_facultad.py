import unittest
from unittest.mock import patch, MagicMock
from app.services.facultad_service import FacultadService
from app.models import Facultad


class TestFacultadService(unittest.TestCase):

    @patch("app.services.facultad_service.requests.get")
    def test_obtener_especialidad_ok(self, mock_get):
       service = FacultadService()

       mock_response = MagicMock()
       mock_response.status_code = 200
       mock_response.json.return_value = {"id": 1, "nombre": "Ingeniería"}

       mock_get.return_value = mock_response

       data = service.obtener_especialidad(1)

       assert data["id"] == 1
       assert data["nombre"] == "Ingeniería"
       mock_get.assert_called_once()




    @patch("app.services.facultad_service.requests.get")
    def test_obtener_especialidad_retry_success(self, mock_get):
        """Debe reintentar si falla y luego funciona"""

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
        """Debe lanzar excepción luego de 3 intentos fallidos"""

        mock_fail = MagicMock()
        mock_fail.status_code = 500
        mock_get.side_effect = [mock_fail, mock_fail, mock_fail]

        service = FacultadService()

        with self.assertRaises(Exception):
            service.obtener_especialidad(99)

        self.assertEqual(mock_get.call_count, 3)


   

    @patch("app.services.facultad_service.FacultadRepository.crear_facultad")
    def test_crear_facultad(self, mock_repo):
        facultad = Facultad(id=1, nombre="Ing. Sistemas")
        result = FacultadService.crear_facultad(facultad)

        mock_repo.assert_called_once_with(facultad)
        self.assertIs(result, facultad)


    @patch("app.services.facultad_service.FacultadRepository.listar_facultades")
    def test_listar_facultades(self, mock_repo):
        mock_repo.return_value = [{"id": 1, "nombre": "Económicas"}]

        result = FacultadService.listar_facultades(page=1, per_page=10, filters=None)

        mock_repo.assert_called_once_with(1, 10, None)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["nombre"], "Económicas")


    @patch("app.services.facultad_service.FacultadRepository.buscar_facultad")
    def test_buscar_facultad(self, mock_repo):
        mock_repo.return_value = {"id": 3, "nombre": "Derecho"}

        result = FacultadService.buscar_facultad(3)

        mock_repo.assert_called_once_with(3)
        self.assertEqual(result["id"], 3)


    @patch("app.services.facultad_service.FacultadRepository.actualizar_facultad")
    def test_actualizar_facultad(self, mock_repo):
        facultad = Facultad(id=5, nombre="Arquitectura")

        result = FacultadService.actualizar_facultad(facultad, 5)

        mock_repo.assert_called_once_with(facultad, 5)
        self.assertIs(result, facultad)


    @patch("app.services.facultad_service.FacultadRepository.eliminar_facultad")
    def test_eliminar_facultad(self, mock_repo):
        mock_repo.return_value = True

        result = FacultadService.eliminar_facultad(7)

        mock_repo.assert_called_once_with(7)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

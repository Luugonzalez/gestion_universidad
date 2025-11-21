import unittest
import os
from app import db
from flask import current_app
from app import create_app
from app.mapping.facultad_mapping import FacultadMapping

class FacultadResourceTestCase(unittest.TestCase):

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

    def test_obtener_todos(self):
        """Probar GET /api/v1/facultad"""
        response = self.client.get('/api/v1/facultad')
        self.assertEqual(response.status_code, 200)

        facultades = response.get_json()

        self.assertIsNotNone(facultades)
        self.assertIsInstance(facultades, list)


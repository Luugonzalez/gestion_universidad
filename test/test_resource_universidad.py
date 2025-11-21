import unittest
import os
from app import db
from flask import current_app
from app import create_app
from app.mapping.universidad_mapping import UniversidadMapping

class UniversidadResourceTestCase(unittest.TestCase):

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
        response = self.client.get('/api/v1/universidad')
        self.assertEqual(response.status_code, 200)
        universidades = response.get_json()
        self.assertIsNotNone(universidades)
        self.assertIsInstance(universidades, list)
        
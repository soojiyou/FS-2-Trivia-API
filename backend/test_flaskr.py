import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://postgres:abc".format(
        #     'localhost:5432', self.database_name)
        self.database_path = 'postgresql://postgres:abc@localhost:5432/trivia'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            self.test_question_1 = {
                'question': 'how many states in United States?',
                'answer': '50',
                'category': 3,
                'difficulty': 1,

            }
            self.test_question_2 = {}

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_question(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])

    def test_delete_question(self):
        response = self.client().delete('/questions/222')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_post_new_question(self):
        response1 = self.client().post('/questions', json=self.test_question_1)
        data1 = json.loads(response1.data)
        self.assertEqual(response1.status_code, 200)

        response2 = self.client().post('/questions', json=self.test_question_2)
        data2 = json.loads(response2.data)
        self.assertEqual(response2.status_code, 400)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

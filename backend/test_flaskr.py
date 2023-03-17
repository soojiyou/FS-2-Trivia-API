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
            self.test_search_term_1 = {'searchTerm': 'movie'}
            self.test_search_term_2 = {}
            self.test_get_quiz_1 = {
                'previous_questions': [],
                'quiz_category': {'id': '1', 'type': 'Science'}
            }
            self.test_get_quiz_2 = {
                'previous_questions': [],
            }

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

    def test_error_get_all_categories(self):
        response = self.client().get('/categories/222')
        self.assertEqual(response.status_code, 404)

    def test_get_question(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_error_get_question(self):
        response = self.client().get('/questions=2')
        self.assertEqual(response.status_code, 404)

    def test_delete_question(self):
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['deleted'], question_id)

    def test_error_delete_question(self):
        response = self.client().delete('/questions/222')
        self.assertEqual(response.status_code, 404)

    def test_post_new_question(self):
        '''test with valid input'''
        response1 = self.client().post('/questions', json=self.test_question_1)
        data1 = json.loads(response1.data)
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(data1['question'])

    def test_error_post_new_question(self):
        '''test with invalid input'''
        response2 = self.client().post('/questions', json=self.test_question_2)
        self.assertEqual(response2.status_code, 400)

    def test_search_question(self):
        '''test with valid input'''
        response1 = self.client().post('/questions/search', json=self.test_search_term_1)
        data = json.loads(response1.data)
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_error_search_question(self):
        '''test with invalid input'''
        response2 = self.client().post('/questions/search', json=self.test_search_term_2)
        self.assertEqual(response2.status_code, 400)

    def test_question_by_category(self):
        '''test with category_id =1 = > expects 200'''
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], 1)
        self.assertTrue(data['total_questions'])

    def test_error_question_by_category(self):
        '''test with category_id =0 = > expects 404'''
        response = self.client().get('/categories/0/questions')
        self.assertEqual(response.status_code, 404)

    def test_get_questions_for_quiz(self):
        response1 = self.client().post('/quiz', json=self.test_get_quiz_1)
        data = json.loads(response1.data)
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(data['question'])

    def test_error_get_questions_for_quiz(self):
        response1 = self.client().post('/quiz', json=self.test_get_quiz_2)
        self.assertEqual(response1.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

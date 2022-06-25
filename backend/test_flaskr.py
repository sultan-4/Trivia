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
        self.database_path = "postgresql://postgres:local@localhost:5432/Trivia"
        setup_db(self.app, self.database_path)

        self.new_question = {"question":"question","answer":"answer","difficulty":1,"category":1}
        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_catogries(self):
        res = self.client().get("/categories")
        data =json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

        
    def test_get_questions_page(self):
        res = self.client().get("/questions?=page=1")
        data =json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["totalQuestions"])



    def test_get_non_exixsting_page(self):
        res = self.client().get("/questions?page=50000")
        data =json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_delete_questions(self):
        res = self.client().delete("/questions/22")
        data =json.loads(res.data)
        question = Question.query.filter(Question.id == 22).one_or_none()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 22)
        self.assertEqual(question,None)


    def test_delete_non_existing_question(self):
            res = self.client().delete("/questions/1000")
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 422)
            self.assertEqual(data["success"], False)
            self.assertEqual(data["message"], "unprocessable")

    def test_create_new_question(self):
        res = self.client().post("/questions" , json = self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
    
    def test_create_new_question_not_allowed(self):
        res = self.client().post("/questions/50" , json = self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
        
    def test_search_for_question(self):
        res = self.client().post("/questions/search" , json = {"searchTerm":"Tom"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])


    def test_search_for_non_existing_question(self):
        res = self.client().post("/questions/search",json = {"searchTerm":"*"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_for_question_in_categories(self):
        res = self.client().get("/categories/1/questions")
        data =json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_for_question_in_non_existing_categories(self):
        res = self.client().get("/categories/992208/questions")
        data =json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    

    def test_for_quizzes(self):
        res = self.client().post("/quizzes" , json = {"quiz_category":{"type":"Science", "id":"1"}, "previous_questions":[20]} )
        data =json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_for_quizzes_with_wrong_category(self):
        res = self.client().post("/quizzes" , json = {"quiz_category":{"type":"", "id":"70"}, "previous_questions":[20]} )
        data =json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
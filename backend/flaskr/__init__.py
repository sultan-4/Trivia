import os
import re
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy import true

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    
    # @TODO: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods','GET, POST, DELETE')
        return response
    

    """
    endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def all_categories():
        category = Category.query.all()
        categories = {cate.id : cate.type for cate in category}
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success':True,
            'categories':categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions',methods=["GET"])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        category = Category.query.all()
        current_questions=paginate_questions(request,questions)
        categories = {cate.id : cate.type for cate in category}
        if len(current_questions)==0:
            abort(404)

        return jsonify({
            'success':True,
            'questions':paginate_questions(request,questions),
            'totalQuestions': len(Question.query.all()),
            'categories':categories,
            'currentCategory':None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_book(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                    abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "deleted": question_id,
                "questions": current_questions,
            })
        except:
                abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        new_question= body['question']
        new_answer = body['answer']
        new_difficulty = body['difficulty']
        new_category = body['category']
        try:
            question = Question(question=new_question,answer=new_answer,difficulty=new_difficulty,category=new_category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_question= paginate_questions(request,selection)
            return jsonify({
                'success':True,
                'created':question.id,
                'questions':current_question,
                'total_questions':len(Question.query.all())
            })
        except:
            abort(422)
    """ 
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_question():
        try:
            body = request.get_json()
            search_term= body['searchTerm']
            questions = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
            result= paginate_questions(request,questions)
            if (len(questions)) == 0:
                abort(404)
            return jsonify({
                'success':True,
                'questions':result,
                'totalQuestions':len(questions),
                'currentCategory':None
            })
        except:
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def specific_category(category_id):
        try:
            questions = Question.query.filter(Question.category == category_id ).all()
            if (len(questions)==0):
                abort(404)

            current_questions = paginate_questions(request , questions)
            current_category = Category.query.filter(Category.id == category_id).one_or_none()
            return jsonify({
                'success':True,
                'questions':current_questions,
                'totalQuestions':len(questions),
                'currentCategory':current_category.type
            })
        except:
            abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_quiz():
        
        try:
                body = request.get_json()
                previous_questions = body['previous_questions']
                quiz_category = body['quiz_category']
                new_question = []
                #check for pressed category
                if(quiz_category['type'] == 'click'):
                    questions = Question.query.all()
                else:
                    questions = Question.query.filter(Question.category == quiz_category['id']).all()
                
                
                if len(questions)==0:
                    abort(404)
                
                #check if questin in previous_questions
                for question in questions:
                    if question.id not in previous_questions:
                        new_question.append(question.format())
                        
                #if there is no question 
                if (len(new_question) == 0):
                    return jsonify({
                        'success':True,
                        'question':None
                    })

                return jsonify({
                            'success':True,
                            'question':new_question[random.randrange(0,len(new_question))]
                })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':404,
            'message':'resource not found'
        }),404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':422,
            'message':'unprocessable'
        }),422
    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':400,
            'message':'bad request'
        }),400   

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':405,
            'message':'method not allowed'
        }),405

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':500,
            'message':'internal server error'
        }),500
    return app

    


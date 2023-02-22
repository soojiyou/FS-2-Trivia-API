import os
from flask import Flask, request, abort, jsonify, abort, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_question(request, all_questions):

    page = int(request.args.get("page", 1))
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in all_questions]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # CORS(app)
    CORS(app, resources={r'/*': {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/')
    def home():
        return redirect('/categories', code=302)

    @app.route('/categories', methods=['GET'])
    def get_all_categories():
        categories = {}
        # categories = Category.query.order_by(Category.type).all()
        for category in Category.query.all():
            categories[category.id] = category.type
        return jsonify({
            'categories': categories
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
    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories = {}
        all_questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.type).all()
        paged_questions = paginate_question(request, all_questions)
        if len(paged_questions) == 0:
            abort(404)

        return jsonify({
            "questions": paged_questions,
            "total_questions": len(all_questions),
            "categories": {category.id: category.type for category in categories},
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if not question:
            return abort(404, f'No question found => question id: {question_id}')
        question.delete()
        return jsonify({
            'deleted': question_id
        })

# https://github.com/skb1129/trivia-api/blob/master/backend/flaskr/__init__.py
# https://github.com/NehaDuvvasi/trivia/blob/main/backend/flaskr/__init__.py
# https://github.com/BenMini/TriviaAPI/blob/master/backend/flaskr/__init__.py
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def post_new_question():

        new_question = request.json.get('question')
        new_answer = request.json.get('answer')
        new_category = request.json.get('category')
        new_difficulty = request.json.get('difficulty')

        if not (new_question and new_answer and new_category and new_difficulty):
            abort(400, 'missing required question objects from request')

        post_question = Question(question=new_question, answer=new_answer,
                                 category=new_category, difficulty=new_difficulty)
        post_question.insert()

        return jsonify({
            'question': post_question.format()
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        search_term = request.json.get('searchTerm', None)
        if not search_term:
            abort(400)

        search_questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")).all()

        paged_questions = paginate_question(request, search_questions)

        return jsonify({
            'questions': paged_questions,
            'total_questions': len(search_questions),
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_by_category(category_id):
        categorized_questions = Question.query.filter(
            Question.category == str(category_id)).all()

        paged_questions = paginate_question(request, categorized_questions)
        if len(paged_questions) == 0:
            abort(404)
        return jsonify({
            'questions': paged_questions,
            'categories': [category.type for category in Category.query.all()],
            'current_category': category_id,
            'total_questions': len(categorized_questions),
        })

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
    @app.route('/quiz', methods=['POST'])
    def get_questions_for_quiz():
        prev_questions = request.json.get('previous_questions', None)
        quiz_category = request.json.get('quiz_category', None)
        category_id = quiz_category['id']

        if not quiz_category:
            return abort(400)
        questions = Question.query.filter_by(category=category_id).filter(
            Question.id.notin_(prev_questions)).all()

        question = questions.filter(Question.id.notin_(prev_questions)).first()
        if not question:
            return jsonify({})
        return jsonify({
            'question': question.format()
        })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False,
                        "error": 404,
                        "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
                     "error": 422,
                     "message": "unprocessable"}), 422
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False,
                        "error": 400,
                        "message": "bad request"}), 400

    @app.errorhandler(500)
    def bad_resquest(error):
        return jsonify({"success": False,
                        "error": 500,
                        "message": "Internal server error"}), 500

    return app

import os
from datetime import timedelta

from flask import Flask, Response, jsonify, request
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

from auth import Auth
from custom_error import CustomError
from db import DB

load_dotenv()

app = Flask(__name__)
AUTH = Auth()
dbs = DB()
app.SECRET_KEY = os.getenv('SECRET_KEY')

SESSION_DURATION = timedelta(hours=3)


@app.errorhandler(CustomError)
def handle_custom_error(error):
    response = jsonify({
        "message": str(error)
    })
    response.status_code = error.status_code
    return response


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify({
        "message": error.description
    })
    response.status_code = error.code
    return response


@app.route('/', methods=['GET'], strict_slashes=False)
def status() -> Response:
    """ GET /home """
    return jsonify({"message": "Welcome"})


@app.route('/register', methods=['POST'], strict_slashes=False)
def new_user() -> tuple[Response, int]:
    """ POST /register """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    gender = data.get("gender")

    try:
        if not all([email, password, first_name, last_name, phone_number, gender]):
            return jsonify({
                "message": "All field required.(email, password, first_name, last_name, phone_number, gender)"
            }), 400

        create_new_user = AUTH.register_user(email, password, first_name, last_name, phone_number, gender)
        return jsonify({
            "email": create_new_user.email,
            "message": "User created successfully. Please check your email for verification."
        }), 201
    except ValueError as e:
        raise CustomError(str(e), 400)


@app.route('/verify_email', methods=['POST'], strict_slashes=False)
def verify_email() -> tuple[Response, int]:
    """ POST /verify_email """
    data = request.get_json()
    email = data.get("email")
    verification_code = data.get("verification_code")

    try:
        if not all([email, verification_code]):
            return jsonify({
                "message": "All field required.(email, verification_code)"
            }), 400

        AUTH.verify_user_email(email, verification_code)
        return jsonify({
            "message": "Email verified successfully. You can now log in."
        }), 200

    except ValueError as e:
        raise CustomError(str(e), 403)


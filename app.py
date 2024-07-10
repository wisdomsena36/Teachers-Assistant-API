import os
from datetime import timedelta, datetime

from flask import Flask, Response, jsonify, request, abort, redirect
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


@app.route('/login', methods=['POST'], strict_slashes=False)
def login() -> Response:
    """ POST /login """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        valid_user = AUTH.valid_login(email, password)

        if not valid_user:
            abort(401, description="Invalid credentials")

        session_id = AUTH.create_session(email)
        message = {"email": email, "message": "Logged in successfully"}
        response = jsonify(message)
        response.set_cookie("session_id", session_id)
        return response

    except ValueError as e:
        raise CustomError(str(e), 403)


@app.route('/logout', methods=['DELETE'], strict_slashes=False)
def logout():
    """ DELETE /logout """
    user_cookie = request.cookies.get("session_id", None)
    user = AUTH.get_user_from_session_id(user_cookie)
    if user_cookie is None or user is None:
        abort(403, description="Session not found or user not authenticated")
    AUTH.destroy_session(user.id)
    return redirect('/')


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile() -> Response:
    """ GET /profile """
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        abort(403, description="Session not found")
    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        abort(403, description="User not authenticated")
    if datetime.utcnow() - user.last_login > SESSION_DURATION:
        AUTH.destroy_session(user.id)
        abort(403, description="Session expired")
    return jsonify({
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "gender": user.gender
    })


@app.route('/profile', methods=['PUT'], strict_slashes=False)
def update_profile() -> tuple[Response, int]:
    """ PUT /profile """
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        abort(403, description="Session not found")
    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        abort(403, description="User not authenticated")

    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    gender = data.get("gender")

    try:
        if not all([first_name, last_name, phone_number, gender]):
            return jsonify({
                "message": "All field required.(first_name, last_name, phone_number, gender)"
            }), 400
        AUTH.update_user(user.id, first_name=first_name, last_name=last_name, phone_number=phone_number, gender=gender)
        return jsonify({
            "message": "Profile updated successfully"
        }), 200
    except ValueError as e:
        raise CustomError(str(e), 400)


@app.route('/forgot_password', methods=['POST'], strict_slashes=False)
def forgot_password() -> tuple[Response, int]:
    """ POST /forgot_password """
    data = request.get_json()
    email = data.get("email")

    try:
        AUTH.forgot_password(email)
        return jsonify({
            "message": "Reset code sent to your email"
        }), 200
    except ValueError as e:
        raise CustomError(str(e), 404)


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def reset_password() -> tuple[Response, int]:
    """ POST /reset_password """
    data = request.get_json()
    email = data.get("email")
    reset_code = data.get("reset_code")
    new_password = data.get("new_password")

    try:
        if not all([email, reset_code, new_password]):
            return jsonify({
                "message": "All field required.(email, reset_code, new_password)"
            }), 400

        AUTH.reset_password_with_code(email, reset_code, new_password)
        return jsonify({
            "message": "Password updated successfully"
        }), 200

    except ValueError as e:
        raise CustomError(str(e), 403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

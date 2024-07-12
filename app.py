import os
import tempfile
import uuid
import json
from datetime import timedelta, datetime
import google.generativeai as genai

from docxtpl import DocxTemplate
from flask import Flask, Response, jsonify, request, abort, redirect, json, url_for, send_file
from dotenv import load_dotenv
from sqlalchemy.exc import NoResultFound
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

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Configure generative AI API key
genai.configure(api_key=os.environ["API_KEY"])

# In-memory storage for contexts
context_storage = {}


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


@app.route('/user_letters', methods=['GET'])
def get_user_letters():
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        return jsonify({"message": "User not authenticated"}), 403

    letters = dbs.get_letters_by_user(user.id)
    letter_list = [
        {
            "id": letter.id,
            "type": letter.type,
            "content": letter.content,
            "generated_at": letter.generated_at,
            "filename": letter.filename
        }
        for letter in letters
    ]

    return jsonify({"letters": letter_list})


@app.route('/user_letters/<letter_id>', methods=['GET'])
def get_user_letter(letter_id):
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        return jsonify({"message": "User not authenticated"}), 403

    try:
        letter = dbs.get_letter(letter_id)
        if letter.user_id != user.id:
            return jsonify({"message": "User not authorized to access this letter"}), 403

        letter_data = {
            "id": letter.id,
            "type": letter.type,
            "content": letter.content,
            "generated_at": letter.generated_at,
            "filename": letter.filename
        }

        return jsonify({"letter": letter_data})

    except NoResultFound:
        return jsonify({"message": "Letter not found"}), 404


@app.route('/download_save_letter/<letter_id>', methods=['GET'])
def download_sava_letter(letter_id):
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        return jsonify({"message": "User not authenticated"}), 403

    try:
        letter = dbs.get_letter(letter_id)
    except NoResultFound:
        return jsonify({"message": "Letter not found"}), 404

    if letter.user_id != user.id and not user.is_admin:
        return jsonify({"message": "User not authorized to download this letter"}), 403

    context = json.loads(letter.content)
    file_id = str(uuid.uuid4())
    context_storage[file_id] = context

    download_url = url_for('download_generated_letter', file_id=file_id, template_name=letter.type, _external=True)
    return jsonify({"message": "Document ready for download", "download_url": download_url})


@app.route('/letter/<letter_id>', methods=['DELETE'], strict_slashes=False)
def delete_user_letter(letter_id: str) -> tuple[Response, int]:
    """ DELETE /letter/<letter_id> """
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    userr = AUTH.get_user_from_session_id(user_cookie)
    if userr is None:
        return jsonify({"message": "User not authenticated"}), 403

    try:
        letter = dbs.get_letter(letter_id)
    except NoResultFound:
        return jsonify({"message": "Letter not found"}), 404

    if letter.user_id != userr.id:
        return jsonify({"message": "User not authorized to delete this letter"}), 403

    try:
        dbs.delete_letter(letter_id)
        return jsonify({"message": "Letter deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/update_letter/<letter_id>', methods=['PUT'])
def update_letter(letter_id):
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        return jsonify({"message": "User not authenticated"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        letter = dbs.get_letter(letter_id)
    except NoResultFound:
        return jsonify({"message": "Letter not found"}), 404

    if letter.user_id != user.id and not user.is_admin:
        return jsonify({"message": "User not authorized to update this letter"}), 403

    allowed_fields = ['content', 'filename', 'type']
    update_data = {key: value for key, value in data.items() if key in allowed_fields}

    if not update_data:
        return jsonify({"error": "No valid fields provided for update"}), 400

    try:
        dbs.update_letter(letter_id, **update_data)
        return jsonify({"message": "Letter updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/admin/login', methods=['POST'], strict_slashes=False)
def admin_login():
    """ POST /admin/login """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON data received"}), 400

    email = data.get("email")
    password = data.get("password")

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session_id = AUTH.create_session(email)  # Assuming AUTH is properly defined
        if session_id:
            message = {"email": email, "message": "Logged in successfully as Admin"}
            response = jsonify(message)
            response.set_cookie("session_id", session_id)
            return response
        else:
            return jsonify({"message": "Failed to create session"}), 500
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route('/admin/users', methods=['GET'], strict_slashes=False)
def get_all_users() -> tuple[Response, int]:
    """ GET /admin/users """
    admin_cookie = request.cookies.get("session_id", None)
    admin_user = AUTH.get_user_from_session_id(admin_cookie)
    if admin_user is None or admin_user.email != ADMIN_EMAIL:
        abort(403, description="Admin privileges required")

    users = AUTH.get_all_users()
    return jsonify(users), 200


@app.route('/admin/user', methods=['POST'], strict_slashes=False)
def get_user() -> tuple[Response, int]:
    """ POST /admin/user """
    global user
    admin_cookie = request.cookies.get("session_id", None)
    admin_user = AUTH.get_user_from_session_id(admin_cookie)
    if admin_user is None or admin_user.email != ADMIN_EMAIL:
        abort(403, description="Admin privileges required")

    data = request.get_json()

    user_id = data.get("id")
    last_name = data.get("last_name")

    if not user_id and not last_name:
        return jsonify({"message": "Please provide a user ID or last name"}), 400

    if user_id:
        user = dbs.get_user_by_id(user_id)
    elif last_name:
        user = dbs.get_user_by_last_name(last_name)

    if user is None:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user), 200


@app.route('/admin/letters', methods=['GET'])
def get_all_letters():
    admin_cookie = request.cookies.get("session_id", None)
    admin_user = AUTH.get_user_from_session_id(admin_cookie)
    if admin_user is None or admin_user.email != ADMIN_EMAIL:
        abort(403, description="Admin privileges required")

    letters = dbs.get_all_letters()
    letter_list = [
        {
            "id": letter.id,
            "user_id": letter.user_id,
            "user_first_name": letter.user_first_name,
            "user_last_name": letter.user_last_name,
            "type": letter.type,
            "content": letter.content,
            "generated_at": letter.generated_at
        }
        for letter in letters
    ]

    return jsonify({"letters": letter_list})


@app.route('/admin/letter', methods=['POST'], strict_slashes=False)
def get_one_user_letters() -> tuple[Response, int]:
    """ POST /admin/letters """
    global user
    admin_cookie = request.cookies.get("session_id", None)
    admin_user = AUTH.get_user_from_session_id(admin_cookie)
    if admin_user is None or admin_user.email != ADMIN_EMAIL:
        abort(403, description="Admin privileges required")

    data = request.get_json()
    user_id = data.get("id")
    last_name = data.get("last_name")

    if not user_id and not last_name:
        return jsonify({"message": "Please provide a user ID or last name"}), 400

    if user_id:
        user = dbs.get_letters_by_user_by_id(user_id)
    elif last_name:
        user = dbs.get_letters_by_user_by_last_name(last_name)

    if user is None:
        return jsonify({"message": "User not found"}), 404

    letters = dbs.get_letters_by_user(user.id)
    letter_list = [
        {
            "id": letter.id,
            "user_id": letter.user_id,
            "user_first_name": letter.user_first_name,
            "user_last_name": letter.user_last_name,
            "type": letter.type,
            "content": letter.content,
            "generated_at": letter.generated_at,
            "filename": letter.filename
        }
        for letter in letters
    ]

    return jsonify({"letters": letter_list}), 200


@app.route('/admin/letter/<letter_id>', methods=['DELETE'], strict_slashes=False)
def delete_letter(letter_id: str) -> tuple[Response, int]:
    """ DELETE /admin/letter/<letter_id> """
    admin_cookie = request.cookies.get("session_id", None)
    admin_user = AUTH.get_user_from_session_id(admin_cookie)
    if admin_user is None or admin_user.email != ADMIN_EMAIL:
        abort(403, description="Admin privileges required")

    try:
        dbs.delete_letter(letter_id)
        return jsonify({"message": "Letter deleted successfully"}), 200
    except NoResultFound:
        return jsonify({"message": "Letter not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/generate_examination_questions', methods=['POST'])
def generate_examination_questions():
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        return jsonify({"message": "User not authenticated"}), 403

    data = request.get_json()

    required_keys = [
        'school_name', 'term', 'subject', 'class', 'duration', 'topics_taught', 'num_of_mul_choice_ques',
        'num_of_subjective_ques', 'num_of_sub_ques_to_ans'
    ]

    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing one or more required parameters"}), 400

    school_name = data['school_name'].upper()
    term = data['term'].upper()
    subject = data['subject'].upper()
    level = data['class'].upper()
    duration = data['duration'].upper()
    topics_taught = data['topics_taught']
    num_of_mul_choice_ques = data['num_of_mul_choice_ques']
    num_of_subjective_ques = data['num_of_subjective_ques']
    num_of_sub_ques_to_ans = data['num_of_sub_ques_to_ans']

    model = genai.GenerativeModel('gemini-1.5-flash')

    mul_ques_response = model.generate_content(
        f"Generate {num_of_mul_choice_ques} multiple choice questions on {subject} for "
        f"{level} learners in the Ghana curriculum covering these topics: {topics_taught}. "
        f"Generate only standard multiple choice questions, do not bold anything, do not add anything and do "
        f"not separate them under topics. The options should be vertical."
    )

    subjective_ques_response = model.generate_content(
        f"Generate {num_of_subjective_ques} subjective questions on {subject} for "
        f"{level} learners in the Ghana curriculum covering these topics: {topics_taught}. "
        f"Generate only subjective questions, do not add anything and do not separate them under topics do not add "
        f"anything and do not separate them under topics."
    )

    mul_choice_ques_ans_response = model.generate_content(
        f"Provide answers with their respective numbers for the following multiple choice questions: "
        f"{mul_ques_response.text}. Generate only the answers."
    )

    sub_ques_ans_response = model.generate_content(
        f"Provide answers with their respective numbers for the following subjective questions: "
        f"{subjective_ques_response.text}. Generate only subjective answers, do not bold anything, do not add "
        f"anything and do not separate them under topics."
    )

    context = {
        "SCHOOL_NAME": school_name,
        "TERM": term,
        "SUBJECT": subject,
        "CLASS": level,
        "DURATION": duration,
        "MUL_CHOICE_QUES": mul_ques_response.text,
        "NUM_OF_QUES_TO_ANS": num_of_sub_ques_to_ans,
        "SUBJECTIVE_QUESTIONS": subjective_ques_response.text,
        "MARKING_SCHEME_SEC_A": mul_choice_ques_ans_response.text,
        "MARKING_SCHEME_SEC_B": sub_ques_ans_response.text,
    }

    # Generate filename
    filename = f"{context['CLASS']}_{context['SUBJECT']}_Examination_Questions_for_{context['SCHOOL_NAME']}.docx"

    # Save context and filename to database
    letter_content = json.dumps(context)
    new_letter = dbs.add_letter(user_id=user.id, type='examination_questions', content=letter_content,
                                filename=filename)

    # Generate file ID for download
    file_id = str(uuid.uuid4())
    context_storage[file_id] = context

    # Generate download URL
    download_url = url_for('download_generated_letter', file_id=file_id, template_name='examination_questions',
                           _external=True)

    return jsonify({"message": "Examination document created successfully", "download_url": download_url})


@app.route('/generate_letter', methods=['POST'])
def generate_letter():
    user_cookie = request.cookies.get("session_id", None)
    if user_cookie is None:
        return jsonify({"message": "Session ID not found"}), 403

    user = AUTH.get_user_from_session_id(user_cookie)
    if user is None:
        return jsonify({"message": "User not authenticated"}), 403

    data = request.get_json()
    letter_type = data.get('letter_type')

    required_keys_map = {
        'maternity_leave_letter': ['name', 'staffid', 'phone', 'registeredno', 'school', 'address', 'district_town',
                                   'address_town', 'district', 'date_on_letter'],
        'upgrading_application_letter': ['name', 'staffid', 'phone', 'registeredno', 'school', 'address',
                                         'district_town',
                                         'address_town', 'district', 'date_on_letter', 'years_in_service', 'program',
                                         'year_completed', 'current_rank', 'next_rank'],
        'acceptance_of_appointment_letter': ['name', 'reference', 'phone', 'school', 'address', 'region_town',
                                             'address_town', 'region', 'date_on_letter', 'date_on_appointment_letter'],
        'transfer_or_reposting_letter': ['name', 'staffid', 'phone', 'registeredno', 'school', 'address',
                                         'district_town',
                                         'address_town', 'district', 'date_on_letter', 'years_in_school', 'reason',
                                         'new_school'],
        'release_transfer_letter': ['name', 'staffid', 'phone', 'registeredno', 'school', 'address', 'district_town',
                                    'address_town', 'district', 'date_on_letter', 'years_in_school', 'reason',
                                    'new_dist_reg', 'curr_dist_reg', 'level_of_transfer'],
        'salary_reactivation_letter': ['name', 'staffid', 'phone', 'registeredno', 'school', 'address', 'district_town',
                                       'address_town', 'district', 'date_on_letter', 'month_or_s', 'circuit']
    }

    if letter_type not in required_keys_map:
        return jsonify({"error": "Invalid letter type"}), 400

    required_keys = required_keys_map[letter_type]

    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing one or more required parameters"}), 400

    original_date = datetime.strptime(data['date_on_letter'], "%Y-%m-%d")
    formatted_date_str = original_date.strftime("%B %d, %Y")

    context = {}
    if letter_type == 'acceptance_of_appointment_letter':
        context = {
            "NAME": data['name'].upper(),
            "SCHOOLNAME": data['school'],
            "ADDRESS": data['address'],
            "ADDRESSTOWN": data['address_town'].upper(),
            "TOWN": data['region_town'].upper(),
            "PHONE": f"({data['phone']})",
            "DATEONLETTER": formatted_date_str.upper()
        }
    else:
        context = {
            "NAME": data['name'].upper(),
            "SCHOOLNAME": data['school'],
            "ADDRESS": data['address'],
            "ADDRESSTOWN": data['address_town'].upper(),
            "TOWN": data['district_town'].upper(),
            "STAFFID": data['staffid'],
            "REGISTERNO": data['registeredno'],
            "PHONE": f"({data['phone']})",
            "DATEONLETTER": formatted_date_str.upper(),
            "DISTRICT": data['district'].upper()
        }

    if letter_type == 'upgrading_application_letter':
        context.update({
            "NUMBEROFYEARSINSERVICE": data['years_in_service'],
            "NAMEOFPROGRAM": data['program'].title(),
            "YEARCOMPLETED": data['year_completed'],
            "CURRENTRANK": data['current_rank'],
            "NEXTRANK": data['next_rank'],
            "NEXTRANKTITLE": data['next_rank'].upper()
        })

    elif letter_type == 'acceptance_of_appointment_letter':
        appointment_date_original = datetime.strptime(data['date_on_appointment_letter'], "%Y-%m-%d")
        appointment_date_formatted = appointment_date_original.strftime("%B %d, %Y")
        context.update({
            "REFERENCEAPPOINTMENTLETTER": data['reference'],
            "DATEONTHEAPPOINTMENTLETTER": appointment_date_formatted.title(),
            "REGION": data['region'].upper()
        })

    elif letter_type == 'transfer_or_reposting_letter':
        context.update({
            "NUMBEROFYEARSSERVED": data['years_in_school'],
            "NEWSCHOOLNAME": data['new_school'].title(),
            "REASON": data['reason'].lower()
        })

    elif letter_type == 'release_transfer_letter':
        context.update({
            "NUMBEROFYEARSSERVED": data['years_in_school'],
            "NEWDISTORREG": data['new_dist_reg'].title(),
            "CURRENTDISTORREG": data['curr_dist_reg'].title(),
            "LEVELOFTRANSFER": data['level_of_transfer'].title(),
            "REASON": data['reason'].lower()
        })

    elif letter_type == 'salary_reactivation_letter':
        context.update({
            "YOURDISTRICT": data['district'].title(),
            "MONTHORS": data['month_or_s'],
            "CIRCUITNAME": data['circuit'].title()
        })

    file_id = str(uuid.uuid4())
    context_storage[file_id] = context

    filename = f"{letter_type.replace('_', ' ').title()} for {context['NAME']}.docx"
    letter_content = json.dumps(context)
    new_letter = dbs.add_letter(user_id=user.id, type=letter_type, content=letter_content, filename=filename)

    download_url = url_for('download_generated_letter', file_id=file_id, template_name=letter_type, _external=True)
    return jsonify(
        {"message": f"{letter_type.replace('_', ' ').title()} generated successfully", "download_url": download_url})


@app.route('/download_generated_letter/<file_id>/<template_name>', methods=['GET'])
def download_generated_letter(file_id, template_name):
    if file_id not in context_storage:
        return jsonify({"error": "Invalid file ID"}), 404

    context = context_storage.pop(file_id)
    template_path = f"letter_templates/{template_name}.docx"
    doc = DocxTemplate(template_path)
    doc.render(context)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        doc.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    # Determine the appropriate name field
    name_field = context.get("NAME", context.get("SCHOOL_NAME", "Document"))

    return send_file(tmp_file_path, as_attachment=True,
                     download_name=f"{template_name.replace('_', ' ').title()} for {name_field.title()}.docx")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

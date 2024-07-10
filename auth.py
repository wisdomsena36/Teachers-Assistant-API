import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import random
from bcrypt import hashpw, gensalt, checkpw
from constant import template_for_password_reset, template_for_email_verification
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class Auth:
    def __init__(self):
        self._db = DB()
        self.SMTP_SERVER = os.getenv('SMTP_SERVER')
        self.SMTP_PORT = 465
        self.SMTP_EMAIL = os.getenv('SMTP_EMAIL')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    def _hash_password(self, password: str) -> str:
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    def _generate_uuid(self) -> str:
        return str(uuid4())

    def _generate_reset_code(self) -> str:
        """ Generates a 6-digit reset code """
        return f"{random.randint(100000, 999999)}"

    def _send_email(self, to_email: str, subject: str, body_html: str):
        """ Sends an email using SMTP """
        msg = MIMEMultipart()
        msg['From'] = self.SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))

        try:
            with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            raise ValueError(f"Failed to send email: {str(e)}")

    def render_template(self, template_str: str, context: dict) -> str:
        template = Template(template_str)
        return template.render(context)

    def register_user(self, email: str, password: str, first_name: str, last_name: str, phone_number: str,
                      gender: str) -> User:
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = self._hash_password(password)
            verification_code = self._generate_reset_code()
            new_user = self._db.add_user(email, hashed_password, first_name, last_name, phone_number, gender,
                                         verification_code=verification_code)
            self.send_verification_email(email, first_name, verification_code)
            return new_user

    def send_verification_email(self, email: str, first_name: str, verification_code: str):
        subject = 'Email Verification'
        template = template_for_email_verification
        context = {
            "first_name": first_name,
            "email": email,
            "verification_code": verification_code
        }
        body_html = self.render_template(template, context)
        self._send_email(email, subject, body_html)

    def verify_user_email(self, email: str, verification_code: str) -> None:
        try:
            user = self._db.find_user_by(email=email)
            if user.verification_code != verification_code:
                raise ValueError("Invalid verification code")
            self._db.update_user(user.id, is_verified=True, verification_code=None)
        except NoResultFound:
            raise ValueError(f"User with email '{email}' not found")

    def valid_login(self, email: str, password: str) -> bool:
        try:
            user = self._db.find_user_by(email=email)
            if not user.is_verified:
                raise ValueError(f"Email '{email}' is not verified. Please check your email for verification.")
            return checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        try:
            user = self._db.find_user_by(email=email)
            session_id = self._generate_uuid()
            self._db.update_user(user.id, session_id=session_id, last_login=datetime.utcnow())
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> User:
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        self._db.update_user(user_id, session_id=None)

    def forgot_password(self, email: str):
        try:
            user = self._db.find_user_by(email=email)
            reset_code = self._generate_reset_code()
            self._db.update_user(user.id, reset_code=reset_code)

            subject = 'Password Reset Request'
            template = template_for_password_reset
            context = {
                "first_name": user.first_name,
                "email": email,
                "reset_code": reset_code
            }
            body_html = self.render_template(template, context)
            self._send_email(email, subject, body_html)

        except NoResultFound:
            raise ValueError(f"User with email '{email}' not found")

    def reset_password_with_code(self, email: str, reset_code: str, new_password: str) -> None:
        try:
            user = self._db.find_user_by(email=email)
            if user.reset_code != reset_code:
                raise ValueError("Invalid reset code")
            hashed_password = self._hash_password(new_password)
            self._db.update_user(user.id, hashed_password=hashed_password, reset_code=None)
        except NoResultFound:
            raise ValueError(f"User with email '{email}' not found")

    def update_user(self, user_id: int, first_name: str, last_name: str, phone_number: str, gender: str) -> None:
        self._db.update_user(user_id, first_name=first_name, last_name=last_name, phone_number=phone_number,
                             gender=gender)

    def get_all_users(self) -> list:
        users = self._db.get_all_users()
        return [{"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
                 "phone_number": user.phone_number, "gender": user.gender, "last_login": user.last_login,
                 "is_logged_in": user.session_id is not None} for user in users]

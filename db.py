from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from user import User, Base, Letter


class DB:
    def __init__(self):
        self._engine = create_engine("sqlite:///users.db")
        # Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine)

    def _create_session(self):
        return self._Session()

    def add_user(self, email: str, hashed_password: str, first_name: str, last_name: str, phone_number: str,
                 gender: str, verification_code: str) -> User:
        session = self._create_session()
        try:
            new_user = User(email=email, hashed_password=hashed_password, first_name=first_name, last_name=last_name,
                            phone_number=phone_number, gender=gender, verification_code=verification_code)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
        finally:
            session.close()
        return new_user

    def find_user_by(self, **kwargs) -> Type[User]:
        session = self._create_session()
        try:
            user = session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound
        finally:
            session.close()
        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        session = self._create_session()
        try:
            user = session.query(User).get(user_id)
            if user is None:
                raise NoResultFound
            for key, value in kwargs.items():
                setattr(user, key, value)
            session.commit()
        finally:
            session.close()

    def get_all_users(self) -> list:
        session = self._create_session()
        try:
            users = session.query(User).all()
        finally:
            session.close()
        return users

    def get_user_by_id(self, user_id) -> dict:
        session = self._create_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return {"id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number,
                        "gender": user.gender
                        }
            return None
        finally:
            session.close()

    def get_user_by_last_name(self, last_name) -> dict:
        session = self._create_session()
        try:
            user = session.query(User).filter_by(last_name=last_name).first()
            if user:
                return {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number,
                        "gender": user.gender
                        }
            return None
        finally:
            session.close()

    def add_letter(self, user_id, type, content, filename):
        session = self._create_session()
        try:
            user = session.query(User).get(user_id)
            if not user:
                raise ValueError("User not found")

            new_letter = Letter(
                user_id=user.id,
                user_first_name=user.first_name,
                user_last_name=user.last_name,
                type=type,
                content=content,
                filename=filename
            )
            session.add(new_letter)
            session.commit()
            session.refresh(new_letter)
            return new_letter
        finally:
            session.close()

    def get_letter(self, letter_id):
        session = self._create_session()
        try:
            letter = session.query(Letter).get(letter_id)
            if letter is None:
                raise NoResultFound
            return letter
        finally:
            session.close()

    def get_letters_by_user(self, user_id):
        session = self._create_session()
        try:
            return session.query(Letter).filter_by(user_id=user_id).all()
        finally:
            session.close()

    def update_letter(self, letter_id, **kwargs):
        session = self._create_session()
        try:
            letter = session.query(Letter).get(letter_id)
            if letter is None:
                raise NoResultFound
            for key, value in kwargs.items():
                setattr(letter, key, value)
            session.commit()
        finally:
            session.close()

    def delete_letter(self, letter_id):
        session = self._create_session()
        try:
            letter = session.query(Letter).get(letter_id)
            if letter is None:
                raise NoResultFound
            session.delete(letter)
            session.commit()
        finally:
            session.close()

    def get_all_letters(self):
        session = self._create_session()
        try:
            return session.query(Letter).all()
        finally:
            session.close()

    def get_letters_by_user_by_id(self, user_id):
        session = self._create_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            return user
        finally:
            session.close()

    def get_letters_by_user_by_last_name(self, last_name):
        session = self._create_session()
        try:
            user = session.query(User).filter_by(last_name=last_name).first()
            return user
        finally:
            session.close()

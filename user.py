import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import backref, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False, unique=True)
    hashed_password = Column(String(250), nullable=False)
    session_id = Column(String(250))
    reset_code = Column(String(6))
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    phone_number = Column(String(20), nullable=False)
    gender = Column(String(10), nullable=False)
    is_verified = Column(Integer, default=0)
    verification_code = Column(String(6))
    last_login = Column(DateTime)
    is_admin = Column(Boolean, default=False)  # Assuming this field is to distinguish admin users


class Letter(Base):
    __tablename__ = 'letters'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_first_name = Column(String(250), nullable=False)
    user_last_name = Column(String(250), nullable=False)
    user = relationship('User', backref=backref('letters', lazy=True))
    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    filename = Column(String, nullable=False)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
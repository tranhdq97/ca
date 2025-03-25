from typing import Dict
from app.models.user import User
from app import db
import jwt
import datetime
from app.config import Config


class AuthService:
    @classmethod
    def get_user(cls, filter_params: Dict[str, str | bool]) -> User:
        """Get a user by phone number"""
        return User.query.filter_by(**filter_params).first()

    @classmethod
    def add_user(cls, phone: str, is_staff: bool, password: str = "") -> User:
        """Add a user with the given phone number"""
        if is_staff:
            user = User(phone=phone, is_staff=True)
            user.set_password(password)
        else:
            user = User(phone=phone, is_staff=False)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def generate_jwt_token(cls, user: User) -> str:
        """
        Generate a JWT token for the given user.

        :param user: User object
        :return: JWT token as a string
        """
        payload = {
            "id": user.id,
            "phone": user.phone,
            "is_staff": user.is_staff,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        }
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
        return token

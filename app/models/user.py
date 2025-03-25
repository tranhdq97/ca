from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=False, nullable=False)
    password_hash = db.Column(db.String(128))
    is_staff = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("phone", "is_staff", name="unique_phone_is_staff"),
    )

    def set_password(self, password):
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

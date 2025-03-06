"""The user table"""

from flask_login import UserMixin
from config import db


class User(db.Model, UserMixin):
    """User model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

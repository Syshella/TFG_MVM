from flask import current_app
from itsdangerous import Serializer
from passlib.hash import pbkdf2_sha256
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp(), nullable=True)

    # Creates password hash
    def set_hash_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def check_hash_password(self, password):
        print(password)
        print(self.password)
        return pbkdf2_sha256.verify(password, self.password)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

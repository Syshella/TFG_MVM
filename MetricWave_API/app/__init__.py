from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from itsdangerous import URLSafeTimedSerializer


db = SQLAlchemy()
s = URLSafeTimedSerializer('SECRET_KEY')


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializa la base de datos y el servidor de mail
    db.init_app(app)
    swagger = Swagger(app)

    # Crea las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()

    from app.routes import register_routes
    register_routes(app)


    return app


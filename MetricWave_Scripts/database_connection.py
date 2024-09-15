import os
from dotenv import load_dotenv
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()


class Config:
    # Puerto 8889
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    # print(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # def create_session(self):
    #     engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    #     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    #     return SessionLocal()

# test connection to db
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session = SessionLocal()
# session.close()

from flask_sqlalchemy import Model
from app import db

class User(db.Model):
    email = 
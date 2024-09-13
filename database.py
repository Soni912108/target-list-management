from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Initialize Flask app
app = Flask(__name__,)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///targets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class TargetList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    users = db.relationship('TargetListUser', backref='target_list', lazy=True, cascade="all, delete-orphan")

    

class TargetUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    job_position = db.Column(db.String(100))
    lists = db.relationship('TargetListUser', backref='target_user', lazy=True,cascade="all, delete-orphan")


# establish the many-to-many relationship between the target list and target user
class TargetListUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_list_id = db.Column(db.Integer, db.ForeignKey('target_list.id'), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('target_user.id'), nullable=False)



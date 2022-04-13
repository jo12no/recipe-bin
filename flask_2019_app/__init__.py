from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
login = LoginManager(app) 
# flask login can force login to view certain pages from a view
login.login_view = 'login' 

app.config.from_object('config') # Input file is ../config.py

file_path = os.path.abspath(os.getcwd())

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/flask_2019_apptest.db'.format(file_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from flask_2019_app import views, models
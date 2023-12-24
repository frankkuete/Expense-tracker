from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
# if login is required to access to a route , the view named 'login' will be called automatically
login_manager.login_view = 'login'
# if login is required then a message will be send to login view with 'login_message_category' category
login_manager.login_message_category = 'info'


from main import routes



from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import yaml

app = Flask(__name__)
yml = yaml.load(open('classget/configure.yaml'))

app.config['SECRET_KEY'] = yml['secret_key']

app.config['SQLALCHEMY_DATABASE_URI'] = yml['mysql_config']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


from classget import routes

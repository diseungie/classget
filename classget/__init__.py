from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import yaml


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'


def create_app():
    app = Flask(__name__)

    # config
    yml = yaml.load(open('classget/configure.yaml'), Loader=yaml.BaseLoader)
    app.config['SECRET_KEY'] = yml['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = yml['mysql_config']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 持ってきたModuleをappに入れる
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # それぞれのBlueprintをappに入れる
    from classget.admin.routes import admin
    from classget.main.routes import main
    from classget.reviews.routes import reviews
    from classget.users.routes import users
    from classget.errors.handlers import errors
    app.register_blueprint(admin)
    app.register_blueprint(main)
    app.register_blueprint(reviews)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    return app

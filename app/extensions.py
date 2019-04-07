from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

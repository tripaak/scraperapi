# import Flask class from flask module
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

#create instance of Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\akash.tripathi\\Personal_projects\\Flask\SCRAPERAPI\\filesystem'

# ALLOWED_EXTENSIONS = {'csv'}
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from flaskblog import routes
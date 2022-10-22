from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# app.config['Fernet_Enc_KEY'] =  = Fernet.generate_key()
app.config['Fernet_Enc_KEY'] = b'iucBjC-pLJi21AmJpMKk_D_SnFymCZe7kJ6bnduOFAc='
f = Fernet(app.config['Fernet_Enc_KEY'])

from passwordManager import routes

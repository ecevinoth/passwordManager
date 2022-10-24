from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from cryptography.fernet import Fernet
from flask_cors import CORS
import secrets
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///market.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.update({"SECRET_KEY": secrets.token_hex(64)})

CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
envVariableStatus = load_dotenv()  # take environment variables from .env.

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

# app.config['Fernet_Enc_KEY'] =  = Fernet.generate_key()
app.config["Fernet_Enc_KEY"] = bytes(os.getenv("Fernet_Enc_KEY"), "utf-8")
f = Fernet(app.config["Fernet_Enc_KEY"])

from passwordManager import routes

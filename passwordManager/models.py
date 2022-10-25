from passwordManager import db, login_manager
from passwordManager import bcrypt
from passwordManager import f
from passwordManager import app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# 2022-10-24: Removed User from model to fulfil okta integration requirements.
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     username = db.Column(db.String(length=30), nullable=False, unique=True)
#     email_address = db.Column(db.String(length=50), nullable=False, unique=True)
#     password_hash = db.Column(db.String(length=60), nullable=False)
#     budget = db.Column(db.Integer(), nullable=False, default=1000)
#     items = db.relationship('Item', backref='owned_user', lazy=True)

#     @property
#     def password(self):
#         return self.password

#     @password.setter
#     def password(self, plain_text_password):
#         self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

#     def check_password_correction(self, attempted_password):
#         return bcrypt.check_password_hash(self.password_hash, attempted_password)


# add based on okta sample program
# Simulate user database
USERS_DB = {}

class User(UserMixin):

    """Custom User class."""

    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

    def claims(self):
        """Use this method to render all assigned claims on profile page."""
        return {'name': self.name,
                'email': self.email}.items()

    @staticmethod
    def get(user_id):
        return USERS_DB.get(user_id)

    @staticmethod
    def create(user_id, name, email):
        USERS_DB[user_id] = User(user_id, name, email)

# class Item(db.Model):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(length=30), nullable=False, unique=True)
#     price = db.Column(db.Integer(), nullable=False)
#     barcode = db.Column(db.String(length=12), nullable=False, unique=True)
#     description = db.Column(db.String(length=1024), nullable=False, unique=True)
#     owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
#     def __repr__(self):
#         return f'Item {self.name}'

class Asset(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    instance = db.Column(db.String(length=255), nullable=False, index=True)
    username = db.Column(db.String(length=12), nullable=False, index=True)
    other_details = db.Column(db.String(length=255), nullable=False, index=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    password_dec = ""

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = f.encrypt(str(plain_text_password).encode()).decode('utf-8') #encrypted password

    def password_decryption(self, password_enc):
        return f.decrypt(bytes(password_enc, 'UTF-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'instance': self.instance,
            'username': self.username,
            'other_details': self.other_details,
            'password_hash': self.password_hash,
            # 'Name': "Vinoth"
        }

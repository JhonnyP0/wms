from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import InputRequired,Length, EqualTo
from flask_login import UserMixin

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('API_KEY')

#user config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self,id,username,password):
        self.id=id
        self.username=username
        self.password=password

#database connection
def db_connect():
    return mysql.connector.connect(
    host = 'localhost',
    port = os.getenv('DB_PORT'),
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    database = os.getenv('DB_NAME')
    )

@login_manager.user_loader
def userload(user_id):
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("select * from users where id = %s", (user_id,)) ###
    user= cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return User(user['id'], user['username'], user['password_hash']) ###
    return None
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField
from wtforms.validators import InputRequired,Length, EqualTo
from flask_login import UserMixin
from functools import wraps
class User(UserMixin):
    def __init__(self,id,username,password, is_admin=False):
        self.id=id
        self.username=username
        self.password=password
        self.is_admin =is_admin
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit=SubmitField('Log In')
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=5,max=10)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password=PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password', message='passwords must be the same')])
    email = EmailField('E-mail', validators=[InputRequired()])
    submit=SubmitField('Register')
class AddProdForm(FlaskForm):
    #products_table
    name = StringField('Name',validators=[InputRequired()])
    sku = StringField ('Sku', validators=[InputRequired()])
    description = StringField('Description')
    #inventory_table
    location=StringField('Location',validators=[InputRequired()])
    quantity=IntegerField('Quantity', validators=[InputRequired()])
    submit=SubmitField('Dodaj')
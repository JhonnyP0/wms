from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField,FieldList, FormField, SelectField
from wtforms.validators import InputRequired,Length, EqualTo, NumberRange,DataRequired
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
    name = StringField('Name',validators=[InputRequired()])
    sku = StringField ('Sku', validators=[InputRequired()])
    description = StringField('Description')
    submit=SubmitField('Dodaj')

class ShipmentProductForm(FlaskForm):
    product_sku = StringField('SKU Produktu', validators=[DataRequired(), Length(min=1, max=50)])
    quantity = IntegerField('Ilość', validators=[DataRequired(), NumberRange(min=1)])
    location_id = SelectField('Lokalizacja', choices=[('', 'Wybierz lokalizację')], validators=[DataRequired()])
    
    class Meta:
        csrf = False 

class AddShipmentForm(FlaskForm):
    products = FieldList(FormField(ShipmentProductForm), min_entries=1, max_entries=20)
    submit = SubmitField('Dodaj Wysyłkę')

# ### ZMIANA TUTAJ ###
# Dziedziczy z FlaskForm dla spójności, zamiast z Form
class ReceiveProductForm(FlaskForm):
    product_sku = StringField('SKU Produktu', validators=[DataRequired(), Length(min=1, max=50)])
    quantity = IntegerField('Ilość', validators=[DataRequired(), NumberRange(min=1)])
    location_id = SelectField('Lokalizacja', choices=[('', 'Wybierz lokalizację')], validators=[DataRequired()])
    
    class Meta:
        csrf = False 

class AddReceiveForm(FlaskForm):
    products = FieldList(FormField(ReceiveProductForm), min_entries=1, label='Produkty')
    submit = SubmitField('Dodaj Przyjęcie')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField,FieldList, FormField
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
    #products_table
    name = StringField('Name',validators=[InputRequired()])
    sku = StringField ('Sku', validators=[InputRequired()])
    description = StringField('Description')
    #inventory_table
    location=StringField('Location',validators=[InputRequired()])
    quantity=IntegerField('Quantity', validators=[InputRequired()])
    submit=SubmitField('Dodaj')

class ShipmentProductForm(FlaskForm):
    product_sku = StringField('SKU Produktu', validators=[InputRequired(), Length(min=1, max=50)])
    quantity = IntegerField('Ilość', validators=[InputRequired(), NumberRange(min=1)])
    class Meta:
        csrf = False # WAŻNA ZMIANA: Wyłączamy walidację CSRF dla tego pod-formularza


# Główny formularz dodawania wysyłki
class AddShipmentForm(FlaskForm):
    barcode = StringField('Kod kreskowy wysyłki', validators=[DataRequired(), Length(min=1, max=255)])
    # Przywrócone pole lokalizacji docelowej
    location_code = StringField('Kod lokalizacji docelowej', validators=[DataRequired(), Length(min=1, max=10)])
    products = FieldList(FormField(ShipmentProductForm), min_entries=1, max_entries=20)
    submit = SubmitField('Dodaj Wysyłkę')
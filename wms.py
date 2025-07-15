from flask import Flask, render_template, request, redirect, url_for, flash
from functools import wraps
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os
from source import User, LoginForm, RegisterForm, AddProdForm

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('API_KEY')

#flask login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#database connection
def db_connect():
    return mysql.connector.connect(
    host = os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT'),
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    database = os.getenv('DB_NAME')
    )

@login_manager.user_loader
def userload(user_id):
    conn = db_connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("select * from users where id = %s", (user_id,))
    user= cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return User(user['id'], user['username'], user['password_hash'])
    return None

#dekorator admin_required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Musisz się zalogować, aby uzyskać dostęp do tej strony.', 'warning')
            return redirect(url_for('login')) 
        if not current_user.is_admin:
            flash('Nie masz wystarczających uprawnień, aby uzyskać dostęp do tej strony.', 'danger')
            return redirect(url_for('dashboard')) 
        return f(*args, **kwargs)
    return decorated_function

# def admin_push():
#     conn=db_connect()
#     cursor=conn.cursor()
    
#     username="admin"
#     password=generate_password_hash("adminpass")
#     email="admin@admin.admin"
#     is_admin=True

#     query="INSERT INTO users (username, password_hash, email, is_admin) VALUES (%s, %s, %s, %s)"
#     cursor.execute(query, (username,password,email,is_admin))
#     conn.commit()
#     cursor.close()
#     conn.close()

# admin_push()

@app.route('/', methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        conn=db_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], form.password.data):
            userobj=User(user['id'], user['username'], user['password_hash'])
            login_user(userobj)
            flash('loged in','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect credentials', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        password=form.password.data
        hashed_password=generate_password_hash(password)
        
        try:
            conn = db_connect()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Username already exists, please choose another one', 'error')
                return redirect(url_for('register'))
            
            cursor.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
            existing_email = cursor.fetchone()
            
            if existing_email:
                flash('Email is already registered', 'error')
                return redirect(url_for('register'))
            
            cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)", (form.username.data, hashed_password, form.email.data))
            conn.commit()
            
            flash('Registration successful', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            print(str(e))
            flash('An error occurred during registration. Please try again.', 'error')

        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
    return render_template('register.html', form=form)

@app.route("/regal/<reg_code>")
@login_required
def regal_detail(reg_code):
    return render_template("shelf.html", reg_code=reg_code)

@app.route("/pozycja/<polka_code>/<regal_code>")
@login_required
def polka(polka_code,regal_code):
    conn=db_connect()
    cursor = conn.cursor(dictionary=True)

    query="""
            SELECT * 
            FROM 
                inventory 
            JOIN
                products ON inventory.product_id = products.id 
            JOIN
                locations ON inventory.location_id = locations.id
            WHERE
                locations.code = %s
        """
    cursor.execute(query, (polka_code,))
    items = cursor.fetchall()
    return render_template("regal_detail.html", polka_code=polka_code, items=items, regal_code=regal_code)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/products', methods=['GET'])
@login_required
def products():
    conn=db_connect()
    cursor=conn.cursor(dictionary=True)
    
    query="""
            SELECT
                i.id AS inventory_id,
                p.name AS product_name,
                p.sku,
                p.description,
                l.code AS location_code, -- Tutaj pobieramy kod lokalizacji z tabeli 'locations'
                i.quantity
            FROM
                inventory i
            JOIN
                products p ON i.product_id = p.id
            JOIN
                locations l ON i.location_id = l.id; -- Tutaj jest JOIN z tabelą 'locations'
        """

    cursor.execute(query)
    prods=cursor.fetchall()
    cursor.close()
    conn.close()    
    return render_template('products.html',prods=prods)

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/recivings', methods=["GET","POST"])
@login_required
def recivings():
    return render_template('recivings.html')

@app.route('/shipments', methods=['GET'])
@login_required
def shipments():
    conn=db_connect()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shipments")
    shipments=cursor.fetchall()
    cursor.close()
    conn.close()    
    return render_template('shipments.html',ship_items=shipments)

@app.route('/add_prod', methods=['GET','POST'])
@login_required
@admin_required
def add_prod():
    """
    Obsługuje dodawanie nowych produktów do bazy danych.
    Najprostsza wersja: wstawia nowy produkt i przypisuje go do lokalizacji.
    """
    form = AddProdForm()

    if form.validate_on_submit():
        name = form.name.data
        sku = form.sku.data
        description = form.description.data
        location_code = form.location.data.upper().strip()
        quantity = form.quantity.data

        conn = db_connect()
        if conn is None:
        
            flash('Błąd połączenia z bazą danych. Spróbuj ponownie.', 'danger')
            return render_template('add_prod.html', form=form)

        cursor = conn.cursor()
        
        try:

            cursor.execute("SELECT id FROM locations WHERE code = %s", (location_code,))
            location_data = cursor.fetchone()
            location_id = None

            if location_data:
                location_id = location_data[0]
            else:
                cursor.execute("INSERT INTO locations (code) VALUES (%s)", (location_code,))
                conn.commit() 
                location_id = cursor.lastrowid 

            if location_id is None:
                flash('Nie udało się ustalić ID lokalizacji.', 'danger')
                return render_template('add_prod.html', form=form)
            cursor.execute("INSERT INTO products (name, sku, description) VALUES (%s, %s, %s)",
                           (name, sku, description))
            conn.commit() 
            product_id = cursor.lastrowid 

            if product_id is None:
                flash('Nie udało się dodać produktu.', 'danger')
                return render_template('add_prod.html', form=form)


            cursor.execute("INSERT INTO inventory (product_id, location_id, quantity) VALUES (%s, %s, %s)",
                           (product_id, location_id, quantity))
            conn.commit() 

            flash('Produkt został pomyślnie dodany do inwentarza!', 'success')
            return redirect(url_for('products')) 

        except mysql.connector.Error as err:
            conn.rollback() 
            app.logger.error(f"Błąd bazy danych podczas dodawania produktu: {err}")
           
            flash('Wystąpił błąd podczas dodawania produktu. Spróbuj ponownie.', 'danger')
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Nieoczekiwany błąd podczas dodawania produktu: {e}")
            flash('Wystąpił nieoczekiwany błąd. Spróbuj ponownie.', 'danger')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('add_prod.html', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)
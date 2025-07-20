from flask import Flask, render_template, request, redirect, url_for, flash
from functools import wraps
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import sys
import os
from source import User, LoginForm, RegisterForm, AddProdForm, AddShipmentForm

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
        return User(user['id'], user['username'], user['password_hash'], user['is_admin'])
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

def add_admin():
    try:
        conn=db_connect()
        cursor=conn.cursor()
        
        username="admin"
        password=generate_password_hash("adminpass")
        email="admin@admin.admin"
        is_admin=True

        query="INSERT INTO users (username, password_hash, email, is_admin) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username,password,email,is_admin))
        conn.commit()
        cursor.close()
        conn.close()
        print("admin added")
    except:
        print("admin not added")

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

@app.route('/receivings', methods=["GET","POST"])
@login_required
def receivings():
    return render_template('receivings.html')

@app.route('/shipments', methods=['GET'])
@login_required
def shipments():
    conn=db_connect()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            s.id, 
            s.username, 
            s.shipment_date, 
            s.barcode, 
            loc.code AS location_code
        FROM shipments s
        JOIN locations loc ON s.location_id = loc.id
    """)
    shipments=cursor.fetchall()
    cursor.close()
    conn.close()    
    return render_template('shipments.html',ship_items=shipments)

@app.route('/add_prod', methods=['GET','POST'])
@login_required
@admin_required
def add_prod():
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

@app.route('/shipment_detail/<string:barcode>', methods=['GET'])
@login_required
def shipments_detail(barcode):
    conn = db_connect()
    if not conn:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM shipments WHERE barcode = %s", (barcode,))
        shipment_info = cursor.fetchone()

        if not shipment_info:
            flash('Wysyłka o podanym kodzie kreskowym nie została znaleziona.', 'warning')
            return redirect(url_for('shipments'))

        shipment_id = shipment_info['id']

        query = """
            SELECT
                sp.quantity AS shipped_quantity,
                p.name AS product_name,
                p.sku,
                p.description
            FROM
                shipment_products sp
            JOIN
                products p ON sp.product_id = p.id
            WHERE
                sp.shipment_id = %s;
        """
        cursor.execute(query, (shipment_id,))
        shipment_products = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Błąd bazy danych: {err}", 'danger')
        shipment_products = []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('shipments_detail.html', shipment_products=shipment_products, barcode=barcode)

@app.route('/add_shipment', methods=['GET', 'POST'])
@login_required
def add_shipment():
    form = AddShipmentForm()
    print("--- Rozpoczęcie funkcji add_shipment ---", flush=True)

    if form.validate_on_submit():
        print("Formularz ZWALIDOWANY pomyślnie.", flush=True)
        shipment_barcode = form.barcode.data
        # Przywrócone pobieranie kodu lokalizacji z formularza
        location_code = form.location_code.data.upper().strip()
        username = current_user.username

        conn = db_connect()
        if conn is None:
            print("BŁĄD: Połączenie z bazą danych nieudane.", flush=True)
            flash('Błąd połączenia z bazą danych.', 'danger')
            return render_template('add_shipment.html', form=form)

        cursor = conn.cursor()

        try:
            print(f"Próba dodania wysyłki z kodem: {shipment_barcode}, lokalizacja: {location_code}, użytkownik: {username}", flush=True)

            # 1. Sprawdź, czy kod kreskowy wysyłki już istnieje
            cursor.execute("SELECT id FROM shipments WHERE barcode = %s", (shipment_barcode,))
            existing_shipment = cursor.fetchone()
            if existing_shipment:
                print(f"OSTRZEŻENIE: Wysyłka z kodem {shipment_barcode} już istnieje.", flush=True)
                flash(f'Wysyłka o kodzie kreskowym "{shipment_barcode}" już istnieje.', 'warning')
                return render_template('add_shipment.html', form=form)

            # 2. Pobierz ID lokalizacji lub utwórz nową
            # Przywrócona logika pobierania/tworzenia lokalizacji
            cursor.execute("SELECT id FROM locations WHERE code = %s", (location_code,))
            location_data = cursor.fetchone()
            location_id = None

            if location_data:
                location_id = location_data[0]
            else:
                cursor.execute("INSERT INTO locations (code) VALUES (%s)", (location_code,))
                conn.commit()
                location_id = cursor.lastrowid
                flash(f'Utworzono nową lokalizację: {location_code}.', 'info')

            if location_id is None:
                print("BŁĄD: Nie udało się ustalić ID lokalizacji docelowej.", flush=True)
                flash('Nie udało się ustalić ID lokalizacji docelowej.', 'danger')
                return render_template('add_shipment.html', form=form)

            # 3. Dodaj nową wysyłkę do tabeli 'shipments'
            print("Wstawianie do tabeli 'shipments'...", flush=True)
            # Przywrócono przekazywanie location_id
            cursor.execute(
                "INSERT INTO shipments (username, barcode, location_id) VALUES (%s, %s, %s)",
                (username, shipment_barcode, location_id)
            )
            conn.commit()
            shipment_id = cursor.lastrowid
            print(f"Dodano wysyłkę. shipment_id: {shipment_id}", flush=True)

            if shipment_id is None:
                print("BŁĄD: Nie uzyskano shipment_id po wstawieniu.", flush=True)
                flash('Nie udało się dodać nowej wysyłki.', 'danger')
                return render_template('add_shipment.html', form=form)

            # 4. Dodaj produkty do tabeli 'shipment_products'
            products_added = 0
            if not form.products.entries:
                print("Brak produktów w formularzu FieldList.", flush=True)

            for i, product_entry in enumerate(form.products.entries):
                product_sku = product_entry.form.product_sku.data.upper().strip()
                quantity = product_entry.form.quantity.data
                print(f"Przetwarzanie produktu {i+1}: SKU={product_sku}, Ilość={quantity}", flush=True)

                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku,))
                product_data = cursor.fetchone()

                if product_data:
                    product_id = product_data[0]
                    print(f"Znaleziono Product ID: {product_id} dla SKU: {product_sku}", flush=True)
                    cursor.execute(
                        "INSERT INTO shipment_products (shipment_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (shipment_id, product_id, quantity)
                    )
                    products_added += 1
                else:
                    print(f"OSTRZEŻENIE: Produkt o SKU '{product_sku}' nie istnieje.", flush=True)
                    flash(f'Ostrzeżenie: Produkt o SKU "{product_sku}" nie istnieje i nie został dodany do wysyłki.', 'warning')

            conn.commit()
            print(f"Zatwierdzono {products_added} produktów do shipment_products.", flush=True)

            if products_added > 0:
                flash(f'Wysyłka "{shipment_barcode}" została pomyślnie dodana z {products_added} produktami!', 'success')
            else:
                flash(f'Wysyłka "{shipment_barcode}" została dodana, ale bez produktów (sprawdź SKU).', 'warning')

            return redirect(url_for('shipments'))

        except mysql.connector.Error as err:
            conn.rollback()
            print(f"BŁĄD BAZY DANYCH: {err}", file=sys.stderr, flush=True)
            flash(f'Wystąpił błąd bazy danych podczas dodawania wysyłki: {err}', 'danger')
        except Exception as e:
            conn.rollback()
            print(f"BŁĄD NIEOCZEKIWANY: {e}", file=sys.stderr, flush=True)
            flash(f'Wystąpił nieoczekiwany błąd: {e}. Spróbuj ponownie.', 'danger')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                print("Połączenie z bazą danych ZAMKNIĘTE.", flush=True)
    else:
        print("Formularz NIEZWALIDOWANY. Błędy formularza:", flush=True)
        for field, errors in form.errors.items():
            if isinstance(errors, dict):
                print(f"  Pole '{field}' (zagnieżdżone błędy):", flush=True)
                for sub_field, sub_errors in errors.items():
                    print(f"    Podpole '{sub_field}': {', '.join(str(e) for e in sub_errors)}", flush=True)
            elif isinstance(errors, list):
                print(f"  Pole '{field}': {', '.join(str(e) for e in errors)}", flush=True)
            else:
                print(f"  Pole '{field}': {str(errors)}", flush=True)

    print("--- Zakończenie funkcji add_shipment (przed renderowaniem) ---", flush=True)
    return render_template('add_shipment.html', form=form)

# TODO: reciva trzeba zrobic podobnie jak shipy (pamietaj o bazie danych !!)

if __name__ == "__main__":
    add_admin()
    app.run(host='0.0.0.0', port=5050, debug=True)
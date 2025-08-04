from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from functools import wraps
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import sys
import os
from barcode import Code128
from barcode.writer import ImageWriter
from source import User, LoginForm, RegisterForm, AddProdForm, AddShipmentForm, AddReceiveForm, ReceiveProductForm

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('API_KEY')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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

        username=os.getenv("username")
        password=generate_password_hash(os.getenv("password"))
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
            flash('Zalogowano pomyślnie!','success') 
            return redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowe dane logowania', 'danger') 
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
                flash('Nazwa użytkownika już istnieje, wybierz inną.', 'error') 
                return redirect(url_for('register'))

            cursor.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
            existing_email = cursor.fetchone()

            if existing_email:
                flash('Adres e-mail jest już zarejestrowany.', 'error') 
                return redirect(url_for('register'))

            cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)", (form.username.data, hashed_password, form.email.data))
            conn.commit()

            flash('Rejestracja zakończona pomyślnie!', 'success') 
            return redirect(url_for('login'))

        except Exception as e:
            print(str(e))
            flash('Wystąpił błąd podczas rejestracji. Spróbuj ponownie.', 'error') 

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
def polka(polka_code, regal_code):
    conn = db_connect()
    if conn is None:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    
    location_barcode_path = None 
    
    try:

        cursor.execute("SELECT barcode_image_path FROM locations WHERE code = %s", (polka_code,))
        polka_data = cursor.fetchone()
        
        if polka_data and polka_data['barcode_image_path']:
            location_barcode_path = polka_data['barcode_image_path']

        query="""
                SELECT 
                    p.name AS product_name, 
                    p.sku, 
                    i.quantity, 
                    p.barcode_image_path AS product_barcode_path
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                JOIN locations l ON i.location_id = l.id
                WHERE l.code = %s AND i.quantity > 0;
            """
        cursor.execute(query, (polka_code,))
        items = cursor.fetchall()
        
    except mysql.connector.Error as err:
        app.logger.error(f"Błąd bazy danych podczas pobierania danych dla półki {polka_code}: {err}", exc_info=True)
        flash(f'Wystąpił błąd podczas pobierania danych półki: {err}', 'danger')
        items = [] 
    except Exception as e:
        app.logger.error(f"Nieoczekiwany błąd podczas pobierania danych dla półki {polka_code}: {e}", exc_info=True)
        flash(f'Wystąpił nieoczekiwany błąd: {e}', 'danger')
        items = [] 
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


    return render_template("regal_detail.html", 
                           polka_code=polka_code, 
                           items=items, 
                           regal_code=regal_code,
                           location_barcode_path=location_barcode_path)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/products', methods=['GET'])
@login_required
def products():
    conn = db_connect()
    if conn is None:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return render_template('products.html', prods=[])

    cursor = conn.cursor(dictionary=True)

    search_query = request.args.get('query', '').strip()

    try:
        sql_query = """
            SELECT
                p.id AS product_id,
                p.name AS product_name,
                p.sku,
                p.description,
                p.barcode_image_path,
                COALESCE(SUM(i.quantity), 0) AS total_quantity,
                GROUP_CONCAT(DISTINCT l.code ORDER BY l.code SEPARATOR ', ') AS locations_summary
            FROM
                products p
            -- ### POCZĄTEK ZMIANY ###
            -- Dołączamy tylko te wpisy z inwentarza, gdzie ilość jest większa od 0.
            LEFT JOIN
                inventory i ON p.id = i.product_id AND i.quantity > 0
            -- ### KONIEC ZMIANY ###
            LEFT JOIN
                locations l ON i.location_id = l.id
        """
        sql_params = []

        if search_query:
            sql_query += """
                WHERE p.name LIKE %s OR p.sku LIKE %s OR p.description LIKE %s
            """
            sql_params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

        sql_query += """
            GROUP BY
                p.id, p.name, p.sku, p.description, p.barcode_image_path
            ORDER BY
                p.name;
        """

        cursor.execute(sql_query, tuple(sql_params))
        prods = cursor.fetchall()
        return render_template('products.html', prods=prods)

    except mysql.connector.Error as err:
        app.logger.error(f"Błąd bazy danych podczas pobierania produktów: {err}", exc_info=True)
        flash(f'Wystąpił błąd podczas pobierania produktów: {err}', 'danger')
        return render_template('products.html', prods=[])
    except Exception as e:
        app.logger.error(f"Nieoczekiwany błąd podczas pobierania produktów: {e}", exc_info=True)
        flash(f'Wystąpił nieoczekiwany błąd: {e}', 'danger')
        return render_template('products.html', prods=[])
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/receives')
@login_required
def receives():
    conn = db_connect()
    if not conn:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:

        cursor.execute("SELECT id, username, receives_date FROM receives ORDER BY receives_date DESC")
        rec_items = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Błąd bazy danych: {err}", 'danger')
        rec_items = []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return render_template('receives.html', rec_items=rec_items)

@app.route('/shipments')
@login_required
def shipments():
    conn = db_connect()
    if not conn:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, shipment_date FROM shipments ORDER BY shipment_date DESC")
        ship_items = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Błąd bazy danych: {err}", 'danger')
        ship_items = []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return render_template('shipments.html', ship_items=ship_items)

@app.route('/add_prod', methods=['GET','POST'])
@login_required
@admin_required
def add_prod():
    form = AddProdForm() 

    if form.validate_on_submit():
        name = form.name.data
        sku = form.sku.data.upper().strip() 
        description = form.description.data

        conn = db_connect()
        if conn is None:
            flash('Błąd połączenia z bazą danych. Spróbuj ponownie.', 'danger')
            return render_template('add_prod.html', form=form)

        cursor = conn.cursor()

        try:

            cursor.execute("SELECT id FROM products WHERE sku = %s", (sku,))
            existing_product = cursor.fetchone()

            if existing_product:
                flash(f'Produkt o SKU "{sku}" już istnieje w katalogu. Nie dodano nowego rekordu.', 'info')
                return redirect(url_for('products')) 
            else:

                cursor.execute("INSERT INTO products (name, sku, description) VALUES (%s, %s, %s)",
                               (name, sku, description))
                conn.commit() 
                product_id = cursor.lastrowid

                if product_id is None:
                    flash('Nie udało się dodać produktu. Wystąpił błąd w bazie danych.', 'danger')
                    return render_template('add_prod.html', form=form)

                flash('Produkt został pomyślnie dodany do katalogu produktów!', 'success')
                return redirect(url_for('products'))

        except mysql.connector.Error as err:
            conn.rollback()
            app.logger.error(f"Błąd bazy danych podczas dodawania produktu: {err}", exc_info=True)
            flash(f'Wystąpił błąd podczas dodawania produktu: {err}. Spróbuj ponownie.', 'danger')
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Nieoczekiwany błąd podczas dodawania produktu: {e}", exc_info=True)
            flash('Wystąpił nieoczekiwany błąd. Spróbuj ponownie.', 'danger')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('add_prod.html', form=form)


@app.route('/shipments_detail/<int:id>', methods=['GET'])
@login_required
def shipments_detail(id):
    conn = db_connect()
    if not conn:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:

        cursor.execute("SELECT id, username, shipment_date FROM shipments WHERE id = %s", (id,))
        shipment_info = cursor.fetchone()

        if not shipment_info:
            flash('Wysyłka o podanym ID nie została znaleziona.', 'warning')
            return redirect(url_for('shipments'))

        shipment_id = shipment_info['id']

        query = """
            SELECT
                sp.quantity AS shipped_quantity,
                p.name AS product_name,
                p.sku,
                p.description,
                l.code as location_code
            FROM
                shipment_products sp
            JOIN
                products p ON sp.product_id = p.id
            JOIN
                locations l ON sp.location_id = l.id
            WHERE
                sp.shipment_id = %s;
        """
        cursor.execute(query, (shipment_id,))
        shipment_products = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Błąd bazy danych: {err}", 'danger')
        print(f"BŁĄD BAZY DANYCH w shipments_detail: {err}", file=sys.stderr, flush=True)
        shipment_products = []
    except Exception as e:
        flash(f"Wystąpił nieoczekiwany błąd: {e}", 'danger')
        print(f"BŁĄD NIEOCZEKIWANY w shipments_detail: {e}", file=sys.stderr, flush=True)
        shipment_products = []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('shipments_detail.html', shipment_products=shipment_products, shipment_id=id, shipment_info=shipment_info)

@app.route('/receives_detail/<int:id>', methods=['GET'])
@login_required
def receives_detail(id):
    conn = db_connect()
    if not conn:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, receives_date FROM receives WHERE id = %s", (id,))
        receive_info = cursor.fetchone()

        if not receive_info:
            flash('Przyjęcie o podanym ID nie zostało znalezione.', 'warning')
            return redirect(url_for('receives'))

        receive_id = receive_info['id']

        query = """
            SELECT
                rp.quantity AS received_quantity,
                p.name AS product_name,
                p.sku,
                p.description,
                l.code AS location_code
            FROM
                receives_products rp
            JOIN
                products p ON rp.product_id = p.id
            JOIN
                locations l ON rp.location_id = l.id
            WHERE
                rp.receive_id = %s;
        """
        cursor.execute(query, (receive_id,))
        receive_products = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Błąd bazy danych: {err}", 'danger')
        print(f"BŁĄD BAZY DANYCH w receives_detail: {err}", file=sys.stderr, flush=True)
        receive_products = []
    except Exception as e:
        flash(f"Wystąpił nieoczekiwany błąd: {e}", 'danger')
        print(f"BŁĄD NIEOCZEKIWANY w receives_detail: {e}", file=sys.stderr, flush=True)
        receive_products = []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('receives_detail.html', receive_products=receive_products, receive_id=id, receive_info=receive_info)

@app.route('/product_detail/<int:product_id>')
@login_required
def product_detail(product_id):
    """
    Wyświetla szczegóły produktu wraz z historią jego przyjęć i wysyłek.
    """
    conn = db_connect()
    if not conn:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return redirect(url_for('products'))

    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Pobierz podstawowe informacje o produkcie
        cursor.execute("SELECT name, sku FROM products WHERE id = %s", (product_id,))
        product_info = cursor.fetchone()

        if not product_info:
            flash('Produkt o podanym ID nie został znaleziony.', 'warning')
            return redirect(url_for('products'))

        # 2. Zaktualizowane zapytanie SQL - dodano PARTITION BY location_code
        history_query = """
            SELECT
                transaction_id,
                transaction_date,
                transaction_type,
                username,
                location_code,
                quantity_change,
                -- ### ZMIANA TUTAJ: Dodano PARTITION BY location_code ###
                -- Oblicza sumę narastająco, ale robi to OSOBNO dla każdej lokalizacji
                SUM(quantity_change) OVER (PARTITION BY location_code ORDER BY transaction_date, transaction_id) AS stock_after
            FROM (
                -- Pobierz wszystkie przyjęcia dla tego produktu
                (
                    SELECT
                        r.id AS transaction_id,
                        r.receives_date AS transaction_date,
                        'Przyjęcie' AS transaction_type,
                        rp.quantity AS quantity_change,
                        r.username,
                        l.code AS location_code
                    FROM receives_products rp
                    JOIN receives r ON rp.receive_id = r.id
                    JOIN locations l ON rp.location_id = l.id
                    WHERE rp.product_id = %s
                )
                UNION ALL
                -- Pobierz wszystkie wysyłki dla tego produktu
                (
                    SELECT
                        s.id AS transaction_id,
                        s.shipment_date AS transaction_date,
                        'Wysyłka' AS transaction_type,
                        -sp.quantity AS quantity_change,
                        s.username,
                        l.code AS location_code
                    FROM shipment_products sp
                    JOIN shipments s ON sp.shipment_id = s.id
                    JOIN locations l ON sp.location_id = l.id
                    WHERE sp.product_id = %s
                )
            ) AS transactions
            ORDER BY transaction_date, transaction_id;
        """
        cursor.execute(history_query, (product_id, product_id))
        product_history = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Błąd bazy danych: {err}", 'danger')
        product_history = []
        product_info = None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('product_detail.html',
                           product=product_info,
                           history=product_history)

@app.route('/get_product_locations/<sku>', methods=['GET'])
@login_required
def get_product_locations(sku):
    conn = db_connect()
    if conn is None:
        return jsonify({'error': 'Błąd połączenia z bazą danych.'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM products WHERE sku = %s", (sku,))
        product_data = cursor.fetchone()

        if not product_data:
            return jsonify({'locations': []}), 200 

        product_id = product_data['id']

        cursor.execute(
            """
            SELECT l.id AS location_id, l.code AS location_code, i.quantity
            FROM inventory i
            JOIN locations l ON i.location_id = l.id
            WHERE i.product_id = %s AND i.quantity > 0
            ORDER BY l.code;
            """,
            (product_id,)
        )
        inventory_data = cursor.fetchall()

        locations = []
        for item in inventory_data:
            locations.append({
                'id': item['location_id'],
                'code': item['location_code'],
                'quantity': item['quantity']
            })

        return jsonify({'locations': locations}), 200

    except mysql.connector.Error as err:
        app.logger.error(f"Błąd bazy danych podczas pobierania lokalizacji: {err}", exc_info=True)
        return jsonify({'error': f'Błąd bazy danych: {err}'}), 500
    except Exception as e:
        app.logger.error(f"Nieoczekiwany błąd podczas pobierania lokalizacji: {e}", exc_info=True)
        return jsonify({'error': f'Nieoczekiwany błąd: {e}'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/get_all_locations', methods=['GET'])
@login_required
def get_all_locations():
    conn = db_connect()
    if conn is None:
        return jsonify({'error': 'Błąd połączenia z bazą danych.'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, code FROM locations ORDER BY code;")
        locations_data = cursor.fetchall()

        locations = [{'id': item['id'], 'code': item['code']} for item in locations_data]
        return jsonify({'locations': locations}), 200

    except mysql.connector.Error as err:
        app.logger.error(f"Błąd bazy danych podczas pobierania wszystkich lokalizacji: {err}", exc_info=True)
        return jsonify({'error': f'Błąd bazy danych: {err}'}), 500
    except Exception as e:
        app.logger.error(f"Nieoczekiwany błąd podczas pobierania wszystkich lokalizacji: {e}", exc_info=True)
        return jsonify({'error': f'Nieoczekiwany błąd: {e}'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/add_shipment', methods=['GET', 'POST'])
@login_required
def add_shipment():
    form = AddShipmentForm()

    conn = db_connect()
    if conn is None:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return render_template('add_shipment.html', form=form)
    cursor = conn.cursor(dictionary=True)

    for product_entry in form.products.entries:
        product_sku = product_entry.form.product_sku.data
        current_choices = [('', 'Wybierz lokalizację')] 
        if product_sku: 
            try:
                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku.upper().strip(),))
                product_data = cursor.fetchone()
                if product_data:
                    product_id = product_data['id']
                    cursor.execute(
                        """
                        SELECT l.id AS location_id, l.code AS location_code, i.quantity
                        FROM inventory i
                        JOIN locations l ON i.location_id = l.id
                        WHERE i.product_id = %s AND i.quantity > 0
                        ORDER BY l.code;
                        """,
                        (product_id,)
                    )
                    inventory_data = cursor.fetchall()
                    for item in inventory_data:
                        current_choices.append((str(item['location_id']), f"{item['location_code']} (Ilość: {item['quantity']})"))
            except mysql.connector.Error as err:
                app.logger.error(f"Błąd bazy danych podczas ładowania choices dla SKU {product_sku}: {err}", exc_info=True)
            except Exception as e:
                app.logger.error(f"Nieoczekiwany błąd podczas ładowania choices dla SKU {product_sku}: {e}", exc_info=True)
        product_entry.form.location_id.choices = current_choices
    
    if form.validate_on_submit():
        username = current_user.username
        shipment_id = None  

        try:

            cursor.execute("INSERT INTO shipments (username) VALUES (%s)", (username,))
            shipment_id = cursor.lastrowid

            if shipment_id is None:
                raise Exception("Nie udało się utworzyć nowego rekordu wysyłki.")


            location_quantities = {}

            for index, product_entry in enumerate(form.products.entries):
                product_sku = product_entry.form.product_sku.data.upper().strip()
                quantity_to_ship = product_entry.form.quantity.data
                selected_location_id = int(product_entry.form.location_id.data)

                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku,))
                product_data = cursor.fetchone()
                if not product_data:
                    raise Exception(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}"): Produkt nie istnieje w katalogu. Dodaj go najpierw.')
                product_id = product_data['id']

                cursor.execute(
                    "SELECT COALESCE(quantity, 0) AS available FROM inventory WHERE product_id = %s AND location_id = %s",
                    (product_id, selected_location_id)
                )
                available_row = cursor.fetchone()
                current_quantity_in_location = available_row['available'] if available_row else 0
                

                already_picked_quantity = location_quantities.get((product_id, selected_location_id), 0)
                effective_quantity = current_quantity_in_location - already_picked_quantity

                if quantity_to_ship > effective_quantity:
                    cursor.execute("SELECT code FROM locations WHERE id = %s", (selected_location_id,))
                    location_code_str = cursor.fetchone()['code']
                    raise Exception(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}", Lokalizacja: {location_code_str}): Za mało produktu. Dostępne: {effective_quantity}, wymagane: {quantity_to_ship}.')
                

                location_quantities[(product_id, selected_location_id)] = already_picked_quantity + quantity_to_ship
                

                cursor.execute(
                    "INSERT INTO shipment_products (shipment_id, product_id, location_id, quantity) VALUES (%s, %s, %s, %s)",
                    (shipment_id, product_id, selected_location_id, quantity_to_ship)
                )


                new_quantity = current_quantity_in_location - quantity_to_ship
                cursor.execute(
                    "UPDATE inventory SET quantity = %s WHERE product_id = %s AND location_id = %s",
                    (new_quantity, product_id, selected_location_id)
                )


            conn.commit()
            flash(f'Nowa wysyłka nr {shipment_id} została pomyślnie utworzona!', 'success')
            return redirect(url_for('shipments_detail', id=shipment_id))

        except Exception as e:

            conn.rollback()
            app.logger.error(f"Błąd podczas dodawania wysyłki: {e}", exc_info=True)
            flash(f'Wystąpił błąd podczas dodawania wysyłki: {e}', 'danger')
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    return render_template('add_shipment.html', form=form)

@app.route('/add_receive', methods=['GET', 'POST'])
@login_required
def add_receive():
    form = AddReceiveForm()

    conn = db_connect()
    if conn is None:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return render_template('add_receive.html', form=form)

    cursor = conn.cursor(dictionary=True)
    all_location_choices = []
    try:
        cursor.execute("SELECT id, code FROM locations ORDER BY code;")
        all_locations_data = cursor.fetchall()
        all_location_choices = [(str(loc['id']), loc['code']) for loc in all_locations_data]
    except Exception as e:
        app.logger.error(f"Błąd podczas pobierania listy lokalizacji: {e}", exc_info=True)
        flash("Wystąpił błąd podczas ładowania listy lokalizacji.", "danger")
    finally:
        if conn and conn.is_connected():
            cursor.close()


    for product_entry in form.products.entries:
        product_entry.form.location_id.choices = [('', 'Wybierz lokalizację')] + all_location_choices

    if form.validate_on_submit():
        username = current_user.username
        

        if not conn or not conn.is_connected():
             conn = db_connect()
        
        if conn is None:
            flash('Błąd połączenia z bazą danych.', 'danger')
            return render_template('add_receive.html', form=form)
            
        cursor = conn.cursor(dictionary=True)
        receive_id = None
        try:
            cursor.execute("INSERT INTO receives (username) VALUES (%s)", (username,))
            receive_id = cursor.lastrowid

            if receive_id is None:
                raise Exception("Nie udało się utworzyć nowego rekordu przyjęcia.")

            for index, product_entry in enumerate(form.products.entries):
                product_sku = product_entry.form.product_sku.data.upper().strip()
                quantity = product_entry.form.quantity.data
                location_id = int(product_entry.form.location_id.data)

                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku,))
                product_data = cursor.fetchone()

                if not product_data:
                    raise Exception(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}"): Produkt nie istnieje w katalogu. Dodaj go najpierw.')
                product_id = product_data['id']

                cursor.execute(
                    "INSERT INTO receives_products (receive_id, product_id, location_id, quantity) VALUES (%s, %s, %s, %s)",
                    (receive_id, product_id, location_id, quantity)
                )

                cursor.execute(
                    "SELECT id, quantity FROM inventory WHERE product_id = %s AND location_id = %s",
                    (product_id, location_id)
                )
                inventory_item = cursor.fetchone()

                if inventory_item:
                    new_total_quantity = inventory_item['quantity'] + quantity
                    cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE id = %s",
                        (new_total_quantity, inventory_item['id'])
                    )
                else:
                    cursor.execute(
                        "INSERT INTO inventory (product_id, location_id, quantity) VALUES (%s, %s, %s)",
                        (product_id, location_id, quantity)
                    )

            conn.commit() 
            flash(f'Nowe przyjęcie nr {receive_id} zostało pomyślnie utworzone!', 'success')
            return redirect(url_for('receives_detail', id=receive_id))

        except Exception as e:
            conn.rollback()
            app.logger.error(f"Błąd podczas dodawania przyjęcia: {e}", exc_info=True)
            flash(f'Wystąpił błąd podczas dodawania przyjęcia: {e}. Spróbuj ponownie.', 'danger')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('add_receive.html', form=form)

if __name__ == "__main__":
    add_admin()
    app.run(host='0.0.0.0', port=5050, debug=True)
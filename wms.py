
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from functools import wraps
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import sys
import os
from source import User, LoginForm, RegisterForm, AddProdForm, AddShipmentForm, AddReceiveForm, ReceiveProductForm

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('API_KEY')

#flask login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#database connection
def db_connect():
    # Upewnij się, że masz dictionary=True w kursorze, jeśli używasz go do pobierania nazw kolumn
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
            flash('Zalogowano pomyślnie!','success') # Zmieniono tekst wiadomości
            return redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowe dane logowania', 'danger') # Zmieniono tekst wiadomości
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
                flash('Nazwa użytkownika już istnieje, wybierz inną.', 'error') # Zmieniono tekst wiadomości
                return redirect(url_for('register'))

            cursor.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
            existing_email = cursor.fetchone()

            if existing_email:
                flash('Adres e-mail jest już zarejestrowany.', 'error') # Zmieniono tekst wiadomości
                return redirect(url_for('register'))

            cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)", (form.username.data, hashed_password, form.email.data))
            conn.commit()

            flash('Rejestracja zakończona pomyślnie!', 'success') # Zmieniono tekst wiadomości
            return redirect(url_for('login'))

        except Exception as e:
            print(str(e))
            flash('Wystąpił błąd podczas rejestracji. Spróbuj ponownie.', 'error') # Zmieniono tekst wiadomości

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

# wms.py

@app.route('/products', methods=['GET'])
@login_required
def products():
    conn=db_connect()
    cursor=conn.cursor(dictionary=True)
    
    query="""
            SELECT
                p.id AS product_id,
                p.name AS product_name,
                p.sku,
                p.description,
                COALESCE(SUM(i.quantity), 0) AS total_quantity, -- Suma ilości dla danego produktu, 0 jeśli brak wpisów w inventory
                GROUP_CONCAT(DISTINCT l.code ORDER BY l.code SEPARATOR ', ') AS locations_summary -- Zsumowanie unikalnych lokalizacji
            FROM
                products p
            LEFT JOIN -- Używamy LEFT JOIN, aby pokazać wszystkie produkty, nawet te bez wpisów w inventory
                inventory i ON p.id = i.product_id
            LEFT JOIN -- Łączymy z lokalizacjami
                locations l ON i.location_id = l.id
            GROUP BY
                p.id, p.name, p.sku, p.description
            ORDER BY
                p.name;
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

# Ten blok starego kodu dla add_prod jest zakomentowany
# @app.route('/add_prod', methods=['GET','POST'])
# @login_required
# @admin_required
# def add_prod():
#     form = AddProdForm()
#     # ... stary kod ...

# Nowa, uproszczona funkcja add_prod - tylko dodaje do tabeli products
@app.route('/add_prod', methods=['GET','POST'])
@login_required
@admin_required
def add_prod():
    form = AddProdForm() # Ten formularz już nie ma pól location i quantity

    if form.validate_on_submit():
        name = form.name.data
        sku = form.sku.data.upper().strip() # Dodano upper() i strip() dla SKU
        description = form.description.data

        conn = db_connect()
        if conn is None:
            flash('Błąd połączenia z bazą danych. Spróbuj ponownie.', 'danger')
            return render_template('add_prod.html', form=form)

        cursor = conn.cursor()

        try:
            # Sprawdzamy, czy produkt o danym SKU już istnieje
            cursor.execute("SELECT id FROM products WHERE sku = %s", (sku,))
            existing_product = cursor.fetchone()

            if existing_product:
                flash(f'Produkt o SKU "{sku}" już istnieje w katalogu. Nie dodano nowego rekordu.', 'info')
                return redirect(url_for('products')) # Przekieruj, bo nie ma nic więcej do dodania
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
                l.code AS location_code -- Dodano kod lokalizacji
            FROM
                receives_products rp
            JOIN
                products p ON rp.product_id = p.id
            JOIN
                receives r ON rp.receives_id = r.id
            JOIN
                inventory i ON p.id = i.product_id AND r.username = (SELECT username FROM users WHERE id = %s) # To jest nieprawidłowe powiązanie
            JOIN
                locations l ON i.location_id = l.id
            WHERE
                rp.receives_id = %s;
        """
        # Poprawka query dla receives_detail: Pobieranie lokalizacji dla każdego produktu
        # Musimy założyć, że jeśli produkt był częścią przyjęcia, to jego lokalizacja jest określona w inventory
        # Ale nie ma bezpośredniego linku z receives_products do location_id
        # Jeśli przyjęcie miało wiele produktów do różnych lokalizacji, to w Receives_detail ciężko pokazać jedną lokalizację przyjęcia
        # Zmienimy receives_detail tak, aby pokazywał lokalizacje z inventory, ale dla każdego wiersza produktu.
        # To wymaga bardziej złożonego zapytania lub dodania location_id do receives_products.
        # Na razie zostawmy proste zapytanie, które działa z obecną strukturą bazy, ale bez konkretnej lokalizacji z receive_products.

        # Nowe query dla receives_detail:
        query = """
            SELECT
                rp.quantity AS received_quantity,
                p.name AS product_name,
                p.sku,
                p.description
            FROM
                receives_products rp
            JOIN
                products p ON rp.product_id = p.id
            WHERE
                rp.receives_id = %s;
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


@app.route('/get_product_locations/<sku>', methods=['GET'])
@login_required
def get_product_locations(sku):
    conn = db_connect()
    if conn is None:
        return jsonify({'error': 'Błąd połączenia z bazą danych.'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Pobierz product_id dla danego SKU
        cursor.execute("SELECT id FROM products WHERE sku = %s", (sku,))
        product_data = cursor.fetchone()

        if not product_data:
            return jsonify({'locations': []}), 200 # Zwróć pustą listę, jeśli SKU nie istnieje

        product_id = product_data['id']

        # Pobierz wszystkie lokalizacje i ich ilości dla danego product_id
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

        # Przygotuj dane do JSON
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

@app.route('/add_shipment', methods=['GET', 'POST'])
@login_required
@admin_required
def add_shipment():
    form = AddShipmentForm()

    conn = db_connect()
    if conn is None:
        flash('Błąd połączenia z bazą danych.', 'danger')
        return render_template('add_shipment.html', form=form)
    cursor = conn.cursor(dictionary=True)

    # KLUCZOWA ZMIANA: Dynamiczne wypełnianie choices dla location_id
    # Dzieje się to PRZED form.validate_on_submit() dla POST
    # i PRZED render_template dla GET, aby Flask-WTF miał poprawne opcje do walidacji.
    for product_entry_index, product_entry in enumerate(form.products.entries):
        # Pobierz SKU z inputu. Jeśli to GET, to będzie puste/domyślne.
        # Jeśli to POST, to będzie wartość wpisana przez użytkownika.
        product_sku = product_entry.form.product_sku.data

        current_choices = [('', 'Wybierz lokalizację')] # Domyślna opcja

        if product_sku: # Jeśli SKU zostało podane (czyli np. nie jest to początkowe ładowanie pustego formularza)
            try:
                # Pobierz product_id dla danego SKU
                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku.upper().strip(),))
                product_data = cursor.fetchone()

                if product_data:
                    product_id = product_data['id']
                    # Pobierz wszystkie lokalizacje i ich ilości dla danego product_id
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
                # Możesz dodać flash tutaj, jeśli chcesz poinformować o błędzie ładowania opcji
            except Exception as e:
                app.logger.error(f"Nieoczekiwany błąd podczas ładowania choices dla SKU {product_sku}: {e}", exc_info=True)
        
        # Ustaw dynamiczne opcje dla SelectField
        product_entry.form.location_id.choices = current_choices
    
    # --- KONIEC DYNAMICZNEGO WYPEŁNIANIA CHOICES ---

    if form.validate_on_submit(): # Teraz walidacja będzie mieć prawidłowe opcje
        username = current_user.username
        
        # ... (reszta logiki add_shipment - jest już prawie poprawna) ...
        # Upewnij się, że używasz product_sku.upper().strip() tak jak w sekcji ładowania choices
        # oraz że walidacja selected_location_id i available_in_location_row jest poprawna.
        # Moje ostatnie zmiany w add_shipment w poprzedniej odpowiedzi były już dość dobre,
        # ale upewnij się, że nie ma tam żadnych duplikacji logicznych czy błędów.

        try:
            # ... (Tworzenie shipments, shipment_id - bez zmian) ...
            cursor.execute("INSERT INTO shipments (username) VALUES (%s)", (username,))
            conn.commit()
            shipment_id = cursor.lastrowid

            if shipment_id is None:
                raise Exception("Nie udało się utworzyć nowego rekordu wysyłki.")

            flash(f'Nowa wysyłka nr {shipment_id} została pomyślnie utworzona!', 'success')

            for index, product_entry in enumerate(form.products.entries):
                product_sku = product_entry.form.product_sku.data.upper().strip() # Upewnij się, że jest .upper().strip()
                quantity_to_ship = product_entry.form.quantity.data
                selected_location_id = product_entry.form.location_id.data

                # --- WALIDACJA 1: SPRAWDŹ ISTNIENIE PRODUKTU W KATALOGU ---
                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku,))
                product_data = cursor.fetchone()

                if not product_data:
                    conn.rollback()
                    flash(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}"): Produkt nie istnieje w katalogu. Dodaj go najpierw.', 'danger')
                    return render_template('add_shipment.html', form=form)

                product_id = product_data['id']

                # --- WALIDACJA 2: SPRAWDŹ ISTNIENIE LOKALIZACJI ---
                # location_id jest teraz wymagane przez DataRequired() w FlaskForm
                # Jeśli jednak z jakiegoś powodu jest puste, to już Flask-WTF powinien to złapać
                # ale dla pewności możesz zostawić tę walidację na wszelki wypadek.
                if not selected_location_id:
                     conn.rollback()
                     flash(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}"): Nie wybrano lokalizacji do wysyłki. (Błąd walidacji SelectField)', 'danger')
                     return render_template('add_shipment.html', form=form)


                # --- WALIDACJA 3: SPRAWDŹ DOSTĘPNĄ ILOŚĆ W WYBRANEJ LOKALIZACJI ---
                cursor.execute(
                    "SELECT COALESCE(quantity, 0) AS available_in_location FROM inventory WHERE product_id = %s AND location_id = %s",
                    (product_id, selected_location_id)
                )
                available_in_location_row = cursor.fetchone()
                current_quantity_in_location = available_in_location_row['available_in_location'] if available_in_location_row else 0

                if quantity_to_ship > current_quantity_in_location:
                    conn.rollback()
                    cursor.execute("SELECT code FROM locations WHERE id = %s", (selected_location_id,))
                    location_code = cursor.fetchone()
                    location_code_str = location_code['code'] if location_code else 'nieznana lokalizacja'
                    flash(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}", Lokalizacja: {location_code_str}): Za mało produktu w wybranej lokalizacji. Dostępne: {current_quantity_in_location}, wymagane: {quantity_to_ship}.', 'danger')
                    return render_template('add_shipment.html', form=form)

                # --- ZAPIS DO shipment_products ---
                cursor.execute(
                    "INSERT INTO shipment_products (shipment_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (shipment_id, product_id, quantity_to_ship)
                )

                # --- LOGIKA ZMNIEJSZANIA ILOŚCI W WYBRANEJ LOKALIZACJI ---
                new_quantity = current_quantity_in_location - quantity_to_ship
                cursor.execute(
                    "UPDATE inventory SET quantity = %s WHERE product_id = %s AND location_id = %s",
                    (new_quantity, product_id, selected_location_id)
                )
                flash(f'Zaktualizowano inwentarz dla "{product_sku}" w wybranej lokalizacji (zmniejszono o {quantity_to_ship}).', 'info')
            
            conn.commit()

            flash(f'Wszystkie produkty wysyłki {shipment_id} zostały pomyślnie przetworzone i usunięte z inwentarza!', 'success')
            return redirect(url_for('shipments_detail', id=shipment_id))

        except mysql.connector.Error as err:
            conn.rollback()
            app.logger.error(f"Błąd bazy danych podczas dodawania wysyłki: {err}", exc_info=True)
            flash(f'Wystąpił błąd podczas dodawania wysyłki: {err}. Spróbuj ponownie.', 'danger')
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Nieoczekiwany błąd podczas dodawania wysyłki: {e}", exc_info=True)
            flash(f'Wystąpił nieoczekiwany błąd: {e}. Spróbuj ponownie.', 'danger')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    # Jeśli formularz nie został zwalidowany (GET request lub błędy walidacji WTForms)
    # W tym przypadku form.products.entries już mają ustawione choices na podstawie powyższej logiki
    return render_template('add_shipment.html', form=form)

@app.route('/add_receive', methods=['GET', 'POST'])
@login_required
@admin_required
def add_receive():
    form = AddReceiveForm() # Ten formularz zawiera location_code i dynamiczną listę produktów

    if form.validate_on_submit():
        username = current_user.username
        # barcode = form.barcode.data # Usunięte - nie ma już pola barcode w tym formularzu

        conn = db_connect()
        if conn is None:
            flash('Błąd połączenia z bazą danych.', 'danger')
            return render_template('add_receive.html', form=form)

        cursor = conn.cursor(dictionary=True) # Używamy dictionary=True, aby łatwiej odwoływać się do kolumn po nazwie
        try:
            # 1. Utwórz nowe przyjęcie w tabeli 'receives'
            cursor.execute("INSERT INTO receives (username) VALUES (%s)", (username,))
            conn.commit()
            receive_id = cursor.lastrowid

            if receive_id is None:
                raise Exception("Nie udało się utworzyć nowego rekordu przyjęcia.")

            flash(f'Nowe przyjęcie nr {receive_id} zostało pomyślnie utworzone!', 'success')

            # 2. Przetwarzaj każdy produkt w przyjęciu
            for index, product_entry in enumerate(form.products.entries):
                product_sku = product_entry.form.product_sku.data.upper().strip()
                quantity = product_entry.form.quantity.data
                location_code = product_entry.form.location.data.upper().strip() # Lokalizacja dla konkretnego produktu

                # Sprawdź, czy produkt o danym SKU istnieje w katalogu
                cursor.execute("SELECT id FROM products WHERE sku = %s", (product_sku,))
                product_data = cursor.fetchone()

                if not product_data:
                    conn.rollback() # Wycofaj całą transakcję, jeśli któryś produkt nie istnieje
                    flash(f'Błąd dla produktu #{index+1} (SKU: "{product_sku}"): Produkt nie istnieje w katalogu. Dodaj go najpierw.', 'danger')
                    return render_template('add_receive.html', form=form)

                product_id = product_data['id'] # Używamy 'id' bo kursor jest dictionary

                # Sprawdź/utwórz lokalizację dla tego produktu
                cursor.execute("SELECT id FROM locations WHERE code = %s", (location_code,))
                location_data = cursor.fetchone()
                location_id = None

                if location_data:
                    location_id = location_data['id']
                else:
                    cursor.execute("INSERT INTO locations (code) VALUES (%s)", (location_code,))
                    conn.commit() # Commit, aby ID było dostępne
                    location_id = cursor.lastrowid
                    if location_id is None:
                        raise Exception(f"Nie udało się utworzyć nowej lokalizacji: {location_code}.")


                # Dodaj do receives_products (szczegóły przyjęcia)
                cursor.execute(
                    "INSERT INTO receives_products (receives_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (receive_id, product_id, quantity)
                )

                # Aktualizuj lub dodaj do inventory
                cursor.execute(
                    "SELECT id, quantity FROM inventory WHERE product_id = %s AND location_id = %s",
                    (product_id, location_id)
                )
                inventory_item = cursor.fetchone()

                if inventory_item:
                    # Produkt już istnieje w tej lokalizacji, zaktualizuj ilość
                    new_total_quantity = inventory_item['quantity'] + quantity
                    cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE id = %s",
                        (new_total_quantity, inventory_item['id'])
                    )
                    flash(f'Zaktualizowano ilość dla "{product_sku}" w "{location_code}" (nowa ilość: {new_total_quantity}).', 'info')
                else:
                    # Produkt nie istnieje w tej lokalizacji, dodaj nowy wpis
                    cursor.execute(
                        "INSERT INTO inventory (product_id, location_id, quantity) VALUES (%s, %s, %s)",
                        (product_id, location_id, quantity)
                    )
                    flash(f'Dodano "{product_sku}" do inwentarza w lokalizacji "{location_code}" (ilość: {quantity}).', 'info')

            conn.commit() # Zatwierdź wszystkie zmiany po pętli produktów

            flash('Wszystkie produkty przyjęcia zostały pomyślnie przetworzone i dodane/zaktualizowane w inwentarzu!', 'success')
            return redirect(url_for('receives_detail', id=receive_id))

        except mysql.connector.Error as err:
            conn.rollback()
            app.logger.error(f"Błąd bazy danych podczas dodawania przyjęcia: {err}", exc_info=True)
            flash(f'Wystąpił błąd podczas dodawania przyjęcia: {err}. Spróbuj ponownie.', 'danger')
        except Exception as e:
            conn.rollback()
            app.logger.error(f"Nieoczekiwany błąd podczas dodawania przyjęcia: {e}", exc_info=True)
            flash(f'Wystąpił nieoczekiwany błąd: {e}. Spróbuj ponownie.', 'danger')
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('add_receive.html', form=form)


if __name__ == "__main__":
    add_admin()
    app.run(host='0.0.0.0', port=5050, debug=True)
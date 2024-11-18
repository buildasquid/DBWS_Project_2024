from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from flask_cors import CORS
import requests

app = Flask(__name__, template_folder='templates')  
app.secret_key = 'your_secret_key'  

CORS(app)


import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/get_location', methods=['GET'])
def get_location():
    # Get the IP address of the user from the request headers
    user_ip = request.remote_addr  # This gives the IP of the client making the request

    # If running behind a proxy or in development, you might want to get the real IP like this:
    # user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Send the request to ipinfo.io to get location info
    ipinfo_url = f'https://ipinfo.io/{user_ip}/json?token=0f9e41f0e05613'
    response = requests.get(ipinfo_url)

    if response.status_code == 200:
        data = response.json()
        # Send location data to frontend
        return jsonify(data)
    else:
        return jsonify({'error': 'Unable to fetch location data'}), 500

if __name__ == '__main__':
    app.run(debug=True)


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  
        user='sdaria', 
        password='SHCfcZ',  
        database='sdaria_db'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/imprint')
def imprint():
    return render_template('imprint.html')

@app.route('/management')
def management():
    if 'username' not in session:
        flash("Log in to access this page.", "error")
        return redirect(url_for('login'))
    return render_template('management.html')

def check_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM Users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and result[0] == password:
        return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('username', None)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('management'))
        else:
            flash("Invalid username or password! Please try again.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@app.route('/customer_input', methods=['GET', 'POST'])
def customer_input():
    if request.method == 'POST':
        customer_name = request.form['customerName']
        
        customer_email = request.form['customerEmail']
        customer_phone = request.form['customerPhone']
        customer_address = request.form['customerAddress']
        customer_type = request.form['customerType']  

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # insert into customer table
            cursor.execute(
                "INSERT INTO Customer (Name, Email, Phone, Address) VALUES (%s, %s, %s, %s)",
                (customer_name, customer_email, customer_phone, customer_address)
            )
            conn.commit()
            customer_id = cursor.lastrowid

            # insert into the right type table
            if customer_type == 'Regular':
                cursor.execute("INSERT INTO RegularCustomer (CustomerID) VALUES (%s)", (customer_id,))
            elif customer_type == 'Premium':
                
                premium_fee = 29.99  
                cursor.execute("INSERT INTO PremiumCustomer (CustomerID, PremiumFee) VALUES (%s, %s)", (customer_id, premium_fee))
            elif customer_type == 'VIP':
                vip_fee = 49.99
                cursor.execute("INSERT INTO VIPCustomer (CustomerID, VIPFee) VALUES (%s, %s)", (customer_id,vip_fee))

            conn.commit()
            flash("Customer added successfully!", "success")
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('customer_feedback'))

    return render_template('customer_input.html')




@app.route('/vinyl_input', methods=['GET', 'POST'])
def vinyl_input():
    if request.method == 'POST':
        vinyl_name = request.form['vinylTitle']
        vinyl_artist = request.form['vinylArtist']
        release_date = request.form['releaseDate']  
        genre = request.form['genre']                
        vinyl_type = request.form['vinylType']
        vinyl_price = request.form['vinylPrice']
        number_of_tracks = request.form['numberOfTracks']
        duration = request.form['duration']

       
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # insert into the vinyl table
            cursor.execute(
                "INSERT INTO Vinyl (Name, Artist, ReleaseDate, Price, Genre) VALUES (%s, %s, %s, %s, %s)",
                (vinyl_name, vinyl_artist, release_date, vinyl_price, genre)
            )
            conn.commit()
            vinyl_id = cursor.lastrowid

            
            if vinyl_type == 'Single':
                cursor.execute(
                    "INSERT INTO Single (VinylID, NumberOfTracks, Duration) VALUES (%s, %s, %s)",
                    (vinyl_id, number_of_tracks, duration)
                )
            elif vinyl_type == 'EP':
                cursor.execute(
                    "INSERT INTO EP (VinylID, NumberOfTracks, Duration) VALUES (%s, %s, %s)",
                    (vinyl_id, number_of_tracks, duration)
                )
            elif vinyl_type == 'LP':
                cursor.execute(
                    "INSERT INTO LP (VinylID, NumberOfTracks, Duration) VALUES (%s, %s, %s)",
                    (vinyl_id, number_of_tracks, duration)
                )

            conn.commit()
            flash("Vinyl added successfully!", "success")
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('vinyl_feedback'))

    return render_template('vinyl_input.html')


from decimal import Decimal

@app.route('/payment_input', methods=['GET', 'POST'])
def payment_input():

    if request.method == 'POST':
        customer_id = request.form['customer']
        payment_for = request.form['paymentFor']
        vinyl_id = request.form.get('vinyl')  # vinyl id if its a vinyl purchase
        discount_id = request.form.get('discount') 

        #init final amount
        final_amount = Decimal('0.00') 

      
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # check if customer is regualr premium or vi
        cursor.execute("SELECT * FROM RegularCustomer WHERE CustomerID = %s", (customer_id,))
        regular_customer = cursor.fetchone()
        
        if regular_customer:
            flash("This customer is a Regular customer. Please change the customer.", "warning")
            cursor.close()
            conn.close()
            return redirect(url_for('payment_input'))  # redirect to the form

        # check if customer is premium or vip
        cursor.execute("SELECT * FROM PremiumCustomer WHERE CustomerID = %s", (customer_id,))
        premium_customer = cursor.fetchone()
        
        if premium_customer:
            cursor.execute("SELECT Cost FROM Fee WHERE FeeType = 'Premium'")
            membership_fee = cursor.fetchone()
            if membership_fee:
                final_amount = Decimal(membership_fee[0]) 

        else:
            cursor.execute("SELECT * FROM VIPCustomer WHERE CustomerID = %s", (customer_id,))
            vip_customer = cursor.fetchone()
            if vip_customer:
                cursor.execute("SELECT Cost FROM Fee WHERE FeeType = 'VIP'")
                membership_fee = cursor.fetchone()
                if membership_fee:
                    final_amount = Decimal(membership_fee[0]) 

        cursor.close()
        conn.close()

        # insert data into payments table
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # vinyl id and discount id are NULL if payment is for membership fee
            cursor.execute(
                "INSERT INTO Payments (CustomerID, Amount, PaymentFor, DiscountID, DiscountApplied, FinalAmount, VinylID) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (customer_id, float(final_amount), payment_for, None if payment_for == 'Membership Fee' else discount_id, float(0), float(final_amount), None if payment_for == 'Membership Fee' else vinyl_id)  # Set VinylID and DiscountID to NULL for Membership Fee
            )
            conn.commit()
            flash("Payment recorded successfully!", "success")
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "error")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('payment_feedback'))

    # customer and vinyl data for dropdowns
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CustomerID, Name FROM Customer")
    customers = cursor.fetchall()
    cursor.execute("SELECT VinylID, Name FROM Vinyl")
    vinyls = cursor.fetchall()
    cursor.execute("SELECT DiscountID, DiscountPercentage, CustomerType FROM Discounts")
    discounts = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('payment_input.html', customers=customers, vinyls=vinyls, discounts=discounts)

@app.route('/catalogue', methods=['GET'])
@app.route('/catalogue/<int:page>', methods=['GET'])
def catalogue(page=1):
    vinyls_per_page = 5
    offset = (page - 1) * vinyls_per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    search_query = request.args.get('search', '')
    genre_filter = request.args.get('genre', '')
    artist_filter = request.args.get('artist', '')

    # query to retrieve all genres for the dropdown
    cursor.execute("SELECT DISTINCT Genre FROM Vinyl")
    genres = [row[0] for row in cursor.fetchall()]

    # build SQL query based on filters
    sql_query = "SELECT VinylID, Name, Artist, Genre, Price FROM Vinyl WHERE 1=1"
    query_params = []

    if search_query:
        sql_query += " AND Name LIKE %s"
        query_params.append(f"%{search_query}%")
    if genre_filter:
        sql_query += " AND Genre = %s"
        query_params.append(genre_filter)
    if artist_filter:
        sql_query += " AND Artist LIKE %s"
        query_params.append(f"%{artist_filter}%")

    sql_query += " LIMIT %s OFFSET %s"
    query_params.append(vinyls_per_page)
    query_params.append(offset)

    cursor.execute(sql_query, query_params)
    vinyls = cursor.fetchall()

    # count how many vinyls we have in total for pagination
    cursor.execute("SELECT COUNT(*) FROM Vinyl WHERE 1=1")
    total_vinyls = cursor.fetchone()[0]
    total_pages = (total_vinyls // vinyls_per_page) + (1 if total_vinyls % vinyls_per_page > 0 else 0)

    cursor.close()
    conn.close()

    return render_template('catalogue.html', vinyls=vinyls, page=page, total_pages=total_pages, search_query=search_query, genres=genres)




@app.route('/vinyl/<int:vinyl_id>')
def vinyl_detail(vinyl_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #get vinyl details again from db
    cursor.execute("SELECT VinylID, Name, Artist, Genre, Price FROM Vinyl WHERE VinylID = %s", (vinyl_id,))
    vinyl = cursor.fetchone()
    
    cursor.close()
    conn.close()

    print(f"Vinyl Price: {vinyl[4]}") 

    return render_template('vinyl_detail.html', vinyl=vinyl)


@app.route('/customer_feedback')
def customer_feedback():
    return render_template('customer_feedback.html')

@app.route('/vinyl_feedback')
def vinyl_feedback():
    return render_template('vinyl_feedback.html')

@app.route('/payment_feedback')
def payment_feedback():
    return render_template('payment_feedback.html')


## AUTOCOMPLETE HW9
@app.route('/autocomplete_vinyl', methods=['GET'])
def autocomplete():
    search = request.args.get('term', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    #query string + max ten rows shown + tuple of my search
    cursor.execute("SELECT Name FROM Vinyl WHERE Name LIKE %s LIMIT 10", (f"%{search}%",))
    results = [row[0] for row in cursor.fetchall()] #interact database + return rows
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route('/autocomplete_artist', methods=['GET'])
def autocomplete_artist():
    search = request.args.get('term', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Artist FROM Vinyl WHERE Artist LIKE %s LIMIT 10", (f"%{search}%",))
    results = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8017, debug=True)
    

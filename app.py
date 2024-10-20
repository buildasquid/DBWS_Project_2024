from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__, template_folder='templates')  
app.secret_key = 'your_secret_key'  


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
    return render_template('management.html')

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



@app.route('/customer_feedback')
def customer_feedback():
    return render_template('customer_feedback.html')

@app.route('/vinyl_feedback')
def vinyl_feedback():
    return render_template('vinyl_feedback.html')

@app.route('/payment_feedback')
def payment_feedback():
    return render_template('payment_feedback.html')

if __name__ == '__main__':
    app.run(debug=True)


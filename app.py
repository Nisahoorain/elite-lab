from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import hashlib
from functools import wraps  

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",        
            user="root",             
            password="",          
            database="elitelab"     
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None



def login_required(f):
    @wraps(f)  
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  
            return redirect(url_for('login'))  
        return f(*args, **kwargs)
    return decorated_function

######################################   Route for login ####################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']
        print(email, password)

        try:
            connection = get_db_connection()
            if connection is None:
                flash('Database connection failed. Please contact the administrator.', 'danger')
                return render_template('login.html')

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            print(user)
            if user:
                session['user_id'] = user['id']  
                session['user_email'] = user['email'] 
                session['user_name'] = user['name'] 
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))  
            else:
                flash('Invalid email or password!', 'danger')

        except Error as e:
            print(f"Database Error: {e}")
            flash('An error occurred while trying to log in. Please try again.', 'danger')
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('login.html')

######################################   Route for home page ####################################################
 
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')



@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')



@app.route('/patient')
@login_required
def patient():
    return render_template('patient.html')



@app.route('/addpatient')
@login_required
def add_patient():
    return render_template('addpatient.html')



@app.route('/cancellation')
@login_required
def cancellation():
    return render_template('cancellation.html')



@app.route('/logout')
@login_required
def logout():
   
    session.pop('user_id', None)
    session.pop('user_email', None) 
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

######################################   Route for creating a new user ####################################################
@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'] 
        sex = request.form['sex']
        role = request.form['role']
        date = request.form['date']
        phone_number = request.form['phone_number']

        
        try:
            connection = get_db_connection()
            if connection is None:
                flash('Database connection failed. Please contact the administrator.', 'danger')
                return redirect(url_for('users'))

            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password, sex, role, date, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, password, sex, role, date, phone_number))

            connection.commit()
            flash('User created successfully!', 'success')

        except Error as e:
            print(f"Database Error: {e}")
            flash('An error occurred while creating the user. Please try again.', 'danger')
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        return redirect(url_for('users'))  

    return render_template('users.html')  


if __name__ == '__main__':
    app.run(debug=True)

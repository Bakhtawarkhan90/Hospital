from flask import Flask, request, redirect, url_for, send_from_directory
import mysql.connector
import os
import time

app = Flask(__name__, static_url_path='/static', static_folder='.')

# MySQL Connection Function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "database"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "qwerty"),
        database=os.getenv("MYSQL_DATABASE", "forms")
    )

# Retry logic for MySQL connection
db = None
for i in range(10):  # Attempt connection 10 times max
    try:
        db = get_db_connection()
        print("✅ Database connection successful")
        break
    except mysql.connector.Error as err:
        print(f"⚠️ Error connecting to MySQL (Retry {i+1}/10): {err}")
        time.sleep(5)
else:
    print("❌ Failed to connect to MySQL after multiple retries. Exiting.")
    exit(1)

# Ensure 'appointments' table exists
with db.cursor() as cursor:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        date DATE,
        department VARCHAR(100),
        phone VARCHAR(20),
        message TEXT
    )
    """)
    db.commit()
print("✅ Table 'appointments' checked/created successfully")

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', 'Unknown')  # Avoid KeyError
    email = request.form.get('email', '')
    date = request.form.get('date', None)
    department = request.form.get('select', 'General')  # Provide default value
    phone = request.form.get('phone', '')
    message = request.form.get('message', '')

    try:
        conn = get_db_connection()  # Open new DB connection
        cursor = conn.cursor()
        query = "INSERT INTO appointments (name, email, date, department, phone, message) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (name, email, date, department, phone, message)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()  # Close DB connection after use
        print("✅ Data inserted successfully")
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")

    return redirect(url_for('thank_you'))

@app.route('/thankyou')
def thank_you():
    return send_from_directory(os.getcwd(), 'thankyou.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

import mysql.connector

# MySQL connection settings (XAMPP defaults)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "dentalapp"
}

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20),
            service VARCHAR(100),
            date VARCHAR(20),
            time VARCHAR(20),
            status VARCHAR(20) DEFAULT 'pending',
            user_id INT
        )
    """)

    # users table - now includes role (patient or owner)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(20),
            password VARCHAR(100),
            role VARCHAR(20)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def save_appointment(data, user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO appointments (name, phone, service, date, time, status, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (data["name"], data["phone"], data["service"], data["date"], data["time"], "pending", user_id))

    conn.commit()
    cursor.close()
    conn.close()

def get_all_appointments():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, phone, service, date, time, status FROM appointments")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def update_appointment_status(appointment_id, new_status):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appointments SET status = %s WHERE id = %s
    """, (new_status, appointment_id))

    conn.commit()
    cursor.close()
    conn.close()

def get_appointments_by_user(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone, service, date, time, status
        FROM appointments
        WHERE user_id = %s
    """, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def create_user(name, email, phone, password, role):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, phone, password, role)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, phone, password, role))

    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_email(email):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, phone, password, role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user
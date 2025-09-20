from flask import Flask, request, jsonify, send_file
import sqlite3, random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DB_FILE = "users.db"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "saha.soumit884@gmail.com"
SMTP_PASSWORD = "dfxu tmaa vapg silr"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            name TEXT,
            verified INTEGER DEFAULT 0,
            verification_code TEXT,
            dob TEXT
        )""")
    conn.commit()
    conn.close()

@app.route('/ca-cert')
def get_ca_cert():
    return send_file("localCA.crt", as_attachment=True)

@app.route('/welcome', methods=['GET'])
def welcome():
    return "Welcome to Server"

@app.route('/test_post', methods=['POST'])
def test_post():
    data = request.json  # Get JSON sent in POST body
    # Just echo back the data with a message
    return jsonify({
        "message": "POST received successfully!",
        "your_data": data
    })

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email, password = data['email'], data['password']
    verification_code = str(random.randint(100000, 999999))
    password_hash = generate_password_hash(password)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password_hash, verification_code) VALUES (?, ?, ?)",
                  (email, password_hash, verification_code))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    finally:
        conn.close()

    print(f"Verification code for {email}: {verification_code}")
    # Send verification email
    try:
        import smtplib
        from email.mime.text import MIMEText

        subject = "Your Verification Code for Call & Message"
        body = f"Hello,\n\nYour verification code is: {verification_code}\n\nThank you!"
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, email, msg.as_string())

        print(f"📧 Verification code sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send code to {email}: {e}")
        return jsonify({"error": "Failed to send verification email"}), 500
    
    return jsonify({"message": "User registered. Verification code sent."}), 200

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    email, code = data['email'], data['code']

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT verification_code FROM users WHERE email=?", (email,))
    row = c.fetchone()
    if not row or row[0] != code:
        print(email)
        return jsonify({"error": "Invalid code"}), 400
    c.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Email verified successfully"})

def retrieve_verification_code(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT verification_code FROM users WHERE email=?", (email,))
    row = c.fetchone()
    verification_code = row[0]
    # Send verification email
    try:
        import smtplib
        from email.mime.text import MIMEText

        subject = "Your Verification Code for Call & Message"
        body = f"Hello,\n\nYour verification code is: {verification_code}\n\nThank you!"
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, email, msg.as_string())

        print(f"📧 Verification code sent to {email}")
        return jsonify({"message": f"Verification code sent to {email}"}), 403
    except Exception as e:
        print(f"❌ Failed to send code to {email}: {e}")
        return jsonify({"error": "Failed to send verification email"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password = data['email'], data['password']

    print(email, password)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, email, dob, password_hash, verified, name FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()

    if not row or not check_password_hash(row[3], password):
        return jsonify({"error": "Invalid credentials"}), 400
    if not row[4]:
        verification_data, status_code = retrieve_verification_code(email)
        return verification_data, status_code

    # Build response with user info
    user_data = {
        "id": row[0],
        "email": row[1],
        "dob": row[2],
        "verified": row[4],
        "name": row[5]
    }

    return jsonify(user_data), 200

if __name__ == "__main__":
    init_db()
    # Run Flask with SSL context
    app.run(
        host="0.0.0.0",  # allows access from other devices on local network
        port=5001,
        debug=True,
        ssl_context=('server.crt', 'server.key')
    )
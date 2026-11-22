"""CodeAlpha Cloud Computing - Task 1: Data Redundancy Removal System.
Registration app: only valid, unique data is stored. Duplicates are rejected."""
import hashlib, os, sqlite3
from flask import Flask, request, jsonify, render_template
from rapidfuzz import fuzz
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "data.db")


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            phone TEXT, hash TEXT UNIQUE NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")


def make_hash(name, email, phone):
    key = f"{name.lower()}|{email}|{phone}"
    return hashlib.sha256(key.encode()).hexdigest()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()

    # 1. Validate (reject false / incomplete data)
    if not name or not email:
        return jsonify(ok=False, message="Name and email are required."), 400
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return jsonify(ok=False, message="Invalid email address."), 400
    if phone and not phone.replace("+", "").isdigit():
        return jsonify(ok=False, message="Phone number must contain digits only."), 400

    with db() as c:
        # 2. Duplicate email
        if c.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            return jsonify(ok=False, message="Duplicate email: this email is already registered."), 409
        # 3. Duplicate phone with same/similar name
        if phone:
            for row in c.execute("SELECT name FROM users WHERE phone=?", (phone,)):
                if fuzz.ratio(name.lower(), row["name"].lower()) >= 90:
                    return jsonify(ok=False, message="Duplicate user: same name and phone already registered."), 409
        # 4. Unique and valid: save
        try:
            c.execute("INSERT INTO users(name,email,phone,hash) VALUES(?,?,?,?)",
                      (name, email, phone, make_hash(name, email, phone)))
        except sqlite3.IntegrityError:
            return jsonify(ok=False, message="Duplicate entry: this user already exists."), 409
    return jsonify(ok=True, message="Registered successfully!"), 201


@app.route("/users")
def users():
    with db() as c:
        return jsonify([dict(r) for r in c.execute("SELECT id,name,email,phone FROM users")])


@app.route("/health")
def health():
    return jsonify(ok=True)


init_db()
if __name__ == "__main__":
    app.run(debug=True)

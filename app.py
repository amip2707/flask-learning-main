from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db
from models import User

app = Flask(__name__)
CORS(app)

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# CREATE TABLES
with app.app_context():
    db.create_all()


# ==========================
# PAGE ROUTES
# ==========================

@app.route('/')
def register_page():
    return render_template('register.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/admin')
def admin_page():
    return render_template('admin_dashboard.html')


@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')


# ==========================
# REGISTER API
# ==========================

@app.route('/register', methods=['POST'])
def register():

    reqdata = request.get_json()

    name = reqdata.get("name")
    username = reqdata.get("username")
    email = reqdata.get("email")
    password = reqdata.get("password")
    phone = reqdata.get("phone")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Invalid Name"
        })

    if not username:
        return jsonify({
            "status": "error",
            "message": "Invalid Username"
        })

    if not email:
        return jsonify({
            "status": "error",
            "message": "Invalid Email"
        })

    if not password:
        return jsonify({
            "status": "error",
            "message": "Invalid Password"
        })

    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:
        return jsonify({
            "status": "error",
            "message": "Username already exists"
        })

    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email:
        return jsonify({
            "status": "error",
            "message": "Email already exists"
        })

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        username=username,
        email=email,
        password=hashed_password,
        phone=phone
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Registration Successful"
    })


# ==========================
# LOGIN API
# ==========================

@app.route('/login', methods=['POST'])
def login():

    reqdata = request.get_json()

    username = reqdata.get("username")
    email = reqdata.get("email")
    password = reqdata.get("password")

    user = User.query.filter_by(
        username=username,
        email=email
    ).first()

    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        })

    if not check_password_hash(
        user.password,
        password
    ):
        return jsonify({
            "status": "error",
            "message": "Wrong Password"
        })

    # ADMIN LOGIN
    if user.role == "admin":
        return jsonify({
            "status": "success",
            "message": "Admin Login Success",
            "role": "admin",
            "username": user.username
        })

    # NORMAL USER LOGIN
    return jsonify({
        "status": "success",
        "message": "Login Successful",
        "role": "user",
        "username": user.username
    })


# ==========================
# RESET PASSWORD
# ==========================

@app.route('/reset-password', methods=['POST'])
def reset_password():

    reqdata = request.get_json()

    email = reqdata.get("email")
    password = reqdata.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        })

    hashed_password = generate_password_hash(password)

    user.password = hashed_password

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Password Updated Successfully"
    })


if __name__ == "__main__":
    app.run(debug=True)
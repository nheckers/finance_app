from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

# Secret key for sessions
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-dev-key")

# Use PostgreSQL on Railway, SQLite locally
database_url = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "finance.db").replace("\\", "/"))

# Railway sets DATABASE_URL with "postgres://" but SQLAlchemy needs "postgresql://"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    transactions = db.relationship("Transaction", backref="owner", lazy=True)

# Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page - requires login
@app.route("/")
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    balance = sum(t.amount for t in transactions)
    return render_template("index.html", transactions=transactions, balance=balance)

# Add transaction - requires login
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        description = request.form.get("description")
        amount = float(request.form.get("amount"))
        category = request.form.get("category")

        new_transaction = Transaction(
            description=description,
            amount=amount,
            category=category,
            user_id=current_user.id
        )
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("add_expense.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
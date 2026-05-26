from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database model for transactions
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    transactions = Transaction.query.all()
    balance = sum(t.amount for t in transactions)
    return render_template("index.html", transactions=transactions, balance=balance)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        description = request.form.get("description")
        amount = float(request.form.get("amount"))
        category = request.form.get("category")

        new_transaction = Transaction(
            description=description,
            amount=amount,
            category=category
        )
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("add_expense.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
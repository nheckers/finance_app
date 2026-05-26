from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

## Temporary storage for transactions (we'll add a database later)
transactions = []

@app.route("/")
def index():
    ## Calculate total balance
    balance = sum(t["amount"] for t in transactions)
    return render_template("index.html", transactions=transactions, balance=balance)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        ## Get form data
        description = request.form.get("description")
        amount = float(request.form.get("amount"))
        category = request.form.get("category")
        
        ## Add to transactions list
        transactions.append({
            "description": description,
            "amount": amount,
            "category": category
        })
        
        return redirect(url_for("index"))
    
    return render_template("add_expense.html")

##if __name__ == "__main__":                ##for running on another device on local network 
    ##app.run(debug=True, host="0.0.0.0")

##if __name__ == "__main__":                ##for running on local machine
    ##app.run(debug=True)

import os

if __name__ == "__main__":                  ##for Railway Hosting
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)



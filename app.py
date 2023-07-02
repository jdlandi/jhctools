# -- Import section --
from flask import Flask
from flask import render_template, request, redirect, make_response

from flask_pymongo import PyMongo

import model
import datatypes

# -- INITIALIZE APP --
app = Flask(__name__)

# CONFIGURE MONGO DB
# create the clent
username = "final"
password = "0lMJvxehFwtomiAx"
url = f"mongodb+srv://{username}:{password}@cluster0.vyy7qf1.mongodb.net/"
url2 = url + "HVACdb"

app.config["MONGO_URI"] = url2
db = PyMongo(app).db


# client = MongoClient(url)

# our database manager object
# db = client["final"]

# View Receipt
@app.route('/invoice', defaults={'invoiceid': None})
@app.route('/invoice/', defaults={'invoiceid': None})
@app.route("/invoice/<invoiceid>")
def view_invoice(invoiceid: str):
    if invoiceid == None:
        return "err"
    username = request.cookies.get("username")
    collection = db.invoices
    invoice = collection.find_one({"id": invoiceid})
    if not invoice:
        return "no invoice"
    name = invoice["name"]
    date = invoice["date"]
    transactions = invoice["transactions"]
    total = invoice["total"]

    return render_template("invoice.html", name=name, date=date, transactions=transactions, total=total)


# New/Edit Invoice
@app.route('/edit', defaults={'invoiceid': None})
@app.route('/edit/', defaults={'invoiceid': None})
@app.route("/edit/<invoiceid>")
def edit_invoice(invoiceid: str):
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    verification = datatypes.input_verification(username, password)
    if verification != "OK" or username != "jlandi5":
        #return render_template("login.html", error=verification)
        return "Error: Unaothorized"
    new = False
    if invoiceid == None:
        invoice = datatypes.gen_invoice()
        new = True
    else:
        collection = db.invoices
        invoice = collection.find_one({"id": invoiceid})
        if not invoice:
            return "Error: Invoice Does Not Exist"

    return render_template("addinvoice.html", invoice=invoice, new=new)


# Save/Update Invoice
@app.route('/save-invoice/<invoiceid>', methods=['POST', 'GET'])
def update_invoice(invoiceid: str):
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    verification = datatypes.input_verification(username, password)
    if verification != "OK" or username != "jlandi5":
        #return render_template("login.html", error=verification)
        return "Error: Unaothorized"
    collection = db.invoices
    print(request.form)
    invoice = collection.find_one({"id": invoiceid})
    if not invoice:
        new_amount = float(request.form["new_transaction[amount]"]) * (
            1 if request.form["new_transaction[sign]"] == "+" else -1)
        new_transaction = {
            "name": request.form["new_transaction[name]"],
            "description": request.form["new_transaction[description]"],
            "date": request.form["new_transaction[date]"],
            "amount": new_amount
        }
        new_invoice = {
            "id": invoiceid,
            "name": request.form["invoice_name"],
            "date": datatypes.get_date(),
            "transactions": [new_transaction],
            "total": new_amount

        }
        collection.insert_one(new_invoice)
    elif request.form['action'] == 'add':
        new_pay = float(request.form["new_transaction[amount]"]) * (
            1 if request.form["new_transaction[sign]"] == "+" else -1)
        new_transaction = {
            "name": request.form["new_transaction[name]"],
            "description": request.form["new_transaction[description]"],
            "date": request.form["new_transaction[date]"],
            "amount": new_pay
        }
        print(new_transaction)
        collection.update_one({"id": invoiceid}, {"$inc": {"total": new_pay}})
        collection.update_one({"id": invoiceid}, {"$push": {"transactions": new_transaction}})
    elif request.form['action'] == "save":
        sum: float = 0
        copy_set = invoice['transactions']
        for i in range(len(copy_set)):
            new_pay = float(request.form["transactions[" + str((i + 1)) + "][amount]"]) * (
                1 if request.form["transactions[" + str((i + 1)) + "][sign]"] == "+" else -1)
            sum += new_pay
            copy_set[i] = {
                "name": request.form["transactions[" + str((i + 1)) + "][name]"],
                "description": request.form["transactions[" + str((i + 1)) + "][description]"],
                "date": request.form["transactions[" + str((i + 1)) + "][date]"],
                "amount": new_pay
            }
        collection.update_one({"id": invoiceid}, {"$set": {"total": sum}})
        collection.update_one({"id": invoiceid}, {"$set": {"transactions": copy_set}})

    response = redirect("/edit/" + invoiceid)
    return response


# HOME PAGE
@app.route("/home")
def dashboard():
    # collection = db.profiles
    # events = collection.find({})
    username = request.cookies.get("username")
    return render_template("index.html", user=username)


# portfolio
@app.route("/portfolio", methods=["POST", "GET"])
def stock_checker():
    collection = db.profiles
    user_portfolios = collection.find_one({"username": request.cookies.get("username")})["portfolios"]
    username = request.cookies.get("username")
    if request.method == "POST":
        input = request.form["new_stock"]
        ticker = model.ask_ai(input, "stock_input")
        stock_list = [datatypes.gen_stock(ticker)]
        # updated_list = datatypes.updated_stock_prices(stock_list)
        new_portfolio = {
            "name": ticker,
            "creation": "4-9-2994",
            "private": True,
            "info": "",
            "stocks": stock_list
        }
        gathered_news = model.get_search(ticker, 5)
        new_portfolio["info"] = model.ask_ai(str(gathered_news), "summ_news")

        user_portfolios.append(new_portfolio)
        collection.update_one({"username": request.cookies.get('username')}, {"$set": {"portfolios": user_portfolios}})

        return render_template("portfolio.html", portfolios=user_portfolios, user=username)


    else:
        return render_template("portfolio.html", portfolios=user_portfolios, user=username)


# news
@app.route("/news", methods=["POST", "GET"])
def news():
    username = request.cookies.get("username")
    if request.method == "POST":
        query = request.form["news_query"]
        num = request.form["num_articles"]
        out = model.get_search(query, num)
        return render_template("news.html", output=out, user=username)
    else:
        return render_template("news.html", user=username)


# currencyConverter
@app.route("/currencyConverter", methods=["POST", "GET"])
def currency():
    username = request.cookies.get("username")
    if request.method == "POST":
        num = int(request.form["num_currencies"])
        out = sorted(datatypes.calculate_forex(datatypes.get_usd_rates(), num), key=lambda pair: pair['final_profit'],
                     reverse=True)
        return render_template("currencyConverter.html", output=out, lim=num, user=username)
    else:
        return render_template("currencyConverter.html", output=[], lim=0, user=username)


# flashcards
@app.route("/flashcards", methods=["POST", "GET"])
def flashcards():
    collection = db.profiles
    user_flashcards = collection.find_one({"username": request.cookies.get("username")})["flashcards"]
    username = request.cookies.get("username")

    if request.method == "POST":
        question = request.form["question"].lower().title()
        answer = model.ask_ai(question, "flashcard")
        return render_template("flashcards.html", input=question, output=answer, flashcards=user_flashcards,
                               user=username)
    else:
        return render_template("flashcards.html", flashcards=user_flashcards, user=username)


@app.route("/save", methods=["POST", "GET"])
def save_flashcards():
    collection = db.profiles
    query = {"username": request.cookies.get("username")}
    user_flashcards = collection.find_one(query)["flashcards"]
    username = request.cookies.get("username")

    if request.method == "POST":
        question = request.form["new_term"].lower().title()
        answer = request.form["new_ans"]
        # print(answer)

        new_flashcard = {
            "topic": question,
            "conversation": [{
                "author": "user",
                "content": answer
            }]
        }
        user_flashcards = [new_flashcard] + user_flashcards
        collection.update_one({"username": request.cookies.get("username")}, {"$set": {"flashcards": user_flashcards}})

        return render_template("flashcards.html", flashcards=user_flashcards, user=username)
    else:
        return render_template("flashcards.html", flashcards=user_flashcards, user=username)


# @app.route("/user-flashcards")
# def get_flashcards():
#   username = request.cookies.get("username")
#   collection = db.profiles
#   flashcards = collection.find_one({"username":username})["flashcards"]
#   print(flashcards)
#   return flashcards


# if successful login/signup, store in cookies and redirect to homepage

# HANDLE POST AND GET for login
@app.route("/")
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if (request.method == "POST"):
        collection = db.profiles
        usr = request.form['username']
        pwd = request.form['password']
        verification = datatypes.input_verification(usr, pwd)
        if verification != "OK":
            return render_template("login.html", error=verification)

        if request.form['action'] == "Signup":
            new_user = datatypes.gen_new_user(usr, datatypes.hash(pwd))
            if collection.find_one({"username": usr}) != None:
                return render_template("login.html", error="Username already exists")
            collection.insert_one(new_user)
        elif request.form['action'] == 'Login':
            profile = collection.find_one({"username": usr})
            if profile == None:
                return render_template("login.html", error="Username not found")
            if not datatypes.password_check(pwd, profile['password']):
                return render_template("login.html", error="Incorrect password")
        # verify
        response = redirect("/home")  # make_response()
        response.set_cookie("username", request.form["username"])
        response.set_cookie("password", request.form["password"])

        return response
    else:
        response = make_response(render_template("login.html"))
        response.set_cookie("username", max_age=0)
        response.set_cookie("password", max_age=0)
        return response  # render_template("login.html")


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


# # CLEAR OUT THE EVENTS
# @app.route("/clear", methods=["POST"])
# def clear_events():
#   collection = db.events
#   collection.delete_many({})
#   return render_template("index.html")


# db.profiles.delete_many({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

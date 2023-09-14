from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime
cluster = MongoClient("mongodb+srv://rahul:rahul@cluster0.zxbxlmr.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number" : number})
    if not bool(user):
        res.message("Hi, thanks for contacting us. \nKindly send below menu options:\n (1) Contact \n (2) Order \n (3) Working hours")
        users.insert_one({"number": number, "status" : "main", "messages" : []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message("You can contact A")
        elif option == 2:
            res.message("Entered ordering mode")
            users.update_one({"number" : number}, {"$set" : {"status" : "ordering"}})
            res.message("You have entered ordering mode \n (1) Red Velvet \n (2) Dark forest \n (3) Black current \n (0) Go back")
        elif option == 3:
            res.message("We work round the clock!")
        else:
            res.message("Please enter a valid response")
            return str(res)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from below options: \nKindly send below menu options:\n (1) Contact \n (2) Order \n (3) Working hours")
        elif 1 <= option <= 3:
            cakes = ["Red Velvet", "Dark forest", "Black current"]
            selected = cakes[option-1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice!!!")
            res.message("Please enter your postal address")

        else:
            res.message("Please enter a valid response")

    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for ordering")
        res.message(f"Your order is {selected} and will be delivered on \naddress: {text}")
        orders.insert_one({"number": number, "item" : selected, "address" : text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        users.update_one({"number": number}, {"$set": {"status": "main"}})
        res.message("You can choose from below options: \nKindly send below menu options:\n (1) Contact \n (2) Order \n (3) Working hours")

    users.update_one({"number" : number}, {"$push" : {"messages" : {"text" : text, "date": datetime.now()}}})



    # if "Hi" in txt:
    #     res.message("Hello")
    # else:
    #     res.message("I don't know what to say!")

    # msg = response.message("Hey")
    # msg.media(
    #     "https://images.unsplash.com/photo-1692533583962-7de22728939e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwxfDB8MXxyYW5kb218MHx8fHx8fHx8MTY5NDQyNTEzMw&ixlib=rb-4.0.3&q=80&w=1080")

    return str(res)

if __name__ == "__main__":
    app.run()

# nodemon --exec python3 main.py
# nodemon --watch "main.py" --exec "lt --subdomain appbrewerykav --port 5000" delay 2
# https://appbrewerykav.loca.lt

import bcrypt
from pymongo import MongoClient
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import spacy

# initialising Flask application
app = Flask(__name__)
api = Api(app)

# initialising the MongoDB client
client = MongoClient("mongodb://db:27017")

# creating new database
db = client.my_database
users = db["users"]

@app.route("/")
def home():
    '''to check if server is running'''
    return "working"

def register_check(input_data):
    '''this function will validate the input data for registering a user'''
    username = input_data["username"]
    if ("username" in input_data) and ("password" in input_data):
        return 200
    elif username in [i["username"] for i in users.find()]:
        return 304
    else:
        return 301

class Register(Resource):
    def post(self):
        '''this method will register a user or send a user specified error message'''
        input_data = request.get_json(force=True)
        username = str(input_data["username"])
        password = str(input_data["password"])

        response_code = register_check(input_data)

        if response_code == 200:
            hashed_password = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
            users.insert_one({"username":username, "password":hashed_password, "token":10})

            response_text = "user registered successfully"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        elif response_code == 304:
            response_text = "username already registered"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        else:
            response_text = "missing value(s)"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

def check_data_validation(input_data):
    '''this function will validate the input data given by user for checking the similarty of the 2 texts'''
    if ("username" in input_data) & ("password" in input_data) & ("text_1" in input_data) & ("text_2" in input_data):
        username = str(input_data["username"])
        password = str(input_data["password"])
        # text_1 = str(input_data["text_1"])
        # text_2 = str(input_data["text_2"])
        if username in [i["username"] for i in users.find()]:
            system_saved_user_password = users.find({"username":username})[0]["password"]
            if bcrypt.checkpw(password.encode("utf8"), system_saved_user_password):
                available_token = users.find({"username": username})[0]["token"]
                if available_token > 0:
                    return 200
                else:
                    return 303
            else:
                return 302
        else:
            return 305
    else:
        return 301


class Check(Resource):
    def post(self):
        '''this method will check the similarity of the 2 texts sent by the user or
        return an error message (given by us)'''
        input_data = request.get_json(force=True)
        username = str(input_data["username"])
        # password = str(input_data["password"])
        text_1 = str(input_data["text_1"])
        text_2 = str(input_data["text_2"])

        response_code = check_data_validation(input_data)
        print(response_code)
        if response_code == 200:
            available_token = users.find({"username": username})[0]["token"]
            nlp = spacy.load('en_core_web_md')
            text1 = nlp(text_1)
            text2 = nlp(text_2)
            ratio = text1.similarity(text2)
            available_token -= 1
            users.update_one({"username": username}, {"$set": {"token": available_token}})
            response_text = f"similarity ratio is {ratio}"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        elif response_code == 305:
            response_text = "username not registered"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        elif response_code == 302:
            response_text = "incorrect password"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        elif response_code == 303:
            response_text = "insufficient tokens"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        else:
            response_text = "missing value(s)"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)


def check_refill(input_data):
    '''this function will validate the input data given by the user'''
    if ("username" in input_data) & ("password" in input_data) & ("refill" in input_data):
        # username = str(input_data["username"])
        password = str(input_data["password"])
        # refill = input_data["refill"]
        if password == "iamadmin":
            return 200
        else:
            return 302
    else:
        return 301


class Refill(Resource):
    def post(self):
        '''this method will refill the tokens of the user or return a specific error message (given by us)'''
        input_data = request.get_json(force=True)

        response_code = check_refill(input_data)

        if response_code == 200:
            username = str(input_data["username"])
            # password = str(input_data["password"])
            refill_token = int(input_data["refill"])
            available_token = int(users.find({"username": username})[0]["token"])
            updated_token = available_token + refill_token
            users.update_one({"username":username},{"$set":{"token":updated_token}})

            response_text = f"{refill_token} tokens added to {available_token}. updated token count for {username} is {updated_token}."

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        elif response_code == 302:
            response_text = "incorrect password"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)

        else:
            response_text = "missing value(s)"

            return_data = {"response_code": response_code, "response_text": response_text}

            return jsonify(return_data)


'''assigning the method to the endpoints'''
api.add_resource(Register ,"/register")
api.add_resource(Check ,"/check")
api.add_resource(Refill ,"/refill")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
    
    

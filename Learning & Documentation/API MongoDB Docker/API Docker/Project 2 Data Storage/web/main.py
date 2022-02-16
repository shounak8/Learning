from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_restful import Api, Resource
import bcrypt

# initialising Flask application
app = Flask(__name__)

api = Api(app)

# initialising the MongoDB client
client = MongoClient("mongodb://db:27017")

# creating new database
db = client.user_data_store
users = db.user_collection


@app.route("/")
def home():
    '''this is created just to check if the server is running'''
    return "active"


def verify_registration_data(input_data):
    '''this function will validate the input data for registering a user'''
    username = input_data["username"]
    if username in [i['username'] for i in users.find()]:
        return 304
    elif ("username" in input_data) and ("password" in input_data):
        return 200
    else:
        return 301

class Register(Resource):
    def post(self):
        '''this method will register a user or send a user specified error message'''
        input_data = request.get_json(force=True)

        response_code = verify_registration_data(input_data)
        # print(response_code)

        if response_code == 200:
            username = input_data["username"]
            password = input_data["password"]

            hashed_pwd = bcrypt.hashpw(str(password).encode("utf8"), bcrypt.gensalt())
            # store user data
            users.insert_one({"username": username,
                          "password": hashed_pwd,
                          "text_data": [],
                          "tokens": 10})

            print([i for i in users.find()])

            return_data = {"response_code" : response_code,
                           "message" : "User Registration Successful"}

            return jsonify(return_data)

        elif response_code == 304:
            return_data = {"response_code" : response_code,
                           "message" : "User already registered"}

            return jsonify(return_data)

        else:
            return_data = {"response_code" : response_code,
                           "message" : "Missing Field(s)"}

            return jsonify(return_data)



def verify_user_input(input_data):
    '''this function will validate the user input during storing the data'''
    if ("username" in input_data) and ("password" in input_data) and ("text_data" in input_data):
        username = input_data["username"]
        password = input_data["password"]
        saved_pwd = users.find({"username":username})[0]["password"]
        if bcrypt.checkpw(str(password).encode("utf8"), saved_pwd):
            user_available_token = users.find({"username":username})[0]["tokens"]
            if user_available_token > 0:
                return 200
            else:
                return 303
        else:
            return 302
    else:
        return 301


class Store(Resource):
    def post(self):
        '''this method will store the textual data sent by the user or return a specific error message (given by us)'''
        input_data = request.get_json(force=True)

        response_code = verify_user_input(input_data)

        if response_code == 200:
            username = input_data["username"]
            text_data = input_data["text_data"]
            user_available_token = users.find({"username": username})[0]["tokens"]
            updated_token = user_available_token - 1
            user_data = users.find({"username": username})[0]["text_data"]
            user_data.append(text_data)
            users.update({"username":username},{"$set":{"text_data": user_data,
                                                "tokens":updated_token}})

            return_data = {"response_code": response_code,
                           "message": "Data Saved"}

            print([i for i in users.find()])
            return jsonify(return_data)

        elif response_code == 301:
            return_data = {"response_code": response_code,
                           "message": "Missing Field(s)"}

            return jsonify(return_data)

        elif response_code == 302:
            return_data = {"response_code": response_code,
                           "message": "Incorrect Password"}

            return jsonify(return_data)

        elif response_code == 303:
            return_data = {"response_code": response_code,
                           "message": "Insufficient tokens"}

            return jsonify(return_data)


def verify_credentials(input_data):
    '''this function will validate the user credentials'''
    if ("username" in input_data) and ("password" in input_data):
        username = input_data["username"]
        password = input_data["password"]
        saved_pwd = users.find({"username":username})[0]["password"]
        if bcrypt.checkpw(str(password).encode("utf8"), saved_pwd):
            return 200
        else:
            return 302
    else:
        return 301


class Retrieve(Resource):
    def post(self):
        '''this method will retrieve the saved data for the user or return a specific error message (given by us)'''
        input_data = request.get_json(force=True)

        response_code = verify_credentials(input_data)

        if response_code == 200:
            username = input_data["username"]
            text_data = users.find({"username":username})[0]["text_data"]
            return_data = {"response_code": response_code,
                           "saved_data": text_data}

            return jsonify(return_data)

        elif response_code == 302:
            return_data = {"response_code": response_code,
                           "message": "Incorrect Password"}

            return jsonify(return_data)
        else:
            return_data = {"response_code": response_code,
                           "message": "Missing Value(s)"}

            return jsonify(return_data)


'''assigning the method to the endpoints'''
api.add_resource(Register,"/register")
api.add_resource(Store,"/store")
api.add_resource(Retrieve,"/retrieve")


if __name__=="__main__":
    app.run(host="0.0.0.0")








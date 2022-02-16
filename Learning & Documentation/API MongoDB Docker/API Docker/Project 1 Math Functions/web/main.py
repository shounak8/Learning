from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

# initialising Flask application
app = Flask(__name__)
api = Api(app)

# initialising the MongoDB client
client = MongoClient("mongodb://db:27017")

# creating new database
db = client.python_db
user_num = db["user_num"]

user_num.insert({"num_of_users": 0})

class Visit(Resource):
    def get(self):
        '''this method will return the number of views the website has received
        i.e. the number of GET requests it has received'''
        prev_num = user_num.find({})[0]["num_of_users"]
        new_num = prev_num + 1
        user_num.update({},{"$set":{"num_of_users": new_num}})
        return str("View Count: " + str(new_num))

@app.route("/")
def home():
    '''this page (home_page) will show the number of APIs'''

    text = "This is the Home Page for testing API\n<br>" \
           "For info, use endpoint as '/info'\n<br>" \
           "For Addition, use endpoint as '/add'\n<br>" \
           "For Subtraction, use endpoint as '/sub'\n<br>" \
           "For Multiplication, use endpoint as '/multiply'\n<br>" \
           "For Division, use endpoint as '/divide'"
    return text


@app.route("/info")
def info():
    '''this page shows the details of the app'''

    data = {"Creator": "Shounak",
            "Add": "/add",
            "Sub": "/sub",
            "Multiply": "/multiply",
            "Divide": "/divide",
            "Input_Format": "Input JSON {'A': first_num, 'B': second_num}"}
    return jsonify(data)


def validation(input_data, operation):
    '''this function will validate the input data'''
    if (operation == "add") or (operation == "sub") or (operation == "multiply"):
        if ("A" in input_data) & ("B" in input_data):
            return 200
        else:
            return 301
    elif (operation == "divide"):
        if input_data["B"] == 0:
            return 302
        elif ("A" in input_data) & ("B" in input_data):
            return 200
        else:
            return 301


class Add(Resource):
    def post(self):
        '''this method will add the 2 input numbers or return back a specifiic error message (given by us)'''
        input_data = request.get_json(force=True)

        # validate input
        code = validation(input_data, "add")

        if code == 200:
            A = float(input_data["A"])
            B = float(input_data["B"])
            result = A + B
        else:
            result = "Missing Value(s)"

        output_data = {"code": code,
                       "result": result}
        return jsonify(output_data)


class Sub(Resource):
    def post(self):
        '''this method will substract the 2 input numbers or return back a specifiic error message (given by us)'''
        input_data = request.get_json(force=True)

        # validate input
        code = validation(input_data, "sub")

        if code == 200:
            A = float(input_data["A"])
            B = float(input_data["B"])
            result = A - B
        else:
            result = "Missing Value(s)"

        output_data = {"code": code,
                       "result": result}
        return jsonify(output_data)


class Multiply(Resource):
    def post(self):
        '''this method will multiply the 2 input numbers or return back a specifiic error message (given by us)'''
        input_data = request.get_json(force=True)

        # validate input
        code = validation(input_data, "multiply")

        if code == 200:
            A = float(input_data["A"])
            B = float(input_data["B"])
            result = A * B
        else:
            result = "Missing Value(s)"

        output_data = {"code": code,
                       "result": result}
        return jsonify(output_data)


class Divide(Resource):
    '''this method will divide the 2 input numbers or return back a specifiic error message (given by us)'''
    def post(self):
        input_data = request.get_json(force=True)

        # validate input
        code = validation(input_data, "divide")

        if code == 200:
            A = float(input_data["A"])
            B = float(input_data["B"])
            result = A / B
        elif code == 302:
            result = "Logical Absurdity as B = 0"
        else:
            result = "Missing Value(s)"

        output_data = {"code": code,
                       "result": result}
        return jsonify(output_data)


'''assigning the method to the endpoints'''
api.add_resource(Add, "/add")
api.add_resource(Sub, "/sub")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visit, "/visit")



if __name__ == "__main__":
    app.run(host="0.0.0.0")

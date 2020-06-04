from flask import Flask, jsonify, render_template, request, abort
from api.utility import struct_msg
from config import api_configuration
from pymongo import MongoClient

app = Flask(__name__,template_folder="../templates")

api_config = api_configuration()
client = MongoClient(api_config["api_database"])
db = client[api_config["api_database_name"]]

def isauthenticated(user_token):
    if db.users.users.find_one({"token": user_token}):
        print(db.users.users.find_one({"token": user_token}))
        return True
    return False

@app.errorhandler(400)
def error_400(error):
    """
    handle 400 error
    Args:
        error: the flask error
    Returns:
        400 JSON error
    """
    return jsonify(
        struct_msg(status="error", msg=error.description)
    ), 400

@app.errorhandler(404)
def error_404(error):
    """
    handle 404 error
    Args:
        error: Authentication Failed
    Returns:
        404 JSON error
    """
    return jsonify(
        struct_msg(status="error", msg=error.description)
    ), 404


@app.route("/submit", methods=["POST"])
def samplefunc():
    if not (isauthenticated(request.args["token"])):
        abort(404, "Invalid API Token")
    return jsonify(
      [{
    'sample': 'Sample output'
  }])

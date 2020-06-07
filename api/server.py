from flask import Flask, jsonify, render_template, request, abort
from werkzeug.utils import secure_filename
from api.utility import struct_msg
from config import api_configuration
from pymongo import MongoClient
from core.compatible import generate_token
import os

app = Flask(__name__,template_folder="../templates")

api_config = api_configuration()
client = MongoClient(api_config["api_database"])
db = client[api_config["api_database_name"]]

def isauthenticated(user_token):
    if db.users.users.find_one({"token": user_token}):
        return True
    return False

def isreportid(report_id):
    if db.submission.submission.find_one({"id": report_id}):
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
def samplesubmit():
    try:
        if request.args["api_key"]:
            if not (isauthenticated(request.args["api_key"])):
                return abort(404, "Invalid authenctication api key")
    except KeyError:
        return abort(404, "Authentication api key not availabale")

    try:
        if request.args["runTime"]:
            time_to_run = request.args["runTime"]
    except KeyError:
        return abort(404, "Duration to run Tenjint not availabale")

    try:
        if request.args["guestImage"]:
            guest_image = request.args["guestImage"]
    except KeyError:
        return abort(404, "Guest Image to run qemu not availabale")

    if not request.files:
        return abort(404, "Sample file not submitted")
    file = request.files['sample']
    new_filename = secure_filename(file.filename)
    file.save(os.path.join('./shared_samples', new_filename))

    sample = {
        'time_to_run': time_to_run,
        'guest_image': guest_image,
        'completed': False,
        'id': generate_token(),
        'submission_file': new_filename
        }
    db.submission.submission.insert_one(sample)

    return jsonify(
    [{
    'submission_id': sample['id']
    }])

@app.route("/report", methods=["GET"])
def report():
    try:
        if request.args["api_key"]:
            if not (isauthenticated(request.args["api_key"])):
                return abort(404, "Invalid authenctication api key")
    except KeyError:
        return abort(404, "Authentication api key not availabale")

    try:
        if request.args["id"]:
            if not (isreportid(request.args["id"])):
                return abort(404, "Invalid Report id")
    except KeyError:
        return abort(404, "Report id not availabale")

    return jsonify(
    [{
    'sample': 'Sample output'
    }])

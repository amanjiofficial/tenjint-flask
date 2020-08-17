from flask import Flask, render_template, request, jsonify, abort, render_template
from werkzeug.utils import secure_filename
from api.utility import struct_msg, isauthenticated
from core.compatible import generate_token
from config import api_configuration
from api.db import db
import os
from tenjint_script.script import newSample

app = Flask(__name__,template_folder="../templates")
api_config = api_configuration()

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

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/adduser", methods=["POST"])
def adduser():
    try:
        if request.args["token"]:
            if request.args["token"] == api_config["api_admin_token"]:
                user = { 'token': generate_token() }
                db.users.users.insert_one(user)
                return user['token']
            else:
                return abort(404, "Invalid Authentication Token")
    except KeyError:
        return abort(404, "Authentication Token Not Availabale")

@app.route("/deluser", methods=["POST"])
def deluser():
    try:
        if request.args["token"]:
            try:
                if request.args["user_token"]:
                    if request.args["token"] == api_config["api_admin_token"]:
                        if db.users.users.count({'token': request.args["user_token"]}) == 0:
                            return abort(404, "User not registered")
                        db.users.users.delete_one({'token': request.args["user_token"]})
                        return "User Deleted"
                    else:
                        return abort(404, "Invalid Authentication Token")
            except KeyError:
                return abort(404, "Token of user to delete not Available")
    except KeyError:
        return abort(404, "Authentication Token Not Availabale")

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
            runTime =  int(request.args["runTime"])
            if runTime <= api_config["max_tenjint_run_time"]:
                if runTime >= api_config["min_tenjint_run_time"]:
                    time_to_run = runTime
                else:
                    return abort(404, "Duration to run Tenjint is less than minimum allowed")
            else:
                return abort(404, "Duration to run Tenjint more than maximum allowed")
    except KeyError:
        return abort(404, "Duration to run Tenjint not availabale")

    try:
        if request.args["guestImage"]:
            guest_image = request.args["guestImage"]
            if guest_image not in api_config["VM"]:
                return abort(404, "Requested Guest Image not available.")
    except KeyError:
        return abort(404, "Guest Image to run qemu not availabale")

    if not request.files:
        return abort(404, "Sample file not submitted")
    file = request.files['sample']
    new_filename = secure_filename(file.filename)
    if len(new_filename) < 1:
        return abort(404, "Sample not submitted")
    origPath = os.getcwd()
    os.chdir('./shared_samples')
    if os.path.exists(new_filename):
        os.chdir(origPath)
        return abort(404, "Sample name already exists")
    file.save(os.path.join(new_filename))
    os.chdir(origPath)

    sample = {
        'time_to_run': time_to_run,
        'guest_image': guest_image,
        'status': 'ready', # ready, running and completed
        'id': generate_token(),
        'submission_file': new_filename,
        'domain': ''
        }
    db.submission.submission.insert_one(sample)
    newSample(sample)
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
            sampleID = request.args["id"]            
    except KeyError:
        return abort(404, "Report id not availabale")
    
    if db.submission.submission.find_one({ "id": sampleID }):
        if db.submission.started.find_one({ "id": sampleID }):
            if db.submission.started.find_one({ "id": sampleID, "status": "completed" }):
                VMdomain = db.submission.started.find_one({ "id": sampleID, "status": "completed" }, { "domain": 1})
                if db.output.output.find_one({ "domain": VMdomain['domain'] }):
                    return db.output.output.find_one({ "domain": VMdomain['domain'] }, { "_id": 0})
                else:
                    response = "Report not generated yet"
            else:
                response = "Sample still in execution"
        else:
            response = "Sample waiting in queue to execute"
    else:
        response = "sample ID is invalid."
    return jsonify(
    [{
    'status': response
    }])
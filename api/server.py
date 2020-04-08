from flask import Flask, jsonify, render_template
from api.utility import struct_msg

app = Flask(__name__,template_folder="../templates")

@app.errorhandler(400)
def error_400(error):
    """
    handle 400 HTTP error
    Args:
        error: the flask error
    Returns:
        400 JSON error
    """
    return jsonify(
        struct_msg(status="error", msg=error.description)
    ), 400


@app.route("/sample", methods=["GET", "POST"])
def samplefunc():
  return jsonify(
      [{
    'sample': 'Sample output'
  }])

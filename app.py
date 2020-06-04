from api.server import app,db,api_config
from flask import render_template,request
from core.compatible import generate_token

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/adduser", methods=["POST"])
def adduser():
    if request.args["token"] == api_config["api_admin_token"]:
        user = { 'token': generate_token() }
        db.users.users.insert_one(user)
        return user['token']
    else:
        return "Invalid authentication Token"

if __name__ == "__main__":
    app.run(debug = True)
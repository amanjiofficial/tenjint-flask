from api.server import app,db,api_config,abort
from flask import render_template,request
from core.compatible import generate_token

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

if __name__ == "__main__":
    app.run(debug = True)

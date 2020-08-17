from api.db import db
def struct_msg(status="", msg=""):
    """
    JSON message structure
    Args:
        status: status (ok, failed)
        msg: the message content
    Returns:
        JSON message
    """
    return {
        "status": status,
        "msg": msg
    }

def isauthenticated(user_token):
    if db.users.users.find_one({"token": user_token}):
        return True
    return False
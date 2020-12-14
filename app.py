from api.server import app
from config import api_configuration

api_config = api_configuration()


if __name__ == "__main__":
    app.run(
        debug = api_config["api_debug_mode"],
        host = api_config["api_host"],
        port = api_config["api_port"],
        )

"""
This is output module. It is responsible for all output that is
produced by tenjint-flask. At the moment, the only output that is produced by
tenjint. Events will be stored in a JSON based on the
configuration of the OutputManager.
"""

import json
import tenjint.config
from tenjint.event import EventCallback
from tenjint.service import manager
import datetime
from datetime import timezone
import os


_manager = None

"""The current output manager.

This is an internal variable that should not be accessed from outside of the
module.
"""

class JSONOutputManager(tenjint.config.ConfigMixin):
    """JSON output manager."""
    _config_section = "OutputManager"
    _config_options = [
        {"name": "store", "default": False,
         "help": "Path where to store events. If set to False no events "
                 "will be recorded."}
    ]

    def __init__(self):
        super().__init__()
        self._cb = EventCallback(self._log_event)
        self._event_manager = manager().get("EventManager")
        self._event_manager.request_event(self._cb)
        self._events = []
        self._out = {}
        self._pluginPath = tenjint.config._config_data['PluginManager']['plugin_dir']
        self._filePath = ""
        with open(self._pluginPath + "/sample.json", 'r') as openfile:
            json_object = json.load(openfile)
            self._filePath = json_object["file"]
        
    def uninit(self):
        if self._cb is not None:
            self._event_manager.cancel_event(self._cb)
            self._cb = None

    def _log_event(self, event):
        self._events.append(event)
        self._out[event.__class__.__name__] = datetime.datetime.now().replace(tzinfo=timezone.utc).timestamp()
        with open(self._pluginPath + self._filePath, 'w') as openfile:
            json.dump(self._out, openfile)       

def init():
    """Initialize the output module."""
    global _manager

    _manager = JSONOutputManager()

init()
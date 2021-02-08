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
import pickle

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
        self._pluginPath = tenjint.config._config_data['PluginManager']['plugin_dir']
        self._filePath = ""
        with open(self._pluginPath + "/sample.json", 'r') as openfile:
            json_object = json.load(openfile)
            self._filePath = json_object["file"]

    def uninit(self):
        self._flush()
        global _manager
        if _manager is not None:
            _manager = None
        if self._cb is not None:                       
            self._event_manager.cancel_event(self._cb)
            self._cb = None

    def _flush(self):
        with open(self._pluginPath + self._filePath, 'wb') as openfile:
            pickle.dump(self._events, openfile)       
        self._events.clear()

    def _log_event(self, event):
        if event.__class__.__name__ not in ["SystemEventVmShutdown", "SystemEventVmStop", "SystemEventVmReady"]:
            result_output = event.serialize()            
            self._events.append(result_output)
        elif event.__class__.__name__  == "SystemEventVmShutdown":
            self.uninit()                               

def init():
    """Initialize the output module."""
    global _manager

    _manager = JSONOutputManager()

init()    
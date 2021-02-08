from tenjint.plugins.plugins import Plugin
from tenjint.api import api
from tenjint.event import EventCallback
import tenjint.config
from tenjint.service import _service_manager
import json
class sampleRun(Plugin):
    
    _abstract = False
    os = api.OsType.OS_LINUX

    _DO_EXIT_SYM = "linux!do_exit"

    def __init__(self):
        super().__init__()
        vaddr = self._os.get_symbol_address(self._DO_EXIT_SYM)
        paddr = self._os.vtop(vaddr, kernel_address_space=True)
        self._cb = EventCallback(self._cb_func,
                                event_name="SystemEventBreakpoint",
                                event_params={"gpa": paddr})

        self._event_manager.request_event(self._cb)

    def _cancel_event(self):
        if self._cb is not None:
            self._event_manager.cancel_event(self._cb)
            self._cb = None

    def uninit(self):
        super().uninit()
        self._cancel_event()        

    def _cb_func(self, e):
        plugin_dir = tenjint.config._config_data['PluginManager']['plugin_dir']
        with open(plugin_dir + "/sample.json", 'r') as openfile:
            json_object = json.load(openfile)
            file_name = json_object["file"]
        self._CMD_LINE = "mount -t 9p -o trans=virtio,version=9p2000.L temp /mnt/ ; cp /mnt/{} /root ; /root/{}".format(file_name, file_name)
        self.injection_cb = EventCallback(self.injection_cb_func,
                                event_name="FunctionCallInjectionEvent",
                                event_params={ "symbol": "linux!run_cmd",
                                "args": [self._CMD_LINE],
                                "kernel": True
                                })
        self._event_manager.request_event(self.injection_cb)
        task = self._os.current_process(e.cpu_num)
        self._logger.debug("EXIT: {:d} - {} ({})".format(task.pid,
                                                         task.name,
                                                         task.commandline))
                                                         
    def injection_cb_func(self, e):
        if self.injection_cb is not None:
            self._event_manager.cancel_event(self.injection_cb)
            self.injection_cb = None
            self.uninit()
from tenjint.plugins.plugins import Plugin, EventPlugin
from tenjint.api import api
from tenjint.event import EventCallback, CpuEvent
import tenjint.config
from tenjint.service import _service_manager

class apiTrace(Plugin):
    
    _abstract = False
    #produces=[apiEvent]
    os = api.OsType.OS_LINUX

    _DO_FORK_SYM = "linux!do_execve"

    def __init__(self):
        super().__init__()
        self._request_id_cntr = 0
        vaddr = self._os.get_symbol_address(self._DO_FORK_SYM)
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
        print("Api Trace Call")

    def request_event(self):
        self._event_manager.request_event(self._cb)
        request_id = self._request_id_cntr
        self._request_id_cntr += 1
        return request_id
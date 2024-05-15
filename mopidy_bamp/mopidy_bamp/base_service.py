
import tornado.web
import threading


class BaseService:

    initialised = False
    core = None
    config = None
    lock = None

    def init(self, core, config):
        self.core = core
        self.config = config

        self.lock = threading.Lock()
        self.initialised = True

    def check_init(self):
        if not self.initialised:
            raise tornado.web.HTTPError(500)
        
    def acquire_lock(self):
        acquired = self.lock.acquire(timeout=2)
        return acquired
    
    def release_lock(self):
        self.release_lock()

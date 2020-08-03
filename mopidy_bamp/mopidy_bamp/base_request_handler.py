import tornado.web
import logging
from mopidy import config

logger = logging.getLogger(__package__)


class BaseRequestHandler(tornado.web.RequestHandler):

    SECURE_COOKIE_USER_FIELD = 'user'

    core = None
    config = None

    def initialize(self, core, config):
        self.core = core
        self.config = config

        self.application.settings['cookie_secret'] = config['mopidy_bamp']['cookie_secret']
        self.application.settings['login_url'] = '/api/login'

        self.set_header("build-hash", config['mopidy_bamp']['build_hash'])

    def get_current_user(self):
        user = self.get_secure_cookie(self.SECURE_COOKIE_USER_FIELD)

        if user is not None:
            user = user.decode('utf-8')

        return user

import json
import tornado.web
import logging

from .dtos import DTOEncoder, ConfigValueDTO

from .base_request_handler import BaseRequestHandler

from .database_connection import DBConnection

logger = logging.getLogger(__package__)


class ConfigRequestHandler(BaseRequestHandler):
    def get(self, name):

        exposed_config = {
            'icecast_url': self.config['mopidy_bamp']['icecast_url']
        }

        try:
            value = exposed_config[name]
            self.write(json.dumps(ConfigValueDTO(name=name, value=value), cls=DTOEncoder))
        except:
            logger.warning(f"Unknown config value requested: {name}")
            raise tornado.web.HTTPError(400)
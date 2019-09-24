from __future__ import absolute_import, unicode_literals

import json
import tornado.web
import logging
import ldap

from .dtos import TrackDTO, DTOEncoder

from .base_request_handler import BaseRequestHandler

from .database_connection import DBConnection

logger = logging.getLogger(__package__)


class IsLoggedInRequestHandler(BaseRequestHandler):
    def get(self):

        logged_in = self.get_current_user() is not None

        response = {'logged_in': logged_in}

        if logged_in:
            # get user details in the db
            user_dto = None
            with DBConnection() as db_connection:
                user_dto = db_connection.user_table.get(self.get_current_user())

            response['user'] = user_dto

        self.write(json.dumps(response, cls=DTOEncoder))


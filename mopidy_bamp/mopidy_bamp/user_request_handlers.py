from __future__ import absolute_import, unicode_literals

import json
import tornado.web
import logging
import ldap

from .dtos import UserDTO, DTOEncoder

from .base_request_handler import BaseRequestHandler
from .database_connection import DBConnection

logger = logging.getLogger(__package__)


class UpdateUserDetailsRequestHandler(BaseRequestHandler):
    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        user_id = data['user_id']
        alias = data['alias']
        new_alias = alias

        if self.get_current_user() is None:
            raise tornado.web.HTTPError(status_code=400, log_message='user not logged in')

        # only allow the logged in user to change their details
        if self.get_current_user() != user_id:
            raise tornado.web.HTTPError(status_code=400, log_message='you cannot change another users details')

        # sanitise the alias
        annoying_whitespace = {(0x200b), (0x200c), (0x200d), (0x200e), (0x200f), (0x205f),
                               (0x2060), (0x2061), (0x2062), (0x2063), (0x2064), (0x206a),
                               (0x206b), 0x206c, 0x206d, 0x206e, 0x206f, 0x202D, 0x2028,
                               0x2029, 0x202a, 0x202b, 0x202c, 0x202e, 0x202f}
        for x in annoying_whitespace:
            new_alias = new_alias.replace(chr(x), '')
        new_alias = new_alias.strip()

        if new_alias == '':
            # try and log out some information - python2 is not good at outputting code points for some chars, so just do a simple replace
            logger.warning('User {0} tried to change alias to invalid alias "{1}"'.format(user_id, alias.encode('ascii', 'replace')))
            raise tornado.web.HTTPError(status_code=400, log_message='you cannot have an empty alias')

        if len(new_alias) > self.config['mopidy_bamp']['max_alias_length']:
            raise tornado.web.HTTPError(status_code=400, log_message='alias is too long')

        # update user details in the db
        with DBConnection() as db_connection:
            db_connection.user_table.update(user_id, new_alias)

        response = {'status': 'ok'}

        self.write(response)


class GetUserDetailsRequestHandler(BaseRequestHandler):
    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        user_id = data['user_id']

        if self.get_current_user() is None:
            raise tornado.web.HTTPError(status_code=400, log_message='user not logged in')

        # get user details in the db
        user_dto = None
        with DBConnection() as db_connection:
            user_dto = db_connection.user_table.get(user_id)

        self.write(json.dumps(user_dto, cls=DTOEncoder))


from __future__ import absolute_import, unicode_literals

import json
import logging
import tornado.web

from .dtos import DTOEncoder, UserDTO
from .base_request_handler import BaseRequestHandler
from .history_service import g_history
from .available_actions import get_available_actions
from .database_connection import DBConnection

logger = logging.getLogger(__package__)


# Request to enable playback within BAMP
class HistoryRequestHandler(BaseRequestHandler):

    @tornado.web.authenticated
    def get(self):

        history_dtos = g_history.get_history_dtos()
        track_dtos = g_history.get_track_dtos(history_dtos)

        user_id_list = list(map(lambda x: x.user_id, history_dtos))

        with DBConnection() as db_connection:
            user_dto_dict = db_connection.user_table.get_dict(user_id_list)

        actions = get_available_actions(track_dtos, self.get_current_user())

        response = {'historyitems': history_dtos, 'tracks': track_dtos, 'actions': actions, 'users': user_dto_dict}
        self.write(json.dumps(response, cls=DTOEncoder))

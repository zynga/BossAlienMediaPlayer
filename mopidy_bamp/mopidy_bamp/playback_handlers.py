from __future__ import absolute_import, unicode_literals

import json
import logging
import tornado.web

from .dtos import DTOEncoder, PlaybackStateDTO, TrackDTO, UserDTO
from .images import update_trackdto_images
from .base_request_handler import BaseRequestHandler
from .queue_metadata_service import g_queue_metadata
from .playback_service import g_playback
from .available_actions import get_available_actions
from .database_connection import DBConnection

logger = logging.getLogger(__package__)


# Request to enable playback within BAMP
class EnablePlaybackRequestHandler(BaseRequestHandler):

    @tornado.web.authenticated
    def post(self):

        g_playback.enable_playback()

        response = {'success': True }

        self.write(json.dumps(response, cls=DTOEncoder))


# Request to disable playback within BAMP
class DisablePlaybackRequestHandler(BaseRequestHandler):

    @tornado.web.authenticated
    def post(self):
        g_playback.disable_playback()

        response = {'success': True }

        self.write(json.dumps(response, cls=DTOEncoder))


# Request to get the current playing track state. Will return empty data if no track is playing,
# but always returns the playback state
class NowPlayingRequestHandler(BaseRequestHandler):

    # This end point is not authenticated as we want to display it on the login page!
    def get(self):
        track = self.core.playback.get_current_track().get()
        mopidy_playback_state = self.core.playback.get_state().get()
        playback_enabled = g_playback.get_playback_enabled()
        playback_state = PlaybackStateDTO(mopidy_playback_state, playback_enabled)

        response = {'track': None, 'queueitem': None, 'user': None, 'playbackstate': playback_state}

        if track is None:
            self.write(json.dumps(response, cls=DTOEncoder))
            return

        response['track'] = TrackDTO(track)
        update_trackdto_images(self.core, response['track'])

        queue_item = g_queue_metadata.get_single_queue_item_dto(track.uri)

        if queue_item is None:
            raise tornado.web.HTTPError(400)

        # TODO: Look up user in DB and get the alias / name from that!
        user = UserDTO()
        with DBConnection() as db_connection:
            user = db_connection.user_table.get(queue_item.user_id)

        available_actions = get_available_actions([response['track']], self.get_current_user())[0]

        playback_state.track_length_seconds = track.length / 1000.0
        playback_state.progress_seconds = self.core.playback.get_time_position().get() / 1000.0
        playback_state.progress_percent = playback_state.progress_seconds / playback_state.track_length_seconds if playback_state.track_length_seconds != 0 else 0

        response['queueitem'] = queue_item
        response['user'] = user
        response['actions'] = available_actions

        self.write(json.dumps(response, cls=DTOEncoder))


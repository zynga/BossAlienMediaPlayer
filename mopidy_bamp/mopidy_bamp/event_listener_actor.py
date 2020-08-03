from __future__ import absolute_import, unicode_literals

import urllib
import logging
import pykka
import requests

from mopidy.core import CoreListener
from .history_service import g_history
from .queue_metadata_service import g_queue_metadata
from .database_connection import DBConnection

logger = logging.getLogger("mopidy_bamp")


class EventListenerFrontend(pykka.ThreadingActor, CoreListener):

    def __init__(self, config, core):
        super(EventListenerFrontend, self).__init__()
        self.config = config
        self.core = core
        self.slack_web_hook = None

        if 'slack_web_hook' in config['mopidy_bamp']:
            self.slack_web_hook = config['mopidy_bamp']['slack_web_hook']

            # Default value?
            if self.slack_web_hook == 'SLACK_WEB_HOOK':
                self.slack_web_hook = None

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_failure(self, exception_type, exception_value, traceback):
        pass

    # Called by mopidy for all events
    def on_event(self, name, **data):
        logger.debug("EVENT: {0}".format(name))
        super(EventListenerFrontend, self).on_event(name, **data)

    # Called by mopidy whenever a track is started
    def track_playback_started(self, tl_track):

        track_uri = tl_track.track.uri
        queue_item = g_queue_metadata.get_single_queue_item_dto(track_uri)

        if queue_item is None:
            logger.warning(
                "Track {0} playback started but it has no metadata! Cannot add to history!".format(track_uri))
            return

        g_history.add_track(queue_item, tl_track.track)

        self.post_to_slack(queue_item, tl_track)

    def post_to_slack(self, queue_item, tl_track):

        if self.slack_web_hook is None:
            logger.warning("Not posting to slack, web hook not set, remember to set it in your secrets file!")
            return

        track_name = tl_track.track.name
        artist_strings = []
        for artist in tl_track.track.artists:
            artist_strings.append(artist.name)
        artists = u','.join(artist_strings)
        album = tl_track.track.album.name
        user_alias = queue_item.user_id
        image_url = u"/mopidy_bamp/assets/default-art.png"

        images = self.core.library.get_images([tl_track.track.uri]).get()
        if tl_track.track.uri in images:
            image_tuple = images[tl_track.track.uri]
            image_url = image_tuple[1].uri

        with DBConnection() as db_connection:
            user = db_connection.user_table.get(queue_item.user_id)

            if user is not None:
                user_alias = user.alias

        payload = u'{{ "blocks": [{{ "type": "section","text": {{ "type": "mrkdwn", "text": ">*{0}*\\n>{1}\\n>{2}\\n>Requested by [{3}]" }}, "accessory": {{ "type": "image", "image_url": "{4}", "alt_text": "{2}" }} }}] }}'

        payload = payload.format(track_name, artists, album, user_alias, image_url)
        payload = sanitise_for_slack(payload)

        logger.debug(payload.encode('ascii', 'ignore'))

        # encode utf-8 for Slack - it needs any unicode code points to be in that format
        payload = payload.encode('utf8')

        headers = {'content-type': 'application/json'}

        r = requests.post(self.slack_web_hook, data=payload, headers=headers)

    # called by mopidy
    def track_playback_ended(self, tl_track, time_position):

        track_uri = tl_track.track.uri
        queue_item = g_queue_metadata.get_single_queue_item_dto(track_uri)

        if queue_item is None:
            # can happen if a track failed to play
            logger.warning('Failed to get queue item after track playback ended!')
            return

        g_history.add_track(queue_item, tl_track.track)

        end_time = (time_position / 1000) + queue_item.epoch  # time_position is in ms

        with DBConnection() as db_connection:
            db_connection.stats_played_table.add(queue_item.instance, queue_item.track_uri, queue_item.user_id, end_time)


def sanitise_for_slack(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


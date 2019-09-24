from __future__ import absolute_import, unicode_literals

import json
import tornado.web
import logging
import time
import random

from .dtos import DTOEncoder, TrackDTO, UserDTO
from .images import update_trackdto_list_images
from .base_request_handler import BaseRequestHandler
from .queue_metadata_service import g_queue_metadata
from .playback_service import g_playback
from .history_service import g_history
from .available_actions import get_available_actions
from .queue_ordering import re_order_queue
from .database_connection import DBConnection

logger = logging.getLogger(__package__)


# Request for interacting with the queue
class QueueRequestHandler(BaseRequestHandler):

    # Get the current state of BAMP's queue
    @tornado.web.authenticated
    def get(self):
        tracks = self.core.tracklist.get_tracks().get()

        response = {'tracks': [], 'queueitems': [], 'actions': [], 'users': {}}

        if len(tracks) <= 0:
            self.write(response)
            return

        now_playing_track = self.core.playback.get_current_track().get()

        for track in tracks:
            # Skip the now playing track, we dont want to return it to the client, it uses /api/nowplaying
            if now_playing_track is not None and track.uri == now_playing_track.uri:
                continue

            response['tracks'].append(TrackDTO(track))

        update_trackdto_list_images(self.core, response['tracks'])
        response['queueitems'] = g_queue_metadata.get_all_queue_item_dtos(tracks)

        if now_playing_track is not None:
            response['queueitems'] = filter(lambda t: t.track_uri != now_playing_track.uri, response['queueitems'])

        # Get the user deets from the db
        with DBConnection() as db_connection:
            user_id_list = map(lambda x: x.user_id, response['queueitems'])
            user_dto_dict = db_connection.user_table.get_dict(user_id_list)
            response['users'] = user_dto_dict

        # Work out what actions the local user can use on the tracks and why!
        local_user_id = self.get_current_user()

        response['actions'] = get_available_actions(response['tracks'], local_user_id)

        self.write(json.dumps(response, cls=DTOEncoder))

    # Add a new track to the queue
    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        logger.debug('Queue got JSON data: {0}'.format(data))

        track_uri = data['track_uri']


        # Before adding the track, check the queue to see if it already exists
        tracks = self.core.tracklist.get_tracks().get()

        # We expect the front-end to dis-allow queuing tracks which cannot be queued
        # This means we need to put an allowed to queue state in search
        # results, and everywhere else tracks can be queued.
        in_mopidy_track_list = filter(lambda t: t.uri == track_uri, tracks)

        if in_mopidy_track_list:
            raise tornado.web.HTTPError(400)

        # Stop re-queuing recent items
        if not g_history.can_play_track(track_uri):
            raise tornado.web.HTTPError(400)

        tl_tracks = self.core.tracklist.add(uris=[track_uri]).get()

        if len(tl_tracks) <= 0:
            raise tornado.web.HTTPError(400)

        # Get the latest list of tracks
        tracks = self.core.tracklist.get_tracks().get()
        g_queue_metadata.on_track_queued(tracks, track_uri, self.get_current_user(), False)

        re_order_queue(self.core, tracks, g_history.get_history_dtos())

        # Try to auto-play if it is possible to do so
        g_playback.start_playing_if_possible()

        response = {'success': True}

        self.write(json.dumps(response, cls=DTOEncoder))


class VoteRequestHandler(BaseRequestHandler):

    __vote_types = {'up', 'down'}

    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        logger.debug('vote got JSON data from user {1}: {0}'.format(data, self.get_current_user()))

        track_uri = data['track_uri']
        vote_type = data['vote_type']

        if vote_type not in self.__vote_types:
            raise tornado.web.HTTPError(400)

        tracks = self.core.tracklist.get_tracks().get()

        user_id = self.get_current_user()

        if vote_type == 'up':
            g_queue_metadata.upvote(tracks, track_uri, user_id)
        else:
            g_queue_metadata.downvote(tracks, track_uri, user_id)

            # check if its hit the max downvotes to remove
            num_downvotes_needed = self.config['mopidy_bamp']['downvotes_before_remove']
            track_data_dto = g_queue_metadata.get_single_queue_item_dto(track_uri)

            if track_data_dto is None:
                raise tornado.web.HTTPError(400)

            should_skip = track_data_dto.downvotes >= num_downvotes_needed
            if 'downvotes_difference_before_remove' in self.config['mopidy_bamp']:
                should_skip = track_data_dto.downvotes - track_data_dto.upvotes > self.config['mopidy_bamp']['downvotes_difference_before_remove']

            if should_skip:
                # goodbye
                logger.debug('Track: ' + track_data_dto.track_uri + ' got ' + str(track_data_dto.downvotes) + ' downvotes and is being taken off the play queue.')

                current_track = self.core.playback.get_current_track()
                is_currently_playing = current_track is not None and current_track.get().uri == track_uri

                if is_currently_playing:
                    # Add downvote sound to track list
                    model_refs = self.core.library.browse("file:///var/lib/mopidy/media/downvote_sounds").get()
                    if len(model_refs) > 0:
                        downvote_uri = random.choice(model_refs).uri
                        self.core.tracklist.add(uris=[downvote_uri], at_position=0)
                        tracks = self.core.tracklist.get_tracks().get()
                        g_queue_metadata.on_track_queued(tracks, downvote_uri, "system", True)

                removed_track = RemoveTrack(self.core, track_data_dto.track_uri)

                # Add to history but mark as voted off so it cannot be played again for a while
                g_history.add_track(track_data_dto, removed_track.track, True)

                # add to evicted tracks stats table
                with DBConnection() as db_connection:
                    db_connection.stats_evicted_table.add(track_data_dto.instance, track_data_dto.track_uri,
                                                          track_data_dto.user_id, time.time(),
                                                          is_currently_playing)

                tracks = self.core.tracklist.get_tracks().get()

        re_order_queue(self.core, tracks, g_history.get_history_dtos())

        response = {'success': True}

        self.write(json.dumps(response, cls=DTOEncoder))


def RemoveTrack(core, track_uri):

    tl_tracks_removed = core.tracklist.remove(criteria={'uri': [track_uri]}).get()

    if len(tl_tracks_removed) != 1:
        logger.error("Removed {0} tracks instead of 1!".format(len(tl_tracks_removed)))
        raise tornado.web.HTTPError(500)

    tracks = core.tracklist.get_tracks().get()

    # sync the queue metadata
    g_queue_metadata.remove_track(tracks)

    # Ensure the queue is re-ordered correctly
    re_order_queue(core, tracks, g_history.get_history_dtos())

    # Ensure playback continues (handles currently playing track removed!)
    g_playback.start_playing_if_possible()

    return tl_tracks_removed[0]


class RemoveRequestHandler(BaseRequestHandler):
    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        logger.debug('Remove got JSON data: {0}'.format(data))

        track_uri = data['track_uri']
        track_data_dto = g_queue_metadata.get_single_queue_item_dto(track_uri)

        if track_data_dto is None:
            raise tornado.web.HTTPError(400)

        response = {'success': False}

        if track_data_dto.user_id == self.get_current_user():
            # user matches - can pull track
            logger.debug('Removing track: ' + track_data_dto.track_uri)

            RemoveTrack(self.core, track_uri)

            tracks = self.core.tracklist.get_tracks().get()
            re_order_queue(self.core, tracks, g_history.get_history_dtos())

            response = {'success': True}

        self.write(json.dumps(response, cls=DTOEncoder))

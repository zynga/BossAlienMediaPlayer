
from __future__ import absolute_import, unicode_literals

import logging
import time
import tornado.web

from .base_service import BaseService
from .dtos import TrackDTO, HistoryItemDTO
from .images import update_trackdto_images
logger = logging.getLogger("mopidy_bamp")


class HistoryItem:
    def __init__(self, queue_item_dto, mopidy_track, was_voted_off=False):
        self.track_uri = queue_item_dto.track_uri
        self.user_id = queue_item_dto.user_id

        self.upvotes = queue_item_dto.upvotes
        self.downvotes = queue_item_dto.downvotes

        self.was_voted_off = was_voted_off

        self.epoch = time.time()

        self.track_dto = TrackDTO(mopidy_track)


# Threadsafe, cross-request service which handles the history of tracks played by BAMP
class HistoryService(BaseService):
    def __init__(self):
        # History is stored as a dict (using track uri) for quick querying
        # it is only returned as an ordered list when required
        self.__history = {}

    # Add a track to the history (queue metadata dto & mopidy track). If it is already in the history it is replaced
    def add_track(self, queue_item_dto, mopidy_track, was_voted_off=False):
        self.lock.acquire()

        try:
            if queue_item_dto.is_downvote_sound:
                return
            logger.debug("Adding track {0} to history".format(queue_item_dto.track_uri))

            # Add the item
            history_item = HistoryItem(queue_item_dto, mopidy_track, was_voted_off)
            update_trackdto_images(self.core, history_item.track_dto)
            self.__history[queue_item_dto.track_uri] = history_item

            # Cull history if required
            max_history_count = self.config['mopidy_bamp']['max_history_count']
            if len(self.__history) > max_history_count:
                self.__reduce_history_to_count(max_history_count)

        finally:
            self.lock.release()

    # Check to see if a track can be played, or if it is too soon
    def can_play_track(self, track_uri):
        self.lock.acquire()

        try:
            # If it is not in the history it can be played
            if track_uri not in self.__history:
                return True

            history_item = self.__history[track_uri]

            seconds_before_replay_allowed = self.config['mopidy_bamp']['seconds_before_replay_allowed']

            seconds_since_played = time.time() - history_item.epoch

            return seconds_since_played > seconds_before_replay_allowed

        finally:
            self.lock.release()

    # Check to see if a track was voted off the queue or entered the history normally
    def was_voted_off_queue(self, track_uri):
        self.lock.acquire()

        try:
            # If it is not in the history it can be played
            if track_uri not in self.__history:
                return False

            history_item = self.__history[track_uri]

            return history_item.was_voted_off

        finally:
            self.lock.release()

    # Get all DTOs for the history, in order
    def get_history_dtos(self):
        self.lock.acquire()

        try:
            dtos = []

            for track_uri, history_item in self.__history.iteritems():
                dtos.append(HistoryItemDTO(history_item))

            # Sort them into order based on the time they were added to the history
            dtos.sort(key=lambda x: x.epoch, reverse=True)

            return dtos
        finally:
            self.lock.release()

    # Get all track dtos in the history, order based on history dtos
    def get_track_dtos(self, history_dtos):
        self.lock.acquire()

        try:
            tracks = []

            for history_dto in history_dtos:
                if history_dto.track_uri not in self.__history:
                    raise tornado.web.HTTPError(500)

                track = self.__history[history_dto.track_uri].track_dto
                tracks.append(track)

            return tracks

        finally:
            self.lock.release()

    # Remove the oldest history entries to get back to target size
    def __reduce_history_to_count(self, target_count):

        # We should not need to worry about doing this more than once, but just in case!
        while len(self.__history) > target_count:

            # Find the oldest item
            oldest_item = None
            for track_uri, history_item in self.__history.iteritems():
                if oldest_item is None or history_item.epoch < oldest_item.epoch:
                    oldest_item = history_item

            # Just-in-case
            if oldest_item is None:
                raise tornado.web.HTTPError(500)

            # Remove the item
            del self.__history[oldest_item.track_uri]


g_history = HistoryService()



from __future__ import absolute_import, unicode_literals

import sys
import logging
import time
import uuid
import tornado.web
import functools

from .dtos import QueueItemDTO
from .base_service import BaseService
from .database_connection import DBConnection

logger = logging.getLogger(__package__)


class QueueItem:
    def __init__(self, track_uri, user_id, is_downvote_sound):
        self.track_uri = track_uri
        self.user_id = user_id

        # Set of user_ids for these, so they cannot have the same user present more than once
        self.upvote_ids = set()
        self.downvote_ids = set()

        self.epoch = time.time()

        self.instance = str(uuid.uuid4())

        self.is_downvote_sound = is_downvote_sound


class TrackOrderDetails:
    def __init__(self, track_uri, user_id, upvotes, downvotes, epoch, num_tracks_since_user_last_played, negative_scores_affect_ordering):
        self.track_uri = track_uri
        self.user_id = user_id
        self.vote_diff = (upvotes - downvotes) if negative_scores_affect_ordering else max((upvotes - downvotes), 0)
        self.epoch = epoch
        self.num_tracks_since_user_last_played = num_tracks_since_user_last_played


# Sort the tracks so that we prioritise tracks which have high first-track votes,
# the user has not played tracks for a while, and have most recently queued tracks.
def remaining_tracks_sort(track_a, track_b):

    vote_diff_a = track_a.vote_diff
    vote_diff_b = track_b.vote_diff

    # Same number of votes?
    if vote_diff_a == vote_diff_b:

        # If the number of votes is the same, ensure users who have not have a track played for ages go first
        num_tracks_a = track_a.num_tracks_since_user_last_played
        num_tracks_b = track_b.num_tracks_since_user_last_played

        if num_tracks_a == num_tracks_b:
            # If both users have played tracks for the same number, sort by time placed on the queue
            if track_a.epoch < track_b.epoch:
                return -1
            else:
                return 1
        else:
            if num_tracks_a > num_tracks_b:
                return -1
            else:
                return 1
    else:
        # Primarily sort by the number of votes a track has
        if vote_diff_a > vote_diff_b:
            return -1
        else:
            return 1


# Get the number of tracks since the user last had a track played based on the user id and list of tracks in the history
def get_num_tracks_since_user_last_played(history_dtos, user_id):
    for index, history_dto in enumerate(history_dtos):
        if history_dto.user_id == user_id:
            return index

    # Nothing in the history, we return the max value an int can be!
    return sys.maxsize


# Threadsafe object for interacting with BAMPS queue metadata.
# This is all in-memory metadata. We need to ensure that this stays in sync with mopidy's tracklist
# so it calls __reconcile_with_mopidy for all actions.
class QueueMetadataService(BaseService):
    def __init__(self):
        self.__queue_dict = {}
        self.__enable_owner_voting = True

    # Call this whenever a track is queued to ensure that we have metadata set up for the track.
    def on_track_queued(self, mopidy_track_list, track_uri, user_id, is_downvote_sound):
        self.lock.acquire()

        try:
            # Add to the queue before the reconcile so we can set the user_id associated with
            # the track, as the reconcile will add it with default values
            if track_uri in self.__queue_dict:
                logger.info("Track {0} already in queue metadata, ignoring".format(track_uri))
                return

            logger.info("Track {0} queued by {1}, adding to queue metadata".format(track_uri, user_id))

            new_item = QueueItem(track_uri, user_id, is_downvote_sound)
            self.__queue_dict[track_uri] = new_item

            with DBConnection() as db_connection:
                # track the queue stat
                db_connection.stats_tracks_table.add(new_item.instance, new_item.track_uri, new_item.user_id, new_item.epoch)

            # Finally reconcile
            self.__reconcile_with_mopidy(mopidy_track_list)

        finally:
            self.lock.release()

    # Upvote a track, if the track has already been upvoted by the user it does nothing.
    def upvote(self, mopidy_track_list, track_uri, user_id):
        self.lock.acquire()

        try:
            self.__reconcile_with_mopidy(mopidy_track_list)

            if track_uri not in self.__queue_dict:
                raise tornado.web.HTTPError(400)

            queue_item = self.__queue_dict[track_uri]

            # Users should not vote on their own tracks
            if (not self.config['mopidy_bamp']['allow_vote_on_own_tracks']) and (queue_item.user_id == user_id):
                raise tornado.web.HTTPError(400)

            # Remove previous downvote if it exists
            if user_id in queue_item.downvote_ids:
                queue_item.downvote_ids.remove(user_id)

            # Voting is a toggle so your vote can be removed without requiring
            # a downvote instead
            if user_id not in queue_item.upvote_ids:
                queue_item.upvote_ids.add(user_id)
            else:
                queue_item.upvote_ids.remove(user_id)

        finally:
            self.lock.release()

    # Downvote a track, if the track has already been downvoted by the user it does nothing.
    def downvote(self, mopidy_track_list, track_uri, user_id):
        self.lock.acquire()

        try:
            self.__reconcile_with_mopidy(mopidy_track_list)

            if track_uri not in self.__queue_dict:
                raise tornado.web.HTTPError(400)

            queue_item = self.__queue_dict[track_uri]

            # Users should not vote on their own tracks
            if (not self.config['mopidy_bamp']['allow_vote_on_own_tracks']) and (queue_item.user_id == user_id):
                raise tornado.web.HTTPError(400)

            # Remove previous upvote if it exists
            if user_id in queue_item.upvote_ids:
                queue_item.upvote_ids.remove(user_id)

            # Voting is a toggle so your vote can be removed without requiring
            # an upvote instead
            if user_id not in queue_item.downvote_ids:
                queue_item.downvote_ids.add(user_id)
            else:
                queue_item.downvote_ids.remove(user_id)

        finally:
            self.lock.release()

    # Check to see if a user has upvoted on a track in the queue
    def has_user_upvoted(self, track_uri, user_id):
        self.lock.acquire()

        try:
            if track_uri not in self.__queue_dict:
                return False
            else:
                queue_item = self.__queue_dict[track_uri]
                return user_id in queue_item.upvote_ids
        finally:
            self.lock.release()

    # Check to see if a user has downvoted on a track in the queue
    def has_user_downvoted(self, track_uri, user_id):
        self.lock.acquire()

        try:
            if track_uri not in self.__queue_dict:
                return False
            else:
                queue_item = self.__queue_dict[track_uri]
                return user_id in queue_item.downvote_ids
        finally:
            self.lock.release()

    # Called after removing a track, to get the metadata in sync
    def remove_track(self, mopidy_track_list):
        self.lock.acquire()

        try:
            self.__reconcile_with_mopidy(mopidy_track_list)
        finally:
            self.lock.release()

    # The only exception to the rule that we reconcile is when we just want a single bit of info about
    # a track. We assume the track exists otherwise this will return None
    def get_single_queue_item_dto(self, track_uri):
        self.lock.acquire()

        try:
            if track_uri not in self.__queue_dict:
                return None

            queue_item = self.__queue_dict[track_uri]
            return QueueItemDTO(queue_item)

        finally:
            self.lock.release()

    # Get the current queue metadata as a dto list (after reconciling with mopidy's tracklist)
    # It returns them in an order-correct manner, based on the reconciliation, so the list should
    # represent the input correctly.
    def get_all_queue_item_dtos(self, mopidy_track_list):
        self.lock.acquire()

        try:
            self.__reconcile_with_mopidy(mopidy_track_list)

            queue_item_dtos = []

            for mopidy_track in mopidy_track_list:
                queue_item = self.__queue_dict[mopidy_track.uri]
                queue_item_dtos.append(QueueItemDTO(queue_item))

            return queue_item_dtos
        finally:
            self.lock.release()

    # Return an ordered track listing (list of track uri's) which can be used to
    # order the mopidy tracklist. We do not modify the mopidy queue here as this
    # service keeps metadata, it is not the controller of the mopidy track list.
    # It is up to the caller to implement the ordering based on the returned values.
    def get_suggested_track_ordering(self, mopidy_track_list, history_dtos):
        self.lock.acquire()

        try:
            self.__reconcile_with_mopidy(mopidy_track_list)

            # Nothing to do?
            if len(self.__queue_dict) <= 0:
                return []

            remaining_tracks = []
            num_tracks_since_last_played = {}

            current_track = self.core.playback.get_current_track().get()

            # First generate a list of all tracks we want to sort, with additional metadata
            for index, track in enumerate(mopidy_track_list):

                if track is None:
                    continue

                # We don't reorder the currently playing track
                if current_track is not None and current_track.uri == track.uri:
                    continue

                queue_item = self.__queue_dict[track.uri]
                user_id = queue_item.user_id

                # Add the tracks since played for a user if not in the dict already
                # (this is just an optimisation to avoid searching the history for each track)
                if user_id not in num_tracks_since_last_played:
                    num_tracks_since_last_played[user_id] = get_num_tracks_since_user_last_played(history_dtos, user_id)

                user_num_tracks_since_last_played = num_tracks_since_last_played[user_id]

                remaining_tracks.append(
                    TrackOrderDetails(
                        track.uri,
                        user_id,
                        len(queue_item.upvote_ids),
                        len(queue_item.downvote_ids),
                        queue_item.epoch,
                        user_num_tracks_since_last_played,
                        self.config['mopidy_bamp']['negative_scores_affect_ordering']))

            # This is our output list
            final_uris = []

            # It always starts with the track now playing if there is one
            if current_track is not None:
                final_uris = [current_track.uri]

            # Now the final algorithm goes like this:
            # - While any items on the remaining_tracks list:
            #  1) Sort the list based on vote, then count since the user played a track, then by the queue time
            #  2) Take the first element off the list, and queue it up
            #  3) Get the queued track's user and update their remaining tracks to have a new count since played value

            while len(remaining_tracks) > 0:

                # 1)
                # TODO Python 3 no longer uses cmp functions, must convert
                # remaining_tracks_sort to a key function
                remaining_tracks.sort(key=functools.cmp_to_key(remaining_tracks_sort))

                # 2)
                selected_track = remaining_tracks[0]
                final_uris.append(selected_track.track_uri)

                selected_track_user_id = selected_track.user_id
                del remaining_tracks[0]

                # 3)
                # Negative because we are predicting into the future
                new_num_tracks_since_last_played = -(len(final_uris) - 1)

                for remaining_track in remaining_tracks:
                    if remaining_track.user_id == selected_track_user_id:
                        remaining_track.num_tracks_since_user_last_played = new_num_tracks_since_last_played

            return final_uris
        finally:
            self.lock.release()

    # We need to compare our list to mopidy's track list and update to ensure they stay in sync
    # any tracks missing in our list should be added to our list with default values
    # any tracks in our list but missing in mopidy's should be removed from our list
    # all other tracks can be left
    def __reconcile_with_mopidy(self, mopidy_track_list):

        # Remove any entries in our metadata not in mopidy
        uris_to_remove = []
        for uri, queue_item in self.__queue_dict.iteritems():
            in_mopidy_track_list = filter(lambda t: t.uri == uri, mopidy_track_list)

            if not in_mopidy_track_list:
                uris_to_remove.append(uri)

        for uri in uris_to_remove:
            logger.info("Track {0} in queue metadata but not mopidy, removing".format(uri))
            del self.__queue_dict[uri]

        # Add any tracks in mopidy but not in our metadata
        for mopidy_track in mopidy_track_list:
            if mopidy_track.uri not in self.__queue_dict:
                logger.warning("Track {0} missing from queue metadata, adding".format(mopidy_track.uri))
                self.__queue_dict[mopidy_track.uri] = QueueItem(mopidy_track.uri, "", "local:" in mopidy_track.uri)


g_queue_metadata = QueueMetadataService()

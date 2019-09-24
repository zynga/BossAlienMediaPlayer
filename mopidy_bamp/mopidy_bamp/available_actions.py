
from __future__ import absolute_import, unicode_literals

from .dtos import AvailableTrackActionsDTO, TrackActionReasons, TrackActions
from .queue_metadata_service import g_queue_metadata
from .history_service import g_history


def get_available_actions(track_dtos, local_user_id):
    action_list = []

    for track_dto in track_dtos:

        actions = []
        reasons = []

        # Users not logged in have no actions available
        if local_user_id is None:
            reasons.append(TrackActionReasons.NOT_LOGGED_IN)
            available_actions = AvailableTrackActionsDTO(track_dto.uri, actions, reasons)
            action_list.append(available_actions)
            continue

        # Is the track in the queue?
        queue_dto = g_queue_metadata.get_single_queue_item_dto(track_dto.uri)

        if queue_dto is not None:
            # Yes? It could possibly be voted on or removed, but not added!
            reasons.append(TrackActionReasons.ON_QUEUE)

            if queue_dto.user_id == local_user_id:
                # Owner cannot vote, only remove from queue
                actions.append(TrackActions.REMOVE)
                reasons.append(TrackActionReasons.OWNER)
            else:
                # Could be voted on, allow both vote actions
                # as they toggle that vote type & remove the opposite vote type
                actions.append(TrackActions.UPVOTE)
                actions.append(TrackActions.DOWNVOTE)

                if g_queue_metadata.has_user_upvoted(track_dto.uri, local_user_id):
                    reasons.append(TrackActionReasons.VOTED_UP)

                if g_queue_metadata.has_user_downvoted(track_dto.uri, local_user_id):
                    reasons.append(TrackActionReasons.VOTED_DOWN)
        else:
            # Not in the queue, it could be added if possible!
            # Check the history!
            if g_history.can_play_track(track_dto.uri):
                actions.append(TrackActions.QUEUE)
            else:
                # Can't play the track, what is the reason?
                if g_history.was_voted_off_queue(track_dto.uri):
                    reasons.append(TrackActionReasons.VOTED_OFF_QUEUE)
                else:
                    reasons.append(TrackActionReasons.TOO_SOON)

        available_actions = AvailableTrackActionsDTO(track_dto.uri, actions, reasons)
        action_list.append(available_actions)

    return action_list


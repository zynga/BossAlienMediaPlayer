from __future__ import absolute_import, unicode_literals

from json import JSONEncoder


# Data about an artist which is a subset of mopidy's Artist object which the frontend requires.
class ArtistDTO:
    def __init__(self, mopidy_artist):
        self.name = mopidy_artist.name
        self.uri = mopidy_artist.uri


# Data about an album which is a subset of mopidy's Album object which the frontend requires.
class AlbumDTO:
    def __init__(self, mopidy_album):
        self.name = mopidy_album.name
        self.uri = mopidy_album.uri
        self.artists = []
        for mopidy_artist in mopidy_album.artists:
            self.artists.append(ArtistDTO(mopidy_artist))
        self.images = []


# Data about a track, which is a subset of mopidy's Track object which the frontend requires.
class TrackDTO:
    def __init__(self, mopidy_track):
        self.uri = mopidy_track.uri
        self.name = mopidy_track.name
        self.artists = []
        for mopidy_artist in mopidy_track.artists:
            self.artists.append(ArtistDTO(mopidy_artist))
        self.images = []
        self.length = mopidy_track.length
        self.album = AlbumDTO(mopidy_track.album)

        if "downvote_sounds" in self.uri:
            self.is_downvote_sound = True
            return
        self.is_downvote_sound = False


# Data about a single user of BAMP
class UserDTO:
    def __init__(self, id="", alias=""):
        self.user_id = id
        self.alias = alias


# Data about an item in BAMP's pending queue
class QueueItemDTO:
    def __init__(self, queue_item):
        self.track_uri = queue_item.track_uri
        self.user_id = queue_item.user_id
        self.upvotes = len(queue_item.upvote_ids)
        self.downvotes = len(queue_item.downvote_ids)
        self.instance = queue_item.instance
        self.epoch = queue_item.epoch
        self.is_downvote_sound = queue_item.is_downvote_sound


# Playback state contains both the mopidy playback state, but also
# BAMP's own playback enabled state.
class PlaybackStateDTO:
    def __init__(self, mopidy_state="invalid", playback_enabled=False):
        self.mopidy_state = mopidy_state
        self.playback_enabled=playback_enabled
        self.track_length_seconds = 0.0
        self.progress_seconds = 0.0
        self.progress_percent = 0.0

# Data about a track in the history
class HistoryItemDTO:
    def __init__(self, history_item):
        self.track_uri = history_item.track_uri
        self.user_id = history_item.user_id

        self.upvotes = history_item.upvotes
        self.downvotes = history_item.downvotes

        self.was_voted_off = history_item.was_voted_off

        self.epoch = history_item.epoch


# List of actions available per track
class TrackActions:
    QUEUE = 'queue'         # User can queue the track
    REMOVE = 'remove'       # User can remove the track from the queue
    UPVOTE = 'upvote'       # User can upvote the track
    DOWNVOTE = 'downvote'   # User can downvote the track


# List of reasons for allowing/disallowing actions per track
class TrackActionReasons:
    ON_QUEUE = 'on_queue'                   # Track is already on the queue so cannot be queued again!
    OWNER = 'owner'                         # User is the owner, cannot vote, but can remove
    TOO_SOON = 'too_soon'                   # Its too soon to be able to queue
    VOTED_OFF_QUEUE = 'voted_off_queue'     # Its too soon to be able to queue as it was voted off the queue
    VOTED_UP = 'voted_up'                   # User already voted up
    VOTED_DOWN = 'voted_down'               # User already voted down
    NOT_LOGGED_IN = 'not_logged_in'         # User is not logged in!


# List of available actions, and the list of reasons actions are available/not available
class AvailableTrackActionsDTO:

    def __init__(self, track_uri, actions, reasons):
        self.track_uri = track_uri
        self.actions = actions
        self.reasons = reasons


# JSON encoder for our custom DTO types which returns all fields of the object instance!
class DTOEncoder(JSONEncoder):
    def default(self, z):
        if isinstance(z, TrackDTO):
            return z.__dict__
        if isinstance(z, AlbumDTO):
            return z.__dict__
        if isinstance(z, ArtistDTO):
            return z.__dict__
        if isinstance(z, UserDTO):
            return z.__dict__
        if isinstance(z, QueueItemDTO):
            return z.__dict__
        if isinstance(z, PlaybackStateDTO):
            return z.__dict__
        if isinstance(z, HistoryItemDTO):
            return z.__dict__
        if isinstance(z, AvailableTrackActionsDTO):
            return z.__dict__
        else:
            return JSONEncoder.default(self, z)


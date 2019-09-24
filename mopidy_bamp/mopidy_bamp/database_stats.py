from .database_table import DBTable

import logging

logger = logging.getLogger(__package__)


# TODO - ADD DATE & TIME COLUMN FOR WHEN IT HAPPENED

# track tracks stats
class StatsQueuedTracksTable(DBTable):
    table_name = "StatsQueuedTracksTable"
    column_key = "Key" # 1
    column_track_instance = "TrackInstance" # guid for track
    column_track_id = "TrackUri" # spotify:blahblah
    column_requester_id = "Requester" # ccarr
    column_time = "Time"

    def create_table(self):
        command = u"CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT, {2} TEXT UNIQUE, {3} TEXT, {4} TEXT, {5} INTEGER)".format(
            self.table_name,
            self.column_key,
            self.column_track_instance,
            self.column_track_id,
            self.column_requester_id,
            self.column_time
        )

        logger.debug('db command:' + command)

        self.connection.execute(command)
        self.connection.commit()

    def add(self, track_instance, track_uri, requester_id, time):
        command = u'INSERT INTO {0}({1}, {2}, {3}, {4}) values (?, ?, ?, ?)'.format(
            self.table_name,
            self.column_track_instance,
            self.column_track_id,
            self.column_requester_id,
            self.column_time
        )

        logger.debug('db command:' + command)

        self.connection.execute(command, (track_instance, track_uri, requester_id, time))
        self.connection.commit()


class StatsPlayedTracksTable(DBTable):
    table_name = "StatsPlayedTracksTable"
    column_key = "Key" # 1
    column_track_instance = "TrackInstance" # guid for track
    column_track_id = "TrackUri" # spotify:blahblah
    column_requester_id = "Requester" # ccarr
    column_time = "Time" # time it finished playing.

    def create_table(self):
        command = u"CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT, {2} TEXT UNIQUE, {3} TEXT, {4} TEXT, {5} INTEGER)".format(
            self.table_name,
            self.column_key,
            self.column_track_instance,
            self.column_track_id,
            self.column_requester_id,
            self.column_time
        )

        logger.debug('db command:' + command)

        self.connection.execute(command)
        self.connection.commit()

    def add(self, track_instance, track_uri, requester_id, time):
        command = u'INSERT INTO {0}({1}, {2}, {3}, {4}) values (?, ?, ?, ?)'.format(
            self.table_name,
            self.column_track_instance,
            self.column_track_id,
            self.column_requester_id,
            self.column_time
        )

        logger.debug('db command:' + command)

        self.connection.execute(command, (track_instance, track_uri, requester_id, time))
        self.connection.commit()

class StatsEvictedTracksTable(DBTable):
    table_name = "StatsEvictedTracksTable"
    column_key = "Key"  # 1
    column_track_instance = "TrackInstance"  # guid for track
    column_track_id = "TrackUri"  # spotify:blahblah
    column_requester_id = "Requester"  # ccarr
    column_time = "Time"  # time it finished playing.
    column_was_playing = "WasPlaying"  # was the track playing when it was evicted

    def create_table(self):
        command = u"CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT, {2} TEXT UNIQUE, {3} TEXT, {4} TEXT, {5} INTEGER, {6} INTEGER)".format(
            self.table_name,
            self.column_key,
            self.column_track_instance,
            self.column_track_id,
            self.column_requester_id,
            self.column_time,
            self.column_was_playing
        )

        logger.debug('db command:' + command)

        self.connection.execute(command)
        self.connection.commit()

    def add(self, track_instance, track_uri, requester_id, time, was_playing):
        command = u'INSERT INTO {0}({1}, {2}, {3}, {4}, {5}) values (?, ?, ?, ?, ?)'.format(
            self.table_name,
            self.column_track_instance,
            self.column_track_id,
            self.column_requester_id,
            self.column_time,
            self.column_was_playing
        )

        logger.debug('db command:' + command)

        self.connection.execute(command, (track_instance, track_uri, requester_id, time, int(was_playing)))
        self.connection.commit()
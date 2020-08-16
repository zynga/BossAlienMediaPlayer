from os import path
import os
import sqlite3

import logging

from .dtos import UserDTO
from .database_stats import StatsQueuedTracksTable, StatsPlayedTracksTable, StatsEvictedTracksTable
from .database_table import DBTable

logger = logging.getLogger(__package__)


class UserTable(DBTable):
    table_name = "UserTable"
    column_key = "UserKey" # 1
    column_id = "UserId" # ccarr
    column_alias = "Alias" # MrRiooooo

    # user id - key, incrementing int
    # user name - onelogin name, e.g. 'ccarr' - unique

    def create_table(self):
        command = u'CREATE TABLE IF NOT EXISTS {0} ({1} INTEGER PRIMARY KEY AUTOINCREMENT, {2} TEXT UNIQUE, {3} TEXT)'.format(
            self.table_name,
            self.column_key,
            self.column_id,
            self.column_alias
        )

        logger.debug('db command:' + command)

        self.connection.execute(command)
        self.connection.commit()

    def add(self, user_id, alias):

        command = u'INSERT INTO {0}({1}, {2}) values (?, ?)'.format(
            self.table_name,
            self.column_id,
            self.column_alias,
        )

        logger.debug('db command:' + command)

        self.connection.execute(command, (user_id, alias))
        self.connection.commit()

    def update(self, user_id, alias):
        '''UPDATE table_name
        SET column1 = value1, column2 = value2, ...
        WHERE condition;'''

        command = u'UPDATE {0} \nSET {1} = ?\nWHERE {2} = ?'.format(
            self.table_name,
            self.column_alias,
            self.column_id
        )

        logger.debug('db command:' + command)

        self.connection.execute(command, (alias, user_id))
        self.connection.commit()

    def row_to_user_dto(self, row_tuple):
        user = UserDTO(id=row_tuple[1], alias=row_tuple[2])
        return user

    def exists(self, user_id):
        return self.get(user_id) is not None

    def get(self, user_id):
        command = u'SELECT * FROM {0} WHERE {1} = ?'.format(
            self.table_name,
            self.column_id
        )

        #logger.debug('db command:' + command)

        cur = self.connection.cursor()
        cur.execute(command, (user_id,))
        ret_tup = None
        try:
            ret_tup = cur.fetchone()
        finally:
            cur.close()

        if ret_tup is None or len(ret_tup) < 3:
            return None

        return self.row_to_user_dto(ret_tup)

    # returns mapping of user id -> user dto
    def get_dict(self, user_id_list):
        quoted_user_id_list = ['"' + x + '"' for x in user_id_list]
        quoted_user_string = ', '.join(quoted_user_id_list)
        replacement_string = ','.join('?' * len(list(user_id_list))) # number of question marks - one for each id

        command = u'SELECT * FROM {0} WHERE {1} IN ({2})'.format(
            self.table_name,
            self.column_id,
            replacement_string
        )

        #logger.debug("command: " + command)

        cur = self.connection.cursor()
        cur.execute(command, tuple(user_id_list))

        user_dto_dict = {}

        try:
            while True:
                ret_tup = cur.fetchone()

                if ret_tup is None:
                    break

                user_dto_dict[ret_tup[1]] = self.row_to_user_dto(ret_tup)
        finally:
            cur.close()

        return user_dto_dict


class DBConnection:

    user_table = None
    stats_tracks_table = None
    stats_played_table = None
    stats_evicted_table = None

    db_path = '/var/lib/mopidy/database/bamp.db'

    def __enter__(self):
        db_dir = path.dirname(self.db_path)

        if not path.exists(db_dir):
            os.makedirs(db_dir)

        self.connection = sqlite3.connect(self.db_path)
        self.user_table = UserTable(self.connection)
        self.stats_tracks_table = StatsQueuedTracksTable(self.connection)
        self.stats_played_table = StatsPlayedTracksTable(self.connection)
        self.stats_evicted_table = StatsEvictedTracksTable(self.connection)

        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()

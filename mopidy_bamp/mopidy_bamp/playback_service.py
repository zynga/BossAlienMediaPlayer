
from __future__ import absolute_import, unicode_literals

import logging
import mopidy
import threading
import time

from .base_service import BaseService

logger = logging.getLogger("mopidy_bamp")


def timer_thread():
    while True:
        time.sleep(2)
        g_playback.start_playing_if_possible()


# Threadsafe, cross-request service which handles playback state
class PlaybackService(BaseService):
    def __init__(self):
        self.__playback_enabled = True
        self.__timerThread = threading.Thread(target=timer_thread)
        self.__timerThread.daemon = True
        self.__timerThread.start()

    # Enable playback, and start playing
    def enable_playback(self):
        acquired = self.acquire_lock()
        if not acquired:
            logger.debug('Lock not acquired')
            return

        try:
            if not self.__playback_enabled:
                self.__playback_enabled = True
                self.core.tracklist.set_consume(True)
                self.core.playback.play()
        finally:
            self.release_lock()

    # Disable playback, and pause anything currently playing
    def disable_playback(self):
        acquired = self.acquire_lock()
        if not acquired:
            logger.debug('Lock not acquired')
            return

        try:
            if self.__playback_enabled:
                self.__playback_enabled = False
                self.core.playback.pause()
        finally:
            self.release_lock()

    # Check to see if playback is enabled or not
    def get_playback_enabled(self):
        acquired = self.acquire_lock()
        if not acquired:
            logger.debug('Lock not acquired')
            return True

        try:
            return self.__playback_enabled
        finally:
            self.release_lock()

    # Start playing, if playback is enabled, does nothing if it is not enabled
    def start_playing_if_possible(self):
        if not self.initialised:
            return
        
        try:
            acquired = self.acquire_lock()
            if not acquired:
                logger.debug('Lock not acquired')
                return
        except:
            logger.debug('Lock not created yet')
            return

        try:

            if self.__playback_enabled:
                should_play = self.core.playback.get_state().get() != mopidy.core.PlaybackState.PLAYING \
                                or self.core.playback.get_current_track().get() is None

                if should_play:
                    self.core.tracklist.set_consume(True)
                    self.core.playback.play()

        finally:
            self.release_lock()


g_playback = PlaybackService()

from mopidy.audio import AudioListener, PlaybackState

import logging
import pykka

logger = logging.getLogger("mopidy_bamp")

class AudioListenerFrontend(pykka.ThreadingActor, AudioListener):

    def __init__(self, config, core):
        super(AudioListenerFrontend, self).__init__()
        self.config = config
        self.core = core
    
    def state_changed(self, old_state:PlaybackState, new_state:PlaybackState, target_state:PlaybackState | None):
        # TODO - Once we can identify how a "Position query failed" occurs here we can do something about that
        logger.debug(f"State has changed (old_state: {old_state}, new_state: {new_state}, target_state: {target_state})")
from __future__ import absolute_import, unicode_literals

import logging

from .queue_metadata_service import g_queue_metadata

logger = logging.getLogger("mopidy_bamp")


def re_order_queue(core, mopidy_track_list, history_dtos):
    # Only one track? It should be the now-playing track so ignore!
    if len(mopidy_track_list) <= 1:
        return

    ordered_track_uris = g_queue_metadata.get_suggested_track_ordering(mopidy_track_list, history_dtos)
    logger.debug('Ordered tracks list ({1}): {0}'.format(ordered_track_uris, len(ordered_track_uris)))
    logger.debug('Mopidy playlist ({1}): {0}'.format(map(lambda t: t.uri, mopidy_track_list), len(mopidy_track_list)))
    logger.debug('Currently playing song index: {0}'.format(get_track_index(core, ordered_track_uris[0])))

    rear_index = len(mopidy_track_list) - 1

    # Go through each track in the ordered track uris (not the first one)
    # and move it to the back from its current position (which will change every loop).
    # This is the simplest way to order the mopidy queue but is a bit heavy-handed! :)
    for track_uri in ordered_track_uris:
        current_track_index = get_track_index(core, track_uri)
        if "file://" in track_uri:
            core.tracklist.move(current_track_index, current_track_index, 0)
            continue
        core.tracklist.move(current_track_index, current_track_index, rear_index)


def get_track_index(core, track_uri):
    tl_tracklist = core.tracklist.filter({'uri': [track_uri]}).get()

    # Confirm we found the track?
    if tl_tracklist is None or len(tl_tracklist) <= 0:
        return -1

    # Now get the index!
    return core.tracklist.index(tl_tracklist[0]).get()


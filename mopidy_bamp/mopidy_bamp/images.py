from __future__ import absolute_import, unicode_literals


# Update a list of TrackDTOs with images
def update_trackdto_list_images(core, tracks):
    if len(tracks) <= 0:
        return

    image_search_uris = []

    for track in tracks:
        image_search_uris.append(track.uri)

        # We used to set the album images but this caused errors, might be because they were
        # not supported on spotify?
        #image_search_uris.append(track.album.uri)

    images = core.library.get_images(image_search_uris).get()

    for track in tracks:
        if hasattr(track, 'album') == False:
            continue
        set_trackdto_images(track, images)


# Update a single TrackDTO with images
def update_trackdto_images(core, track):

    # downvote sounds don't have albums but count as tracks
    if hasattr(track, 'album') == False:
        return
    image_search_uris = [track.uri]

    # We used to set the album images but this caused errors, might be because they were
    # not supported on spotify?
    #image_search_uris.append(track.album.uri)

    images = core.library.get_images(image_search_uris).get()

    set_trackdto_images(track, images)


# Set images for a TrackDTO given a dictionary of uri to image tuple
def set_trackdto_images(track, images):
    if track.uri in images:
        image_tuple = images[track.uri]

        for image in image_tuple:
            track.images.append(image.uri)

    set_albumdto_images(track.album, images)


# Set images for an AlbumDTO given a dictionary of uri to image tuple
def set_albumdto_images(album, images):
    if album.uri in images:
        image_tuple = images[album.uri]

        for image in image_tuple:
            album.images.append(image.uri)






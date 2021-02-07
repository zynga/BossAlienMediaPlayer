from __future__ import absolute_import, unicode_literals

import json
import logging
import tornado.web

from .images import update_trackdto_list_images
from .dtos import TrackDTO, DTOEncoder
from .base_request_handler import BaseRequestHandler
from .available_actions import get_available_actions

logger = logging.getLogger(__package__)


# All search options we support. Default is the first entry.
class SearchOptions:
    all_search_options = ['any', 'track_name', 'album', 'artist', 'uri']


# Request handler for searching mopidy's backend and returning a list of TrackDTOs based on the search terms.
class SearchRequestHandler(BaseRequestHandler):

    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        logger.debug('Search got JSON data: {0}'.format(data))

        response = {'tracks': []}

        search_text = data['search_text']

        if search_text.strip() == '':
            self.write(json.dumps(response, cls=DTOEncoder))
            return

        search_option = SearchOptions.all_search_options[0]
        exact_match = False

        if 'search_option' in data:
            search_option = data['search_option']

            if search_option not in SearchOptions.all_search_options:
                raise tornado.web.HTTPError(400)

        if 'exact_match' in data:
            exact_match = data['exact_match']

        search_terms = search_text.split()

        # uris should include all providers we wish to search through. When the field is ommitted, we can also search for local files, which will break things
        search_results = self.core.library.search({search_option: search_terms}, uris=['spotify:'], exact=exact_match).get()

        num_search_results = len(search_results)

        if num_search_results <= 0:
            self.write(response)
            return

        for search_result in search_results:
            tracks = search_result.tracks
            for track in tracks:
                response['tracks'].append(TrackDTO(track))

        update_trackdto_list_images(self.core, response['tracks'])

        response['actions'] = get_available_actions(response['tracks'], self.get_current_user())

        self.write(json.dumps(response, cls=DTOEncoder))


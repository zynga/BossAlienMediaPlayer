from __future__ import absolute_import, unicode_literals

import os
import logging

import tornado.web
from tornado.web import RedirectHandler
from mopidy import ext, config

from .search_request_handler import SearchRequestHandler
from .login_request_handler import LoginRequestHandler, LogoutRequestHandler
from .is_logged_in_request_handler import IsLoggedInRequestHandler
from .queue_request_handlers import QueueRequestHandler, VoteRequestHandler, RemoveRequestHandler
from .playback_handlers import EnablePlaybackRequestHandler, DisablePlaybackRequestHandler, NowPlayingRequestHandler
from .playback_service import PlaybackService, g_playback
from .queue_metadata_service import QueueMetadataService, g_queue_metadata
from .history_service import g_history
from .history_request_handlers import HistoryRequestHandler
from .config_request_handler import ConfigRequestHandler
from .user_request_handlers import UpdateUserDetailsRequestHandler, GetUserDetailsRequestHandler
from .database_connection import DBConnection

__version__ = '0.1'

logger = logging.getLogger(__package__)


def bamp_factory(config, core):
    if not config['mopidy_bamp']['csrf_protection']:
        logger.warn('HTTP Cross-Site Request Forgery protection is disabled')
    
    # Create cross-request services. These services need to be thread safe
    g_playback.init(core, config)
    g_queue_metadata.init(core, config)
    g_history.init(core, config)

    handler_args = {'core': core, 'config': config}

    return [
        (r'/', RedirectHandler, {'url': 'index.html'}),
        (r'/api/search', SearchRequestHandler, handler_args),
        (r'/api/login', LoginRequestHandler, handler_args),
        (r'/api/logout', LogoutRequestHandler, handler_args),
        (r'/api/isloggedin', IsLoggedInRequestHandler, handler_args),
        (r'/api/queue', QueueRequestHandler, handler_args),
        (r'/api/vote', VoteRequestHandler, handler_args),
        (r'/api/remove', RemoveRequestHandler, handler_args),
        (r'/api/enableplayback', EnablePlaybackRequestHandler, handler_args),
        (r'/api/disableplayback', DisablePlaybackRequestHandler, handler_args),
        (r'/api/nowplaying', NowPlayingRequestHandler, handler_args),
        (r'/api/history', HistoryRequestHandler, handler_args),
        (r'/api/updateuser', UpdateUserDetailsRequestHandler, handler_args),
        (r'/api/getuser', GetUserDetailsRequestHandler, handler_args),
        (r'/api/config/([^/]+)', ConfigRequestHandler, handler_args),

        (r'/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),
    ]


class BAMPExtension(ext.Extension):

    dist_name = 'mopidy_bamp'
    ext_name = 'mopidy_bamp'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(BAMPExtension, self).get_config_schema()
        schema['hostname'] = config.Hostname()
        schema['port'] = config.Port()
        schema['zeroconf'] = config.String(optional=True)
        schema['allowed_origins'] = config.List(optional=True)
        schema['csrf_protection'] = config.Boolean(optional=True)
        schema['xheaders_enabled'] = config.Boolean(optional=False)
        schema['cookie_secret'] = config.Secret()
        schema['ldap_uri'] = config.Secret()
        schema['ldap_schema'] = config.Secret()
        schema['downvotes_before_remove'] = config.Integer(minimum=1)
        schema['downvotes_difference_before_remove'] = config.Integer(optional=True)
        schema['allow_vote_on_own_tracks'] = config.Boolean(optional=False)
        schema['negative_scores_affect_ordering'] = config.Boolean(optional=False)
        schema['seconds_before_replay_allowed'] = config.Integer(minimum=0)
        schema['max_history_count'] = config.Integer(minimum=1)
        schema['max_alias_length'] = config.Integer(minimum=1)
        schema['slack_web_hook'] = config.String(optional=False)
        schema['build_hash'] = config.String(optional=False)
        schema['icecast_url'] = config.String(optional=True)
        schema['use_ldap_starttls'] = config.Boolean(optional=False)
        schema['ldap_certificate_path'] = config.String(optional=False)

        return schema

    def validate_environment(self):
        try:
            import tornado.web  # noqa
        except ImportError as e:
            raise exceptions.ExtensionError('tornado library not found', e)

    def setup(self, registry):
        from .actor import HttpFrontend
        from .event_listener_actor import EventListenerFrontend

        with DBConnection() as db_connection:
            db_connection.user_table.create_table()
            db_connection.stats_tracks_table.create_table()
            db_connection.stats_played_table.create_table()
            db_connection.stats_evicted_table.create_table()

        HttpFrontend.apps = registry['http:app']
        HttpFrontend.statics = registry['http:static']

        registry.add('frontend', HttpFrontend)
        registry.add('frontend', EventListenerFrontend)
        registry.add('http:app', {
            'name': self.ext_name,
            'factory': bamp_factory,
        })

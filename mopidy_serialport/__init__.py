from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.0'

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-SerialPort'
    ext_name = 'serialport'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['port'] = config.String()
        schema['baud'] = config.Integer()
        schema['channels'] = config.List()
        schema['min_volume'] = config.Integer()
        schema['max_volume'] = config.Integer()
        schema['volume_step'] = config.Integer()
        schema['enable_noise'] = config.Boolean()
        return schema

    def setup(self, registry):
        from .frontend import SerialPortFrontend
        registry.add('frontend', SerialPortFrontend)


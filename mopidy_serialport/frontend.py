import pykka
import serial
import logging
from mopidy import core

logger = logging.getLogger(__name__)

MAX_VOLUME = 100
VOLUME_STEP = 5
MIN_VOLUME = 0

class SerialPortFrontend(pykka.ThreadingActor, core.CoreListener):
    
    def __init__(self, config, core):
        super(SerialPortFrontend, self).__init__()
        self.config = config['serialport']
        self.core = core
        self.running = False
        self.volume = core.mixer.get_volume()
        self.channel = 0
        self.channels = self.config['channels']
        logger.info('Available channels:')
        for channel in self.config['channels']:
            logger.info(channel)

    def on_start(self):
        logger.info('[serialport] on start')
        self.connect()
        self.loop()

    def on_stop(self):
	logger.info('[serialport] on stop')
        self.disconnect()

    def connect(self):
        try:
            self.arduino = serial.Serial(self.config['port'], self.config['baud'], timeout=1)
            # signal we're ready
            self.arduino.write('OK\n\r')
            self.running = True
        except:
            logger.error('[serialport] Could not connect to serial port ' + self.config['port'])

    def disconnect(self):
        self.arduino.close()
        self.running = False

    def set_volume(self, volume):
        # normalize
        if volume > 0:
            volume = max(volume, MAX_VOLUME)
        if volume < 0:
            volume = min(volume, MIN_VOLUME)
        try:
            if volume != self.volume:
                logger.debug('[serialport] Setting volume to ' + str(volume))
                self.core.mixer.set_volume(volume)
                self.volume = volume
        except:
            logger.error('[serialport] Failed to set volume to ' + str(volume))
            pass

    def set_channel(self, direction):
        channel = (self.channel + direction) % len(self.channels)
        try:
            if channel != self.channel:
                # get channel uri from config
                channel_uri = self.config['channels'][channel]
                logger.info('[serialport] Channel URI: ' + channel_uri)
                # stop playback, clear tracklist, load new tracks, play
                self.core.playback.stop()
                logger.info('[serialport] stopped playback')
                self.core.tracklist.clear()
                logger.info('[serialport] cleared tracklist')
                self.core.tracklist.add(uris=[channel_uri])
                logger.info('[serialport] added tracks from channel')
                self.core.playback.play()
                self.channel = channel
        except:
            logger.error('Failed to set channel to ' + str(channel))
            pass

    def handle_message(self, message):
        try:
            if message == 'V+' and self.volume < MAX_VOLUME:
                self.set_volume(VOLUME_STEP)
            if message == 'V-' and self.volume > MIN_VOLUME:
                self.set_volume(VOLUME_STEP * -1)
            if message == 'C+':
                self.set_channel(1)
            if message == 'C-':
                self.set_channel(-1)
        except BaseException as e:
            logger.error('[serialport] Could not handle serial message "' + message + '"')
            logger.error(e)
            pass

    def loop(self):
        message = 'noop';
        while self.running:
            message = self.arduino.readline()
            if len(message) > 0:
                # strip newline
                self.handle_message(message.rstrip())

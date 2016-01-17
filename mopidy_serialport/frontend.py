import pykka
import serial
import logging
from mopidy import core

logger = logging.getLogger(__name__)

MAX_VOLUME = 100
VOLUME_STEP = 2
MIN_VOLUME = 0

def flatten(listOfLists):
    return reduce(list.__add__, listOfLists)

class SerialPortFrontend(pykka.ThreadingActor, core.CoreListener):
    
    def __init__(self, config, core):
        super(SerialPortFrontend, self).__init__()
        self.config = config['serialport']
        self.core = core
        self.running = False
        self.volume = core.mixer.get_volume().get()
	if self.volume == None:
            self.volume = 100
            core.mixer.set_volume(self.volume)
        self.channel = 0
        self.channels = self.config['channels']
        logger.info('Available channels:')
        for channel in self.config['channels']:
            logger.info(channel)

    def on_start(self):
        logger.info('[serialport] on start')
        self.connect()
        self.set_channel(1)
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

    def set_volume(self, step):
        # normalize
        volume = self.volume + step
        if step > 0:
            volume = min(volume, MAX_VOLUME)
        if step < 0:
            volume = max(volume, MIN_VOLUME)
        try:
            if volume != self.volume:
                logger.info('[serialport] Setting volume to ' + str(volume))
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
                channel_uri = self.channels[channel]
                logger.info('[serialport] Switching to channel: ' + channel_uri)

                tracks = flatten(map(lambda ref: self.core.library.lookup(ref.uri).get(), self.core.library.browse(channel_uri).get()))
                self.core.tracklist.add(tracks=tracks, at_position=0).get()
                tracklist = self.core.tracklist.get_tl_tracks().get()
                self.core.playback.play(tl_track=tracklist[0])
                self.channel = channel
        except BaseException as e:
            logger.error('Failed to set channel to ' + str(channel))
            logger.error(e)
            pass

    def handle_message(self, message):
        logger.info('[serialport] incoming message "' + message + '"')
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

import pykka
import serial
import logging
from mopidy import core

logger = logging.getLogger(__name__)

class SerialPortFrontend(pykka.ThreadingActor, core.CoreListener):
    
    def __init__(self, config, core):
        super(SerialPortFrontend, self).__init__()
        self.config = config['serialport']
        self.core = core
        self.running = False
        self.volume = core.mixer.get_volume()
        self.channel = 1

    def on_start(self):
        self.connect()
        self.loop()

    def on_stop(self):
        self.disconnect()

    def connect(self):
        try:
            self.arduino = serial.Serial(self.config['port'], self.config['baud'], timeout=1)
            # signal we're ready
            self.arduino.write('OK\n\r')
            self.running = True
        except:
            logger.error('Could not connect to serial port')

    def disconnect(self):
        self.arduino.close()
        self.running = False

    def set_volume(self, volume):
        try:
            if volume != self.volume:
                self.core.mixer.set_volume(volume)
                self.volume = volume
                logger.debug('Volume: ' + volume)
        except:
            logger.error('Failed to set volume to ' + volume)
            pass

    def set_channel(self, channel):
        try:
            if channel != self.channel:
                # get channel uri from config
                channel_uri = self.config['channels'][channel]
                # stop playback, clear tracklist, load new tracks, play
                self.core.playback.stop()
                self.core.tracklist.clear()
                self.core.tracklist.add(uris=[channel_uri])
                self.core.playback.play()
                self.channel = channel
                logger.debug('Channel: ' + channel)
        except:
            logger.error('Failed to set channel to ' + channel)
            pass

    def handle_message(self, message):
        try:
            if message[0] == 'V':
                self.set_volume(int(message[1:]))
            if message[0] == 'C':
                self.set_channel(int(message[1:]))
        except:
            logger.error('Could not handle serial message "' + message + '"')
            pass

    def loop(self):
        message = 'noop';
        while self.running:
            message = self.arduino.readline()
            if len(message) > 0:
                self.handle_message(message)

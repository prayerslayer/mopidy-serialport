import pykka
import serial
import logging
import pygame
import os
from time import sleep
from mopidy import core

logger = logging.getLogger(__name__)

class SerialPortFrontend(pykka.ThreadingActor, core.CoreListener):
    
    def __init__(self, config, core):
        super(SerialPortFrontend, self).__init__()
        self.config = config['serialport']
        self.core = core
        self.make_noise = self.config['enable_noise']
        pygame.init()
        self.noise = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), 'noise.mp3'))
        self.running = False
        self.channels = self.config['channels']

    def on_start(self):
        self.connect()
        self.set_channel(0)
        self.loop()

    def on_stop(self):
        self.disconnect()

    def connect(self):
        try:
            self.arduino = serial.Serial(
                port=self.config['port'],
                baudrate=self.config['baud']
            )
            # signal we're ready
            sleep(3)
            self.arduino.write('OK\n\r')
            self.running = True
        except:
            logger.error('[serialport] Could not connect to serial port ' + self.config['port'])

    def disconnect(self):
        self.arduino.close()
        self.running = False

    def set_volume(self, step):
        # normalize
        volume = self.core.mixer.get_volume().get() + step
        if step > 0:
            volume = min(volume, self.config['max_volume'])
        if step < 0:
            volume = max(volume, self.config['min_volume'])
        try:
            logger.info('[serialport] Setting volume to ' + str(volume))
            self.core.mixer.set_volume(volume)
        except:
            logger.error('[serialport] Failed to set volume to ' + str(volume))
            pass

    def set_channel(self, channel):
        try:
            # get channel uri from config
            channel_uri = self.channels[channel]
            logger.info('[serialport] Switching to channel: ' + channel_uri)

            self.core.playback.stop()
            if self.make_noise:
                self.noise.play(loops=-1, fade_ms=2000)

            refs = self.core.library.browse(channel_uri).get()
            tl_tracks = self.core.tracklist.add(at_position=0, uris=[ref.uri for ref in refs]).get()
            self.core.playback.play(tl_track=tl_tracks[0]).get()
            if self.make_noise:
                sleep(4)
                self.noise.fadeout(2000)

        except Exception as e:
            logger.error('Failed to set channel to %s: %s', channel, e)
            pass

    def handle_message(self, message):
        logger.debug('[serialport] incoming message "' + message + '"')
        volume_step = self.config['volume_step']
        try:
            if message == 'V+':
                self.set_volume(volume_step)
            if message == 'V-':
                self.set_volume(volume_step * -1)
            if message[0] == 'C':
                self.set_channel(int(message[1:]))
        except BaseException as e:
            logger.error('[serialport] Could not handle serial message "%s": %s', message, e)
            pass

    def loop(self):
        message = 'noop';
        while self.running:
            message = self.arduino.readline()
            if len(message) > 0:
                # strip newline
                self.handle_message(message.rstrip())

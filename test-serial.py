import serial

arduino = serial.Serial(
    port='/dev/cu.usbmodem1421',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS)

while True:
    arduino.write('OK\n\r')
    line = arduino.readline()
    print str(len(line)) + ': ' + line

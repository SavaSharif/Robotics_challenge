#!/usr/bin/env python
# coding: Latin-1

# Creates a web-page interface for YetiBorg v2

# Import library functions we need
# import ZeroBorg
import ZeroBorg3 as ZeroBorg
import time
import sys
import threading
import SocketServer
import picamera
import picamera.array
import cv2
import datetime

# Settings for the web-page
webPort = 80                            # Port number for the web-page, 80 is what web-pages normally use
imageWidth = 240                        # Width of the captured image in pixels
imageHeight = 180                       # Height of the captured image in pixels
frameRate = 10                          # Number of images to capture per second
displayRate = 2                         # Number of images to request per second
photoDirectory = '/home/pi'             # Directory to save photos to
flippedImage = True                     # True if the camera needs to be rotated

# Global values
global ZB
global lastFrame
global lockFrame
global camera
global processor
global running
global watchdog
running = True

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x44                  # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print('No ZeroBorg found, check you are attached :)')
    else:
        print('No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress))
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the IÂ²C address change the setup line so it is correct, e.g.')
        print('ZB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()
#ZB.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.SetCommsFailsafe(False)
ZB.ResetEpo()
ZB.SetLed(False)

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Timeout thread
class Watchdog(threading.Thread):
    def __init__(self):
        super(Watchdog, self).__init__()
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.timestamp = time.time()

    def run(self):
        timedOut = True
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for a network event to be flagged for up to one second
            if timedOut:
                if self.event.wait(1):
                    # Connection
                    print('Reconnected...')
                    timedOut = False
                    self.event.clear()
            else:
                if self.event.wait(1):
                    self.event.clear()
                else:
                    # Timed out
                    print('Timed out...')
                    timedOut = True
                    ZB.MotorsOff()

# Image stream processing thread
class StreamProcessor(threading.Thread):
    def __init__(self):
        super(StreamProcessor, self).__init__()
        self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.begin = 0

    def run(self):
        global lastFrame
        global lockFrame
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    # Read the image and save globally
                    self.stream.seek(0)
                    if flippedImage:
                        flippedArray = cv2.flip(self.stream.array, -1) # Flips X and Y
                        retval, thisFrame = cv2.imencode('.jpg', flippedArray)
                        del flippedArray
                    else:
                        retval, thisFrame = cv2.imencode('.jpg', self.stream.array)
                    lockFrame.acquire()
                    lastFrame = thisFrame
                    lockFrame.release()
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

# Image capture thread
class ImageCapture(threading.Thread):
    def __init__(self):
        super(ImageCapture, self).__init__()
        self.start()

    def run(self):
        global camera
        global processor
        print('Start the stream using the video port')
        camera.capture_sequence(self.TriggerStream(), format='bgr', use_video_port=True)
        print('Terminating camera processing...')
        processor.terminated = True
        processor.join()
        print('Processing terminated.')

    # Stream delegation loop
    def TriggerStream(self):
        global running
        while running:
            if processor.event.is_set():
                time.sleep(0.01)
            else:
                yield processor.stream
                processor.event.set()

# Class used to implement the web server
class WebServer(SocketServer.BaseRequestHandler):
    def handle(self):
        global ZB
        global lastFrame
        global watchdog
        # Get the HTTP request data
        reqData = self.request.recv(1024).strip()
        reqData = reqData.split('')
        # Get the URL requested
        getPath = ''
        for line in reqData:
            if line.startswith('GET'):
                parts = line.split(' ')
                getPath = parts[1]
                break
        watchdog.event.set()
        if getPath.startswith('/cam.jpg'):
            # Camera snapshot
            lockFrame.acquire()
            sendFrame = lastFrame
            lockFrame.release()
            if sendFrame != None:
                self.send(sendFrame.tostring())
        elif getPath.startswith('/off'):
            # Turn the drives off
            httpText = '<html><body><center>'
            httpText += 'Speeds: 0 %, 0 %'
            httpText += '</center></body></html>'
            self.send(httpText)
            ZB.MotorsOff()
        elif getPath.startswith('/set/'):
            # Motor power setting: /set/driveLeft/driveRight
            parts = getPath.split('/')
            # Get the power levels
            if len(parts) >= 4:
                try:
                    driveLeft = float(parts[2])
                    driveRight = float(parts[3])
                except:
                    # Bad values
                    driveRight = 0.0
                    driveLeft = 0.0
            else:
                # Bad request
                driveRight = 0.0
                driveLeft = 0.0
            # Ensure settings are within limits
            if driveRight < -1:
                driveRight = -1
            elif driveRight > 1:
                driveRight = 1
            if driveLeft < -1:
                driveLeft = -1
            elif driveLeft > 1:
                driveLeft = 1
            # Report the current settings
            percentLeft = driveLeft * 100.0;
            percentRight = driveRight * 100.0;
            httpText = '<html><body><center>'
            httpText += 'Speeds: %.0f %%, %.0f %%' % (percentLeft, percentRight)
            httpText += '</center></body></html>'
            self.send(httpText)
            # Set the outputs
            driveLeft *= maxPower
            driveRight *= maxPower
            ZB.SetMotor1(-driveRight * maxPower) # Rear right
            ZB.SetMotor2(-driveRight * maxPower) # Front right
            ZB.SetMotor3(-driveLeft  * maxPower) # Front left
            ZB.SetMotor4(-driveLeft  * maxPower) # Rear left
        elif getPath.startswith('/photo'):
            # Save camera photo
            lockFrame.acquire()
            captureFrame = lastFrame
            lockFrame.release()
            httpText = '<html><body><center>'
            if captureFrame != None:
                photoName = '%s/Photo %s.jpg' % (photoDirectory, datetime.datetime.utcnow())
                try:
                    photoFile = open(photoName, 'wb')
                    photoFile.write(captureFrame)
                    photoFile.close()
                    httpText += 'Photo saved to %s' % (photoName)
                except:
                    httpText += 'Failed to take photo!'
            else:
                httpText += 'Failed to take photo!'
            httpText += '</center></body></html>'
            self.send(httpText)
        elif getPath == '/':
            # Main page, click buttons to move and to stop
            httpText = '<html>'
            httpText += '<head>'
            httpText += '<script language="JavaScript"><!--'
            httpText += 'function Drive(left, right) {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' var slider = document.getElementById("speed");'
            httpText += ' left *= speed.value / 100.0;'
            httpText += ' right *= speed.value / 100.0;'
            httpText += ' iframe.src = "/set/" + left + "/" + right;'
            httpText += '}'
            httpText += 'function Off() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/off";'
            httpText += '}'
            httpText += 'function Photo() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/photo";'
            httpText += '}'
            httpText += '//--></script>'
            httpText += '</head>'
            httpText += '<body>'
            httpText += '<iframe src="/stream" width="100%" height="500" frameborder="0"></iframe>'
            httpText += '<iframe id="setDrive" src="/off" width="100%" height="50" frameborder="0"></iframe>'
            httpText += '<center>'
            httpText += '<button onclick="Drive(-1,1)" style="width:200px;height:100px;"><b>Spin Left</b></button>'
            httpText += '<button onclick="Drive(1,1)" style="width:200px;height:100px;"><b>Forward</b></button>'
            httpText += '<button onclick="Drive(1,-1)" style="width:200px;height:100px;"><b>Spin Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Drive(0,1)" style="width:200px;height:100px;"><b>Turn Left</b></button>'
            httpText += '<button onclick="Drive(-1,-1)" style="width:200px;height:100px;"><b>Reverse</b></button>'
            httpText += '<button onclick="Drive(1,0)" style="width:200px;height:100px;"><b>Turn Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Off()" style="width:200px;height:100px;"><b>Stop</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Photo()" style="width:200px;height:100px;"><b>Save Photo</b></button>'
            httpText += '<br /><br />'
            httpText += '<input id="speed" type="range" min="0" max="100" value="100" style="width:600px" />'
            httpText += '</center>'
            httpText += '</body>'
            httpText += '</html>'
            self.send(httpText)
        elif getPath == '/hold':
            # Alternate page, hold buttons to move (does not work with all devices)
            httpText = '<html>'
            httpText += '<head>'
            httpText += '<script language="JavaScript"><!--'
            httpText += 'function Drive(left, right) {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' var slider = document.getElementById("speed");'
            httpText += ' left *= speed.value / 100.0;'
            httpText += ' right *= speed.value / 100.0;'
            httpText += ' iframe.src = "/set/" + left + "/" + right;'
            httpText += '}'
            httpText += 'function Off() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/off";'
            httpText += '}'
            httpText += 'function Photo() {'
            httpText += ' var iframe = document.getElementById("setDrive");'
            httpText += ' iframe.src = "/photo";'
            httpText += '}'
            httpText += '//--></script>'
            httpText += '</head>'
            httpText += '<body>'
            httpText += '<iframe src="/stream" width="100%" height="500" frameborder="0"></iframe>'
            httpText += '<iframe id="setDrive" src="/off" width="100%" height="50" frameborder="0"></iframe>'
            httpText += '<center>'
            httpText += '<button onmousedown="Drive(-1,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Spin Left</b></button>'
            httpText += '<button onmousedown="Drive(1,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Forward</b></button>'
            httpText += '<button onmousedown="Drive(1,-1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Spin Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onmousedown="Drive(0,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Turn Left</b></button>'
            httpText += '<button onmousedown="Drive(-1,-1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Reverse</b></button>'
            httpText += '<button onmousedown="Drive(1,0)" onmouseup="Off()" style="width:200px;height:100px;"><b>Turn Right</b></button>'
            httpText += '<br /><br />'
            httpText += '<button onclick="Photo()" style="width:200px;height:100px;"><b>Save Photo</b></button>'
            httpText += '<br /><br />'
            httpText += '<input id="speed" type="range" min="0" max="100" value="100" style="width:600px" />'
            httpText += '</center>'
            httpText += '</body>'
            httpText += '</html>'
            self.send(httpText)
        elif getPath == '/stream':
            # Streaming frame, set a delayed refresh
            displayDelay = int(1000 / displayRate)
            httpText = '<html>'
            httpText += '<head>'
            httpText += '<script language="JavaScript"><!--'
            httpText += 'function refreshImage() {'
            httpText += ' if (!document.images) return;'
            httpText += ' document.images["rpicam"].src = "cam.jpg?" + Math.random();'
            httpText += ' setTimeout("refreshImage()", %d);' % (displayDelay)
            httpText += '}'
            httpText += '//--></script>'
            httpText += '</head>'
            httpText += '<body onLoad="setTimeout(\'refreshImage()\', %d)">' % (displayDelay)
            httpText += '<center><img src="/cam.jpg" style="width:640;height:480;" name="rpicam" /></center>'
            httpText += '</body>'
            httpText += '</html>'
            self.send(httpText)
        else:
            # Unexpected page
            self.send('Path : "%s"' % (getPath))

    def send(self, content):
        self.request.sendall('HTTP/1.0 200 OK%s' % (content))


# Create the image buffer frame
lastFrame = None
lockFrame = threading.Lock()

# Startup sequence
print('Setup camera')
camera = picamera.PiCamera()
camera.resolution = (imageWidth, imageHeight)
camera.framerate = frameRate

print('Setup the stream processing thread')
processor = StreamProcessor()

print('Wait ...')
time.sleep(2)
captureThread = ImageCapture()

print('Setup the watchdog')
watchdog = Watchdog()

# Run the web server until we are told to close
httpServer = SocketServer.TCPServer(("0.0.0.0", webPort), WebServer)
try:
    print('Press CTRL+C to terminate the web-server')
    while running:
        httpServer.handle_request()
except KeyboardInterrupt:
    # CTRL+C exit
    print('User shutdown')
finally:
    # Turn the motors off under all scenarios
    ZB.MotorsOff()
    print('Motors off')
# Tell each thread to stop, and wait for them to end
running = False
captureThread.join()
processor.terminated = True
watchdog.terminated = True
processor.join()
watchdog.join()
del camera
ZB.SetLed(True)
print('Web-server terminated.')
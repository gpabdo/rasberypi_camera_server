import socket
import time
import picamera
import errno

# Start a socket listening for connections on 0.0.0.0:8000 
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

print "Server started on port 8000"

while True:
    try:
        # Accept a single connection and make a file-like object out of it
        #connection = server_socket.accept()[0].makefile('rb')
        remote, address = server_socket.accept()
        connection = remote.makefile('rb')

        print "Connection Accepted from:", address[0]

        # Setup the camera
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 24
            # Start a preview and let the camera warm up for 2 seconds
            camera.start_preview()
            time.sleep(2)
            # Start recording, sending the output to the connection for 60
            # seconds, then stop
            camera.start_recording(connection, format='h264')
            camera.wait_recording()

    except socket.error, e:
        if e[0] == errno.EPIPE:
            # remote peer disconnected
            print "Detected remote disconnect"
            pass

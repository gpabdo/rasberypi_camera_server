import io
import socket
import struct
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

        while True:
            # Setup the camera
            with picamera.PiCamera() as camera:
                camera.resolution = (640, 480)
                camera.start_preview()
                time.sleep(2)

                # Note the start time and construct a stream to hold image data
                # temporarily (we could write it directly to connection but in this
                # case we want to find out the size of each capture first to keep
                # our protocol simple)
                start = time.time()
                stream = io.BytesIO()
                for foo in camera.capture_continuous(stream, 'jpeg'):
                    # Write the length of the capture to the stream and flush to
                    # ensure it actually gets sent
                    connection.write(struct.pack('<L', stream.tell()))
                    connection.flush()

                    # Rewind the stream and send the image data over the wire
                    stream.seek(0)
                    connection.write(stream.read())

                    # Reset the stream for the next capture
                    stream.seek(0)
                    stream.truncate()

                connection.write(struct.pack('<L', 0))

    except socket.error, e:

        if e[0] == errno.EPIPE:
            # remote peer disconnected
            print "Detected remote disconnect"
            pass
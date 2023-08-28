from audioop import add
from math import e
from re import T
from shlex import join
import sys
import socket
import threading

"""
    TCP Proxy:
        used for:
            forwarding tarffic to bounce from host to host 
            assessing network-based software
            see unknown protocols
            modify traffic being sent to an application
            create test cases for fuzzers
        
        has four main functions
            hexdump: display the communication between the local and remote machines to the console
            receive_from: receive data from an incoming socket from either the local or romote machine
            proxy_handler: manage the traffic direction between remote and local machines
            server_loop: set up a listening socket and pass it to our proxy_handler
"""

# string that contains ASCII printable characters, '.' if representation not exist
# using Boolean short-ciruit technique 
# if length of the corresponding character equals 3, get the character (chr(i)), else get the dot (.)
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
)
# provides a way to watch the communication going through the proxy in real time
# input: bytes or string
# output: print a hexdump to the console
# output the packet details with both their hexadecimal values and ASCII-printable 
def hexdump(src, length=16, show=True):
    # if have string => decoding the bytes if a byte string was passed 
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        # grab a piece of the string to dump and put it into the 'word' var
        word = str(src[i:i+length])

        # use 'translate' built-in function to substitute the string representation of each character for the corresponding character in the raw string (printable)
        printable = word.translate(HEX_FILTER)
        hexa = ''.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        # substitute the hex representation of the integer value of evrey character in the raw string(hexa)
        # create a new array to hold the string, 'results', that contains the hex value of the index of the first byte in the word, printable the representation 
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')

    if show:
        for line in results:
            print(line)
        else:
            return results
        
# tow ends of the prowy will use to receive data
# for receiving both local and remote data, pass in the socket obj to be used
def receive_from(connection):
    buffer = b""
    # empty string 'buffer', that will accumulate responses from the socket
    # by default, set 5 second time-out 
    connection.settimeout(5)
    try:
        #set up a loop to read response data into 'buffer'
        # until no more data or we time out 
        while True:
            data = connection(4096)
            if not data:
                break
            buffer +=data
    except Exception as e:
        pass
    # return 'buffer' byte string to the caller
    return buffer

# modify the response or request packets before the proxy sends them on their way
# like: fuzzing tasks, test for auth issues, ...
def request_handler(buffer):
    #preform packet modification
    return buffer

def response_handler(buffer):
    #preform packet modification
    return buffer

# bulk of the logic for our proxy
# to start off, we connect to the remote host
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # check to make sure we don't need to first initiate a connection to the remote side
    # request data before going into the main loop
    # FTP: server send a banner first for exemple
    if receive_first:
        # use recieve_from function for both sides of communication
        # accepts a connected socket obj and perfroms a recieve
        remote_buffer = receive_from(remote_socket)
        # dump the contents of the packet so that we can inspect it for anything intersting
        hexdump(remote_buffer)

    # hand the output to the 'response_handler' function and
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        # send the received buffer to the local client
        client_socket.send(remote_buffer)
    
    while True:
        # read from the local client
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from mocalhost;" % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            # process the data, send it to remote cilent 
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")
        
        # read from the remote client
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            # process the dats, send it to the on either side of the connection
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")
        
        # close both the local and remote socket and break out of the loop
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

# function creates a socket
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # binds to the local host and lostens
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    # main loop
    while True:
        # connection request comes
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], add[1])
        print(line)
        # start a thread to talk to hte remote host (hand off to the 'proxy_handler' in a new thread
        # does all the sending and receiving of juicy bitro either side of the data stream
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

# take same command line arguments and start server loop
def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./TCP_Proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [reveive_first]")
        print("Example: ./TCP_Proxy 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
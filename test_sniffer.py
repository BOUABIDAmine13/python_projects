import socket
import os

# host to listen on
HOST = '192.168.100.203'

def main():
    # create row socket, bin to public interface
    # check if machine is windows (sniffe on all protocols) or linux (sniffe on ICMP packet onely)
    if os.name =='nt':
        socket_prorocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((HOST,0))
    # include IP header in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
    # read one packet
    print(sniffer.recvfrom(65565))

    # if turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctk(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == '__main__':
    main()
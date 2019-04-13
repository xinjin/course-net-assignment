#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    # print "sending on interface %s to %s" % (iface, str(addr))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    src_port = random.randint(49152,65535)
    pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=src_port) / sys.argv[2]
    print "src_port", src_port
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()

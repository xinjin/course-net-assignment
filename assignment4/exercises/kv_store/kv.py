#!/usr/bin/python


import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import sniff
from scapy.all import ShortField, IntField, LongField, BitField, ByteField

import sys

class KeyValue(Packet):
    name = "KeyValue"
    fields_desc = [
        ByteField("type", 0),
        IntField("key", 0),
        IntField("value", 0),
    ]

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
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print "Usage: kv.py [type] [parameters]"
        print "For example: kv.py get 0"
        print "             kv.py put 1 10"
        sys.exit(1)

    iface = get_if()
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    # pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
    pkt = pkt /IP() / TCP(dport=100, sport=random.randint(49152,65535))
    if (sys.argv[1] == 'get'):
        pkt = pkt / KeyValue(type = 1, key = int(sys.argv[2]))
    elif (sys.argv[1] == 'put'):
        pkt = pkt / KeyValue(type = 2, key = int(sys.argv[2]), value = int(sys.argv[3]))
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)

if __name__ == '__main__':
    main()

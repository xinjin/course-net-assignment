###############################################################################
# receiver.py
# Name:
# JHED ID:
###############################################################################

import sys
import socket

from util import *

def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))
    while True:
        # receive packet
        pkt, address = s.recvfrom(2048)

        # extract header and payload
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        # verify checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        if pkt_checksum != computed_checksum:
            print "checksums not match"

        # print payload
        print msg

def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()

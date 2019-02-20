###############################################################################
# sender.py
# Name:
# JHED ID:
###############################################################################

import sys
import socket

from util import *

def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pkt_header = PacketHeader(type=2, seq_num=10, length=14)
    pkt_header.checksum = compute_checksum(pkt_header / "Hello, world!\n")
    pkt = pkt_header / "Hello, world!\n"
    s.sendto(str(pkt), (receiver_ip, receiver_port))

def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, window_size)

if __name__ == "__main__":
    main()

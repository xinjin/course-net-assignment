# Assignment 2: Reliable Transport

### Due: Friday, March 8

## Overview

In this project, you will build a simple reliable transport protocol, RTP, **on top of UDP**. Your RTP implementation must provide in­ order, reliable delivery of UDP datagrams in the presence of events like packet loss, delay, corruption, duplication, and re­ordering.

**This assignment can be done individually or in groups of 2 students.**

There are a variety of ways to ensure a message is reliably delivered from a sender to a receiver. You are to implement a sender (`sender`) and a receiver (`receiver`) that follows the following RTP specification.

### RTP Specification
RTP sends data in the format of a header, followed by a chunk of data.

RTP has four header types: `START`, `END`, `DATA`, and `ACK`, all following the same format:

```
PacketHeader:
  int type;      // 0: START; 1: END; 2: DATA; 3: ACK
  int seq_num;   // Described below
  int length;    // Length of data; 0 for ACK, START and END packets
  int checksum;  // 32-bit CRC
```

To initiate a connection, `sender` starts with a `START` message along with a random `seq_num` value, and wait for an ACK for this `START` message. After sending the `START` message, additional packets in the same connection are sent using the `DATA` message type, adjusting `seq_num` appropriately. After everything has been transferred, the connection should be terminated with `sender` sending an `END` message, and waiting for the corresponding ACK for this message.

The ACK `seq_num` values for `START` and `END` messages should both be set to whatever the `seq_num` values are that were sent by `sender`.

`sender` will use 0 as the initial sequence number for data packets in that connection.

### Packet Size
An important limitation is the maximum size of your packets. The UDP protocol has an 8 byte header, and the IP protocol underneath it has a header of 20 bytes. Because we will be using Ethernet networks, which have a maximum frame size of 1500 bytes, this leaves 1472 bytes for your entire `packet` structure (including both the header and the chunk of data).

### Outline

Overall, this assignment has the following components:

* [Part 1](#part1): Implement `sender`
* [Part 2](#part2): Implement `receiver`
* [Part 3](#part3): Optimizations
* [Important notes](#tips)
* [Submission Instructions](#submission-instr)

Similar to assignement 1, we provide scaffolding code in `sender_reciver`. We use the same VM as assignment 1.

* Use `vagrant up` to boot the VM.
* Use `vagrant ssh` to log into the VM.
* Use `vagrant suspend` to save the state of the VM and stop it.
* Use `vagrant halt` to gracefully shutdown the VM operating system and power down the VM.
* Use `sudo pip install scapy` in the VM to install `scapy` package required by this assignment.

## Learning Outcomes

After completing this programming assignment, students should be able to:

* Explain the mechanisms required to reliably transfer data
* Describe how different sliding window protocols work

<a name="part1"></a>
## Part 1: Implement `sender`

`sender` should read an input message and transmit it to a specified receiver using UDP sockets following the RTP protocol. It should split the input message into appropriately sized chunks of data, and append a `checksum` to each packet. `seq_num` should increment by one for each additional packet in a connection. Please use the 32-bit CRC header we provide in `sender_receiver/util.py`, in order to add a checksum to your packet.

You will implement reliable transport using a sliding window mechanism. The size of the window (`window-size`) will be specified in the command line. `sender` must accept cumulative `ACK` packets from `receiver`.

After transferring the entire message, you should send an `END` message to mark the end of connection.

`sender` must ensure reliable data transfer under the following network conditions:

* Loss of arbitrary levels;
* Re­ordering of ACK messages;
* Duplication of any amount for any packet;
* Delay in the arrivals of ACKs.

To handle cases where `ACK` packets are lost, you should implement a 500 milliseconds retransmission timer to automatically retransmit packets that were never acknowledged.
Whenever the window moves forward (i.e., some ACK(s) are received and some new packets are sent out), you reset the timer. If after 500ms the window still has not advanced, you retransmit all packets in the window because they are all never acknowledged.

### Running `sender`
`sender` should be invoked as follows:

`python sender.py [Receiver IP] [Receiver Port] [Window Size] < [Message]`

* `Receiver IP`: The IP address of the host that `receiver` is running on.
* `Receiver Port`: The port number on which `receiver` is listening.
* `Window Size`: Maximum number of outstanding packets.
* `Message`: The message to be transferred. It can be a text as well as a binary message.


<a name="part2"></a>
## Part 2: Implement `receiver`

`receiver` needs to handle only one `sender` at a time and should ignore `START` messages while in the middle of an existing connection. It must receive and store the message sent by the sender on disk completely and correctly.

`receiver` should also calculate the checksum value for the data in each `packet` it receives using the header mentioned in part 1. If the calculated checksum value does not match the `checksum` provided in the header, it should drop the packet (i.e. not send an ACK back to the sender).

For each packet received, it sends a cumulative `ACK` with the `seq_num` it expects to receive next. If it expects a packet of sequence number `N`, the following two scenarios may occur:

1. If it receives a packet with `seq_num` not equal to `N`, it will send back an `ACK` with `seq_num=N`. Note that this is slightly different from the Go-Back-N (GBN) mechanism discussed in class. GBN totally discards out-of-order packets, while here `receiver` buffers out-of-order packets. The mechanism here is more efficient than GBN.
2. If it receives a packet with `seq_num=N`, it will check for the highest sequence number (say `M`) of the in­order packets it has already received and send `ACK` with `seq_num=M+1`.

If the next expected `seq_num` is `N`, `receiver` will drop all packets with `seq_num` greater than or equal to `N + window_size` to maintain a `window_size` window.

Put the programs written in parts 1 and 2 of this assignment into a folder called `RTP-base`.

### Running `receiver`
`receiver` should be invoked as follows:
`python receiver.py [Receiver Port] [Window Size] > Message`

* `Receiver Port`: The port number on which `receiver` is listening for data.
* `Window Size`: Maximum number of outstanding packets.
* `Message`: The received message received.

<a name="part3"></a>
## Part 3: Optimizations

For this part of the assignment, you will be making a few modifications to the programs written in the previous two sections. Consider how the programs written in the previous sections would behave for the following case where there is a window of size 3:

<img src="base_case.PNG" title="Inefficient transfer of data" alt="" width="250" height="250"/>

In this case `receiver` would send back two ACKs both with the sequence number set to 0 (as this is the next packet it is expecting). This will result in a timeout in `sender` and a retransmission of packets 0, 1 and 2. However, since `receiver` has already received and buffered packets 1 and 2. Thus, there is an unnecessary retransmission of these packets.

In order to account for situations like this, you will be modifying your `receiver` and `sender` accordingly (save these different versions of the program in a folder called `RTP-opt`):

* `receiver` will not send cumulative ACKs anymore; instead, it will send back an ACK with `seq_num` set to whatever it was in the data packet (i.e., if a sender sends a data packet with `seq_num` set to 2, `receiver` will also send back an ACK with `seq_num` set to 2). It should still drop all packets with `seq_num` greater than or equal to `N + window_size`, where `N` is the next expected `seq_num`.
* `sender` must maintain information about all the ACKs it has received in its current window and maintain an individual timer for each packet. So, for example, packet 0 having a timeout would not necessarily result in a retransmission of packets 1 and 2.

For a more concrete example, here is how your improved `sender` and `receiver` should behave for the case described at the beginning of this section:

<img src="improvement.PNG" title="only ACK necessary data" alt="" width="250" height="250"/>

`receiver` individually ACKs both packet 1 and 2.

<img src="improvement_2.PNG" title="only send unACKd data" alt="" width="250" height="250"/>

`sender` receives these ACKs and denotes in its buffer that packets 1 and 2 have been received. Then, the it waits for the 500 ms timeout and only retransmits packet 0 again.

The command line parameters passed to these new `sender` and `receiver` are the same as the previous two sections.

<a name="tips"></a>
## Impotant Notes

* **Please closely follow updates on Piazza**. All further clarifications will be posted on Piazza via pinned Instructor Notes. We recommend you **follow** these notes to receive updates in time.
* You **MUST NOT** use TCP sockets.
* We are **NOT** providing any test cases. You can take a look at the test script in assignment 1, and write your own test script.

<a name="submission-instr"></a>
## Submission Instructions

You must submit:

* The source code for `sender` and `receiver` from parts 1 and 2: all source files should be in a folder called `RTP-base`.
* The source code for `sender` and `receiver` from part 3: all source files should be in a folder called `RTP-opt`.
* Submit the assignment by uploading your files to [Gradescope](https://www.gradescope.com/). Join the course with entry code 95KRDN.

## Additional Challenges

For students that find this assignment not challenging enough, you can

* Complete it individually.
* Complete it with C.
* Allow the receiver to receive messages from multiple concurrent senders.
* Add congestion control to the sender and receiver, so that the sender and receiver can figure out the sizes of their sliding windows by themselves.
* Implement different congestion control algorithms, and compare their pros and cons.
* Design your own congestion control algorithms. You can try crazy ideas like using deep learning to learn good congestion control algorithms.

## Acknowledgements
This programming assignment is based on UC Berkeley's Project 2 from EE 122: Introduction to Communication Networks.

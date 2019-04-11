# Assignment 4: P4 and Mininet

### Due: Wednesday, May 1st

## Deliverables

Submit your source code for the two exercises, in two separate folders `acl` and `load_balance`, and together in one
`assignment4.zip` file. For every exercise, submit the p4 code and the corresponding json file that configures the table entries.

You can try implementing key-value store for bonus. The maximal bonus can be 2 points. Submit your p4 code and the corresponding json file in a folder called `kv_store` in the zip file.

## Introduction

This assignment includes 2 exercises: *Access Control List*
and *Load Balance*. Both exercises assume that you possess basic networking
knowledge and some familiarity with the P4 language. Please take a look at the
[P4 language spec](https://p4.org/p4-spec/docs/P4-16-v1.1.0-spec.pdf).
*Access Control List* asks you to write a P4 program to implement an ACL on a switch. *Load Balance* asks you to write a P4 program to implement a form of load balancing based on a simple version of Equal-Cost Multipath Forwarding. We use P4_16 in this assignment.


## Obtaining required software

to complete the exercises, you will need to either build a
virtual machine or install several dependencies.

To build the virtual machine:
- Install [Vagrant](https://vagrantup.com) and [VirtualBox](https://virtualbox.org)
- git clone https://github.com/xinjin/course-net-assignment.git
- `cd assignment4/vm`
- `vagrant up`. This will take about 1 hour or even longer.
- Log in with username `p4` and password `p4` and issue the command `sudo shutdown -r now`
- When the machine reboots, you should have a graphical desktop machine with the required
software pre-installed.

*Note: Before running the `vagrant up` command, make sure you have enabled virtualization in your environment; otherwise you may get a "VT-x is disabled in the BIOS for both all CPU modes" error. Check [this](https://stackoverflow.com/questions/33304393/vt-x-is-disabled-in-the-bios-for-both-all-cpu-modes-verr-vmx-msr-all-vmx-disabl) for enabling it in virtualbox and/or BIOS for different system configurations.

You will need the script to execute to completion before you can see the `p4` login on your virtual machine's GUI. In some cases, the `vagrant up` command brings up only the default `vagrant` login with the password `vagrant`. Dependencies may or may not have been installed for you to proceed with running P4 programs. Please try from the beginning again.*

To install dependencies by hand, please reference the [vm](../vm) installation scripts.
They contain the dependencies, versions, and installation procedure.
You should be able to run them directly on an Ubuntu 16.04 machine, although note that the scripts currently assume the existence of a directory `/home/vagrant`:
- `sudo ./root-bootstrap.sh`
- `sudo ./user-bootstrap.sh`

## Exercise 1: Access Control List

Place yourself in the `assignment4/exercises/acl` directory.

### Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`acl.p4`, which initially forwards all packets. Your job will be to
extend this skeleton program to properly implement an ACL with two rules.

- drop all the UDP packets with dstPort=80
- drop all the packets with dstIP=10.0.1.4

Before that, let's compile the incomplete `acl.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   make run
   ```
   This will:
   * compile `acl.p4`, and
   * start a Mininet instance with one switch (`s1`) connected to four host (`h1`, `h2`, `h3` and `h4`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.1.2`, `10.0.1.3` and `10.0.1.4`.

2. You should now see a Mininet command prompt. Open two terminals
for `h1` and `h2`, respectively:
   ```bash
   mininet> xterm h1 h2
   ```
3. Each host includes a small Python-based messaging client and
server. In `h2`'s xterm, start the server:
   ```bash
   ./receive.py
   ```
4. In `h1`'s xterm, send a message to `h2`:
   ```bash
   ./send.py 10.0.1.2 "P4 is cool"
   ```
   The message will be received and displayed in `h2`.
5. Type `exit` to leave each xterm and the Mininet command line.
   Then, to stop mininet:
   ```bash
   make stop
   ```
   And to delete all pcaps, build files, and logs:
   ```bash
   make clean
   ```

### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules
within each table are inserted by the control plane. When a rule
matches a packet, its action is invoked with parameters supplied by
the control plane as part of the rule.

As part of bringing up the Mininet instance, the
`make run` command will install packet-processing rules in the tables of
each switch. These are defined in the `s1-acl.json` files.

**Important:** We use P4Runtime to install the control plane rules. The
content of files `s1-acl.json` refer to specific names of tables, keys, and
actions, as defined in the P4Info file produced by the compiler (look for the
file `build/acl.p4info` after executing `make run`). Any changes in the P4
program that add or rename tables, keys, or actions will need to be reflected in
these `s1-acl.json` files.

### Step 2: Implement ACL

The `acl.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file---replace each `TODO` with logic
implementing the missing piece.

A complete `acl.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`), IPv4 (`ipv4_t`), TCP (`tcp_t`) and UDP (`udp_t`).
2. Parsers for Ethernet, IPv4, TCP or UDP headers.
3. An action to drop a packet, using `mark_to_drop()`.
4. An action (called `ipv4_forward`) that:
	1. Sets the egress port for the next hop.
	2. Updates the ethernet destination address with the address of the next hop.
	3. Updates the ethernet source address with the address of the switch.
	4. Decrements the TTL.
5. **TODO:** A control that:
    1. Defines a table that will read UDP dstPort, and
       invoke either `drop` or `NoAction`.
    2. An `apply` block that applies the table.
    3. A rule added to `s1-acl.json` that denies all the UDP packets with dstPort=80.  
6. **TODO:** Updates the rule of table `ipv4_lpm` in `s1-acl.json`.
7. A `package` instantiation supplied with the parser, control, and deparser.
    > In general, a package also requires instances of checksum verification
    > and recomputation controls. These are not necessary for this assignment
    > and are replaced with instantiations of empty controls.

### Step 3: Run your solution

Follow the instructions from Step 1. This time, your message from
`h1` should not be delivered to `h4` and any message with a udp.dstPort=80 will be dropped by the switch.


## Exercise 2: Load Balance

Place yourself in the `assignment4/exercises/load_balance` directory.

In this exercise, you will implement a form of load balancing based on
a simple version of Equal-Cost Multipath Forwarding. The switch you
will implement will use two tables to forward packets to one of two
destination hosts at random. The first table will use a hash function
(applied to a 5-tuple consisting of the source and destination IP
addresses, IP protocol, and source and destination TCP ports) to
select one of two hosts. The second table will use the computed hash
value to forward the packet to the selected host.

### Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`load_balance.p4`, which initially drops all packets.  Your job (in
the next step) will be to extend it to properly forward packets.

Before that, let's compile the incomplete `load_balance.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   make
   ```   
   This will:
   * compile `load_balance.p4`, and
   * start a Mininet instance with one switch (`s1`) connected to four host (`h1`, `h2`, `h3` and `h4`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.1.2`, `10.0.1.3` and `10.0.1.4`.  
   * We use the IP address 10.0.1.10 to indicate traffic that should be
     load balanced between `h2` and `h3`.

2. You should now see a Mininet command prompt.  Open three terminals
   for `h1`, `h2` and `h3`, respectively:
   ```bash
   mininet> xterm h1 h2 h3
   ```   
3. Each host includes a small Python-based messaging client and
   server.  In `h2` and `h3`'s XTerms, start the servers:
   ```bash
   ./receive.py
   ```
4. In `h1`'s XTerm, send a message from the client:
   ```bash
   ./send.py 10.0.1.10 "P4 is cool"
   ```
   The message will not be received.
5. Type `exit` to leave each XTerm and the Mininet command line.

The message was not received because each switch is programmed with
`load_balance.p4`, which drops all packets on arrival.  Your job is to
extend this file.

### Step 2: Implement Load Balancing

The `load_balance.p4` file contains a skeleton P4 program with key
pieces of logic replaced by `TODO` comments.  These should guide your
implementation---replace each `TODO` with logic implementing the
missing piece.

A complete `load_balance.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`) and IPv4 (`ipv4_t`).
2. Parsers for Ethernet and IPv4 that populate `ethernet_t` and `ipv4_t` fields.
3. An action to drop a packet, using `mark_to_drop()`.
4. **TODO:** An action (called `set_ecmp_select`), which will:
	1. Hashes the 5-tuple specified above using the `hash` extern
	2. Stores the result in the `meta.ecmp_select` field
5. **TODO:** A control that:
    1. Applies the `ecmp_group` table.
    2. Applies the `ecmp_nhop` table.
6. A deparser that selects the order in which fields inserted into the outgoing
   packet.
7. A `package` instantiation supplied with the parser, control, and deparser.

### Step 3: Run your solution

Follow the instructions from Step 1.  This time, your message from
`h1` should be delivered to `h2` or `h3`. If you send several
messages, some should be received by each server.


## Bonus: Key-Value Store

### What is key-value store

A key-value store is a storage service. Each item in the key-value store has a key, which is the name of the item, and a value, which is the actual content of the item. A key-value store provides two basic funcions: `get(key)` and `put(key, value)`. The function `get(key)` gets the value of the corresponding key from the key-value store. The function `put(key, value)` updates the value of the corresponding key in the key-value store.

### What you need to do

You will implement a key-value store in the switch with P4. The key-value packets may look like this:
```
type (1 byte) | key (4 bytes) | value (4 bytes)
```

The tcp.dstPort is always set to be 100 for such key-value store packets.
The type field indicates the type of the query, which can be 1 (get request), 2 (put request), 3 (get reply), and 4 (put reply). The key and value field contains the key and value of a item, respectively.

For a `get` query, the type field should be 1 and the key field contains the key for the queried item. The value field is not meaningful. The switch should update the type field to 3, and update the value field based on the value stored in the switch. Then the switch sends the packet back to the sender as the reply.

For a `put` query, the type field should be 2, the key field should contain the key for the queried item, and the value field should contain the new value of the item. The switch should update its key-value store with the new value, update the type field to 4, and then send the packet back to the sender as the reply.

To make it simple, you do not need to implement sophisticated routing in this assignment. You can assume that the client is directly connect to the switch, and the switch simply sends the packet to the ingress port to reply to the client.

You can use part of the code in ACL and Load Balance and implement the key-value store functionality. Set the size of the key-value store in the switch to be 100.

### Performance requirement

1. Open a terminal on host 1 with `xterm h1` and run `./kv.py`, you should be able to issue the `get` and `put` query with commands `put [key] [value]` and `get [key]`, for example `put 1 11` and `get 1`.
2. You should receive reply messages from switch 1 on host 1 and display the type, key and value fields in each reply
message.

### Hints

1. You could open a second terminal on h1 and run an adjusted receive.py to receive and display reply messages.
2. You can assume the key and value are both integers, and use key as the array index to access register.

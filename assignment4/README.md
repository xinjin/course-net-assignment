# Assignment 4: P4 and Mininet

### Due: Wednesday, May 1st

## Deliverables

Submit your source code for the two exercises, in two separate folders `acl` and `load_balance`, and together in one
`assignment4.zip` file. For every exercise, submit the p4 code and the corresponding json file that configures the table entries.

## Introduction

This assignment includes 2 exercises: *Access Control List*
and *Load Balance*. Both exercises assume that you possess basic networking
knowledge and some familiarity with the P4 language. Please take a look at the
[P4 language spec](https://p4.org/p4-spec/docs/P4-16-v1.1.0-spec.pdf).
*Access Control List* asks you to write a P4 program to implement an ACL on a switch. *Load Balance* asks you to write a P4 program to implement a form of load balancing based on a simple version of Equal-Cost Multipath Forwarding. We use P4_16 in this assignment.


## Obtaining required software

We provide a new VM for this assignment. The vagrantfile is under `course-net-assignment/assignment4/`.

To build the virtual machine:
- get the latest `course-net-assignment` repo
- `cd course-net-assignment/assignment4/`
- `vagrant up`. This will take about 1 hour or even longer.

## Exercise 1: Access Control List

Place yourself in the `course-net-assignment/assignment4/exercises/acl` directory.

### Step 1: Run the (incomplete) starter code

We provide a skeleton P4 program,
`acl.p4`, which initially forwards all packets. Your job will be to
extend this skeleton program to properly implement an ACL with two following rules:

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
   * start a Mininet instance with one switch (`s1`) connected to four hosts (`h1`, `h2`, `h3` and `h4`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.1.2`, `10.0.1.3` and `10.0.1.4`.

2. You should now see a Mininet command prompt. Open two terminals
for `h1` and `h2`, respectively:
   ```bash
   mininet> xterm h1 h2
   ```
3. Each host includes a small Python-based messaging client and
server. In `h2`'s xterm, go to the current exercise folder (`cd exercises/acl`) and start the server with the listening port:
   ```bash
   ./receive.py 80
   ```
4. In `h1`'s xterm, go to the current exercise folder (`cd exercises/acl`) and send a message to `h2`:
   ```bash
   ./send.py 10.0.1.2 UDP 80 "P4 is cool"
   ```
   The command line means `h1` will send a message to `10.0.1.2` with udp.dstport=80.
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
   make run
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
   server.  In `h2` and `h3`'s XTerms, go to the current exercise folder (`cd exercises/load_balance`) and start the servers with listening port:
   ```bash
   ./receive.py 1234
   ```
4. In `h1`'s XTerm, go to the current exercise folder (`cd exercises/load_balance`) and send a message from the client:
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

The bash script `test.sh` will run all the exercises with your own implementations. You may need to run `chmod 744 test.sh` first to make the script executable.  You can also pass "acl" or "lb" as an argument to `test.sh` (e.g. `test.sh acl`) to test only ACL implementation.


### Hints

1. You could open a second terminal on h1 and run an adjusted receive.py to receive and display reply messages.
2. You can assume the key and value are both integers, and use key as the array index to access register.
3. Do remember run `make stop` and `make clean` every time before you run your program.

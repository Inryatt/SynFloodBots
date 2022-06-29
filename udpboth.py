import select
import selectors
import socket
import struct
import sys
import fcntl
import os
multicast_group = ('224.3.29.71', 10000)
server_address = ('', 10000)
ttl = struct.pack('b', 2)

# set sys.stdin non-blocking
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

def recvm():
    print("reveiving")
    try:
     data, server = sock.recvfrom(1024)
     print ( 'received %s bytes from %s' % (len(data), server))
     print ( data)
    except socket.timeout:
        print("timeout")
        pass


def sendm(msg):
    print("Sending")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    sock.sendto(msg, ('224.3.29.71', 10000))
    return



def got_keyboard_data():
        input = sys.stdin.read().rstrip("\n")   #Get user's input
        if input == "exit":                 #Ends Client Session
            sock.close()
            exit()
        else:
            if input != "":                                     
                sys.stdout.write('\x1b[1A')                     
                sendm(input.encode("utf-8"))
                return

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)



group = socket.inet_aton('224.3.29.71')
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

sel = selectors.DefaultSelector()

sock.bind(server_address)
sel.register(sock, selectors.EVENT_READ, recvm)
sel.register(sys.stdin, selectors.EVENT_READ, got_keyboard_data)   # Listen for input activity


while True:
    # Look for responses from all recipients
    #print ('waiting to receive')
    toDo = sel.select(0)

    for event, data in toDo:
            callback = event.data
            msg = callback()    
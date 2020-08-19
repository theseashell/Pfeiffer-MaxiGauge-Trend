import sys
import socket
import time
import signal
import math

import matplotlib.pyplot as plt

class PfeifferMaxiGauge:
    def __init__(self, ipaddress, port):
        self.ipaddress = ipaddress
        self.port = port
        self.cmt = '/r'
        self.isconnected = False
        self.timeout = 0.1

    def establishConnection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to {} port {}'.format(self.ipaddress, self.port))
        self.sock.connect((self.ipaddress, self.port))
        self.connected = True
        self.sock.settimeout(self.timeout)
        print('Connection established.')

    def closeConnection(self):
        if self.connected == True:
            self.sock.close()
        self.connected = False
        print('Disconnected.')

    def getReply(self):
        reply = b""
        CRLF = False
        while CRLF == False:
            answer = self.sock.recv(1024)
            reply += answer
            if reply[-2:] == b"\r\n":
                CRLF = True
        return reply

    def checkPressure(self,gaugeNo):
        #Ask for Pressure
        message = ('PR{}\x0D'.format(gaugeNo)).encode()
        #print(message)
        self.sock.sendall(message)

        #Get acknowledgement
        self.getReply()

        #Enquire
        message = b'\x05\x0D'
        #print(message)
        self.sock.sendall(message)
        
        #GetThePressure
        reply = self.getReply()
        pressure = float(reply.decode()[-10:-2])
        return pressure

    def checkStatus(self,gaugeNo):
        #Ask for Pressure
        message = ('PR{}\x0D'.format(gaugeNo)).encode()
        #print(message)
        self.sock.sendall(message)

        #Get acknowledgement
        self.getReply()

        #Enquire
        message = b'\x05\x0D'
        #print(message)
        self.sock.sendall(message)
        
        #GetThePressure
        reply = self.getReply()
        isgaugeOn = int(reply.decode()[0])
        return isgaugeOn

    def getTimeout(self):
        print(self.sock.gettimeout())

MaxiGauge = PfeifferMaxiGauge('192.168.140.200', 10002)
MaxiGauge.establishConnection()

#Read all the gauges that are turned on

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

line_g1, = ax.plot([],[], label='g1')
line_g2, = ax.plot([],[], label='g2')
line_g3, = ax.plot([],[], label='g3')
line_g4, = ax.plot([],[], label='g4')
line_g5, = ax.plot([],[], label='g5')
line_g6, = ax.plot([],[], label='g6')

lineDict = {
    "g1" : line_g1,
    "g2" : line_g2,
    "g3" : line_g3,
    "g4" : line_g4,
    "g5" : line_g5,
    "g6" : line_g6
    }

gaugeNoDict = {
    "g1" : 1,
    "g2" : 2,
    "g3" : 3,
    "g4" : 4,
    "g5" : 5,
    "g6" : 6
    }

xdataDict = {
    "g1" : [],
    "g2" : [],
    "g3" : [],
    "g4" : [],
    "g5" : [],
    "g6" : []
    }

ydataDict = {
    "g1" : [],
    "g2" : [],
    "g3" : [],
    "g4" : [],
    "g5" : [],
    "g6" : []
    }

plt.grid(True, which="both")
ax.set_yscale('log')
ax.set_ylim(1e-10, 1e-2)

ax.set_xlabel("Time [arb. u.]")
ax.set_ylabel("Pressure [mbar]")

ax.legend(loc='upper left')

i = 0
while 1:

    for gauge in sys.argv[1:]:
        pressure = MaxiGauge.checkPressure(gaugeNoDict[gauge])
        xdataDict[gauge].append(i)
        ydataDict[gauge].append(pressure)
        lineDict[gauge].set_xdata(xdataDict[gauge])
        lineDict[gauge].set_ydata(ydataDict[gauge])
        ax.set_xlim(len(ydataDict[gauge])-100,len(ydataDict[gauge]))

    i += 1

    plt.tight_layout()
    fig.canvas.draw()
    time.sleep(0.01)
    fig.canvas.flush_events()


MaxiGauge.closeConnection()




        

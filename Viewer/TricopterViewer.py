###############################################
# Tricopter viewer by Etienne
# Displays the data send over xbee by the tricopter
###############################################
from __future__ import print_function
from collections import deque
import serial
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import io
import struct
import argparse

class TricopterData:
  # constr
  def __init__(self, args):
    print('reading from serial port %s...' % args.strPort)
    # open serial port
    self.ser = serial.Serial(args.strPort, args.baudrate)
    self.n32 = args.n32
    self.d32 = [[] for x in xrange(args.n32)]
    self.n16 = args.n16
    self.d16 = [[] for x in xrange(args.n16)]
    self.n8 = args.n8
    self.d8 = [[] for x in xrange(args.n8)]
    self.nf = args.nf
    self.df = [[] for x in xrange(args.nf)]

    #This is the header of the packet, it's where it starts
    self.header=args.header
    self.headerLength = len(self.header.decode('hex'))
    self.buffer=""
    self.headerComplete = False # is turned to true once a header has been complete.
    self.packet=""
    self.newData=False
    self.packetCorrect=True
    

#This function checks the packet for errors (superfluous 0x00 )
  def check(self):
    offset = 0
    for i in range (0, self.n32):
      self.packetCorrect &= (int(self.packet[offset+i*5].encode('hex'),16) == i)
    offset += 5*self.n32 
    for i in range (0, self.n16):
      self.packetCorrect &= (int(self.packet[offset+i*3].encode('hex'),16) == self.n32 + i)
    offset += 3*self.n16 
    for i in range (0, self.n8):
      self.packetCorrect &= (int(self.packet[offset+i*2].encode('hex'),16) == self.n32 + self.n16 + i)
    offset += 2*self.n8 
    for i in range (0, self.nf):
      self.packetCorrect &= (int(self.packet[offset+i*5].encode('hex'),16) == self.n32 + self.n16 + self.n8 + i)


  #this function parse the packet (complete) in the data
  def parse(self):
    offset = 0
    for i in range (0, self.n32):
        (self.d32[i]).append(  struct.unpack('<i',self.packet[offset+i*5+1:offset+i*5+5])[0])
      #print((self.d32[i])[self.elements],end="\t")
    offset += 5*self.n32 
    for i in range (0, self.n16):
      (self.d16[i]).append(struct.unpack('<h',self.packet[offset+i*3+1:offset+i*3+3])[0])
      #print((self.d16[i])[self.elements],end="\t")
    offset += 3*self.n16 
    for i in range (0, self.n8):
      (self.d8[i]).append(struct.unpack('<c',self.packet[offset+i*2+1:offset+i*2+2])[0])
      #print((self.d8[i])[self.elements],end="\t")
    offset += 2*self.n8
    for i in range (0, self.nf):
      self.df[i].append(struct.unpack('<f',self.packet[offset+i*5+1:offset+i*5+5])[0])
      #print((self.df[i]),end="\t")

  # update plot
  #def update(self, frameNum, a0, a1):
  def update(self):
    try:
      if (self.headerComplete):
        # The header is complete, we read 
        # the content of the packet
        self.packet += self.ser.read(5*self.n32 + 3*self.n16 + 2*self.n8 + 5*self.nf)
        #print(self.packet.encode('hex'))
        #The packet is complete (if no error...) 
        #Check it for errors:
        self.check()
        if(self.packetCorrect):
          #Parse it !
          self.parse()
          self.newData=True
        else:
          print("Faulty packet")
          self.packetCorrect = True
        self.packet = ""
        self.headerComplete = False
      else:
        #We haven't reached a header yet, 
        # let roll over the incoming bytes
        self.buffer +=  self.ser.read()
        if (len(self.buffer) > self.headerLength):
          self.buffer = self.buffer[1:]
        if (self.buffer.encode('hex') == self.header):
          self.headerComplete = True
          #print("got packet !")
          #print(self.buffer.encode('hex'))
          self.buffer = ""
        #else:
          #print(self.buffer.encode('hex'))
    except KeyboardInterrupt:
        print('exiting')

  # clean up
  def close(self):
    # close serial
    self.ser.flush()
    self.ser.close()    

# main() function
def main():

  # arguments of the cli
  parser = argparse.ArgumentParser(description='Casts and plots binary serial data.')
  parser.add_argument('-p','--port',action="store",dest="strPort",default='/dev/ttyUSB0',help='The serial port to listen to. /dev/tty* on UNIX, COM* works maybe on Windows')
  parser.add_argument('-l','--long',action="store",dest="n32",type=int,default='1',help='The number of uint32 expected in the packet.')
  parser.add_argument('-s','--short',action="store",dest="n16",type=int,default='0',help='The number of uint16 expected in the packet.')
  parser.add_argument('-c','--char',action="store",dest="n8",type=int,default='0',help='The number of uint8/char expected in the packet.')
  parser.add_argument('-f','--float',action="store",dest="nf",type=int,default='27',help='The number of floats expected in the packet.')
  parser.add_argument('-b','--baudrate',action="store",dest="baudrate",type=int,default='57600',help='The baudrate used .')
  parser.add_argument('-m','--maxLen',action="store",dest="maxLen",type=int,default='0',help='The number of points to be printed. If 0 (default) whole history printed.')
  parser.add_argument('-H','--header',action="store",dest="header",default="ffffffff",help='The header of the packet. Default = ffffffff.')
  args = parser.parse_args()
  print(args)

  plt.figure(1,figsize=(20,15))
#Geometry of the figures
  a=0.025
  b=(1-3*a)/2.0

  plt.ion() #animates plot
  ax1 = plt.axes([a,a,b,b],label="Servo angles")
  #make plot
  g11,g12,g13, = ax1.plot([], [], 'r', [],[],'g', [],[],'b')

  ax2 = plt.axes([a,2*a+b,b,b],label="IMU angles")
  #make plot
  g21,g22,g23, = ax2.plot([], [], 'r', [],[],'g', [],[],'b')

  ax3 = plt.axes([2*a+b,a,b,b],label="First joystick")
  #make plot
  g31,g32,g33 = ax3.plot([], [], 'r', [],[],'g', [], [], 'b')
  #ax3.title('')

  ax4 = plt.axes([2*a+b,2*a+b,b,b],label="Second joystick")
  #make plot
  g41,g42,g43 = ax4.plot([], [], 'r', [],[],'g', [], [], 'b')

  plt.show()

  # The tricopter struct
  tricopterData = TricopterData(args)
  while True:
    tricopterData.update();
    if(tricopterData.newData):
      startPoint = 0
      if(args.maxLen):
        points = len(tricopterData.df[0])
        if(points>args.maxLen):
          startPoint = points-args.maxLen
      #print(tricopterData.d32[0])
      #print(tricopterData.df[0])
      g11.set_xdata(tricopterData.df[0][startPoint:])
      g11.set_ydata(tricopterData.df[1][startPoint:])
      g12.set_xdata(tricopterData.df[0][startPoint:])
      g12.set_ydata(tricopterData.df[2][startPoint:])
      g13.set_xdata(tricopterData.df[0][startPoint:])
      g13.set_ydata(tricopterData.df[3][startPoint:])
      
      ax1.relim()
      ax1.autoscale_view()

      g21.set_xdata(tricopterData.df[0][startPoint:])
      g21.set_ydata(tricopterData.df[15][startPoint:])
      g22.set_xdata(tricopterData.df[0][startPoint:])
      g22.set_ydata(tricopterData.df[16][startPoint:])
      g23.set_xdata(tricopterData.df[0][startPoint:])
      g23.set_ydata(tricopterData.df[17][startPoint:])

      ax2.relim()
      ax2.autoscale_view()

      g31.set_xdata(tricopterData.df[0][startPoint:])
      g31.set_ydata(tricopterData.df[18][startPoint:])
      g32.set_xdata(tricopterData.df[0][startPoint:])
      g32.set_ydata(tricopterData.df[19][startPoint:])
      g33.set_xdata(tricopterData.df[0][startPoint:])
      g33.set_ydata(tricopterData.df[20][startPoint:])

      ax3.relim()
      ax3.autoscale_view()

      g41.set_xdata(tricopterData.df[0][startPoint:])
      g41.set_ydata(tricopterData.df[21][startPoint:])
      g42.set_xdata(tricopterData.df[0][startPoint:])
      g42.set_ydata(tricopterData.df[22][startPoint:])
      g43.set_xdata(tricopterData.df[0][startPoint:])
      g43.set_ydata(tricopterData.df[23][startPoint:])
      
      ax4.relim()
      ax4.autoscale_view()

      plt.draw()

      # Wait for new data to come
      tricopterData.newData = False
  # clean up
  tricopterData.close()

# call main
if __name__ == '__main__':
  main()

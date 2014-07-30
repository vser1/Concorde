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

class TricopterData:
  # constr
  def __init__(self, strPort, baudrate, maxLen, n32, n16, n8, nf):
    # open serial port
    self.ser = serial.Serial(strPort, baudrate)
    self.n32 = n32
    self.d32 = [[] for x in xrange(n32)]
    self.n16 = n16
    self.d16 = [[] for x in xrange(n16)]
    self.n8 = n8
    self.d8 = [[] for x in xrange(n8)]
    self.nf = nf
    self.df = [[] for x in xrange(nf)]

    #self.ax = deque([0.0]*maxLen)
    #self.ay = deque([0.0]*maxLen)
    self.maxLen = maxLen
    #This is the header of the packet, it's where it starts
    self.header='ffffffff'
    self.buffer=""
    self.packet=""
    self.newData=False
    
  #this function parse the packet (complete) in the data
  def parse(self):
    offset = 4 
    for i in range (0, self.n32):
      if (len(self.d32[i]) == self.maxLen):
        del self.d32[i][0]
      (self.d32[i]).append(  struct.unpack('<i',self.packet[offset+i*5+1:offset+i*5+5])[0])
      #print((self.d32[i])[self.elements],end="\t")
    offset = 4 + 5*self.n32 
    for i in range (0, self.n16):
      if (len(self.d16[i]) == self.maxLen):
        del self.d16[i][0]
      (self.d16[i]).append(struct.unpack('<h',self.packet[offset+i*3+1:offset+i*3+3])[0])
      #print((self.d16[i])[self.elements],end="\t")
    offset = 4 + 5*self.n32 + 3*self.n16 
    for i in range (0, self.n8):
      if (len(self.d8[i]) == self.maxLen):
        del self.d8[i][0]
      (self.d8[i]).append(struct.unpack('<c',self.packet[offset+i*2+1:offset+i*2+2])[0])
      #print((self.d8[i])[self.elements],end="\t")
    offset = 4 + 5*self.n32 + 3*self.n16 + 2*self.n8
    for i in range (0, self.nf):
      if (len(self.df[i]) == self.maxLen):
        del self.df[i][0]
      self.df[i].append(struct.unpack('<f',self.packet[offset+i*5+1:offset+i*5+5])[0])
      #print((self.df[i]),end="\t")
    #print("")
    #print(self.elements)

  # update plot
  #def update(self, frameNum, a0, a1):
  def update(self):
    try:
      self.buffer +=  self.ser.read()
      if (len(self.buffer) == 5):
        self.buffer = self.buffer[1:]
      if (self.buffer.encode('hex') == self.header):
        #print(self.packet.encode('hex'))
        #In some cases, the packet might not be complete. 
        #We check this 
        if( len(self.packet) == 4 + 5*self.n32 + 3*self.n16 + 2*self.n8 + 5*self.nf ):
          #the packet is complete
          #We should decode it:
          #if(self.elements == self.maxLen):
          #print(self.packet.encode('hex'))
          self.newData=True
          self.parse()
        else:
          print("Packet not complete !");
        self.packet = self.buffer[0]
      else:
        self.packet += self.buffer[0]
    except KeyboardInterrupt:
        print('exiting')

  # clean up
  def close(self):
    # close serial
    self.ser.flush()
    self.ser.close()    



# main() function
def main():
  strPort = '/dev/ttyUSB0'
  baudrate = 57600
  print('reading from serial port %s...' % strPort)

  # protocol
  n32 = 1;    # count of int32 values
  n16 = 0;    # count of int16 values
  n8 = 0;     # count of uint8 values
  nf = 27;     # count of float values
  n = n32+n16+n8+nf;
  #max elements in a plot
  maxLen = 100
  
  plt.figure(1)

  plt.ion() #animates plot
  ax1 = plt.axes()
  #make plot
  g11,g12,g13 = plt.plot([], [], 'r', [],[],'g', [],[],'b')
  plt.title('Servo angles')

  plt.figure(2)
  plt.ion() #animates plot
  ax2 = plt.axes()
  #make plot
  g21,g22,g23 = plt.plot([], [], 'r', [],[],'g', [],[],'b')
  plt.title('IMU angles')

  # The tricopter struct
  tricopterData = TricopterData(strPort, baudrate, maxLen, n32, n16, n8, nf)
  while True:
    tricopterData.update();
    if(tricopterData.newData):
      #print(tricopterData.d32[0])
      #print(tricopterData.df[0])
      plt.figure(1)
      g11.set_xdata(tricopterData.df[0])
      g11.set_ydata(tricopterData.df[1])
      g12.set_xdata(tricopterData.df[0])
      g12.set_ydata(tricopterData.df[2])
      g13.set_xdata(tricopterData.df[0])
      g13.set_ydata(tricopterData.df[3])
      
      plt.draw()
      ax1.relim()
      ax1.autoscale_view()

      plt.figure(2)
      g21.set_xdata(tricopterData.df[0])
      g21.set_ydata(tricopterData.df[15])
      g22.set_xdata(tricopterData.df[0])
      g22.set_ydata(tricopterData.df[16])
      g23.set_xdata(tricopterData.df[0])
      g23.set_ydata(tricopterData.df[17])
      plt.draw()
      ax2.relim()
      ax2.autoscale_view()

      # Wait for new data to come
      tricopterData.newData = False
  # clean up
  tricopterData.close()

# call main
if __name__ == '__main__':
  main()

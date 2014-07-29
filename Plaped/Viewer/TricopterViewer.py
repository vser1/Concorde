"""
###############################################
# Tricopter viewer by Etienne
# Displays the data send over xbee by the tricopter
# 
# inspired by ldr.py by Mahesh Venkitachalam (electronut.in)
###############################################
"""
from __future__ import print_function
import serial
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import io
import struct

class AnalogPlot:
  # constr
  def __init__(self, strPort, baudrate, maxLen, n32, n16, n8, nf):
      # open serial port
      self.ser = serial.Serial(strPort, baudrate)
      self.n32 = n32
      self.n16 = n16
      self.n8 = n8
      self.nf = nf

      #self.ax = deque([0.0]*maxLen)
      #self.ay = deque([0.0]*maxLen)
      self.maxLen = maxLen
      #This is the header of the packet, it's where it starts
      self.header='ffffffff'
      self.buffer=""
      self.packet=""

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
            offset = 4 
            for i in range (0, self.n32):
              x = struct.unpack('<i',self.packet[offset+i*5+1:offset+i*5+5])[0]
              print(x,end="\t")
            offset = 4 + 5*self.n32 
            for i in range (0, self.n16):
              x = struct.unpack('<h',self.packet[offset+i*3+1:offset+i*3+3])[0]
              print(x,end="\t")
            offset = 4 + 5*self.n32 + 3*self.n16 
            for i in range (0, self.n8):
              x = struct.unpack('<c',self.packet[offset+i*2+1:offset+i*2+2])[0]
              print(x,end="\t")
            offset = 4 + 5*self.n32 + 3*self.n16 + 2*self.n8
            for i in range (0, self.nf):
              x = struct.unpack('<f',self.packet[offset+i*5+1:offset+i*5+5])[0]
              print(x,end="\t")
            print("\n")
          else:
            print("Packet not complete !");
          self.packet = self.buffer[0]
        else:
          self.packet += self.buffer[0]
           #data = [float(val) for val in line.split()]
          # print data
          #if(len(data) == 2):
              #self.add(data)
              #a0.set_data(range(self.maxLen), self.ax)
              #a1.set_data(range(self.maxLen), self.ay)
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

  # plot parameters
  analogPlot = AnalogPlot(strPort, baudrate, 100, n32, n16, n8, nf)
  while True:
    analogPlot.update();

  # clean up
  analogPlot.close()

# call main
if __name__ == '__main__':
  main()

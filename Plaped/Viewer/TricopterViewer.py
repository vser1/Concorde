"""
###############################################
# Tricopter viewer by Etienne
# Displays the data send over xbee by the tricopter
# 
# inspired by ldr.py by Mahesh Venkitachalam (electronut.in)
###############################################
"""
import serial
import matplotlib.pyplot as plt 
import matplotlib.animation as animation

# main() function
def main():
  strPort = '/dev/ttyUSB0'
  print('reading from serial port %s...' % strPort)

# call main
if __name__ == '__main__':
  main()

Concorde
========

This is a repository for my Concorde code

tricopterViewer.py parses data coming to the ttyUSB0 (serial) over xBee and plots the data.

You might need sudo to access ttyUSB0.

Known bugs:
-I lose periodically 3 packets, I guess it's because my code isn't efficient to catch/interpret the whole stream live.

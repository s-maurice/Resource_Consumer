todo:
handle malicious connection to new client finder in server
handle client disconnection without async task crash
handle server close before client

make server not load up draw handlers
redo draw handlers so that the textures only need to be loaded once
the two above can be achieved by moving the drawing into the RCScreen.py

have chunk style map loading and live map generation

resync can resync specific machines - or on timers
todo:
handle malicious connection to new client finder in server
handle client disconnection without async task crash
handle server close before client
handle server storing the data queues for each client

make server not load up draw handlers
redo draw handlers so that the textures only need to be loaded once
the two above can be achieved by moving the drawing into the RCScreen.py

add tick speed handler (game and connection) - similar to framerate handler to handle the tick speed of the client and server

have 2d array for machines on map, with the tiles each machine occupying referencing the machine

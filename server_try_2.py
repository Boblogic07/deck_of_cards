import socket
from _thread import *
import sys

#----------------------------------------------------------------------
# Konstants and Globals

knDebug         = 0
gcMsgs          = []
gcConn          = []
gnNumPlayers    = 0

#----------------------------------------------------------------------
class clsConn:
    def __init__(self, conn, addr):
        self.conn       = conn
        self.addr       = addr
        self.connected  = True

#----------------------------------------------------------------------
class clsMsgs:
    def __init__(self, currentPlayer):
        self.Player     = currentPlayer
        self.tMsg       = []

#----------------------------------------------------------------------
def threaded_client_listener(player, junk):
    global gcMsgs, gcConn, gnNumPlayers

    if knDebug >= 1 : print("Listener created for player {:d}.".format(player))

    count = 0

    bAllOK = True

    while gcConn[player].connected:
        count = count + 1
        if knDebug >= 3 : print ("Listener for player {:d} count={:d}.".format(player, count))

        try:
            # Wait for data from the player
            data = gcConn[player].conn.recv(2048).decode()
        except:
            bAllOK = False
            if knDebug >= 0 : print ("Listener conn.recv failed with exception.")
            if knDebug >= 0 : print (socket.error)

        if bAllOK:            
            if knDebug >= 3 : print ("Received data from player {:d} '{:s}'. Count={:d}".format(player, data, count))
            if not data:
                if knDebug >= 3 : print ("At the IF")
                gcConn[player].connected = False
                if knDebug >= 0 : print ("Listener failed (no data) for player {:d}.".format(player))
                break
            else:
                tSend = "Z!"
                if knDebug >= 3 : print ("Data[0:2]=" + data[0:2])
                if ((data[0:2] == 'M!') or (data[0:2] == 'S!')):
                    for i in range(0, gnNumPlayers):
                        gcMsgs[i].tMsg.append(data)
                elif data[0:2] == 'R!':
                    if len(gcMsgs[player].tMsg) > 0:
                        tSend = gcMsgs[player].tMsg[0]
                        gcMsgs[player].tMsg.pop(0)
                else:
                    pass

                try:
                    gcConn[player].conn.sendall(str.encode(tSend))
                except:
                    bAllOK = False
                    if knDebug >= 0 : print ("Listener conn.sendall failed with exception.")
                    if knDebug >= 0 : print (socket.error)
                if bAllOK:
                    if knDebug >= 3 : print ("Sent '{:s}' to player {:d}.".format(tSend, player))

        if bAllOK == False:
            break

    gcConn[player].conn.close()
    gcConn[player].connected = False

    if knDebug >= 0 : print("Listener stopped for player {:d}, because the connection was closed.".format(player))

#----------------------------------------------------------------------
def threaded_client_sender(player):
    global gcMsgs, gcConn, gnNumPlayers

    if knDebug >= 0 : print("Sender created for player {:d}.".format(player))

    while gcConn[player].connected:
        while len(gcMsgs[player].tMsg) > 0:
            try:
                tSend = gcMsgs[player].tMsgs[0]
                print ("Trying to send to player {:d} string '{:s}'".format(player, tSend))
                conn.sendall(str.encode(tSend))
                gcMsgs[player].tMsg.pop(0)
            except:
                gcConn[player].connected = False
                print ("Sender failed (exception) for player {:d}.".format(player))
                break

    conn.close()

    if knDebug >= 0 : print("Sender stopped for player {:d}, becuase the connection was closed.".format(player))

#----------------------------------------------------------------------

def main():
    global gcMsgs, gcConn, gnNumPlayers

    bAllOK = True

    server = "192.168.0.77"
    port = 5555
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((server, port))
    except socket.error as e:
        bAllOK = False
        if knDebug >= 0 : print("Bind failed with exception")
        if knDebug >= 0 : print (str(e))

    if bAllOK:
        s.listen(4)
        if knDebug >= 0 : print("Server Started.   Waiting for connections.")

        gnNumPlayers = 0
        while True:
            conn, addr = s.accept()
            conn.sendall(str.encode("#P,{:03d}".format(gnNumPlayers)))
            gcConn.append(clsConn(conn, addr))
            if knDebug >= 0 : print("Connected to:", addr)

            gcMsgs.append(clsMsgs(gnNumPlayers))
            start_new_thread(threaded_client_listener, (gnNumPlayers, 1))
            #start_new_thread(threaded_client_sender, (gnNumPlayers))

            gnNumPlayers = gnNumPlayers + 1

#----------------------------------------------------------------------

main()

#----------------------------------------------------------------------

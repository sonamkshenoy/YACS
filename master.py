import socket
import threading
import json
from queue import Queue
from allConfigs import *


queueOfRequests = Queue()

# THREAD 1: LISTENS TO REQUESTS (ACTS AS CLIENT)

def listenRequest():
    # Set up socket for listening to request

    # create an INET, STREAMing socket
    mastersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Listen to requests on Port 5000
    # "localhost" below only listens to requests from the same system. To access server from a different machine, have to give a globally available IP instead of "localhost"
    mastersocket.bind((MASTER_IP, MASTER_PORT))

    # become a server socket, can have 500 requests max in the queue (can we not have a limit?)
    mastersocket.listen() #(500)

    # Once socket is set up, listen and schedule requests
    while True:
        # accept connections from outside
        (reqGeneratorSocket, address) = mastersocket.accept()

        while True:

            # address has (host ip, port) of client (requests.py)
            # print(clientsocket, "\n", address)
            data = reqGeneratorSocket.recv(4096).decode()
            # print(data)

            if len(data) == 0: # the client does not send anything but just closes its side
                # Close the connection with the client but keep socket open for new connections
                reqGeneratorSocket.close()
                print('Request Generator disconnected')
                break

            queueOfRequests.put(data)

            # print("Received", data)
            reqGeneratorSocket.send(b"Received request successfully")

            # # now do something with the clientsocket
            # # in this case, we'll pretend this is a threaded server
            # ct = client_thread(clientsocket)
            # ct.run()





    
# THREAD 2 : SCHEDULES TASKS (ACTS AS SERVER)

def scheduleRequest():

    while(True):
        if(not queueOfRequests.empty()):
            newRequest = queueOfRequests.get()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 4000))
                message= json.dumps(newRequest)
                #send task
                s.send(message.encode())


if __name__ == "__main__":

    try:
        t1 = threading.Thread(target = listenRequest)
        t2 = threading.Thread(target = scheduleRequest)

        t1.start()
        t2.start()

    except Exception as e:
        print("Error in starting thread: ", e)




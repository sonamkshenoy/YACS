import socket

REQUESTIP = "localhost"
REQUESTPORT = 5000
if __name__ == "__main__":

    # THREAD 1: LISTENS TO REQUESTS (ACTS AS CLIENT)
    # Set up socket for listening to request

    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Listen to requests on Port 5000
    # "localhost" below only listens to requests from the same system. To access server from a different machine, have to give a globally available IP instead of "localhost"
    serversocket.bind((REQUESTIP, REQUESTPORT))

    # become a server socket, can have 500 requests max in the queue (can we not have a limit?)
    serversocket.listen() #(500)

    # Once socket is set up, listen and schedule requests
    while True:
        # accept connections from outside
        (clientsocket, address) = serversocket.accept()

        while True:

            # address has (host ip, port) of client
            # print(clientsocket, "\n", address)
            data = clientsocket.recv(4096).decode()

            if len(data) == 0: # the client does not send anything but just closes its side
                # Close the connection with the client but keep socket open for new connections
                clientsocket.close()
                print('Client disconnected')
                break

            # print("Received", data)
            clientsocket.send(b"Received request successfully")

            # # now do something with the clientsocket
            # # in this case, we'll pretend this is a threaded server
            # ct = client_thread(clientsocket)
            # ct.run()


    # THREAD 2 : SCHEDULES TASKS (ACTS AS SERVER)

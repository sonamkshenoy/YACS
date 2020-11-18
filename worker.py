import socket
import json
import sys

WORKERIP = "localhost"

if __name__ == "__main__":

    # THREAD 1: LISTENS TO TASKS TO EXECUTE (ACTS AS CLIENT)
    # Set up socket for listening to tasks

    # Make sure user passes port number for worker
    if len(sys.argv) < 2:
        print("Usage: python worker.py <port no.>", file=sys.stderr)
        sys.exit(-1)

    WORKERPORT = int(sys.argv[1])

    with open("master_config.json", "r") as f:
        configs = f.read()

    configs = json.loads(configs)
    configs = configs["Workers"]

    for config in configs:
        if config["port"] == WORKERPORT:
            # print(config)
            WORKER_CONFIG = config

    WORKER_ID = WORKER_CONFIG["worker_id"]

    # serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #
    # # Listen to requests on Port entered by user
    # serversocket.bind((WORKERIP, WORKERPORT))
    #
    # serversocket.listen()
    #
    # # Once socket is set up, add task to execution pool
    # while True:
    #     # accept connections from outside
    #     (clientsocket, address) = serversocket.accept()

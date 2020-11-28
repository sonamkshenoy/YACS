import socket
import json
import sys
from allConfigs import *


# Worker configs:
# 1. WORKER_PORT
# 2. WORKER_CONFIG
# 3. WORKER_ID
# 4. WORKER_IP (Only this is fetched from allConfigs.py)

# Worker variables
numSlotsUsed = 0

if __name__ == "__main__":

    # THREAD 1: LISTENS TO TASKS TO EXECUTE (ACTS AS CLIENT)

    # First get worker details

    # Make sure user passes port number for worker
    if len(sys.argv) < 2:
        print("Usage: python worker.py <port no.>", file=sys.stderr)
        sys.exit(-1)

    WORKER_PORT = int(sys.argv[1])

    with open(CONFIGFILE, "r") as f:
        configs = f.read()

    configs = json.loads(configs)
    configs = configs[MAINKEYINCONFIG]

    for config in configs:
        if config["port"] == WORKER_PORT:
            print(config)
            WORKER_CONFIG = config

    WORKER_ID = WORKER_CONFIG["worker_id"]



    # Once details fetched, set up socket for listening to tasks

    workersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    workersocket.bind((WORKER_IP, WORKER_PORT))
    workersocket.listen()
    
    while True:
        (mastersocket, address) = workersocket.accept()

        while True:

            data = mastersocket.recv(4096).decode()
            print(data)

            if(len(data) == 0):

                mastersocket.close()
                print('Server disconnected')
                break

            mastersocket.send(b"Received request successfully")



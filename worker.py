import sys
import json
import socket
import threading
import time
import datetime

from allConfigs import *

"""
Worker configs:
    1. WORKER_PORT
    2. WORKER_CONFIG
    3. WORKER_ID
    4. WORKER_IP (Only this is fetched from allConfigs.py)
"""

# Worker variables
totalNumSlots = 0
freeSlotsNum = totalNumSlots


# THREAD 1: LISTENS TO TASKS TO EXECUTE (ACTS AS CLIENT)

def listenToTasks(lock):

    global freeSlotsNum

    workersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    workersocket.bind((WORKER_IP, WORKER_PORT))
    workersocket.listen()

    
    while True:
        (mastersocket, address) = workersocket.accept()

        while True:

            data = mastersocket.recv(4096).decode()

            if(len(data) == 0):

                mastersocket.close()
                # print('Master disconnected')
                break

            # Return "Slots not available" if no free slots, so that master can re-allot task
            print(freeSlotsNum)

            if(freeSlotsNum <= 0):
                mastersocket.send(SLOTS_NOT_AVAILABLE.encode())
                mastersocket.close()
                break

            else:
                mastersocket.send(SLOTS_AVAILABLE.encode())


            task = json.loads(data)
                
                # mastersocket.send(b"Received request successfully")


            # Allot task by creating new thread (thread = slot)
            # Pass task_id and duration to thread (slot)
            # info = {
            taskid = task["task_id"]
            duration = task["duration"]
            # }

            t = threading.Thread(target = executeTaskAndUpdateMaster, args=(lock, taskid, duration))
            t.start()

            # Number of available slots decreases by one
            with lock:
                freeSlotsNum -= 1

            # Once duration of task done, update master
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                s.connect((MASTER_IP, MASTER_UPDATE_PORT))
                message = json.dumps({NUMFREESLOTS: (WORKER_PORT, freeSlotsNum), TYPETASK: FREESLOTUPDATE})
                s.send(message.encode())



# THREAD 2: EXECUTES TASKS AND UPDATES MASTER ABOUT THIS

def executeTaskAndUpdateMaster(lock, task_id, durationOfTask):
    global freeSlotsNum

    print("Started execution of", task_id, "with duration", durationOfTask)

    # Execute task of x duration
    while(durationOfTask):
        # Reduce remaining task by 1 after 1 second (simulate passing of 1 second using time.sleep())

        # Can check if reducing after 1 second (of course variations in milliseconds) with following line:
        # print(datetime.datetime.now())

        time.sleep(1) 
        durationOfTask -= 1

    print("Finished execution of", task_id)

    # Current slot now becomes free
    with lock:
        freeSlotsNum += 1

    # Once duration of task done, update master
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((MASTER_IP, MASTER_UPDATE_PORT))
        message = json.dumps({NUMFREESLOTS: (WORKER_PORT, freeSlotsNum), "taskid": task_id, TYPETASK: TASKEXEC_AND_FREESLOTUPDATE})
        s.send(message.encode())




"""
# THREAD 3: SENDS HEARTBEATS ABOUT NUMBER OF FREE SLOTS TO MASTER

def sendHeartbeats():

    while(True):    
        print("Sending...")        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.connect((MASTER_IP, MASTER_UPDATE_PORT))
            message = json.dumps({"typeTask": HEARTBEAT, "numFreeSlots": (WORKER_PORT, freeSlotsNum)})
            s.send(message.encode())
        time.sleep(0.001)
"""     


# MAIN FUNCTION   
if __name__ == "__main__":


    # First get worker details

    # Make sure user passes port number for worker
    if len(sys.argv) < 3:
        print("Usage: python worker.py <port no.> <worker_id>", file=sys.stderr)
        sys.exit(-1)

    WORKER_PORT = int(sys.argv[1])
    WORKER_ID = int(sys.argv[2])

    with open(CONFIGFILE, "r") as f:
        configs = f.read()

    configs = json.loads(configs)
    configs = configs[MAINKEYINCONFIG]

    for config in configs:
        if config["port"] == WORKER_PORT and config["worker_id"] == WORKER_ID:
            print(config)
            WORKER_CONFIG = config

    
    # Scanned entire config file, port number not present
    if(not WORKER_CONFIG):
        print("Configurations for entered port number is not present in the config file")
        sys.exit(0)

    # WORKER_ID = WORKER_CONFIG["worker_id"]
    totalNumSlots = WORKER_CONFIG["slots"]
    freeSlotsNum = totalNumSlots


    # Once details fetched, set up socket for listening to tasks and thread for executing them

    # Set up locks to prevent multiple threads from modifying "freeSlotsNum" at the same time
    lock = threading.Lock()

    try:
        t1 = threading.Thread(target = listenToTasks, args=(lock,))
        # t2 = threading.Thread(target = sendHeartbeats)

        t1.start()
        # t2.start()

        # We don't want to join (stop master till threads finish executing, they don't stop executing)

    except Exception as e:
        print("Error in starting thread: ", e)






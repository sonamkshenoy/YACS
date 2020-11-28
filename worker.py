import socket
import json
import sys
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
queueOfTasks = Queue()


# THREAD 1: LISTENS TO TASKS TO EXECUTE (ACTS AS CLIENT)

def listenToTasks():
    workersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    workersocket.bind((WORKER_IP, WORKER_PORT))
    workersocket.listen()
    
    while True:
        (mastersocket, address) = workersocket.accept()

        # if(freeSlotsNum <= 0):
        #     return("No available slots")

        while True:

            data = mastersocket.recv(4096).decode()

            if(len(data) == 0):

                mastersocket.close()
                print('Master disconnected')
                break

            task = json.loads(data)
            
            # mastersocket.send(b"Received request successfully")


            # Allot task
            t = threading.Thread(target = executeTask, args=({taskid: task["task_id"]}))
            t.start()
            freeSlotsNum -= 1


# THREAD 2: EXECUTES TASKS AND UPDATES MASTER ABOUT THIS

def executeTaskAndUpdateMaster(task_id):

    durationOfTask = int(newTaskRequest["duration"])

    # Execute task of x duration
    while(durationOfTask):
        durationOfTask -= 1

    # Once duration of task done
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Random selection of machine
        selectedWorker = random.choice(allPorts)
        print("Allotting task", task, "to", selectedWorker)
        s.connect(("localhost", MASTER_UPDATE_PORT))
        message = jsong.dumps({taskid: task_id})
        s.send(message.encode())

    freeSlotsNum += 1

     


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
    totalNumSlots = int(WORKER_CONFIG["slots"])
    freeSlotsNum = totalNumSlots


    # Once details fetched, set up socket for listening to tasks and thread for executing them

    try:
        t1 = threading.Thread(target = listenToTasks)
        t2 = threading.Thread(target = allotTasks)

        t1.start()
        t2.start()

        # We don't want to join (stop master till threads finish executing, they don't stop executing)

    except Exception as e:
        print("Error in starting thread: ", e)






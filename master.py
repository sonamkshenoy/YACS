import sys
import socket
import threading
import json
import random
from queue import Queue
from allConfigs import *


SCHEDULING_ALGO = 1


queueOfRequests = Queue()
queueOfReduceRequests = Queue()
allPorts = []
executingMapTasks = {} # Keeps count of map tasks that are still running and the job they belong to

# THREAD 1: LISTENS TO REQUESTS (ACTS AS CLIENT)

def listenRequest():

    global queueOfRequests

    # Set up socket for listening to request

    # create an INET, STREAMing socket
    mastersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Listen to requests on Port 5000
    # "localhost" below only listens to requests from the same system. To access server from a different machine, have to give a globally available IP instead of "localhost"
    mastersocket.bind((MASTER_IP, MASTER_SCHEDULING_PORT))

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
            # reqGeneratorSocket.send(b"Received request successfully")



    
# THREAD 2 : SCHEDULES TASKS - both map and reduce (ACTS AS SERVER)

def scheduleRequest():

    global executingMapTasks
    global queueOfReduceRequests
    global queueOfRequests

    while(True):

        # Only one map task and one reduce map task are executed in one iteration. All map tasks in the map queue are not executed at once to prevent starvation of reduce tasks and thus of the job (from completing)

        # Execute only map tasks
        if(not queueOfRequests.empty()):

            # Get the job
            newJobRequest = queueOfRequests.get()
            newJobRequest = json.loads(newJobRequest)




            # Extract map and reduce requests before scheduling (going to) next job

            mapTasks = newJobRequest["map_tasks"]
            job_id = newJobRequest["job_id"]
            executingMapTasks[job_id] = {}
            

            for task in mapTasks:

                # Now allot the task to a worker machine
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                    # Random selection of machine
                    selectedWorker = random.choice(allPorts)
                    print("Allotting task", task, "to", selectedWorker)
                    s.connect(("localhost", selectedWorker))

                    # Send task
                    message= json.dumps(task)
                    s.send(message.encode())

                    executingMapTasks[job_id].append(task["task_id"])


        # Execute only reduce tasks (if present)
        # These are added to reduceQueue only once all map tasks belonging to that job are done executing

        if(not queueOfReduceRequests.empty()):

            # Get the job
            newJobRequest = queueOfRequests.get()
            newJobRequest = json.loads(newJobRequest)

            reduceTasks = newJobRequest["reduce_tasks"]

            for task in reduceTasks:

                # Now allot the task to a worker machine
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                    # Random selection of machine
                    selectedWorker = random.choice(allPorts)
                    print("Allotting task", task, "to", selectedWorker)
                    s.connect(("localhost", selectedWorker))

                    # Send task
                    message= json.dumps(task)
                    s.send(message.encode())


# THREAD 3 : LISTENS TO UPDATES FROM WORKERS


def listenToUpdatesFromWorker():

    global executingMapTasks


    # Set up socket
    mastersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mastersocket.bind((MASTER_IP, MASTER_UPDATE_PORT))
    mastersocket.listen()
    
    while True:
        (workersocket, address) = mastersocket.accept()

        while True:

            data = workersocket.recv(4096).decode()

            if(len(data) == 0):

                workersocket.close()
                print('Worker disconnected')
                break

            # Get the update
            update = json.loads(data)

            task_id = update["taskid"]

            # Search the job the task belongs to
            for executingJob in executingMapTasks:
                if(task_id in executingJob):
                    job_id = executingJob
                    executingMapTasks[executingJob].remove(task_id)
                    break

                # Should ideally not come to this condition, yet handle
                else:
                    continue

            # If all map tasks of this job id have finished executing, remove this record from "executing" list and add to the reduce task queue
            if(len(executingMapTasks[job_id]) == 0):
                executingMapTasks.pop(job_id)
                queueOfReduceRequests.put(newJobRequest)






if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python master.py <path to config file> <scheduling algorithm>", file=sys.stderr)
        sys.exit(-1)

    PATH_TO_CONFIG = sys.argv[1]
    SCHEDULING_ALGO = sys.argv[2]

    if(SCHEDULING_ALGO not in ["R", "RR", "LL"]):
        print("Please enter R, RR or LL only.\nR for Random\nRR for Round Robin\nLL for Least Loaded\n")
        sys.exit(-1)

    """
    while(True):
        algo = int(input("Select type of scheduling algorithm:\n1 for RANDOM\n2 for ROUND ROBIN\n3 for LEAST LOADED\n\n"))

        if(algo == 1):
            SCHEDULING_ALGO = 1
            break
        elif(algo == 2):
            SCHEDULING_ALGO = 2
            break
        elif(algo == 3):
            SCHEDULING_ALGO = 3
            break
        else:
            print("Please enter 1, 2 or 3 only")
    """

    # Get all workers and their port numbers from the config file

    with open(PATH_TO_CONFIG, "r") as f:
        configs = f.read()

    configs = json.loads(configs)
    configs = configs[MAINKEYINCONFIG]

    for config in configs:
        allPorts.append(config["port"])


    print("\n\n----------REQUESTS BEGIN------------\n")


    try:
        t1 = threading.Thread(target = listenRequest)
        t2 = threading.Thread(target = scheduleRequest)

        t1.start()
        t2.start()

        # We don't want to join (stop master till threads finish executing, they don't stop executing)

    except Exception as e:
        print("Error in starting thread: ", e)




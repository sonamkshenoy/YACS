import sys
import socket
import threading
import json
import random
import time
import datetime

from queue import Queue

from allConfigs import *

import logging
logging.basicConfig(
    level=logging.INFO,
    format="(%(asctime)s) %(message)s",  
    handlers=[  
        logging.FileHandler("logs/master.log"),
    ]
)

# Initialise scheduling algo to "random"
SCHEDULING_ALGO = "R"


queueOfRequests = Queue()
queueOfReduceRequests = Queue()
allPorts = []
tasksInProcess = {} # Keeps record of jobs whose map or reduce tasks are still running
lastUsedWorkerPortIndex = 0 # Used only for Round Robin Scheduling
numFreeSlotsInAllMachines = {}
maxFreeSlotsMachine = {} # Used only for Least Loaded Machine
maxFreeSlots = 0
jobTotalTime = {}

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
            data = reqGeneratorSocket.recv(4096).decode()

            if len(data) == 0: # the client does not send anything but just closes its side
                # Close the connection with the client but keep socket open for new connections
                reqGeneratorSocket.close()
                break

            queueOfRequests.put(data)



# Returns port number of worker depending on scheduling algo
def getWorkerId():

    global lastUsedWorkerPortIndex

    # Random selection of machine
    if(SCHEDULING_ALGO == "R"):
        return(random.choice(allPorts))

    # Round Robin selection
    elif(SCHEDULING_ALGO == "RR"):
        firstAvailablePortIndex = lastUsedWorkerPortIndex
        lastUsedWorkerPortIndex = (lastUsedWorkerPortIndex + 1) % len(allPorts)
        return(allPorts[firstAvailablePortIndex])

    # Least Loaded selection
    else:
        # If max free slots is 0, sleep for 1 second till it finds one
        while(maxFreeSlots <= 0):
            time.sleep(1)
        return maxFreeSlotsMachine["port"]

    
# THREAD 2 : SCHEDULES TASKS - both map and reduce (ACTS AS SERVER)
# New thread since we don't want scheduling to block listening to events

def scheduleRequest(lock):

    global tasksInProcess
    global queueOfReduceRequests
    global queueOfRequests

    # Get jobs from queue and execute (FIFO)

    while(True):

        # Only one map task and one reduce map task are executed in one iteration. All map tasks in the map queue are not executed at once to prevent starvation of reduce tasks and thus of the job (from completing). They have after all waited so long for their map tasks to complete executing!

        # Execute only map tasks
        if(not queueOfRequests.empty()):

            # Get the job
            newJobRequest = queueOfRequests.get()
            newJobRequest = json.loads(newJobRequest)


            # Extract and schedule map tasks before scheduling (going to) next job

            mapTasks = newJobRequest["map_tasks"]
            reduceTasks = newJobRequest["reduce_tasks"]
            job_id = newJobRequest["job_id"]

            # Create an entry for current job in "executing"
            tasksInProcess[job_id] = {"mapTasks":[], "reduceTasks":[], "reduceTasksInfo":[]}

            # Mark the sent map task of current job as "executing"
            tasksInProcess[job_id]["mapTasks"] = [x[list(x.keys())[0]] for x in mapTasks]
            tasksInProcess[job_id]["reduceTasks"] = [x[list(x.keys())[0]] for x in reduceTasks]
            tasksInProcess[job_id]["reduceTasksInfo"] = reduceTasks

            logging.info("[START] Job-{0} Started Execution".format(job_id))

            # Keep log of time at which job began
            jobTotalTime[job_id] = datetime.datetime.now()


            for task in mapTasks:

                # Now allot the map task to a worker machine
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:


                    while(True):
                        # Get machine to execute according to chosen scheduling algorithm
                        selectedWorker = getWorkerId()

                        # If no free slots, search for a machine with free slot
                        if(numFreeSlotsInAllMachines[selectedWorker] <= 0):
                            continue
                        
                        # If free slots, connect and send task

                        s.connect((WORKER_IP, selectedWorker))
                        
                        message= json.dumps(task)
                        s.send(message.encode())

                        logging.info("[INFO] Allotting task-{0} to {1} [SUCCESS]".format(task, selectedWorker))

                        # Number of available slots decreases by one since allotment successful
                        with lock:
                            numFreeSlotsInAllMachines[selectedWorker] -= 1

                        break



        # Execute only reduce tasks (if present)
        # These are added to reduceQueue only once all map tasks belonging to that job have completed executing

        if(not queueOfReduceRequests.empty()):

            # Get the job
            reduceTasks = queueOfReduceRequests.get()

            for task in reduceTasks:

                # Now allot the task to a worker machine
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:


                    while(True):
                        # Get machine to execute according to chosen scheduling algorithm
                        selectedWorker = getWorkerId()

                        if(numFreeSlotsInAllMachines[selectedWorker] <= 0):
                            continue

                        s.connect((WORKER_IP, selectedWorker))

                        # Send task
                        message= json.dumps(task)
                        s.send(message.encode())

                        logging.info("[INFO] Allotting task-{0} to {1} [SUCCESS]".format(task, selectedWorker))

                        with lock:
                            numFreeSlotsInAllMachines[selectedWorker] -= 1

                        break




# THREAD 3 : LISTENS TO UPDATES AND HEARTBEATS FROM WORKERS

def listenToUpdatesFromWorker(lock):

    global tasksInProcess
    global queueOfReduceRequests
    global numFreeSlotsInAllMachines
    global maxFreeSlotsMachine
    global maxFreeSlots


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
                break

            # Get the update from worker (and hence the task id of the map task that finished executing)
            update = json.loads(data)


            # Update number of free slots on that machine
            with lock:
                numFreeSlotsInAllMachines[update[PORTNUMBER]] += 1 


            maxFreeSlots = 0

            for machine in numFreeSlotsInAllMachines:
                if(numFreeSlotsInAllMachines[machine] > maxFreeSlots):
                    maxFreeSlotsMachine["port"] = machine
                    maxFreeSlotsMachine["numFreeSlots"] = numFreeSlotsInAllMachines[machine]
                    maxFreeSlots = numFreeSlotsInAllMachines[machine]


            # Execution update
            task_id = update["taskid"]

            job_id = None


            # Search the job the task belongs to and mark it as "no more executing" (by deleting its entry)
            for executingJob in tasksInProcess:
                if(task_id in tasksInProcess[executingJob]["mapTasks"]):
                    job_id = executingJob
                    tasksInProcess[executingJob]["mapTasks"].remove(task_id)
                    taskType = "mapTask"
                    break

            for executingJob in tasksInProcess:
                if(task_id in tasksInProcess[executingJob]["reduceTasks"]):
                    job_id = executingJob
                    tasksInProcess[executingJob]["reduceTasks"].remove(task_id)
                    taskType = "reduceTask"
                    break

            # If job_id is not initialised (Should ideally never come to this condition, yet handle)
            if not job_id:           
                break

            # If all reduce tasks of this job id have finished executing, remove this record (job) from "executing" list
            if(taskType == "reduceTask" and len(tasksInProcess[job_id]["reduceTasks"]) <= 0):
                tasksInProcess.pop(job_id)

                # Calculate time taken to complete job
                starttime = jobTotalTime.pop(job_id)
                duration = datetime.datetime.now() - starttime

                logging.info("[FINISH] JOB {0} Finished execution. Total duration - {1:.3f}".format(job_id, duration.total_seconds()*1000))

            # If all map tasks of this job id have finished executing, add to the reduce task queue
            if(taskType == "mapTask" and len(tasksInProcess[job_id]["mapTasks"]) <= 0):
                currentJob = tasksInProcess[job_id]

                # Push all reduce tasks belonging to that job in queue to be executed (reduce tasks can be executed parallelly)                     
                queueOfReduceRequests.put(currentJob["reduceTasksInfo"])




if __name__ == "__main__":
        
    if len(sys.argv) < 3:
        print("Usage: python master.py <path to config file> <scheduling algorithm>", file=sys.stderr)
        sys.exit(-1)

    PATH_TO_CONFIG = sys.argv[1]
    SCHEDULING_ALGO = sys.argv[2]

    if(SCHEDULING_ALGO not in ["R", "RR", "LL"]):
        print("Please enter R, RR or LL only.\nR for Random\nRR for Round Robin\nLL for Least Loaded\n")
        sys.exit(-1)

    # debug -> if logs should be print to the terminal
    debug = True
    if(len(sys.argv) == 4):
        debug = sys.argv[3]
        if(debug == 'False'): debug = False


    if(debug): 
        logging.getLogger().addHandler(logging.StreamHandler())

    # Get all workers and their port numbers from the config file
    with open(PATH_TO_CONFIG, "r") as f:
        configs = f.read()

    configs = json.loads(configs)
    configs = configs[MAINKEYINCONFIG]


    maxFreeSlots = 0

    for config in configs:
        allPorts.append(config["port"])
        numFreeSlotsInAllMachines[config["port"]] = config["slots"]

        # Update if this machine has the maximum number of slots (used for LL scheduling)
        if(config["slots"] > maxFreeSlots):
            maxFreeSlotsMachine["port"] = config["port"]
            maxFreeSlotsMachine["numFreeSlots"] = config["slots"]
            maxFreeSlots = config["slots"]


    if(debug):
        print("\n----------REQUESTS BEGIN------------\n")

    # Set up locks to prevent multiple threads from modifying "freeSlotsNum" at the same time
    
    lock = threading.Lock()

    try:
        t1 = threading.Thread(target = listenRequest)
        t2 = threading.Thread(target = scheduleRequest, args=(lock,))
        t3 = threading.Thread(target = listenToUpdatesFromWorker, args=(lock,))

        t1.start()
        t2.start()
        t3.start()
        
        # We don't want to join (stop master till threads finish executing, they don't stop executing)

    except Exception as e:
        if(debug): 
            print("Error in starting thread: ", e)


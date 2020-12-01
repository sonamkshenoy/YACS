import sys
import json
import socket
import threading
import time
import datetime

from allConfigs import *

import logging

"""
Worker configs:
    1. WORKER_PORT
    2. WORKER_CONFIG
    3. WORKER_ID
    4. WORKER_IP
"""


# THREAD 1: LISTENS TO TASKS TO EXECUTE (ACTS AS CLIENT)

def listenToTasks():

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
                break

            task = json.loads(data)
                

            taskid = task["task_id"]
            duration = task["duration"]

            t = threading.Thread(target = executeTaskAndUpdateMaster, args=(taskid, duration))
            t.start()


# THREAD 2: EXECUTES TASKS AND UPDATES MASTER ABOUT THIS

def executeTaskAndUpdateMaster(task_id, durationOfTask):
    global freeSlotsNum

    logging.info("[START] Task-{0} Started Execution".format(task_id))
    starttime = datetime.datetime.now()

    # Execute task of x duration
    while(durationOfTask):
        # Reduce remaining task by 1 after 1 second (simulate passing of 1 second using time.sleep())
        time.sleep(1) 
        durationOfTask -= 1

    # Once duration of task done, update master
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((MASTER_IP, MASTER_UPDATE_PORT))
        duration = datetime.datetime.now() - starttime
        message = json.dumps({PORTNUMBER: WORKER_PORT, "taskid": task_id})
        logging.info("[FINISH] TASK {0} Finished execution. Total duration - {1:.3f}".format(task_id, duration.total_seconds()*1000))
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

	logging.basicConfig(
		level=logging.INFO,
		format="(%(asctime)s) %(message)s",
		handlers=[
			logging.FileHandler("logs/worker_{0}.log".format(WORKER_ID)),
		]
	)
	
	# debug -> if logs should be print to the terminal
	debug = True
	if(len(sys.argv) == 4):
		debug = sys.argv[3]
		if(debug == 'False'): debug = False
		
	if(debug): logging.getLogger().addHandler(logging.StreamHandler())


	# Once details fetched, set up socket for listening to tasks and thread for executing them

	try:
		t1 = threading.Thread(target = listenToTasks)
		# t2 = threading.Thread(target = sendHeartbeats)

		t1.start()
		# t2.start()

		# We don't want to join (stop master till threads finish executing, they don't stop executing)

	except Exception as e:
		print("Error in starting thread: ", e)






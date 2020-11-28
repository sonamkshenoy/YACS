import socket
import random
import sys
import json

HOST = "localhost"
PORT = 5000

if __name__ == "__main__":

    # Make sure user passes no. of requests
    if len(sys.argv) < 2:
        print("Usage: python request.py <no. of requests>", file=sys.stderr)
        sys.exit(-1)

    numRequests = int(sys.argv[1])

    task_id = 1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Create socket connection to Port 5000 of master
        s.connect((HOST, PORT))

        # Generate random durations between 1 and 50 seconds

        for i in range(numRequests):
            request = {
                "job_id": "job_" + str(i),
                "map_tasks":[],
                "reduce_tasks": []
            }

            # Generalise even number of map and reduce tasks. Just make sure there is at least 1 map task, and more map tasks than reduce
            numMapTasks = random.randint(5, 30)
            numRedTasks = random.randint(1, 5)

            for j in range(numMapTasks):
                mapTask = {
                    "task_id" : "task_" + str(task_id),
                    "duration" : random.randint(0, 50)
                }
                task_id += 1
                request["map_tasks"].append(mapTask)


            for j in range(numRedTasks):
                redTask = {
                    "task_id" : "task_" + str(task_id),
                    "duration" : random.randint(0, 50)
                }
                task_id += 1
                request["reduce_tasks"].append(redTask)

            print(request)

            # Send request
            s.send(b"" + json.dumps(request).encode())

            # Add a time limit here, if doesn't receive response from server till 1 minute => master node not working (listening).
            data = s.recv(1024)

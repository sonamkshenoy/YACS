# YACS
Big Data Scheduler YACS - "Yet Another Centralized Scheduler"   



## Folder Structure  

* config.json : Contains the info about worker (worker id, port worker is running on, number of slots in the worker)   
* allconfigs.py : Common variable names that are used in almost all files   
* master.py : The main resource scheduler   
* worker.py : The worker that runs slots for execution of tasks   
* requests.py : The request generator    
* resources/references.txt : References for certain Python functions   
* resources/variableDescriptions.txt : Explanation of structure of certain variables that have a slightly complicated structure in master.py   
* resources/functionDescriptions.txt : Explanation of functions in both master.py and worker.py    
* resources/sample_request.txt : Structure of a job request (sent by a request generator)   

---

## Terminologies   
* Master: The main node that schedules the tasks of the jobs amongst the workers depending on the scheduling algorithm and availability of free slots in the worker   
* Job: A job is made up of tasks. Tasks can be either map or reduce tasks   
* Task: A map or reduce task   
* Worker: The machine running one or more tasks. A worker consists of one or more slots depending on the resources available   
* Slot: A slot is the basic unit of a worker on which a single task can run   

---

## Scheduling Algorithms  
1. Random  
2. Round-Robin (A slight modification has been made here. Instead of starting search from the first worker id everytime, it starts search in round-robin fashion from the last allocated node.)  
3. Least Loaded

----

## Working   
The worker has 2 threads - one that listens to requests from the master and another that simulates a slot for execution and updating the master.  
The master has 2 threads too - one hat listens to requests from the request generator and another that listens to updates from the workers.   
Since we are just simulating the working of a scheduler, the number of slots in a worker has been fixed in the `config.json` file instead of checking the resources in the machine. The execution of the task has been simulated as well by decreasing the remaining duration of the task every second. As soon as the task finishes executing, the master (scheduler) is updated.  


**Implementation**

- First, the request generator sends a sequence of jobs to the master (scheduler) for execution.   
- The master on receiving the jobs, adds them to a queue and schedules them one at a time.  
- Since reduce tasks are dependent on map tasks belonging to the job, they are scheduled only once all map tasks belonging to the job have completed execution. Thus, initially only map tasks are scheduled amongst workers depending on the scheduling algorithm. All tasks belonging to a job are scheduled at once back-to-back to avoid starvation.  
- Once it has allocated map tasks belonging to a job to workers, the master checks if there are any reduce tasks in the queue. If yes, it schedules them amongst workers, before going to the next set (job) of map tasks (more explanation in Bullet point x).  
- The master on choosing a node for execution of a task, establishes a socket connection with that worker.   
- The worker first checks if there are any free slots available with it. If yes, it sends a positive response and goes ahead with execution of the task, else sends a negative feedback.  
- The worker executes the task by creating a new thread. This thread simulates the behaviour of a slot. It runs for the duration specified for the task.  
- Once done, it updates the master about this.  
- Whenever, there is a decrease (on allocating) or increase (on finishing execution) in the number of free slots in a worker, it sends an update to the master, which runs a separate thread just for listening for updates from the workers.  
- Now, coming back to master, if it receives positive feedback from the worker as mentioned in Bullet point y it continues with allocating the next map task, else retries selecting another machine for the same task, depending on the scheduling algorithm chosen.   
- When a master receives updates from a worker that has finished execution of a map task, it reduces the count of remaining map tasks by one. If the all map tasks belonging to a job have finished execution, it now schedules the reduce tasks in the exact same manner it did with the map tasks.  
- This way it reduces count of reduce tasks as and when they finish execution.  
- Once all map and reduce tasks belonging to a job have finished execution, it logs that job as "done".




----

## Steps to execute  
1. Run master  

Scheduling algorithm can take these values:.  
* `R` for Random
* `RR` for Round Robin
* `LL` for Least Loaded

```
python3 master.py <path to config file> <scheduling algorithm>

Example:
python3 master.py config.json RR
```

2. Run workers
Each worker has to be run on a separate terminal. The port number and worker ids should correspond to the configurations specified in `config.json`.   
```
python3 worker.py <worker port number> <worker id>

Example:
python3 worker.py 4000 1
python3 worker.py 4001 2
python3 worker.py 4002 3
```

3. Run request generator
```
python3 requests.py <number of requests>

Example:
python3 requests.py 50
```

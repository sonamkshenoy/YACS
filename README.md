# YACS
Big Data Scheduler YACS - "Yet Another Centralized Scheduler"

#Steps to run
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
Each worker is to be run on a separate terminal.
```
python3 worker.py <worker port number> <worker if>

Example:
python3 worker.py 4000 1
python3 worker.py 4000 2
python3 worker.py 4000 3
```

3.
Run request generator
```
python3 requests.py <number of requests>

Example:
python3 requests.py 50
```

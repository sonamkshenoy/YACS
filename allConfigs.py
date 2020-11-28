# File and variable names
CONFIGFILE = "config.json"
MAINKEYINCONFIG = "workers"

# IPs and Ports
MASTER_SCHEDULING_PORT = 5000 # Port that listens to requests from request generator and schedules them to workers
MASTER_UPDATE_PORT = 5001 # Port that listens to updates from workers and executes reduce tasks once done
MASTER_IP = "localhost"
WORKER_IP = "localhost"
FIRST_WORKER_PORT = 4000 # Any random value is fine (preferably correct one), used only during first initialisation, but which is not used anywhere

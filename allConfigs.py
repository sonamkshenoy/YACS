# File and variable names
CONFIGFILE = "config.json"
MAINKEYINCONFIG = "workers"

# IPs and Ports
MASTER_SCHEDULING_PORT = 5000 # Port that listens to requests from request generator and schedules them to workers
MASTER_UPDATE_PORT = 5001 # Port that listens to updates from workers and executes reduce tasks once done
MASTER_IP = "localhost"
WORKER_IP = "localhost"


# Variables
# SLOTS_AVAILABLE = "Available"
# SLOTS_NOT_AVAILABLE = "Not Available"
# NUMFREESLOTS = "numFreeSlots"
# TYPETASK = "typeTask"
PORTNUMBER = "portNumber"
# FREESLOTUPDATE = "UpdateFreeSlots"
# TASKEXEC_AND_FREESLOTUPDATE = "MapTaskOverAndUpdateFreeSlots"
# HEARTBEAT = "Heartbeat"
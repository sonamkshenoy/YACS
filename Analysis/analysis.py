import argparse
import json
import numpy as np
from datetime import datetime

# NOTE: 'data.json' contains the extracted data which is used for plotting necessary graphs

# create the data.json file if it doesn't exist
from os import path
if(path.exists('data.json') == False):
	fp = open('data.json', 'w+')
	fp.close()
	
if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help='Location of configuration file', required = 'True')
	parser.add_argument('-a', '--algo', help='Scheduling Algorithm', required = 'True')
	parser.add_argument('-b', '--bin_interval', help='Binning interval', required = 'True')
	args = parser.parse_args()
	
	config = args.config
	algo = args.algo
	bins = int(args.bin_interval)
	
	with open('data.json', 'r') as fp:
		data = fp.read()
		
	# if 'data.json' is empty, create a new dictionary, else read the json file
	if(data): data = json.loads(data)
	else: data = {}
	
	# read the config file to get list of worker ID
	with open(config, "r") as fp:
		configs = fp.read()		
	configs = json.loads(configs)
	configs = configs['workers']
	worker_id = []
	for config in configs:
		worker_id.append(config["worker_id"])		
			
	# extract time taken to finish each job from log file of master
	time = []
	with open('logs/master.log', 'r') as fp:
		lines = fp.readlines()
		
		for line in lines:		
			if(line.split()[2] == '[FINISH]'):
				time.append(float(line.split()[-1]))
		
	data[algo] = {'mean':np.mean(time)/1000, 'median':np.median(time)/1000}	
	data[algo]['workers'] = []
	
	# for each worker machine
	for id in worker_id:
		time = []
		with open('logs/worker_{0}.log'.format(id), 'r') as fp:
			lines = fp.readlines()
			
			# convert start time to datetime format
			start = lines[0].split()
			start_time = start[0] + ' ' + start[1]
			start_time = datetime.strptime(start_time, '(%Y-%m-%d %H:%M:%S,%f)')
			
			# convert end time to datetime format
			end = lines[-1].split()
			end_time = end[0] + ' ' + end[1]
			end_time = datetime.strptime(end_time, '(%Y-%m-%d %H:%M:%S,%f)')
			
			# calculate total duration to determine the binning interval of graph
			total_duration = (end_time - start_time).seconds + 1
			keys = list(range(0, total_duration+1, bins))
			keys.append(total_duration)
			keys.sort()
			tasks = {}
			
			# initialise all values of tasks to -1 
			for i in keys:
				tasks[i] = -1
			tasks[0] = 0
			ind = 1			
			
			active = 0 # number of active tasks
			for line in lines:	
				line = line.split()
				
				# calculate the current time
				date_time = line[0] + ' '+ line[1]
				timestamp = datetime.strptime(date_time, '(%Y-%m-%d %H:%M:%S,%f)')
				
				# if difference is more than the current bin, update 'tasks'
				diff = (timestamp - start_time).total_seconds()
				if(diff >= keys[ind]):
					tasks[keys[ind]] = active
					ind += 1
				
				# active tasks increments by one
				if(line[2] == '[START]'):
					active += 1
					
				# active tasks decrements by one
				if(line[2] == '[FINISH]'):
					active -= 1
					time.append(float(line[-1]))
					
			# account for missing bin values
			tmp = tasks[0]
			for i in keys[1:]:
				if(tasks[i] == -1):
					tasks[i] = tmp
				else: tmp = tasks[i]
				
			# update 'data'
			data[algo]['workers'].append({'id':id, 'mean':np.mean(time)/1000, 'median':np.median(time)/1000, 'schedule':tasks})
		
	# write the updated 'data' to json file
	with open("data.json", "w") as outfile:  
		json.dump(data, outfile) 
				
	
	

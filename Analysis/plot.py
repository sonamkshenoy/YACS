import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

with open('data.json', "r") as fp:
	data = fp.read()
data = json.loads(data)

# TASK 1 - Compare the mean and median task and job completion times for the 3 scheduling algorithms.
means = []
median = []
for key in data:
	tmp1 = []
	tmp1.append(data[key]['mean'])
	
	tmp2 = []
	tmp2.append(data[key]['median'])
	
	for workers in data[key]['workers']:
		tmp1.append(workers['mean'])
		tmp2.append(workers['median'])
		
	means.append(tmp1)	
	median.append(tmp2)
	
x_label = ['Master']
for workers in data[key]['workers']:
	x_label.append('Worker_{0}'.format(workers['id']))

width = 0.2
r1 = np.arange(len(means[0]))
r2 = [x + width for x in r1]
r3 = [x + width for x in r2]


fig, ax = plt.subplots()
rects1 = ax.bar(r1, means[0], width, label='Random')
rects2 = ax.bar(r2, means[1], width, label='Round Robin')
rects3 = ax.bar(r3, means[2], width, label='Least Load')

ax.set_ylabel('Mean time')
ax.set_title('Mean time for master and workers')
ax.set_xticks(r1)
ax.set_xticklabels(x_label)
ax.legend()
plt.savefig('Graphs/Mean.png')

fig, ax = plt.subplots()
rects1 = ax.bar(r1, median[0], width, label='Random')
rects2 = ax.bar(r2, median[1], width, label='Round Robin')
rects3 = ax.bar(r3, median[2], width, label='Least Load')

ax.set_ylabel('Median time')
ax.set_title('Median time for master and workers')
ax.set_xticks(r1)
ax.set_xticklabels(x_label)
ax.legend()
plt.savefig('Graphs/Median.png')

# TASK 2 - Plots the number of tasks scheduled on each machine, against time for each scheduling algorithm.
for key in data:
	
	plot_data = []
	for worker in data[key]['workers']:
		plot_data.append(worker['schedule'])
		
	fig, ax = plt.subplots()
	for i, worker in zip(plot_data, x_label[1:]):
		x_values = list(i.keys())
		y_values = list(i.values())
		ax.plot(x_values, y_values ,label = worker)
		
	plt.savefig('Graphs/{0}.png'.format(key))
			











	
	
	


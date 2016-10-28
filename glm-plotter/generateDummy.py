"""
    JAC - jdechalendar@stanford.edu
    Oct 27, 2016
    Generate dummy data for quick demo of glm-plotter app
"""

import myParser, random
objs,modules,commands = myParser.readGLM("uploads/curr.glm")
#print([obj['name'] for obj in objs])

# with open("uploads/archive/load_11.csv", 'r') as fr:
# 	lines = fr.readlines()
# templateDates = [l.split(',')[0][:-7] + ' PST' for l in lines if l[0] != "#"]

# for ii in range(len(templateDates)):
# 	templateDates[ii]=templateDates[ii][:11] + str(ii) + templateDates[ii][13:]
# print(templateDates)

import pandas as pd
datelist = pd.date_range(pd.datetime.today(), periods=96, freq = "15min").tolist()

templateDates = [d.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' PST' for d in datelist]
for obj in objs:
	with open("uploads/"+obj['name']+'.csv', 'w') as fw:
		fw.write("# timestamp,voltage_A.real\n")
		for myDate in templateDates:
			fw.write(myDate + ',' + str(round(1000*random.random())/10) + '\n')


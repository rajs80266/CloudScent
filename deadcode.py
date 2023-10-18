import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 6})
import csv

x = []
y = []

with open('deadcode.csv','r') as csvfile:
	lines = csv.reader(csvfile, delimiter=',')
	for row in lines:
		x.append(row[0])
		y.append(float(row[1]))

plt.plot(x, y, color = 'red', linestyle = 'dashed',
		marker = 'X')

plt.xticks(rotation = 25)
plt.xlabel('loc',fontsize=12)
plt.ylabel('# code smells', fontsize=12)
plt.title('Dead code', fontsize = 12)
plt.grid()
plt.legend()
plt.savefig('deadcode.pdf')
plt.show()


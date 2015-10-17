import abstractions as ab
from time import sleep
import plotly.plotly as py
from plotly.graph_objs import Scatter

def loop(i):
	d = ab.response_dict()
	var1,var2,var3,var4,var5,var6,var7, var8 = ab.create_row_template(d)
	var0 = i

	if i == 1:
		ab.create_price_table('test_table2.sqlite')
	ab.update_prices((var0,var1,var2,var3,var4,var5,var6,var7,var8),'test_table2.sqlite')

	x_data = ab.get_column('time', 'data', 'test_table2.sqlite')
	y_data = ab.get_column('last', 'data', 'test_table2.sqlite')

	'''some magic that makes the plot and uploads it to the plotly hosting site'''
	trace0 = Scatter(x=x_data, y=y_data)
	data = [trace0]
	unique_url = py.plot(data, filename = 'basic-line')

	'''waits for n seconds before repeating the loop and adding one to the 
	counter (for use in the ID parapater of each row in the data set)'''
	sleep(10)

for x in range(11):
	loop(x)

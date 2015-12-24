import abstractions as ab
from time import sleep
import plotly.plotly as py
from plotly.graph_objs import Scatter

def graph():
	print("Graphing")
	"""Fetching data from the table and piping it into to plotly to generate the graph"""
	num_rows = ab.count_rows("prices", 'test_table2.sqlite') 
	x_data = ab.get_column('time', 'prices', 'test_table2.sqlite', num_rows - 10)
	y_data = ab.get_column('last', 'prices', 'test_table2.sqlite', num_rows - 10)

	# some magic that makes the plot and uploads it to the plotly hosting site
	trace0 = Scatter(x=x_data, y=y_data)
	data = [trace0]
	unique_url = py.plot(data, filename = 'basic-line', auto_open=False)
	# waiting before running again



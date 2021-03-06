from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class PlotCanvas(FigureCanvas):
	def __init__(self, parent=None, width=4.6, height=4, dpi=70):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.toolbar = NavigationToolbar(self, self)
		self.toolbar.hide()
		fig.canvas.mpl_connect('button_release_event', self.toolbar.pan)

	def plot(self, title, points):
		ax = self.figure.add_subplot(111)
		f = zoom_factory(ax, base_scale=1.2)

		ax.cla()
		if points is not None:
			vertices = []
			for item in points:
				ax.annotate("{}({:.2f}, {:.2f})".format(*item), (item[1], item[2])).set_fontsize(8)
				vertices.append([item[1], item[2]])
			tr = plt.Polygon(np.array(vertices))
			ax.add_patch(tr)
			ax.set_xlim(-5, 10)
			ax.set_ylim(-5, 10)
			ax.set_title(title).set_fontsize(9)
		self.draw()

	def matrix(self, title, points):
		ax = self.figure.add_subplot(111)
		ax.cla()

		if points is not None:
			points = np.abs(np.uint8(points))
			size = np.max(points) + 2
			data = np.zeros((size, size))

			for item in points:
				data[int(item[1]), int(item[0])] = 1

			ax.annotate("A", (points[0][0] + .4, points[0][-1] + .3)).set_color('white')
			if len(points) > 1:
				ax.annotate("B", (points[-1][0]+.4, points[-1][-1]+.3)).set_color('white')

			if len(points) > 2:
				data[points[0][-1], points[0][0]] = .5
				data[points[-1][-1], points[-1][0]] = .5

			ax.pcolor(data, cmap='gist_yarg', edgecolor='black', lw=0.5)

			ax.xaxis.set(ticks=np.arange(0.5, size), ticklabels=range(size))
			ax.yaxis.set(ticks=np.arange(0.5, size), ticklabels=range(size))

			ax.set_title(title).set_fontsize(9)
		self.draw()


def zoom_factory(ax, base_scale=2.):
	def zoom_fun(event):
		# get the current x and y limits
		cur_xlim = ax.get_xlim()
		cur_ylim = ax.get_ylim()
		# set the range
		cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
		cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
		xdata = event.xdata  # get event x location
		ydata = event.ydata  # get event y location
		if event.button == 'up':
			# deal with zoom in
			scale_factor = 1/base_scale
		elif event.button == 'down':
			# deal with zoom out
			scale_factor = base_scale
		else:
			# deal with something that should never happen
			scale_factor = 1
		# set new limits
		ax.set_xlim([xdata - cur_xrange*scale_factor, xdata + cur_xrange*scale_factor])
		ax.set_ylim([ydata - cur_yrange*scale_factor, ydata + cur_yrange*scale_factor])
		ax.figure.canvas.draw() # force re-draw

	fig = ax.get_figure() # get the figure of interest
	# attach the call back
	fig.canvas.mpl_connect('scroll_event', zoom_fun)

	# return the function
	return zoom_fun

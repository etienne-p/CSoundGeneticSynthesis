import wave
import numpy as np
import matplotlib.pyplot as plt
from itertools import count
from graphviz import Digraph

def plot_audio_file(filename):
	spf = wave.open(filename + '.wav','r')
	signal = spf.readframes(-1)
	signal = np.fromstring(signal, 'Int16')
	fs = spf.getframerate()
	time = np.linspace(0, len(signal)/fs, num=len(signal))
	plt.figure(1)
	plt.title(filename)
	plt.plot(time,signal)
	plt.show()

def plot_tree(tree, filename):
	g = Digraph('G', filename=filename, format='png')
	# assign ids to nodes
	for i, n in zip(count(), tree.depth_first()):
		n.id = str(i)
	# create nodes
	for n in tree.depth_first():
		g.node(n.id, n.value.value if isinstance(n.value.value, str) else '{0:.2f}'.format(n.value.value))
	# create edges
	for n in tree.depth_first():
		for c in n.children:
			g.edge(c.id, n.id)
	# render image
	g.view()
	
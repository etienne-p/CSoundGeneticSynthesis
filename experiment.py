import os
import shutil
from subprocess import TimeoutExpired
import matplotlib.pyplot as plt
import numpy as np
import imageio

from code_gen import graph_to_csound 
from tree import make_dsp_graph, clone_graph
from elements import read_op_set, make_arg
from genetic_operators import mutate_consts, subtree_mutation
from analysis import spectrogram_from_file, sound_similarity
from util import lerp, render_audio, clean_dir, wait_for_processes_completion
from vizualisation import plot_tree

class Individual:
	def __init__(self, tree):
		self.tree = tree
		self.total_nodes = tree.total_nodes_count()
		self.filename = None
		self.similarity = -1
		self.fitness = -1

def initialize(count, terminal_likelyhood, max_depth, intern_op_set, term_op_set):
	'generate an initial population of individuals with random programs'
	return [Individual(make_dsp_graph(intern_op_set, term_op_set, \
		terminal_likelyhood, max_depth)) \
		for i in range(count)]

def generate_offsprings(population, lerp_factor, intern_op_set, \
	term_op_set, terminal_likelyhood, max_depth):
	'generate offsprings based on the current generation individuals'
	# note we recycle the current generation as is:
	# you want good solutions to be allowed survival
	offsprings = population[:]
	# part of the offsprings are generated through constants mutation
	offsprings += [Individual(mutate_consts(i.tree, lerp_factor)) for i in population]
	# part of the offsprings are generated through subtree mutation
	for i in population:
		child, success = subtree_mutation(i.tree, intern_op_set, term_op_set, terminal_likelyhood, max_depth) 
		if success:
			offsprings.append(Individual(child))
	# the number of offsprings generated through each method is arbitrary
	offsprings += initialize(len(population), terminal_likelyhood, max_depth, intern_op_set, term_op_set)
	return offsprings

def render_individuals(population, duration, directory):
	# assign filenames
	count = 0
	for i in population:
		i.filename = os.path.join(directory, 'tmp_' + str(count).zfill(5))
		count = count + 1
	# launch audio rendering processes using csound, asynchronously
	processes = [render_audio(graph_to_csound(i.tree), duration, i.filename, False) for i in population]
	# csound may hang randomly, looks like memory allocation issues, not sure yet
	# happens once in a while but that's enough to compromise an experiment,
	# so we watch processes and kill those who don't respond (ok that sounds bad)
	for p in processes:
		try:
			outs, errs = p.communicate(timeout=5)
		except TimeoutExpired:
			p.kill()
			outs, errs = p.communicate()
			print('killed non responsive process: ', outs, errs)
	return processes

def evaluate_similarity(population, duration, ref_spectrum, directory):
	# render individuals that need it (no need to render those who are exact copies of their parent)
	new_individuals = [x for x in population if x.similarity < 0]
	processes = render_individuals(new_individuals, duration, directory)
	wait_for_processes_completion(processes)
	# evaluate per individual similarity with the target sound
	for i in new_individuals:
		if os.path.isfile(i.filename + '.wav'):
			spectr = spectrogram_from_file(i.filename + '.wav')[2]
			i.similarity = sound_similarity(spectr, ref_spectrum) if spectr is not None else 0
	
def selection(population, num_selected, ref_spectrum, duration, complexity_factor, directory):
	'select the population best candidates based on our fitness function'
	evaluate_similarity(population, duration, ref_spectrum, directory)
	average_total_nodes = np.mean([i.total_nodes for i in population])
	for i in population:
		# we reward simple solutions, that is those who have less nodes
		complexity_deviation = i.total_nodes / average_total_nodes
		i.fitness = i.similarity# / lerp(1., complexity_deviation, complexity_factor)
		print(i.fitness)
	# sort by descending fitness
	sorted_population = sorted(population, key=lambda i: i.fitness, reverse=True)
	# only return the fittest individuals
	return sorted_population[:num_selected]

def plot_fitness(fitness_over_time, save_path=None):
	t = np.arange(0, fitness_over_time.shape[0], 1)
	fig, ax = plt.subplots()
	for i in range(fitness_over_time.shape[1]):
		ax.plot(t, fitness_over_time[:,i])
	ax.set(xlabel='generation', ylabel='fitness',
	       title='Fitness Over Generations')
	ax.grid()
	if save_path is not None:
		plt.savefig(save_path)
	plt.show()

class ExperimentParms:
	def __init__(self, 
				file,
				intern_op_set,
				term_op_set,
				num_generations,
				init_population_size,
				selected_population_size, 
				max_depth,
				terminal_likelyhood,
				lerp_factor,
				complexity_factor):
		self.file = file
		self.intern_op_set = intern_op_set
		self.term_op_set = term_op_set
		self.num_generations = num_generations
		self.init_population_size = init_population_size
		self.selected_population_size = selected_population_size
		self.max_depth = max_depth
		self.terminal_likelyhood = terminal_likelyhood
		self.lerp_factor = lerp_factor
		self.complexity_factor = complexity_factor


class ExperimentViz:
	def __init__(self, directory):
		self.directory = directory
		self.best_candidate = None
		self.frames = []
	def update(self, population):
		if self.best_candidate != population[0]:
			count = len(self.frames)
			graph_path = os.path.join(self.directory, 'frame_' + str(count).zfill(5))
			plot_tree(population[0].tree, graph_path)
			self.frames.append(graph_path)
	def save(self, path):
		images = [imageio.imread(f + '.png') for f in self.frames]
		s0, s1 = 0, 0
		# determine max dimensions
		for i in images:
			s0 = max(s0, i.shape[0])
			s1 = max(s1, i.shape[1])
		# knowing max dimensions, pad images
		padded_images = []
		for i in images:
			d0 = s0 - i.shape[0]
			d1 = s1 - i.shape[1]
			hd0 = int(d0 * .5)
			hd1 = int(d1 * .5)
			padded = np.ones((s0, s1, i.shape[2]), dtype=np.uint8) * 255
			padded[hd0:hd0+i.shape[0],hd1:hd1+i.shape[1]] = i
			padded_images.append(padded)
		imageio.mimsave(path, padded_images)

class Experiment:
	def __init__(self, parms, viz=None):
		self.parms = parms
		self.viz = viz

	def initialize(self):
		times, _, self.ref_spectrum = spectrogram_from_file(self.parms.file)
		self.audio_duration = times[-1]
		self.fitness_over_time = np.zeros((self.parms.num_generations, self.parms.selected_population_size))
		self.population = initialize(
			self.parms.init_population_size, 
			self.parms.terminal_likelyhood, 
			self.parms.max_depth, 
			self.parms.intern_op_set, 
			self.parms.term_op_set)
		
	def generation_step(self):
		self.population = generate_offsprings(
			self.population, 
			self.parms.lerp_factor, 
			self.parms.intern_op_set,
			self.parms.term_op_set, 
			self.parms.terminal_likelyhood, 
			self.parms.max_depth)
		self.population = selection(
			self.population, 
			self.parms.selected_population_size, 
			self.ref_spectrum, 
			self.audio_duration, 
			self.parms.complexity_factor, 'tmp')
		if self.viz is not None:
			self.viz.update(self.population)
		return [i.fitness for i in self.population]

	def end(self):
		dir_name = 'output'
		if not os.path.exists(dir_name):
			os.makedirs(dir_name)
		if self.viz is not None:
			self.viz.save(os.path.join(dir_name, 'anim.gif'))
		clean_dir('tmp')
		# render best candidate in output folder
		processes = render_individuals(self.population[:1], self.audio_duration, dir_name)
		wait_for_processes_completion(processes)
		# plot fitness and save it in output folder
		plot_fitness(self.fitness_over_time, os.path.join(dir_name, 'fitness_over_time'))
		# also store a plot of the dsp graph
		plot_tree(self.population[0].tree, os.path.join(dir_name, 'graph'))

	def run(self):
		self.initialize()
		for i in range(self.parms.num_generations):
			fitness = self.generation_step()
			self.fitness_over_time[i,:] = np.array(fitness)[:self.fitness_over_time.shape[1]]
		self.end()

intern_op_set, term_op_set = read_op_set()

parms = ExperimentParms(
	file='clap.wav',
	intern_op_set=intern_op_set, 
	term_op_set=term_op_set,
	num_generations=10,
	init_population_size=6,
	selected_population_size=6,
	max_depth=5,
	terminal_likelyhood=0.5,
	lerp_factor=0.2,
	complexity_factor=0.4)

Experiment(parms, ExperimentViz('tmp')).run()







	







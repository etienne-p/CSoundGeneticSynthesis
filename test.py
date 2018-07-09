import os
from code_gen import graph_to_csound 
from elements import read_op_set, make_arg
from util import render_audio
from tree import make_dsp_graph
from vizualisation import plot_tree, plot_audio_file
from genetic_operators import subtree_mutation

def viz_genetic_op():
	terminal_likelyhood = 0
	max_depth = 2
	intern_op_set, term_op_set = read_op_set()

	# viz genetic ops
	base_tree = make_dsp_graph(intern_op_set, term_op_set, terminal_likelyhood, max_depth)
	plot_tree(base_tree, 'before')
	child_tree, _ = subtree_mutation(base_tree, intern_op_set, term_op_set, terminal_likelyhood, max_depth)
	plot_tree(child_tree, 'after')

def test_program_gen():
	terminal_likelyhood = 0
	max_depth = 5
	intern_op_set, term_op_set = read_op_set()
	duration = 2

	for i in range(32):
		g = make_dsp_graph(make_arg('a'), intern_op_set, term_op_set, \
			terminal_likelyhood, max_depth)
		prg = graph_to_csound(g)
		print(prg)
		render_audio(prg, duration, 'tmp')
		assert(os.path.isfile('tmp.wav'))
		os.remove('tmp.wav')


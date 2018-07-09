from random import random, choice
from elements import const_from_arg, pick_opcode, pick_opcode_weighted, make_arg

class Node:
	def __init__(self, value):
		self.children = []
		self.value = value
		self.id = -1
	def __len__(self):
		return len(self.children)
	def __getitem__(self, position):
		return self.children[position]
	def add_child(self, child):
		self.children.append(child)
	def clone(self):
		return Node(self.value.clone())
	def depth_first(self):
		yield self # first return current node
		for child in self.children:
			yield from child.depth_first()
	def total_nodes_count(self):
		count = 1 # itself
		for n in self.depth_first():
			count = count + 1
		return count

def clone_graph(node):
	v = node.clone()
	if len(node) > 0:
		for child in node:
			v.add_child(clone_graph(child))
	return v

opcode_selection_weight_matrix = [
#OSC, 	RAND, 	ENV, 	DELAY, 	FILTER, REVERB, MATH
#---------------------------------------------------
#OSC
[1, 	1, 		4, 		1, 		1, 		1, 		1],
#RAND
[1, 	1, 		2, 		1, 		1, 		1, 		1], 	
#ENV 
[1, 	1, 		1, 		1, 		1, 		1, 		1],	
#DELAY
[1, 	1, 		0, 		1, 		1, 		1, 		1],	
#FILTER 
[1, 	1, 		0, 		1, 		1, 		1, 		1],
#REVERB
[1, 	1, 		0, 		1, 		1, 		0,		1],
#MATH
[1, 	1, 		1, 		1, 		1, 		1, 		1],
#OUT	
[1, 	1, 		0, 		2, 		2, 		2, 		2]]

def continue_dsp_graph(parent_tag, dst_arg, intern_op_set, term_op_set, terminal_likelyhood, max_depth):
	# TMP debug, depth is -1 as we add consts to terminal nodes, should not go below -1
	assert(max_depth >= -1), 'dst arg:' + str(dst_arg)
	# special case if dst_arg type is 'i', we have to use a const
	if dst_arg.type_ == 'i':
		return Node(const_from_arg(dst_arg))
	# add a terminal on an internal node
	use_terminal = random() < terminal_likelyhood or max_depth == 0
	opcode, tag = pick_opcode_weighted( \
		term_op_set if use_terminal else intern_op_set, dst_arg, \
		opcode_selection_weight_matrix[parent_tag])
	node = Node(opcode)
	# add children to the node
	for arg in node.value.args:
		node.add_child(continue_dsp_graph(tag, arg, \
			intern_op_set, term_op_set, terminal_likelyhood, max_depth - 1))
	return node

# free the user from specifying the tag and arg type when generating a new tree
def make_dsp_graph(intern_op_set, term_op_set, terminal_likelyhood, max_depth):
	return continue_dsp_graph(7, make_arg('a'), intern_op_set, term_op_set, terminal_likelyhood, max_depth)
	


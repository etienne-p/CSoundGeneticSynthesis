from random import choice, random
from util import lerp
from tree import clone_graph, continue_dsp_graph 
from elements import value_from_spec, OpType

def update_const(const, lerp_factor):
	new_value = value_from_spec(const.spec)
	if isinstance(new_value, float):
		new_value = lerp(new_value, const.value, lerp_factor)
	return const._replace(value=new_value)

# lerp factor lets us decide how far we wanna move from the parent const value
def mutate_consts(parent, lerp_factor):
	child = clone_graph(parent)
	for node in child.depth_first():
		if node.value.type_ == OpType.CONST:
			node.value = update_const(node.value, lerp_factor)
	return child

def subtree_mutation(parent, intern_op_set, term_op_set, terminal_likelyhood, max_depth):
	child = clone_graph(parent)
	# we try picking a nide at half depth
	node = child
	depth = 0
	depth_threshold = max_depth * random() * 0.5
	while len(node) > 0 and depth <= depth_threshold:
		# try picking an opcode, use a rejection mehtod
		next_node = node.children[0]
		attempts = 0
		while attempts < 3:
			next_node = choice(node.children)
			if next_node.value.type_ == OpType.OPCODE:
				break
			attempts = attempts + 1
		node = next_node
		depth = depth + 1

	assert(max_depth > depth)

	if node.value.type_ == OpType.OPCODE and len(node.value.args) > 0:
		arg_index = int(len(node.value.args) * random())
		node.children[arg_index] = continue_dsp_graph(node.value.tag, node.value.args[arg_index], \
			intern_op_set, term_op_set, terminal_likelyhood, max_depth - depth)
		return child, True
	return child, False

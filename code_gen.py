from elements import OpType

# simply to make sure we use unique identifiers
class LocalRegister:
	def __init__(self):
		self.cache = dict()

	def get_name(self, name):
		v = 'local' if name is None else name
		if v in self.cache:
			nv = v + '_' + str(self.cache[v])
			self.cache[v] = self.cache[v] + 1
			return nv
		else:
			self.cache[v] = 1
			return v

def gen_arg(node, statements, local_register, arg):
	# in case of an opcode we'll have to introduce alocal var
	# (CSound6 supports a functional syntax 
	# but we do not restrict oursleves to this new syntax at the moment)
	if node.value.type_ == OpType.OPCODE:
		# a local var to be inserted in the parent expression
		local = arg.type_ + local_register.get_name(arg.name)
		# parse subtree, assign to local
		i, s = node_to_code(node, local, local_register)
		statements.extend(s)
		statements.append(i)
		return local
	else:
		i, s = node_to_code(node, False, local_register)
		statements.extend(s)
		return i

def gen_opcode_call(node, statements, local_register):
	'generate function call code'
	args = ', '.join([gen_arg(node[i], statements, local_register, node.value.args[i]) \
		for i in range(len(node))])
	return ' '.join([node.value.value, args])
	
def node_to_code(node, dst, local_register):
	'builds an expression from a graph, with standard syntax'
	ls, statements = [], []

	if dst:
		ls.append(dst)
		if node.value.type_ == OpType.OPCODE:
			ls.append(' ')
		else:
			ls.append(' = ')

	if node.value.type_ == OpType.CONST:
		ls.append(str(node.value.value))
	else:
		ls.append(gen_opcode_call(node, statements, local_register))

	return ''.join(ls), statements

def graph_to_csound(node):
	i, s = node_to_code(node, 'aout__', LocalRegister())
	s.append(i)
	s.append('out aout__')
	s.insert(0, 'instr 1')
	s.append('endin')
	return '\n'.join(s)





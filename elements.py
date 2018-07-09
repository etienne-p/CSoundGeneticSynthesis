from collections import namedtuple
from random import choice, choices, random, normalvariate
from itertools import product, chain
from math import exp, pow, log
from util import lerp, clip
from csound_reference import opcodes, wavetables, OpTag

class OpType:
	CONST = 0
	OPCODE = 1

class OpArg(namedtuple('OpArg', ['type_', 'name', 'spec'])):
	__slots__ = ()
	def clone(self):
		return OpArg(**self._asdict())

class Opcode(namedtuple('Opcode', ['value', 'type_', 'return_type', 'args', 'tag'])):
	__slots__ = ()
	def clone(self):
		return Opcode(**self._asdict())

# we use recordclass has we need mutability
class Const(namedtuple('Const', ['value', 'type_', 'spec'])):
	__slots__ = ()
	def clone(self):
		return Const(**self._asdict())

# a bunch of factories handling namedtuple default args

def make_arg(type_, name=None, spec=None):
	return OpArg(type_, name, spec)

def make_const(value, spec):
	return Const(value, OpType.CONST, spec)

def make_opcode(value, return_type, args, tag):
	return Opcode(value, OpType.OPCODE, return_type, args, tag)

def random_time():
	return lerp(0.01, 2, random())

def distribution(x):
	b = .01 # curve peak
	c = 0.5 # curve steepness
	return exp(-pow(log(x) - log(b), 2) * c)

def random_freq():
	x, i = 0, 0
	# rejection sampling, with a watchdog
	while i < 64:
		# sample a random point
		x, y = random(), random()
		# if that point is below the distribution curve, the sample is accepted
		if (y < distribution(x)):
			break
		i = i + 1
	return lerp(1, 6000, x)

def value_from_spec(arg_spec):
	'return a generator based on variable specification'
	# interval / range
	if arg_spec[0] == '[':
		v = arg_spec[1:-1].split(',')
		return lerp(float(v[0]), float(v[1]), random())
	# set
	elif arg_spec[0] == '(':
		v = arg_spec[1:-1].split(',')
		# note: we assume sets are composed of ints
		return int(choice(v))
	# time
	elif arg_spec[0] == 't':
		return random_time()
	# frequency
	elif arg_spec[0] == 'f':
		# is there a modifier?
		if len(arg_spec) > 1:
			if arg_spec[1] == 'd': # difference
				return abs(random_freq() - random_freq())
			elif arg_spec[1] == 'r': # reciprocal
				return 1. / random_freq()
			else:
				# in case we missed something
				print('Unexpected freq modifier: ' + arg[1])
				return 0
		return random_freq()
	# wavetable
	elif arg_spec[0] == 'w':
		return choice(wavetables)
	return random()

def const_from_arg(arg):
	if arg.spec is None:
		return make_const(random(), None)
	return make_const(value_from_spec(arg.spec), arg.spec)

def parse_arg(arg_str):
	'parse a reference signature arg'
	type_ = arg_str[0]
	# remove trailing comma
	rest = arg_str[1:-1] if arg_str[-1] == ',' else arg_str[1:]
	# handle spec
	spec_index = rest.find(':')
	if spec_index == -1:
		return make_arg(type_, rest, None)
	else:
		return make_arg(type_, rest[:spec_index], rest[spec_index+1:])

def parse_signature(sign_str):
	'extracts the return and arguments type_ of an opcode from its reference description'
	words = sign_str.split()
	assert(len(words) > 1)
	return_type = words[0][0]
	opcode = words[1]
	args = [parse_arg(words[i]) for i in range(2, len(words))]
	return opcode, return_type, args 

def expand_args(args):
	ls = []
	for arg in args:
		ls.append([make_arg(t, arg.name, arg.spec) for t in ['i', 'k', 'a']] \
			if arg.type_ == 'x' else [arg])
	return [list(e) for e in product(*ls)] # cartesian product

def parse_opcode(op_str, tag):
	'generate a set of elements matching the string description'
	opcode, return_type, arg_types = parse_signature(op_str)
	arg_sets = expand_args(arg_types)
	return [make_opcode(opcode, return_type, args, tag) for args in arg_sets]

def is_terminal(op):
	for i in op.args:
		if i.type_ != 'i':
			return False
	return True

def parse_tagged_opcodes(data):
	'parse opcodes, sort them by category, return type and tag'
	v = [{'i': dict(), 'k': dict(), 'a': dict()},
		{'i': dict(), 'k': dict(), 'a': dict()}]
	current_tag = None
	for i in data:
		if isinstance(i, OpTag):
			current_tag = i.value
		else:
			# check current tag has been set
			assert(current_tag is not None)
			for op in parse_opcode(i, current_tag):
				cat = 1 if is_terminal(op) else 0
				if current_tag not in v[cat][op.return_type]:
					v[cat][op.return_type][current_tag] = [op]
				else:
					v[cat][op.return_type][current_tag].append(op)
	return v[0], v[1]

def read_op_set():
	return parse_tagged_opcodes(opcodes)

# TODO probabilities could be learned from existing CSound programs
# by picking a tag THEN an opcode we prevent opcodes with similar role
# yet lots of variations from taking over
def pick_opcode(tagged_opcodes, arg):
	'pick an opcode matching the provided argument'
	assert(arg.type_ in tagged_opcodes)
	tag = choice(list(tagged_opcodes[arg.type_].keys()))
	assert(len(tagged_opcodes[arg.type_][tag]) > 0)
	return choice(tagged_opcodes[arg.type_][tag]), tag

def pick_opcode_weighted(tagged_opcodes, arg, weights):
	'pick an opcode matching the provided argument'
	assert(arg.type_ in tagged_opcodes)
	tags = [k for k in tagged_opcodes[arg.type_]]
	selected_weights = [weights[k] for k in tags]
	tag = choices(tags, selected_weights)[0]
	assert(len(tagged_opcodes[arg.type_][tag]) > 0)
	# collect tag weights
	return choice(tagged_opcodes[arg.type_][tag]), tag

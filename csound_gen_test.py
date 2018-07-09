from code_gen import graph_to_csound 
from tree import make_dsp_graph
from elements import read_op_set, make_arg

# Generate random CSound programs and check wether they compile properly

tree = make_dsp_graph(make_arg('a'), read_op_set(), 0.1, 5)
print(graph_to_csound(tree))


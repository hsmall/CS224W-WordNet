from snap import *

import time
from WordNet import WordNet
import matplotlib.pyplot as plt

def __main__():
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"])
	print "Number of Total Nodes: {0}, Regular Nodes: {1}, Super-Nodes: {2}".format(*GetNodeCounts(wordnet))
	print "Number of Total Edges: {0}, Across Synsets: {1}, Between Super-Nodes: {2}".format(*GetEdgeCounts(wordnet))

	degree_distr, min_degree, max_degree = GetDegreeDistribution(wordnet.graph)
	#print "Degree Distrubition: {0}".format(degree_distr)

	average_degree = sum([i * degree_distr[i] for i in range(len(degree_distr))])
	print "Average Degree: {0}, Min: {1}, Max: {2}".format(average_degree, min_degree, max_degree)

	#plt.plot(range(len(degree_distr)), degree_distr)
	#plt.xlabel('Degree'); plt.ylabel('% of Nodes')
	#plt.xscale('log'); plt.yscale('log');
	#plt.show()

	print "Average Clustering Coefficient: {0}".format(GetClustCf(wordnet.graph))

def GetNodeCounts(wordnet):
	total_nodes = wordnet.graph.GetNodes()
	super_nodes = total_nodes - len(wordnet.all_words)

	return (total_nodes, total_nodes-super_nodes, super_nodes)

def GetEdgeCounts(wordnet):
	total_edges = wordnet.graph.GetEdges()
	between_synsets = 0
	between_super_nodes = 0
	for key, synset in wordnet.synsets.items():
		for pointer in synset["pointers"]:
			src_key, src, dst_key, dst = pointer["connection"]
			if src == 0:
				between_super_nodes += 1
			else:
				between_synsets += 1

	return (total_edges/2, between_synsets/2, between_super_nodes/2)


def GetDegreeDistribution(graph):
	node_degrees = [node.GetOutDeg() for node in graph.Nodes()]
	min_degree = min(node_degrees)
	max_degree = max(node_degrees)
	
	degree_distr = [0] * (max_degree + 1)
	for degree in node_degrees:
		degree_distr[degree] += 1

	return normalize(degree_distr), min_degree, max_degree

def normalize(vector):
	total = float(sum(vector))
	return [elem / total for elem in vector]

__main__()
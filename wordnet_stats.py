from snap import *

import time
from WordNet import WordNet
import matplotlib.pyplot as plt
import numpy as np

def __main__():
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"], "data/word_to_year_formatted.txt")
	getStatsForWordNetGraph(wordnet)
	print
	getStatsForDirectedGraph(wordnet)

def getStatsForWordNetGraph(wordnet):
	print "WordNet graph stats:"
	print "Number of Total Nodes: {0}, Regular Nodes: {1}, Super-Nodes: {2}".format(*GetNodeCounts(wordnet))
	print "Number of Total Edges: {0}, Across Synsets: {1}, Between Super-Nodes: {2}".format(*GetEdgeCounts(wordnet))

	degree_distr, min_degree, max_degree = GetDegreeDistribution(wordnet.graph)
	print "Degree Distribution: {0}".format(degree_distr)

	average_degree = sum([i * degree_distr[i] for i in range(len(degree_distr))])
	print "Average Degree: {0}, Min: {1}, Max: {2}".format(average_degree, min_degree, max_degree)

	plt.plot(range(len(degree_distr)), degree_distr)
	plt.xlabel('Degree'); plt.ylabel('% of Nodes')
	plt.xscale('log'); plt.yscale('log');
	plt.show()

	print "Average Clustering Coefficient: {0}".format(GetClustCf(wordnet.graph))

def getStatsForDirectedGraph(wordnet):
	print "Directed WordNet graph stats:"
	print "Number of Total Nodes: {0}, Regular Nodes: {1}, Super-Nodes: {2}".format(*GetNodeCounts(wordnet, directed=True))
	print "Number of Total Edges: {0}, Across Synsets: {1}, Between Super-Nodes: {2}".format(*GetEdgeCountsDirected(wordnet))

	degree_distr, min_degree, max_degree = GetDegreeDistribution(wordnet.time_directed_graph)
	print "Degree Distribution: {0}".format(degree_distr)

	average_degree = sum([i * degree_distr[i] for i in range(len(degree_distr))])
	print "Average Degree: {0}, Min: {1}, Max: {2}".format(average_degree, min_degree, max_degree)

	plt.plot(range(len(degree_distr)), degree_distr)
	plt.xlabel('Degree'); plt.ylabel('% of Nodes')
	plt.xscale('log'); plt.yscale('log');
	plt.show()

	print "Average Clustering Coefficient: {0}".format(GetClustCf(wordnet.time_directed_graph))
	print

	getStatsByYear(wordnet)

def getWordAndDecade(node_id, wordnet):
	word = wordnet.node_to_word_directed[node_id]
	year = wordnet.word_to_date[word]
	decade = year - year%10

	return word, decade

def getListAvg(list_of_values):
	if len(list_of_values) == 0: return 0
	return float(sum(list_of_values))/float(len(list_of_values))


def getAveragesByDecade(wordnet, calculate_betweenness=False):
	word_node_ids = set(wordnet.node_to_word_directed.keys())
	min_decade = 600
	max_decade = 2000
	year = min_decade
	decade_to_out_deg = {}
	decade_to_in_deg = {}
	decade_to_cc = {}
	decade_to_deg_centr = {}
	decade_to_btw_centr = {}
	decade_to_close_centr = {}
	while(year <= max_decade):
		decade_to_out_deg[year] = []
		decade_to_in_deg[year] = []
		decade_to_cc[year] = []
		decade_to_deg_centr[year] = []
		decade_to_btw_centr[year] = []
		decade_to_close_centr[year] = []
		year += 10

	node_out_deg = TIntPrV()
	GetNodeOutDegV(wordnet.time_directed_graph, node_out_deg)
	undir_graph_copy = ConvertGraph(PUNGraph, wordnet.time_directed_graph)

	for item in node_out_deg:
		node_id = item.GetVal1()
		out_deg = item.GetVal2()
		if node_id not in word_node_ids: continue

		word,decade = getWordAndDecade(node_id, wordnet)

		close_centr = GetClosenessCentr(wordnet.time_directed_graph, node_id, True, True)
		cc = GetNodeClustCf(wordnet.time_directed_graph, node_id)
		deg_centr = GetDegreeCentr(undir_graph_copy, node_id)
		
		decade_to_out_deg[decade].append(out_deg)
		decade_to_close_centr[decade].append(close_centr)
		decade_to_deg_centr[decade].append(deg_centr)
		decade_to_cc[decade].append(cc)

	node_in_deg = TIntPrV()
	GetNodeInDegV(wordnet.time_directed_graph, node_in_deg)
	for item in node_in_deg:
		node_id = item.GetVal1()
		in_deg = item.GetVal2()
		if node_id not in word_node_ids: continue

		word,decade = getWordAndDecade(node_id, wordnet)
	
		decade_to_in_deg[decade].append(in_deg)

	if calculate_betweenness:
		nodes = TIntFltH()
		edges = TIntPrFltH()
		GetBetweennessCentr(wordnet.time_directed_graph, nodes, edges, 1, True)
		for node_id in nodes:
			if node_id not in word_node_ids: continue
			btw_centr = nodes[node_id]

			word,decade = getWordAndDecade(node_id, wordnet)

			decade_to_btw_centr[decade].append(btw_centr)

	for decade in decade_to_out_deg.keys():
		avg_in_deg = getListAvg(decade_to_in_deg[decade])
		decade_to_in_deg[decade] = avg_in_deg

		avg_out_deg = getListAvg(decade_to_out_deg[decade])
		decade_to_out_deg[decade] = avg_out_deg

		avg_cc = getListAvg(decade_to_cc[decade])
		decade_to_cc[decade] = avg_cc

		avg_close_centr = getListAvg(decade_to_close_centr[decade])
		decade_to_close_centr[decade] = avg_close_centr

		avg_deg_centr = getListAvg(decade_to_deg_centr[decade])
		decade_to_deg_centr[decade] = avg_deg_centr

		if calculate_betweenness:
			decade_to_words = getWordsPerDecade(wordnet)
			plotAndPrintYearData(decade_to_words, "Num Words Per Decade")

	return decade_to_in_deg, decade_to_out_deg, decade_to_cc, decade_to_deg_centr, decade_to_close_centr, decade_to_btw_centr

def plotAndPrintYearData(decade_to_avg, title):
	print title
	print decade_to_in_deg
	print

	x = decade_to_avg.keys()
	y = decade_to_avg.values()

	plt.bar(x, y)
	plt.xlabel('Year')
	plt.ylabel('Average Value')
	plt.title(title)
	plt.savefig('graphs/hist-'+title+'.png')
	plt.show()

def getWordsPerDecade(wordnet):
	min_decade = 600
	max_decade = 2000
	year = min_decade
	decade_to_words= {}
	while(year <= max_decade):
		decade_to_words[year] = 0
		year += 10
	for word in wordnet.all_words_directed:
		year = wordnet.word_to_date[word]
		decade = year - year%10
		decade_to_words[decade] += 1
	return decade_to_words

def getStatsByYear(wordnet, calc_btw_centr=False):
	print "Directed WordNet graph stats by year:"

	decade_to_words = getWordsPerDecade(wordnet)
	plotAndPrintYearData(decade_to_words, "Num Words Per Decade")

	decade_to_in_deg, decade_to_out_deg, decade_to_cc, decade_to_deg_centr, decade_to_close_centr, decade_to_btw_centr = getAveragesByDecade(wordnet, calculate_betweenness=calc_btw_centr)

	plotAndPrintYearData(decade_to_out_deg, "Average In Degree by Year")
	plotAndPrintYearData(decade_to_in_deg, "Average Out Degree by Year")
	plotAndPrintYearData(decade_to_cc, "Average Clustering Coefficient by Year")
	plotAndPrintYearData(decade_to_close_centr, "Average Node Closeness Centrality by Year")
	plotAndPrintYearData(decade_to_deg_centr, "Average Node Degree Centrality by Year")
	if calc_btw_centr:
		plotAndPrintYearData(decade_to_btw_centr, "Average Node Betweenness Centrality by Year")


def GetNodeCounts(wordnet, directed=False):
	if directed:
		total_nodes = wordnet.time_directed_graph.GetNodes()
		super_nodes = total_nodes - len(wordnet.all_words_directed)
	else:
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

def GetEdgeCountsDirected(wordnet):
	total_edges = wordnet.time_directed_graph.GetEdges()
	between_synsets = 0
	between_super_nodes = 0
	word_node_ids = set(wordnet.node_to_word_directed.keys())
	for e in wordnet.time_directed_graph.Edges():
		src = e.GetSrcNId()
		dst = e.GetDstNId()
		if src in wordnet.supernodes_in_directed_graph and dst in wordnet.supernodes_in_directed_graph:
			between_super_nodes += 1
		if src in word_node_ids and dst in word_node_ids:
			between_synsets += 1

	return total_edges, between_synsets, between_super_nodes


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
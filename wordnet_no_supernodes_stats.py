from snap import *

import time
from WordNet import WordNet
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def __main__():
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"], "data/word_to_year_formatted.txt")
	
	node_to_out_deg, node_to_in_deg = getGeneralStats(wordnet)

	getStatsByYear(node_to_out_deg, node_to_in_deg, wordnet)


def getGeneralStats(wordnet):
	print "WordNet Time Directed Graph without Supernodes Stats:"
	g = wordnet.time_directed_graph_no_supernodes
	print "Number of Nodes: ", g.GetNodes()
	print "Number of Edges: ", g.GetEdges()
	node_to_out_deg, out_degree_distr, min_out_degree, max_out_degree, node_to_in_deg, in_degree_distr, min_in_degree, max_in_degree = GetDegreeDistribution(g)
	
	print
	#print "In-Degree Distribution: {0}".format(in_degree_distr)
	average_degree = sum([i/2.0 * in_degree_distr[i] for i in range(len(in_degree_distr))])/g.GetNodes()
	print "Average In Degree: {0}, Min: {1}, Max: {2}".format(average_degree, min_in_degree, max_in_degree)
	plt.plot([x*.5 for x in range(0, len(in_degree_distr))], in_degree_distr)
	plt.xlabel('Degree'); plt.ylabel('% of Nodes')
	plt.xscale('log'); plt.yscale('log');
	plt.savefig('graphs/nosupernodesindegree.png')
	plt.close()

	print
	#print "Out-Degree Distribution: {0}".format(out_degree_distr)
	average_degree = sum([i/2.0 * out_degree_distr[i] for i in range(len(out_degree_distr))])/g.GetNodes()
	print "Average Out Degree: {0}, Min: {1}, Max: {2}".format(average_degree, min_out_degree, max_out_degree)
	plt.plot([x*.5 for x in range(0, len(out_degree_distr))], out_degree_distr)
	plt.xlabel('Degree'); plt.ylabel('% of Nodes')
	plt.xscale('log'); plt.yscale('log');
	plt.savefig('graphs/nosupernodesoutdegree.png')
	plt.close()

	print
	print "Average Clustering Coefficient: {0}".format(GetClustCf(g))
	return node_to_out_deg, node_to_in_deg

def getStatsByYear(node_to_out, node_to_in, wordnet, calc_btw_centr=True):
	print "Time Directed WordNet Graph without Supernodes stats by year:"

	decade_to_words = getWordsPerDecade(wordnet)
	plotAndPrintYearData(decade_to_words, "Num Words Per Decade")

	decade_to_out_deg, decade_to_in_deg = getInAndOutAvgByDecade(wordnet, node_to_out, node_to_in)
	plotAndPrintYearData(decade_to_out_deg, "Average Out Degree by Year")
	plotAndPrintYearData(decade_to_in_deg, "Average In Degree by Year")

	decade_to_cc, decade_to_deg_centr, decade_to_close_centr, decade_to_btw_centr = getAveragesByDecade(wordnet, calculate_betweenness=calc_btw_centr)

	plotAndPrintYearData(decade_to_cc, "Average Clustering Coefficient by Year")
	plotAndPrintYearData(decade_to_close_centr, "Average Node Closeness Centrality by Year")
	plotAndPrintYearData(decade_to_deg_centr, "Average Node Degree Centrality by Year")
	if calc_btw_centr:
		plotAndPrintYearData(decade_to_btw_centr, "Average Node Betweenness Centrality by Year")

def getInAndOutAvgByDecade(wordnet, node_to_out, node_to_in):
	word_node_ids = set(wordnet.node_to_word_directed_no_supernodes.keys())
	min_decade = 600
	max_decade = 2000
	year = min_decade
	decade_to_out_deg = {}
	decade_to_in_deg = {}
	while(year <= max_decade):
		decade_to_out_deg[year] = []
		decade_to_in_deg[year] = []
		year += 10

	for nId, out_deg in node_to_out.items():
		word, year, decade = getWordAndDecade(nId, wordnet)
		decade_to_out_deg[decade].append(out_deg)

	for nId, in_deg in node_to_in.items():
		word, year, decade = getWordAndDecade(nId, wordnet)
		decade_to_in_deg[decade].append(in_deg)

	out_res = {}
	in_res = {}
	for decade in decade_to_out_deg.keys():
		avg_out = getListAvg(decade_to_out_deg[decade])
		out_res[decade] = avg_out

		avg_in = getListAvg(decade_to_in_deg[decade])
		in_res[decade] = avg_in

	print "dec to out:", out_res
	print
	print "dec to in:", in_res
	return out_res, in_res


def getWordAndDecade(node_id, wordnet):
	word = wordnet.node_to_word_directed_no_supernodes[node_id]
	year = wordnet.word_to_date[word]
	decade = year - year%10

	return word, year, decade

def getListAvg(list_of_values):
	if len(list_of_values) == 0: return 0
	return float(sum(list_of_values))/float(len(list_of_values))


def getAveragesByDecade(wordnet, calculate_betweenness=False):
	word_node_ids = set(wordnet.node_to_word_directed_no_supernodes.keys())
	min_decade = 600
	max_decade = 2000
	year = min_decade
	decade_to_cc = {}
	decade_to_deg_centr = {}
	decade_to_btw_centr = {}
	decade_to_close_centr = {}
	while(year <= max_decade):
		decade_to_cc[year] = []
		decade_to_deg_centr[year] = []
		decade_to_btw_centr[year] = []
		decade_to_close_centr[year] = []
		year += 10

	undir_graph_copy = ConvertGraph(PUNGraph, wordnet.time_directed_graph_no_supernodes)

	for node in wordnet.time_directed_graph_no_supernodes.Nodes():
		node_id = node.GetId()
		if node_id not in word_node_ids: continue

		word,year,decade = getWordAndDecade(node_id, wordnet)

		close_centr = GetClosenessCentr(wordnet.time_directed_graph_no_supernodes, node_id, True, True)
		cc = GetNodeClustCf(wordnet.time_directed_graph_no_supernodes, node_id)
		deg_centr = GetDegreeCentr(undir_graph_copy, node_id)
		
		decade_to_close_centr[decade].append(close_centr)
		decade_to_deg_centr[decade].append(deg_centr)
		decade_to_cc[decade].append(cc)

	if calculate_betweenness:
		nodes = TIntFltH()
		edges = TIntPrFltH()
		GetBetweennessCentr(wordnet.time_directed_graph_no_supernodes, nodes, edges, 1, True)
		for node_id in nodes:
			if node_id not in word_node_ids: continue
			btw_centr = nodes[node_id]

			word,year,decade = getWordAndDecade(node_id, wordnet)

			decade_to_btw_centr[decade].append(btw_centr)

	for decade in decade_to_cc.keys():
		avg_cc = getListAvg(decade_to_cc[decade])
		decade_to_cc[decade] = avg_cc

		avg_close_centr = getListAvg(decade_to_close_centr[decade])
		decade_to_close_centr[decade] = avg_close_centr

		avg_deg_centr = getListAvg(decade_to_deg_centr[decade])
		decade_to_deg_centr[decade] = avg_deg_centr

		if calculate_betweenness:
			avg_btw_centr = getListAvg(decade_to_btw_centr[decade])
			decade_to_btw_centr[decade] = avg_btw_centr

	print "cc ", decade_to_cc
	print 
	print "deg-centr ", decade_to_deg_centr
	print
	print "close-centr ", decade_to_close_centr
	print
	print "btw-centr ", decade_to_btw_centr
	print 

	return decade_to_cc, decade_to_deg_centr, decade_to_close_centr, decade_to_btw_centr

def plotAndPrintYearData(decade_to_avg, title):
	x = decade_to_avg.keys()
	y = decade_to_avg.values()

	plt.bar(x, y)
	plt.xlabel('Year')
	plt.ylabel('Average Value')
	plt.title(title)
	plt.savefig('graphs/nosupernodes-hist-'+title+'.png')
	plt.close()

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

def GetDegreeDistribution(graph):
	node_to_out_deg = defaultdict(float)
	node_to_in_deg = defaultdict(float)

	for e in graph.Edges():
		src = e.GetSrcNId()
		dst = e.GetDstNId()
		w = graph.GetFltAttrDatE(e, "weight")
		node_to_out_deg[src] += w
		node_to_in_deg[dst] += w

	in_deg = node_to_in_deg.values()
	out_deg = node_to_out_deg.values()

	min_in_degree = min(in_deg)
	min_out_degree = min(out_deg)
	max_in_degree = max(in_deg)
	max_out_degree = max(out_deg)
	
	in_degree_distr = [0] * (int(max_in_degree * 2) + 1)
	for degree in in_deg:
		in_degree_distr[int(degree*2)] += 1

	out_degree_distr = [0] * (int(max_out_degree *2) + 1)
	for degree in out_deg:
		out_degree_distr[int(degree*2)] += 1

	return node_to_out_deg, out_degree_distr, min_out_degree, max_out_degree, node_to_in_deg, in_degree_distr, min_in_degree, max_in_degree

def normalize(vector):
	total = float(sum(vector))
	return [elem / total for elem in vector]

__main__()

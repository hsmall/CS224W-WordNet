from snap import *

from WordNet import WordNet
import matplotlib.pyplot as plt
import random
import time

def __main__():
	'''wordnet = LoadWordNet(is_null_model=False)

	for centrality_type in ['Betweenness']:
		centrality_by_era = GetCentralityByEra(wordnet, centrality_type)

		eras = []
		centralities = []
		for era in sorted(centrality_by_era.keys()):
			eras.append(era)
			centralities.append(centrality_by_era[era])

		plt.plot(eras, scale_by_max(centralities), label="{0} Centrality".format(centrality_type))
		print("Finished {0} Centrality...".format(centrality_type))
		print("Eras = {0}".format(eras))
		print("Centralities = {0}\n".format(centralities))
	
	print("Done.")
	'''
	eras = [600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
	degree =[27.875, 23.75968992248062, 26.45016611295681, 19.93851132686084, 18.51159196290572, 17.612716763005782, 21.73521505376344, 15.18063014679556, 11.753684598378777, 9.193469569080408, 7.549621621621622, 6.266587911006104, 5.240792216817234, 4.6260582283708445, 4.25]
	closeness = [0.130, 0.13211239618390297, 0.12737105698893567, 0.1266707129460605, 0.12607775104979493, 0.1243577440403726, 0.12810770268582072, 0.1249677852698286, 0.12289090202120762, 0.11791960042630491, 0.11647133159897531, 0.11433829295052597, 0.1103202763492783, 0.10916293204832352, 0.09]
	betweenness = [6731.861938292907, 10344.914123724506, 11947.643367996056, 7207.860979295215, 5406.633242835245, 5399.446592435749, 8188.65579441855, 3809.4952526062893, 2403.7412043932004, 1185.5273289450095, 755.5786347712457, 464.73584859333323, 378.46756463397276, 196.53228462666172, 0.0]

	plt.plot(eras, scale_by_max(degree), label="Degree Centrality")
	plt.plot(eras, scale_by_max(closeness), label="Closeness Centrality")
	plt.plot(eras, scale_by_max(betweenness), label="Betweenness Centrality")
	plt.title("Normalized Average Centralities By Century")
	plt.xlabel("Century"); plt.ylabel("Normalized Average Centrality");
	plt.legend()
	plt.show()

def GetCentralityByEra(wordnet, centrality_type):
	graph = wordnet.graph
	centrality_map = {}

	if centrality_type == 'Degree':
		for node in graph.Nodes():
			if node.GetId() not in wordnet.node_to_word: continue
			word = wordnet.node_to_word[node.GetId()]
			
			if word not in wordnet.word_to_date: continue
			centrality_map[word] = node.GetOutDeg()

	if centrality_type == 'Closeness':
		count = 0
		node_ids = [node.GetId() for node in graph.Nodes()]
		random.shuffle(node_ids)

		for node_id in node_ids[:int(len(node_ids)/10)]:
			if node_id not in wordnet.node_to_word: continue
			word = wordnet.node_to_word[node_id]
			
			if word not in wordnet.word_to_date: continue
			centrality_map[word] = GetClosenessCentr(graph, node_id)
			count += 1
			print "{0} out of {1}".format(count, len(wordnet.node_to_word)/10)
	
	if centrality_type == 'Betweenness':
		Nodes = TIntFltH()
		Edges = TIntPrFltH()
		GetBetweennessCentr(graph, Nodes, Edges, 0.001)
		for node_id in Nodes:
			if node_id not in wordnet.node_to_word: continue
			word = wordnet.node_to_word[node_id]
			
			if word not in wordnet.word_to_date: continue
			centrality_map[word] = Nodes[node_id]

	era_length = 100
	centrality_by_era = {era: list() for era in range(600, 2001, era_length)}
	for word, centrality in centrality_map.items():
		year = wordnet.word_to_date[word]
		era = year - year % era_length
		centrality_by_era[era].append(centrality)

	for era in centrality_by_era.keys():
		centrality_by_era[era] = mean(centrality_by_era[era])

	return centrality_by_era

def mean(vector):
	return sum(vector) / float(len(vector)) if len(vector) != 0 else 0

def scale_by_max(vector):
	return normalize(vector)
	max_value = float(max(vector))
	min_value = float(min(vector))
	return [(elem - min_value) / (max_value - min_value) for elem in vector]

def normalize(vector):
	total = float(sum(vector))
	return [elem / total for elem in vector]

def LoadWordNet(is_null_model=False):
	print "Loading WordNet Graph..."
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"], "data/word_to_year_formatted.txt", is_null_model)
	#wordnet = WordNet(["data/dict/data.adv"], "data/word_to_year_formatted.txt", is_null_model)
	print "Finished Loading Graph!"
	return wordnet

__main__()
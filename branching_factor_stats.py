from snap import *

from WordNet import WordNet
import matplotlib.pyplot as plt
import pickle

def __main__():
	depths = [1, 2, 3] # What depths to run for computing the branching factors
	filename_template = "branching_factor_by_decade_{0}.txt" #filenames where data is saved

	# The next couple lines lines compute all of the branching factors for the graph and then saves them to a file
	# CAN COMMENT THEM OUT to avoid recomputing when just trying to tweak the graphs
	#wordnet = LoadWordNet()
	#SaveBranchingFactorsToFile(wordnet, depths, filename_template)
	

	# This section manipulates the computed branching factors and produces a graph
	for max_depth in depths:
		branching_factor_by_era = GroupDecades(pickle.load(open(filename_template.format(max_depth), "r")), 10)

		average_by_era = []
		for era in sorted(branching_factor_by_era.keys()):
			if len(branching_factor_by_era[era]) == 0:
				average_by_era.append(0)
				continue

			avg = 0.0
			for word, year, branching_factor, out_degree in branching_factor_by_era[era]:
				if out_degree == 0: continue
				
				# I made a seperate graph for each of the below branching factor definitions.
				#avg += branching_factor #This is the standard "branching factor" as we defined at our meeting
				avg += (branching_factor/out_degree**max_depth) #This weights the branching factor by the out degree of the node to remove bias of high-degree nodes
				
			avg = avg / len(branching_factor_by_era[era])
			average_by_era.append(avg)
			
			#print "{0} -> {1}".format(decade, branching_factor_by_decade[decade])
			#print "{0}\n".format(avg)

		plt.plot(sorted(branching_factor_by_era.keys()), average_by_era, label="Max Depth = {0}".format(max_depth))
	
	plt.title('Average Weighted Branching Factor by Century')
	plt.xlabel('Century'); plt.ylabel('Average Weighted Branching Factor')
	plt.legend()
	plt.show()

def LoadWordNet():
	print "Loading WordNet Graph..."
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"], "data/word_to_year_formatted.txt")
	print "Finished Loading Graph!"
	return wordnet

# Computes the branching factor for each node (or word) at each of the given |depths|, then saves them to a file
# based upon the given |filename_template|
def SaveBranchingFactorsToFile(wordnet, depths, filename_template):
	graph = wordnet.time_directed_graph_no_supernodes
	for max_depth in depths:
		print "Calculating Branching Factors (Depth = {0})".format(max_depth)
		node_to_branching_factor = ComputeBranchingFactor(graph, max_depth)
		
		branching_factor_by_decade = {decade: list() for decade in range(600, 2001, 10)}

		for node in node_to_branching_factor.keys():
			word = wordnet.node_to_word_directed_no_supernodes[node]
			year = wordnet.word_to_date[word]
			branching_factor = node_to_branching_factor[node]
			out_degree = graph.GetNI(node).GetOutDeg()

			decade = year - year % 10
			branching_factor_by_decade[decade].append((word, year, branching_factor, out_degree))

		pickle.dump(branching_factor_by_decade, open(filename_template.format(max_depth), "w"))

# Compute the branching factor for each node using the given |max_depth|
def ComputeBranchingFactor(graph, max_depth):
	node_to_branching_factor = {}
	nodes = [node.GetId() for node in graph.Nodes()]
	
	for i in range(len(nodes)):
		if i % 10000 == 0: print "{0} of {1}".format(i, len(nodes))
		node_to_branching_factor[nodes[i]] = ComputeBranchingFactorHelper(graph, nodes[i], max_depth)
	
	return node_to_branching_factor

# Recursive helper function for the above method. the weight multiplier is used so that when you
# traverse an edge with weight != 1, it reduces the weight of all subsequent edges in the traversal
def ComputeBranchingFactorHelper(graph, node, max_depth, weight_multiplier=1.0):
	if max_depth == 0: return 0
	
	branching_factor = 0;
	for neighbor in graph.GetNI(node).GetOutEdges():
		edge = graph.GetEI(node, neighbor)
		edge_weight = graph.GetFltAttrDatE(edge, "weight")
		
		branching_factor += edge_weight*weight_multiplier
		branching_factor += ComputeBranchingFactorHelper(graph, neighbor, max_depth-1, edge_weight*weight_multiplier)

	return branching_factor

# This method is used to smooth the data from "by-decade" data to some other time period. For example:
# if num_to_group = 5, the data will now be grouped by half-century (aka 50-year intervals/buckets) 
def GroupDecades(branching_factor_by_decade, num_to_group):
	grouped_data = {}
	decades = sorted(branching_factor_by_decade.keys())
	for i in range(0, len(decades), num_to_group):
		start_decade = decades[i]
		grouped_data[start_decade] = list()
		for j in range(i, min(i+num_to_group, len(decades))):
			grouped_data[start_decade].extend(branching_factor_by_decade[decades[j]])

	return grouped_data

# Returns a normalized version of the input |vector|
def normalize(vector):
	total = float(sum(vector))
	return [elem / total for elem in vector]

__main__()
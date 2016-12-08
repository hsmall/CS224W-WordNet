from snap import *

from WordNet import WordNet
import matplotlib.pyplot as plt
import pickle

POS_LIST = ['s', 'adj', 'n', 'adv', 'v']

def __main__():
	depths = [1, 2, 3] # What depths to run for computing the branching factors
	filename_template = "branching_graphs/null_branching_factor_by_decade_{0}.txt" #filenames where data is saved
	filename_template2 = "branching_graphs/null_branching_factor_by_pos_{0}.txt"

	# The next couple lines lines compute all of the branching factors for the graph and then saves them to a file
	# CAN COMMENT THEM OUT to avoid recomputing when just trying to tweak the graphs
#	wordnet = LoadWordNet()
#	SaveBranchingFactorsToFile(wordnet, depths, filename_template, filename_template2)

	# This section manipulates the computed branching factors and produces a graph
	for max_depth in depths:
		branching_factor_by_era = GroupDecades(pickle.load(open(filename_template.format(max_depth), "r")), 10)
        branching_factor_by_pos = pickle.load(open(filename_template2.format(max_depth,), "r"))

        # Part of speech calculations
        print "Current Max Depth:", max_depth
        for elem in POS_LIST:
            pos_bar_x.append(elem)
            avg = 0.0
            avgW = 0.0
            count = 0
            for word, pos, branching_factor, out_degree in branching_factor_by_pos[elem]:
                if out_degree == 0: continue
                avg += branching_factor #/out_degree**max_depth
                avgW += (branching_factor/out_degree**max_depth)
                count += 1
            avg = avg / count
            avgW = avgW / count
            print elem, "Average Branching Factor: ", avg, "| Sample Size:", len(branching_factor_by_pos[elem])
            print elem, "Average Branching Factor (W):", avgW

        average_by_era = []
        for era in sorted(branching_factor_by_era.keys()):
			if len(branching_factor_by_era[era]) == 0:
				average_by_era.append(0)
				continue

			avg = 0.0
			for word, year, branching_factor, out_degree in branching_factor_by_era[era]:
				if out_degree == 0: continue
				
				# I made a seperate graph for each of the below branching factor definitions.
				avg += branching_factor #This is the standard "branching factor" as we defined at our meeting
				#avg += (branching_factor/out_degree**max_depth) #This weights the branching factor by the out degree of the node to remove bias of high-degree nodes
				
			avg = avg / len(branching_factor_by_era[era])
			average_by_era.append(avg)
			
			#print "{0} -> {1}".format(decade, branching_factor_by_decade[decade])
			#print "{0}\n".format(avg)

#        plt.plot(sorted(branching_factor_by_era.keys()), normalize(average_by_era), label="Max Depth = {0}".format(max_depth))
#
#	plt.title('Normalized Average Branching Factor by Century')
#	plt.xlabel('Century'); plt.ylabel('Normalized Average Branching Factor')
#	plt.legend()

    # Plotting parts of speech results using pre-calculated branching factor data
	pos_real = {'pos': ['Adj', 'Noun', 'Adv', 'Verb'], 'real_d1': [2.87, 2.76, 9.43, 7.85], 'real_d2': [15.3, 16.1, 114, 87.1], 'real_d3': [95.5, 97.3, 1138, 835]}
	pos_real_w = {'real_w_d1': [0.871, 0.691, 0.806, 0.725], 'real_w_d2': [1.51, 1.3, 1.19, 1.17], 'real_w_d3': [4.74, 3.76, 2.8, 3.34]}
	pos_null = {'null_d1': [2.79, 2.4, 9.1, 6.97], 'null_d2': [11.8, 9.55, 67.4, 46.9], 'null_d3': [46.3, 37.1, 368, 250]}
	pos_null_w = {'null_w_d1': [0.729, 0.704, 0.715, 0.706], 'null_w_d2': [0.901, 0.912, 0.688, 0.767], 'null_w_d3': [1.48, 1.59, 0.913, 1.37]}

	position = list(range(len(pos_null_w['null_w_d1'])))
	width = 0.25
	fig, ax = plt.subplots(figsize = (10,5))
	plt.bar(position, pos_null_w['null_w_d1'], width, color='#EE3224')
	plt.bar([p + width for p in position], pos_null_w['null_w_d2'], width, color='#F78F1E')
	plt.bar([p + width*2 for p in position], pos_null_w['null_w_d3'], width, color='#FFC222')
	ax.set_ylabel('Branching Factor')
	ax.set_title('Branching Factor by Part of Speech (Null, Weighted)')
	ax.set_xticks([p + 1.5 * width for p in position])
	ax.set_xticklabels(pos_real['pos'])
    # plt.ylim([0, 2])
	plt.legend(['Depth = 1', 'Depth = 2', 'Depth = 3'])
	plt.show()

def LoadWordNet(is_null_model=False):
	print "Loading WordNet Graph..."
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"], "data/word_to_year_formatted.txt", is_null_model)
	print "Finished Loading Graph!"
	return wordnet

# Computes the branching factor for each node (or word) at each of the given |depths|, then saves them to a file
# based upon the given |filename_template|
def SaveBranchingFactorsToFile(wordnet, depths, filename_template, filename_template2):
	graph = wordnet.time_directed_graph_no_supernodes
	for max_depth in depths:
		print "Calculating Branching Factors (Depth = {0})".format(max_depth)
		node_to_branching_factor = ComputeBranchingFactor(graph, max_depth)
		
		branching_factor_by_decade = {decade: list() for decade in range(600, 2001, 10)}
        branching_factor_by_pos = {pos: list() for pos in POS_LIST}

        for node in node_to_branching_factor.keys():
			word = wordnet.node_to_word_directed_no_supernodes[node]
			year = wordnet.word_to_date[word]
			branching_factor = node_to_branching_factor[node]
			out_degree = graph.GetNI(node).GetOutDeg()

			decade = year - year % 10
			branching_factor_by_decade[decade].append((word, year, branching_factor, out_degree))

            # Part of speech calculations
			for pos in wordnet.word_to_pos[word]:
				if pos in POS_LIST:
					branching_factor_by_pos[pos].append((word, pos, branching_factor, out_degree))

        pickle.dump(branching_factor_by_decade, open(filename_template.format(max_depth), "w"))
        pickle.dump(branching_factor_by_pos, open(filename_template2.format(max_depth), "w"))


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

from snap import *

from WordNet import WordNet
import matplotlib.pyplot as plt
import pickle
import math

def __main__():
	depths = [1, 2, 3] # What depths to run for computing the branching speeds
	filename_template = "branching_graphs/null_branching_speed_by_decade_{0}.txt" #filenames where data is saved
	

	# CAN COMMENT THIS LINE OUT to avoid recomputing when just trying to tweak the graphs
	# wordnet = LoadWordNet(is_null_model=True)
	# SaveBranchingSpeedsToFile(wordnet, depths, filename_template)

	# This section manipulates the computed branching factors and produces a graph
	for max_depth in depths:
		branching_speed_by_era = GroupDecades(pickle.load(open(filename_template.format(max_depth), "r")), 1)

		average_by_era = []
		for era in sorted(branching_speed_by_era.keys()):
			if len(branching_speed_by_era[era]) == 0:
				average_by_era.append(0)
				continue

			branching_speeds = []
			for word, year, branching_speed in branching_speed_by_era[era]:
				branching_speeds.append(branching_speed)
			
			average_by_era.append(mean(branching_speeds))
			
			#print "{0} -> {1}".format(decade, branching_factor_by_decade[decade])
			#print "{0}\n".format(avg)

		plt.plot(sorted(branching_speed_by_era.keys()), average_by_era, label="Max Depth = {0}".format(max_depth))
	
	plt.title('Average Branching Speed by Decade')
	plt.xlabel('Decade'); plt.ylabel('Average Branching Speed')
	plt.legend(loc=2)
	plt.show()

def LoadWordNet(is_null_model=False):
	print "Loading WordNet Graph..."
	wordnet = WordNet(["data/dict/data.noun", "data/dict/data.verb", "data/dict/data.adj", "data/dict/data.adv"], "data/word_to_year_formatted.txt", is_null_model)
	print "Finished Loading Graph!"
	return wordnet

# Computes the branching speed for each node (or word) at each of the given |depths|, then saves them to a file
# based upon the given |filename_template|
def SaveBranchingSpeedsToFile(wordnet, depths, filename_template):
	# all_years_histogram contains the expected average distance between a word in a given year
	# and all words that follow it in time.
	all_years = sorted(wordnet.word_to_date.values())
	all_years_histogram = {}
	for i in range(len(all_years)):
		if i < len(all_years)-1 and all_years[i] == all_years[i+1]: continue
		all_years_histogram[all_years[i]] = mean(all_years[i:]) - all_years[i] 

	for max_depth in depths:
		print "Calculating Branching Speeds (Depth = {0})".format(max_depth)
		node_to_branching_speed, node_to_influence_set_words = ComputeBranchingSpeed(wordnet, all_years_histogram, max_depth)
		
		'''
		for node, branching_speed in sorted(node_to_branching_speed.items(), reverse=True, key=lambda x: x[1])[:20]:
			word = wordnet.node_to_word_directed_no_supernodes[node]
			year = wordnet.word_to_date[word]
			print "{0} ({1}) = {2} --- {3}".format(word, year, branching_speed, node_to_influence_set_words[node])
		for node, branching_speed in sorted(node_to_branching_speed.items(), reverse=True, key=lambda x: x[1])[-20:]:
			word = wordnet.node_to_word_directed_no_supernodes[node]
			year = wordnet.word_to_date[word]
			print "{0} ({1}) = {2} --- {3}".format(word, year, branching_speed, node_to_influence_set_words[node])
		'''

		branching_speed_by_decade = {decade: list() for decade in range(600, 2001, 10)}

		for node in node_to_branching_speed.keys():
			word = wordnet.node_to_word_directed_no_supernodes[node]
			year = wordnet.word_to_date[word]
			branching_speed = node_to_branching_speed[node]

			decade = year - year % 10
			branching_speed_by_decade[decade].append((word, year, branching_speed))

		pickle.dump(branching_speed_by_decade, open(filename_template.format(max_depth), "w"))

# Compute the branching speed for each node using the given |max_depth|
def ComputeBranchingSpeed(wordnet, all_years_histogram, max_depth):
	node_to_branching_speed = {}
	node_to_influence_set_words = {}
	graph = wordnet.time_directed_graph_no_supernodes
	nodes = [node.GetId() for node in graph.Nodes()]
	for i in range(len(nodes)):
		if i % 10000 == 0: print "{0} of {1}".format(i, len(nodes))

		# Computing average distance between word and its influence set (in years)
		influence_set = ComputeInfluenceSet(graph, nodes[i], max_depth)
		influence_set_years = []
		influence_set_words = []

		current_word = wordnet.node_to_word_directed_no_supernodes[nodes[i]]
		current_year = wordnet.word_to_date[current_word]

		for node in influence_set:
			word = wordnet.node_to_word_directed_no_supernodes[node]
			year = wordnet.word_to_date[word]
			if year >= current_year:
				influence_set_years.append(year)
				influence_set_words.append((word, year))

		average_year_in_influence_set = mean(influence_set_years)
		
		# Branching Speed = 1 - (true avg dist to words in influence set) / (expected avg dist to words in influence)
		if average_year_in_influence_set > 0:
			branching_speed = 1 - (average_year_in_influence_set - current_year) / all_years_histogram[current_year]
			node_to_branching_speed[nodes[i]] = branching_speed
			#print (word, year, branching_speed, influence_set_words)
		else:
			node_to_branching_speed[nodes[i]] = 0
		node_to_influence_set_words[nodes[i]] = influence_set_words
	
	return node_to_branching_speed, node_to_influence_set_words

def mean(vector):
	return sum(vector) / float(len(vector)) if len(vector) != 0 else 0

def median(vector):
	sorted_vector = sorted(vector)
	if len(vector) % 2 == 1:
		return sorted_vector[(len(vector) - 1)/2]
	else:
		lower_index = int(math.floor((len(vector) - 1)/2.0))
		upper_index = int(math.ceil((len(vector) - 1)/2.0))
		return (sorted_vector[lower_index] + sorted_vector[upper_index])/2.0

# Find all of the nodes in the graph which are with |max_depth| steps of |node|
def ComputeInfluenceSet(graph, node, max_depth):
	influence_set = set()
	
	if max_depth == 0: return influence_set
	
	for neighbor in graph.GetNI(node).GetOutEdges():
		influence_set.add(neighbor)
		influence_set.update(ComputeInfluenceSet(graph, neighbor, max_depth-1))

	return influence_set

# This method is used to smooth the data from "by-decade" data to some other time period. For example:
# if num_to_group = 5, the data will now be grouped by half-century (aka 50-year intervals/buckets) 
def GroupDecades(branching_speed_by_decade, num_to_group):
	grouped_data = {}
	decades = sorted(branching_speed_by_decade.keys())
	for i in range(0, len(decades), num_to_group):
		start_decade = decades[i]
		grouped_data[start_decade] = list()
		for j in range(i, min(i+num_to_group, len(decades))):
			grouped_data[start_decade].extend(branching_speed_by_decade[decades[j]])

	return grouped_data

def GetExpectedBranchingSpeed(year, all_years):
	for i in range(len(all_years)):
		if all_years[i] > year: break

	return mean(all_years[i:]) - year


def normalize(vector):
	total = float(sum(vector))
	return [elem / total for elem in vector]

__main__()
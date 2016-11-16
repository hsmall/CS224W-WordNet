from snap import *

'''
This class encapsulates all of the information needed to create, maintain, and analyze an instance of a WordNet graph.
More specifically, this class contains the following instance variables:
	1.  parts_of_speech = A container of all included parts of speech in this graph.
	2.  synsets = A map from keys to synsets
	3.  graph = A TNEANet graph which holds the populated structure of the WordNet
	4.  node_to_word = A map from node_ids to words
	5.  word_to_node = A map from words to node_ids
	6.  all_words = A set containing every word in the graph
	7.  word_to_synset = A map from every word to a list of the keys for every synset containing the word
	8.  time_directed_graph = A TNEANet graph which holds the populated structure of the WordNet with time relations between words included
	9.  node_to_word_directed = A map from node_ids to words in the directed graph
	10. word_to_node_directed = A map from wrods to node_ids in the directed graph
	11. all_words_directed = A set containing every word in the directed graph

'''
class WordNet:

	PARTS_OF_SPEECH_OFFSET = {
		"n": 100000000,
		"v": 200000000,
		"a": 300000000,
		"s": 300000000,
		"r": 500000000
	} 

	PARTS_OF_SPEECH_TRANSLATION = {
		"n.": "n",
		"v.": "v",
		"adj.": "a",
		"adv.": "r"
	}

	'''
	Initialzes a WordNet.
	Args:
		filenames = list of data.* filenames which contain WordNet data.
		parts_of_speech = list of the parts of speech this WordNet should include.
		time_data_file = file containing information about word 'creation' dates
	'''
	def __init__(self, filenames, time_data_file):
		self.parts_of_speech = self.__GetPartsOfSpeech(filenames)
		self.synsets = self.__ReadSynsets(filenames)
		self.graph = self.__CreateGraph(self.synsets, self.parts_of_speech)
		self.word_and_pos_to_date = self.__ReadTimeData(time_data_file)
		self.time_directed_graph = self.__CreateTimeDirectedGraph(self.synsets, self.parts_of_speech, self.word_and_pos_to_date)


		self.word_to_synsets = {word : [] for word in self.all_words}
		for key, synset in self.synsets.items():
			for word in synset["words"]:
				self.word_to_synsets[word].append(key)

	'''
	Returns the pointer symbol along the directed edge (node1 -> node2)
	'''
	def GetSymbolOnEdge(self, node1, node2):
		return self.graph.GetStrAttrDatE(self.graph.GetEI(node1, node2), "symbol")


	'''
	Returns returns a pair of words in age order (older, younger)
	'''
	def __GetWordsInAgeOrder(self, word1, word2, part_of_speech, word_and_pos_to_date):
		older = word1
		newer = word2
		word1_and_pos = word1 + part_of_speech
		word2_and_pos = word2 + part_of_speech
		if word_and_pos_to_date[word2_and_pos] > word_and_pos_to_date[word2_and_pos]:
			newer = word1
			older = word2
		return older, newer

	'''
	Parses and returns the appropriate parts of speech based upon the given filenames.
	'''
	def __GetPartsOfSpeech(self, filenames):
		parts_of_speech = set()
		for filename in filenames:
			if filename.endswith(".noun"):
				parts_of_speech.add("n")
			elif filename.endswith(".verb"):
				parts_of_speech.add("v")
			elif filename.endswith(".adj"):
				parts_of_speech.update(["a", "s"])
			elif filename.endswith(".adv"):
				parts_of_speech.add("r")
		return parts_of_speech
	'''
	Reads in synsets from a list of data.* files.
	'''
	def __ReadSynsets(self, filenames):
		synsets = {}
		for filename in filenames:
			with open(filename, 'r') as file:
				# Ignore the Liscense Agreements at beginning of file.
				while True:
					last_position = file.tell()
					if file.readline()[0:2] != "  ":
						break

				file.seek(last_position)
				for line in file:
					key, synset = self.__ConvertToSynset(line.split(' '))
					synsets[key] = synset

		return synsets

	'''
	Reads in time data for words from the given file.
	'''
	def __ReadTimeData(self, filename):
		word_and_pos_to_date = {}
		keys = set()
		with open(filename, 'r') as file:
			for line in file:
				word, parts_of_speech, year = line.split(' <delim> ')
				parts_of_speech = parts_of_speech.split(' and ')
				for pos in set(parts_of_speech):
					# ignore interjections and pronouns
					if pos in WordNet.PARTS_OF_SPEECH_TRANSLATION.keys():
						key = word+pos
						# add earliest year for repeat keys in data
						if key in keys:
							if word_and_pos_to_date[key] > int(year):
								word_and_pos_to_date[key] = int(year)
						else:
							keys.add(key)
							word_and_pos_to_date[key] = int(year)
		return word_and_pos_to_date


	'''
	Takes a single line of a data file and converts it into a meaningful representation
	of a synset. A synset contains the following info:
		1. synset_type = the part of speech of synset.
	 	2. words = list of the words in the synset.
	 	3. pointers = list of pointers between this synset and others.
	 	4. description = given description for the synset.
	'''
	def __ConvertToSynset(self, line):
		synset_type = line[2]
		
		key = int(line[0]) + WordNet.PARTS_OF_SPEECH_OFFSET[synset_type]

		word_count = int(line[3], 16)
		word_start_index = 4
		pointer_count = int(line[word_start_index + 2 * word_count])
		pointer_start_index = word_start_index + 2 * word_count + 1
		
		words = []
		for index in range(word_start_index, word_start_index + 2 * word_count, 2):
			words.append(line[index])

		pointers = []
		for index in range(pointer_start_index, pointer_start_index + 4 * pointer_count, 4):
			src = int(line[index+3][0:2], 16)
			dst = int(line[index+3][2:], 16)
			pos = line[index+2]
			dst_key = int(line[index+1]) + WordNet.PARTS_OF_SPEECH_OFFSET[pos]
			pointers.append({"symbol": line[index], "pos": pos,
					   		 "connection": (key, src, dst_key, dst)})

		description = " ".join(line[line.index("|")+1:]).strip()
		
		return (key, {"synset_type": synset_type, "words": words,
				  	  "pointers": pointers, "description": description})

	'''
	Create the basic version of the WordNet graph.
	'''
	def __CreateGraph(self, synsets, parts_of_speech):
		graph = TNEANet.New()

		# Create the super-nodes for each synset
		self.all_words = set()
		for key, synset in synsets.items():
			self.all_words.update(synset["words"])
			graph.AddNode(key)

		# Create the nodes for the individual words
		self.node_to_word = {}
		self.word_to_node = {}
		for word in sorted(list(self.all_words)):
			node_id = graph.AddNode(-1)
			graph.AddStrAttrDatN(node_id, word, "word")
			self.node_to_word[node_id] = word
			self.word_to_node[word] = node_id

		# Add in edges between words
		for key, synset in synsets.items():
			# Add in connections from words to supernode for synset

			for word in synset["words"]:
				self.__AddEdge(graph, key, self.word_to_node[word], "synset")
			
			# Add connections between indiviual words in synset
			for word1 in synset["words"]:
				for word2 in synset["words"]:
					if word1 == word2: continue

					node1 = self.word_to_node[word1]
					node2 = self.word_to_node[word2]
					
					self.__AddEdge(graph, node1, node2, "synonym")

			# Add connections for pointers
			for pointer in synset["pointers"]:
				if pointer["pos"] not in parts_of_speech: continue

				_, src, key2, dst = pointer["connection"]
				if src == 0 and dst == 0:
					self.__AddEdge(graph, key, key2, pointer["symbol"], directed=True)
				else:
					node1 = self.word_to_node[synset["words"][src-1]]
					node2 = self.word_to_node[synsets[key2]["words"][dst-1]]
					self.__AddEdge(graph, node1, node2, pointer["symbol"], directed=True)

		return graph

	'''
	Create the time directed version of the WordNet graph.
	'''
	def __CreateTimeDirectedGraph(self, synsets, parts_of_speech, word_and_pos_to_date):
		directed_graph = TNEANet.New()

		# Create the super-nodes for each synset
		self.all_words_directed = set()
		supernodes_in_directed_graph = set()
		words_with_time_data = word_and_pos_to_date.keys()
		for key, synset in synsets.items():
			add_supernode = False
			for word in synset["words"]:
				if word + synset["synset_type"] in words_with_time_data:
					self.all_words_directed.add(word)
					add_supernode = True
			if add_supernode:
				supernodes_in_directed_graph.add(key)
		 		directed_graph.AddNode(key)

		# Create the nodes for the individual words
		self.node_to_word_directed = {}
		self.word_to_node_directed = {}
		for word in sorted(list(self.all_words_directed)):
			node_id = directed_graph.AddNode(-1)
			directed_graph.AddStrAttrDatN(node_id, word, "word")
			self.node_to_word_directed[node_id] = word
			self.word_to_node_directed[word] = node_id

		# Add in edges between words
		for key, synset in synsets.items():
			if key not in supernodes_in_directed_graph: continue
			# Add in connections from words to supernode for synset

			for word in synset["words"]:
				if word in self.all_words_directed:
					self.__AddEdge(directed_graph, key, self.word_to_node_directed[word], "synset")
			
			# Add connections between indiviual words in synset
			for word1 in synset["words"]:
				if word1 not in self.all_words_directed: continue
				for word2 in synset["words"]:
					if word1 == word2: continue
					if word2 not in self.all_words_directed: contiue
					older, newer = self.__GetWordsInAgeOrder(word1, word2, synset["synset_type"], word_and_pos_to_date)

					node1 = self.word_to_node_directed[older]
					node2 = self.word_to_node_directed[newer]
					
					self.__AddEdge(directed_graph, node1, node2, "synonym", directed=True)

			# Add connections for pointers
			for pointer in synset["pointers"]:
				if pointer["pos"] not in parts_of_speech: continue

				_, src, key2, dst = pointer["connection"]
				if src == 0 and dst == 0:
					if key2 not in supernodes_in_directed_graph: continue
					self.__AddEdge(directed_graph, key, key2, pointer["symbol"], directed=True)
				else:
					node1 = self.word_to_node_directed[synset["words"][src-1]]
					node2 = self.word_to_node_directed[synsets[key2]["words"][dst-1]]
					self.__AddEdge(directed_graph, node1, node2, pointer["symbol"], directed=True)

		return directed_graph

	'''
	Adds an edge with the given symbol from node1 to node2 (and vice versa if directed = True).
	'''
	def __AddEdge(self, graph, node1, node2, symbol, directed=False):
		graph.AddStrAttrDatE(graph.AddEdge(node1, node2), symbol, "symbol")
		if not directed:
			self.__AddEdge(graph, node2, node1, symbol, True)

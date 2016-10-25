from snap import *

'''
This class encapsulates all of the information needed to create, maintain, and analyze an instance of a WordNet graph.
More specifically, this class contains the following instance variables:
	1. parts_of_speech = A container of all included parts of speech in this graph.
	2. synsets = A map from keys to synsets
	3. graph = A TNEANet graph which holds the populated structure of the WordNet
	4. node_to_word = A map from node_ids to words
	5. word_to_node = A map from words to node_ids
	6. all_words = A set containing every word in the graph
	7. word_to_synset = A map from every word to a list of the keys for every synset containing the word
'''
class WordNet:

	PARTS_OF_SPEECH_OFFSET = {
		"n": 100000000,
		"v": 200000000,
		"a": 300000000,
		"s": 300000000,
		"r": 500000000
	} 

	'''
	Initialzes a WordNet.
	Args:
		filenames = list of data.* filenames which contain WordNet data.
		parts_of_speech = list of the parts of speech this WordNet should include.
	'''
	def __init__(self, filenames):
		self.parts_of_speech = self.__GetPartsOfSpeech(filenames)
		self.synsets = self.__ReadSynsets(filenames)
		self.graph = self.__CreateGraph(self.synsets, self.parts_of_speech)

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
	Adds an edge with the given symbol from node1 to node2 (and vice versa if directed = True).
	'''
	def __AddEdge(self, graph, node1, node2, symbol, directed=False):
		graph.AddStrAttrDatE(graph.AddEdge(node1, node2), symbol, "symbol")
		if not directed:
			self.__AddEdge(graph, node2, node1, symbol, True)

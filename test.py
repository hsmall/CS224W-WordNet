from WordNet import WordNet

def makeGraphGetStats():
	filenames = ['data/dict/data.adj', 'data/dict/data.adv', 'data/dict/data.noun', 'data/dict/data.verb']
	time_data_file = "data/word_to_year_formatted.txt"
	wordnet = WordNet(filenames, time_data_file)


if __name__ == '__main__':
	print "Test WordNet class"
	print
	makeGraphGetStats()
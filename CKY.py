import nltk
from pathlib import Path
from nltk import CFG
from nltk.tree import ImmutableTree
import string
import myGrammar


class CKY:

	'''
	grammar_cnf is an nltk.grammar.CFG in chomsky normal form.
	the attribute _rhs_lhs is a dictionary where the keys are tuples of the right-hand-side symbols,
	the values are lists of left hand side symbols:
	{(terminal,):[A1,...,An] for the preterminal rules, (B,C):[A1,...,An] for the non-preterminal rules}
	'''
	def __init__(self,grammar_cnf):
		self._grammar=grammar_cnf
		self._rhs_lhs=dict()
		for prod in self._grammar.productions():
			if prod.rhs() in self._rhs_lhs.keys():
				self._rhs_lhs[prod.rhs()].append(prod.lhs())
			else:
				self._rhs_lhs[prod.rhs()]=[prod.lhs()]



	'''
	given a sentence as a list of words, instantiates and fills in self._table attribute (the CKY chart) with the CKY algorithm.  
	The table is a dictionary. The keys are tuples of the indexes of the 'cells', the values are dictionaries.
	In each of these 'cell' (dictionary), the keys are the non-terminal symbols (A), the values are the terminal symbols for preterminal rules,
	lists of triples of (B,C,i+k) for the non-preterminal rules, where B and C are the right-hand side of A, i+k serves as backpointer to the
	cells from which B and C are originated.
	The key for each cell is instantiated only if the cell is actually filled with something.
	'''
	def __parse(self,sentence):
		self._table=dict()
		for i in range(len(sentence)):	#my i index starts from 0.
			try:
				preterminal_prods=self._rhs_lhs[(sentence[i],)]	#if there is no preterminal rule for the word, there is no correspondent 
																#key in self._rhs_lhs: a KeyError is raised.
				self._table[i,i+1]=dict()	
				for A in preterminal_prods:
					self._table[i,i+1][A]=sentence[i]
			except KeyError:	#if there is no preterminal rule for a given word, the sentence is ungrammatical.
				return False
		for b in range(2, len(sentence)+1):
			for i in range(len(sentence)-b+1):	#my i index starts from 0.
				for k in range(1,b):
					for B in self._table.get((i,i+k),dict()).keys():	#an empty dictionary is returned if the key (i,i+k) doesn't exist,
																		#which means that the cell is empty, and the iteration goes on 
																		#to the next step
						for C in self._table.get((i+k,i+b),dict()).keys():	#same as above
							for A in self._rhs_lhs.get((B,C),[]):	#an empty list is returned if the key (B,C) doesn't exist,
																	#which means that there is no rule whose right-hand side is B C, 
																	#and the iteration goes on to the next step
								if (i,i+b) not in self._table.keys():	#The key is instantiated only if the cell is filled with something.
									self._table[i,i+b]=dict()
								if A in self._table[i,i+b].keys():
									self._table[i,i+b][A].append((B,C,i+k))									
								else:
									self._table[i,i+b][A]=[(B,C,i+k)]



	#returns True if the sentence is grammatical, False otherwise.
	def recognize(self,sentence):
		self.__parse(sentence)
		try:
			if self._grammar.start() in self._table[0,len(sentence)].keys(): #if the cell was not instantiated at all, a KeyError is raised.
				return True
			else:	#the cell was instantiated, but it doesn't contain the start symbol.
				return False
		except KeyError:
			return False



	#returns the number of trees for a given entry, if there are any.
	def number_of_trees(self,sentence,i,i_plus_b,A):
		self.__parse(sentence)
		if (i,i_plus_b) in self._table.keys():
			if A in self._table[i,i_plus_b].keys():
				return self.__count_trees(i,i_plus_b,A)
		return 'There are no grammatical trees for this entry.'



	'''
	recursively counts the number of trees underlying a given grammatical entry (A(i,i+b)): 
	for a given A, the number of underlying trees is the sum (over all the productions A → B C) 
	of the number of trees underlying B times the number of trees underlying C. 
	If the rule is preterminal, there is only one underlying tree.
	returns the number of trees.
	'''
	def __count_trees(self,i,i_plus_b,A):
		number_of_trees=0
		for prods in self._table[i,i_plus_b][A]:
			if i_plus_b==i+1:
				number_of_trees= 1
			else:
				i_plus_k = prods[2]
				number_of_trees_B=self.__count_trees(i,i_plus_k,prods[0])
				number_of_trees_C=self.__count_trees(i_plus_k,i_plus_b,prods[1])
				number_of_trees+=number_of_trees_B*number_of_trees_C
		return number_of_trees



	#returns a set of ImmutableTrees for a given sentence, if it's grammatical.
	def trees(self,sentence):
		if self.recognize(sentence)==False:
			return 'The sentence is not grammatical.'
		else:
			trees_strings= self.__write_trees(0,len(sentence),self._grammar.start())
			trees=set()
			for tree_string in trees_strings:
				tree=ImmutableTree.fromstring(tree_string)
				trees.add(tree)
			return trees



	'''
	recursively enumerates and writes down the trees strings for a given grammatical sentence.
	returns a set of trees strings.
	'''
	def __write_trees(self,i,i_plus_b,A):
		trees_strings=set()
		for prods in self._table[i,i_plus_b][A]:
			if i_plus_b==i+1:	##if the rule is preterminal
				trees_strings.add('('+str(A)+' '+self._table[i,i_plus_b][A]+')') #adds the preterminal and terminal symbol.
			else:
				i_plus_k = prods[2]
				for tree_B in self.__write_trees(i,i_plus_k,prods[0]):
					for tree_C in self.__write_trees(i_plus_k,i_plus_b,prods[1]):
						trees_strings.add('('+str(A)+' ('+tree_B+') ('+tree_C+'))')
		return(trees_strings)
			












if __name__ == '__main__':

	#load the grammar.
	grammar_original= nltk.data.load("grammars/large_grammars/atis.cfg")

	#load the raw sentences.
	text = nltk.data.load("grammars/large_grammars/atis_sentences.txt")

	#extract the test sentences (a list of lists of split sentences).
	sentences= nltk.parse.util.extract_test_sentences(text)
	
	'''
	#NLTK already implements a number of parsing algorithms. I tried BottomUpChartParser
	#to see if I loaded the grammar correctly:
	# initialize the parser
	parser = nltk.parse.BottomUpChartParser(grammar_original)

	# parse all test sentences
	for sentence in sentences:
		for t in parser.parse(sentence[0]):
			print(t)
	'''


	#checks whether atis-grammar-cnf.cfg files exist, else downloads it.
	grammar_cnf_file="atis-grammar-cnf.cfg"
	if Path(grammar_cnf_file).is_file()==False:
		url="http://www.coli.uni-saarland.de/~koller/materials/anlp/atis.zip"
		urllib.request.urlretrieve(url, "atis.zip")
		myzip=zipfile.ZipFile('atis.zip')
		myzip.extractall()
		myzip.close()


	#reads in the cfg grammar.
	with open (grammar_cnf_file) as cnf:
		grammar_cnf_1=CFG.fromstring(cnf.readlines())

	#cnf_1 is in Chomsky normal form
	print('cnf_1 is in Chomsky normal form:',grammar_cnf_1.is_chomsky_normal_form())



	#the original grammar is nonlexical, but not in cnf
	print('Original grammar is nonlexical:',grammar_original.is_nonlexical())
	print('Original grammar is in Chomsky normal form:',grammar_original.is_chomsky_normal_form())

	#converts the original grammar to cnf
	grammar_cnf_2=myGrammar.convert_to_cnf(grammar_original)

	#cnf_2 is in Chomsky normal form, cnf_1 and cnf_2 have the same number of rules
	print('cnf_2 is in Chomsky normal form:',grammar_cnf_2.is_chomsky_normal_form())
	print('Number of rules in cnf_1:',len(grammar_cnf_1.productions()))
	print('Number of rules in cnf_2:',len(grammar_cnf_2.productions()))
	


	'''
	given one of the two cnf grammars and an output filename, writes a list of ATIS test sentences with tab-separated numbers of
	parse trees to the output file, and displays the parse trees for the first ATIS test sentence with 4 parse trees.
	'''
	def ATIS_output(grammar,filename):
		cky=CKY(grammar)

		with open(filename,'w') as f:
			sentence_of_choice=None   #during the iteration, we select the first sentence with 4 parse trees. 
			'''
			the words in the sentence are appended in a string. We did not use the 'join' method because it would
			also put a space before punctuation symbols. 
			'''
			for sentence in sentences:	
				sentence_string=''
				first_word=True
				for word in sentence[0]:
					if first_word:	#at the beginning of the sentence no space is added before the word.
						sentence_string+=word
						first_word=False
					else:
						if word[0] in string.punctuation: #if the first symbol of a word is a punctuation symbol, no space is added before the word.
							sentence_string+=word
						else:
							sentence_string+=' '+word
				number_of_trees=cky.number_of_trees(sentence[0],0,len(sentence[0]),grammar.start())
				if sentence_of_choice==None:	#We assign the first sentence with 4 parse trees to sentence_of_choice.
					if number_of_trees==4:
						sentence_of_choice=sentence[0]
				f.write(sentence_string+'\t'+str(number_of_trees)+'\n')
		#draws the trees for the chosen sentence
		for tree in cky.trees(sentence_of_choice):
			tree.draw()



	#ATIS_output is called on both cnf grammars, to compare the results

	ATIS_output(grammar_cnf_1,'ATIS_output1.txt')

	ATIS_output(grammar_cnf_2,'ATIS_output2.txt')



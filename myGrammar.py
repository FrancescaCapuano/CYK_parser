import nltk
from nltk import CFG


'''
given a non-lexical grammar, returns and equivalent grammar in chomsky normal form, 
if the start symbol never appears in the right-hand side of the rules.
'''
def convert_to_cnf(grammar):
	new_grammar=eliminate_more_than_2_nonterm(grammar)
	return eliminate_unary_rules(new_grammar)



'''
given a non-lexical grammar, returns an equivalent grammar with no more than two non-terminals 
on the right-hand side of each rule, if the start symbol never appears in the right-hand side.
the rules with less than 3 symbols on the right-hand side are simply added to the new grammar.
as for the rules with more than 2 symbols on the right-hand side, such as A -> X1,X2,...,Xn,
following new rules are added to the new grammar:
A -> X1 A1
A1 -> X2 A2
.
.
.
An-2 -> Xn-1 Xn

an index of the original production is added to the new nonterminals, otherwise they would make the rules
overlap and create new rules not allowed in the original grammar. 
'''
def eliminate_more_than_2_nonterm(grammar):
	new_grammar_strings=set()
	new_grammar_strings.add('%'+'start SIGMA') #this string must be added to let the CFG.fromstring function recognize the start symbol as SIGMA
	for j in range(len(grammar.productions())):
		prod=grammar.productions()[j]
		if grammar.start() in prod.rhs():#break if start symbol is on the right hand side - it never happens
			return "Can't convert grammar to cnf."
		if len(prod.rhs())>2:
			lhs=prod.lhs()	#the initial left-hand side symbol stays 'A'
			for i in range(1,len(prod.rhs())-1):
				new_nonterminal=nltk.Nonterminal(str(prod.lhs())+str(j)+'_'+str(i))#j=index of the original production, i=index of the new nonterminal

				if i ==len(prod.rhs())-2:	#the last of the new productions 
					rhs=prod.rhs()[-2:]		#leads to the last 2 symbols of the right-hand side of the original production
					new_prod=nltk.Production(new_nonterminal,rhs)
					new_grammar_strings.add(str(new_prod))
					pass
				rhs=[prod.rhs()[i-1],new_nonterminal]
				new_prod=nltk.Production(lhs,rhs)
				new_grammar_strings.add(str(new_prod)) #the new productions are added to a set of strings
				lhs=new_nonterminal
		else:
			new_grammar_strings.add(str(prod))
	return CFG.fromstring(new_grammar_strings)	#the set of strings is transformed into a grammar
					

'''
given a non-lexical grammar with no more than two non-terminals on the right-hand side of each rule , 
returns and equivalent grammar in chomsky normal form.
the rules with 2 symbols or with 1 terminal symbol on the right-hand side are simply added to the new grammar.
if the production rules are unary and non preterminal, such as A -> B, for each rule whose left-hand side is B
(such as B -> 's', B -> C or B -> C D), we add the rules A -> 's', A -> C, A -> C D.
if, at the end of the iteration, there are still unary rules (the grammar is still not in cnf), 
we repeat the procedure.
'''
def eliminate_unary_rules(grammar):
	new_grammar_strings=set()
	new_grammar_strings.add('%'+'start SIGMA') #this string must be added to let the CFG.fromstring function recognize the start symbol as SIGMA
	lhs_rhs=dict()	#a dictionary to access the right-hand sides from the left-hand sides
	for prod in grammar.productions():	
		if prod.lhs() in lhs_rhs.keys():
			lhs_rhs[prod.lhs()].add(prod.rhs())
		else:
			lhs_rhs[prod.lhs()]=set()
			lhs_rhs[prod.lhs()].add(prod.rhs())
	for prod in grammar.productions():
		if len(prod.rhs())==1:			#if the production rules are unary
			if prod.is_nonlexical():	#and non preterminal
				for rhs1 in prod.rhs():		
					for rhs2 in lhs_rhs[rhs1]:	#for each rule whose left-hand side is B
						new_prod=nltk.Production(prod.lhs(),rhs2)
						new_grammar_strings.add(str(new_prod))	#we add the new rules
			else:
				new_grammar_strings.add(str(prod))	#the new productions are added to a set of strings
		else:
			new_grammar_strings.add(str(prod))
	cnf_grammar=CFG.fromstring(new_grammar_strings)	#the set of strings is transformed into a grammar
	if cnf_grammar.is_chomsky_normal_form()==False:	#if the grammar is still not in cnf, repeat the procedure
		return eliminate_unary_rules(cnf_grammar)
	else:
		return cnf_grammar

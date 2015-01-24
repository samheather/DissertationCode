import urllib
import wikipedia_utils
from pymongo import MongoClient
import math

import compare
import dbpediaParser
import wikiPageParser

client = MongoClient('localhost', 27017)
db = client.dis
wordReferencePairs = db.wordReferencePairs

def removeWikiChars(input):
	for c in '!@#${}|':
		input = input.replace(c, '')
	return input
	
def findArgumentOnPage(argument, page):

	# Sources (in priority order in list)
	# TODO - neaten to 2 lines of code.
	fromDbpedia = dbpediaParser.getInfobox(page)
	fromWikiPage = wikiPageParser.getInfobox(page)
	sources = [fromDbpedia, fromWikiPage]
	
	answer = None
	propertyReturned = None
	maxCertaintySoFar = -1.0
	for source in sources:
		localAnswer, localPropertyReturned, certainty = matchAmbiguousArgumentToProperty(
			argument, source)
		# TODO - test if answer is None - it shouldn't crash - just can't remember how
		# python handles this.
		if (certainty > maxCertaintySoFar):
			answer = localAnswer
			propertyReturned = localPropertyReturned
			maxCertaintySoFar = certainty
		if (maxCertaintySoFar == 1.0):
			# DBPedia produced best result, 1.0 can't be beaten by other source, return
			break
	if (answer == None):
		answer = "An answer to your question could not be found."
	return removeWikiChars(answer), propertyReturned

def matchAmbiguousArgumentToProperty(argument, infobox):
	print infobox
	for property in infobox:
		if argument.lower() == str(property).lower():
			return infobox[property], property, 1.0
	
	# Score the relatedness of each property against the argument and compare to the
	# max so far.  If it is higher, store the key.
	localMax = -1.0
	currentMaxKey = None
	for property in infobox:
		similarityScore = compare.similarity(argument, str(property))
		similarityScore = adjustSimilarityWithRanking(similarityScore, argument, property)
		print similarityScore, ' - ', argument, ' - ', property
		# If this property has a higher semantic similarity AND is not None (implicit):
		if (similarityScore > localMax):
			localMax = similarityScore
			currentMaxKey = property
	print 'max: ', currentMaxKey, ' with val: ', localMax
	
	# If a match wasn't found, just back Nones and this value to be handed above.
	if (localMax == -1.0):
		return None, None, localMax
	# Now simply use the key with the largest similarity to retrieve the results
	return infobox[currentMaxKey], currentMaxKey, localMax
	
def adjustSimilarityWithRanking(similarity, argument, property):
	adjustment = getQualityMultiplier(argument, property)
	if (adjustment < 0):
		return similarity * math.pow(0.95,abs(adjustment))
	elif (adjustment > 0):
		return similarity * math.pow(1.05,abs(adjustment))
	
def getQualityMultiplier(argument, property):
	pairEntry = wordReferencePairs.find_one({
					'givenProperty' : argument,
					'returnedProperty' : property
				})
	if (pairEntry == None):
		return 0
	return pairEntry['ranking']
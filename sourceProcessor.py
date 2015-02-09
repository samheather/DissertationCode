import urllib
import wikipedia_utils
from pymongo import MongoClient
import math
import re

import compare
import dbpediaParser
import wikiPageParser

# Setup Mongo
client = MongoClient('localhost', 27017)
db = client.dis
wordReferencePairs = db.wordReferencePairs

"""
	wikiPageParser tends to return strings with additional formatting, which is not
	needed.  This function removes these.
"""
def removeWikiChars(input):
	for c in '!@#${}|':
		input = input.replace(c, '')
	return input
	
"""
	Given a (potentially ambiguous) argument and a valid wikipedia page name, this returns
	the value of that property and the name of the returned property.
"""
def findArgumentOnPage(argument, page):
	# Sources (in priority order)
	sources = [dbpediaParser.getInfobox(page)]#, wikiPageParser.getInfobox(page)]
	
	# Preset answer, propertyReturned and the certainty - these are then set from
	# iterating through the sources.
	answer = None
	propertyReturned = None
	maxCertaintySoFar = -1.0
	for source in sources:
		localAnswer, localPropertyReturned, certainty = matchAmbiguousArgumentToProperty(
			argument, source)
		if (certainty > maxCertaintySoFar):
			answer = localAnswer
			propertyReturned = localPropertyReturned
			maxCertaintySoFar = certainty
		if (maxCertaintySoFar == 1.0):
			# DBPedia produced best result, 1.0 can't be beaten by other source, return
			break
	# No answer was found (certaintySoFar never raised above -1)
	if (answer == None):
		answer = "An answer to your question could not be found."
	return removeWikiChars(answer), propertyReturned

"""
	Takes a requested parameter and an infobox, containing a list of keys. Returns the 
	value, key and certainty of semantic match between the key in the infobox and the
	 parameter you request from the infobox.
"""
def matchAmbiguousArgumentToProperty(argument, infobox):
	# First look for a perfect match between the requested parameter and the parameters in
	# the infoboxes.  If a match is found, return it with 100% semantic match certainty.
	print infobox
	for property in infobox:
		if argument.lower() == str(property).lower():
			return infobox[property], property, 1.0
	
	# Score the relatedness of each property against the argument and compare to the
	# max so far.  If it is higher, store the key.
	localMax = -1.0
	currentMaxKey = None
	for property in infobox:
		# CamelCase not recognised in compare.similarity(), but snake_case is, so convert!
		similarityScore = compare.similarity(argument, camelCaseToSnakeCase(str(property)))
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
	
""" TODO: Fill this in once the 5 star ranking system is complete """
def adjustSimilarityWithRanking(similarity, argument, property):
	adjustment = getQualityMultiplier(argument, property)
	if (adjustment == None):
		return similarity
	else:
		return similarity
		# TODO - finish this
		
# 	if (adjustment < 0):
# 		return similarity * math.pow(0.95,abs(adjustment))
# 	elif (adjustment > 0):
# 		return similarity * math.pow(1.05,abs(adjustment))

""" TODO: Fill this in once the 5 star ranking system is complete """
def getQualityMultiplier(argument, property):
	pairEntry = wordReferencePairs.find_one({
					'givenProperty' : argument,
					'returnedProperty' : property
				})
	if (pairEntry == None):
		return None
	# TODO - finish this
	return pairEntry['ranking']
	
# From: http://stackoverflow.com/questions/1175208/
# Required for semantic comparison of CamelCase keys in the infoboxes.
def camelCaseToSnakeCase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

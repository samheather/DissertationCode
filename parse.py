# Based off information on:
# https://blog.scraperwiki.com/2011/12/how-to-scrape-and-parse-wikipedia/

import lxml.etree
import urllib
import wikipedia_utils
from pymongo import MongoClient
import math

import compare

client = MongoClient('localhost', 27017)
db = client.dis
wordReferencePairs = db.wordReferencePairs

def removeWikiChars(input):
	for c in '!@#${}|':
		input = input.replace(c, '')
	return input
	
def findArgumentOnPage(argument, page):
	page = wikipedia_utils.GetWikipediaPage(page)
	# If unexpected block, below prints that block.
	parsedPage = wikipedia_utils.ParseTemplates(page["text"])

	# infobox_ukcave = dict(parsedPage["templates"]).get("Infobox cave")
	# print infobox_ukcave

	templates = dict(parsedPage["templates"])
	
	infobox = None
	for key in templates.keys():
		if 'box' in key.lower():
			infobox = templates.get(key)
			break
	
	if (infobox == None):
		print 'there was no infobox on this page!'
		
# 	print infobox
	answer, propertyReturned = matchAmbiguousArgumentToProperty(argument, infobox)
	return removeWikiChars(answer), propertyReturned

def matchAmbiguousArgumentToProperty(argument, infobox):
	for property in infobox:
		if argument.lower() == str(property).lower():
			return infobox[property], property
	
	# Score the relatedness of each property against the argument and compare to the
	# max so far.  If it is higher, store the key.
	localMax = -1
	currentMaxKey = None
	for property in infobox:
		similarityScore = compare.similarity(argument, str(property))
		similarityScore = adjustSimilarityWithRanking(similarityScore, argument, property)
		print similarityScore, ' - ', argument, ' - ', property
		if (similarityScore > localMax):
			localMax = similarityScore
			currentMaxKey = property
	print 'max: ', currentMaxKey, ' with val: ', localMax
			
	# Now simply use the key with the largest similarity to retrieve the results
	return infobox[currentMaxKey], currentMaxKey
	
def adjustSimilarityWithRanking(similarity, argument, property):
	adjustment = getQualityMultiplier(argument, property)
	if (adjustment < 0):
		return similarity * math.pow(0.95,abs(adjustment))
	elif (adjustment > 0):
		return similarity * math.pow(1.05,abs(adjustment))
	
def getQualityMultiplier(argument, property):
	wordReferencePairs.find_one({
					'givenProperty' : argument,
					'returnedProperty' : property
				})
	if (wordReferencePairs == None):
		return None
	return wordReferencePairs['ranking']
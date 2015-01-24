import lxml.etree
# import urllib
import wikipedia_utils
# from pymongo import MongoClient
# import math

# import compare

# client = MongoClient('localhost', 27017)
# db = client.dis
# wordReferencePairs = db.wordReferencePairs

# def removeWikiChars(input):
# 	for c in '!@#${}|':
# 		input = input.replace(c, '')
# 	return input
	
def getInfobox(page):
	page = wikipedia_utils.GetWikipediaPage(page)
# 	print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
# 	print page
# 	print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
	# If unexpected block, can print the below to view all blocks.
	parsedPage = wikipedia_utils.ParseTemplates(page["text"])

	templates = dict(parsedPage["templates"])
	
	infobox = None
	for key in templates.keys():
		if 'box' in key.lower():
			infobox = templates.get(key)
			break
	
	if (infobox == None):
		print 'there was no infobox on this page!'
	
	return infobox

# def matchAmbiguousArgumentToProperty(argument, infobox):
# 	print infobox
# 	for property in infobox:
# 		if argument.lower() == str(property).lower():
# 			return infobox[property], property
# 	
# 	# Score the relatedness of each property against the argument and compare to the
# 	# max so far.  If it is higher, store the key.
# 	localMax = -1
# 	currentMaxKey = None
# 	for property in infobox:
# 		similarityScore = compare.similarity(argument, str(property))
# 		similarityScore = adjustSimilarityWithRanking(similarityScore, argument, property)
# 		print similarityScore, ' - ', argument, ' - ', property
# 		if (similarityScore > localMax):
# 			localMax = similarityScore
# 			currentMaxKey = property
# 	print 'max: ', currentMaxKey, ' with val: ', localMax
# 			
# 	# Now simply use the key with the largest similarity to retrieve the results
# 	return infobox[currentMaxKey], currentMaxKey
# 	
# def adjustSimilarityWithRanking(similarity, argument, property):
# 	adjustment = getQualityMultiplier(argument, property)
# 	if (adjustment < 0):
# 		return similarity * math.pow(0.95,abs(adjustment))
# 	elif (adjustment > 0):
# 		return similarity * math.pow(1.05,abs(adjustment))
# 	
# def getQualityMultiplier(argument, property):
# 	pairEntry = wordReferencePairs.find_one({
# 					'givenProperty' : argument,
# 					'returnedProperty' : property
# 				})
# 	if (pairEntry == None):
# 		return 0
# 	return pairEntry['ranking']
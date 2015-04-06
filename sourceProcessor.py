import urllib
import wikipedia_utils
from pymongo import MongoClient
import math
import numpy

import compare
import dbpediaParser
import wikiPageParser

# Setup Mongo
client = MongoClient('localhost', 27017)
db = client.dis
wordReferencePairs = db.wordReferencePairs
pastWholeQuestionRating = db.pastWholeQuestionRating

minThreshold = 0.2

# TODO - remove this repetition from server.py:
ratingKeys = ["oneStarRatings", "twoStarRatings", "threeStarRatings", "fourStarRatings",
    "fiveStarRatings"]

def checkPastQuestions(question):
    # Check if there was a past question with high rating and high semantic relatedness
    pastQuestions = pastWholeQuestionRating.find({'rating':5})
    currentMax = -1
    maxAnswer = ''
    for pastQuestion in pastQuestions:
        similarity = compare.similarityOfQuestion(question, pastQuestion['question'])
        if similarity > currentMax:
            currentMax = similarity
            maxAnswer = pastQuestion['answer']
    if currentMax > 0.8:
        print 'Answer found from past questions, with value: ', currentMax
        return maxAnswer
    else:
        return None

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
    sources = [dbpediaParser.getInfobox(page), wikiPageParser.getInfobox(page)]
    
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
        if (maxCertaintySoFar > minThreshold):
            # If a good result (above threshold_ has been found, break. 
            # If not, as a last resort, try the second source (Wikipedia).
            break
    # No answer was found or no answer with certainty above 0.2 was found
    if (answer == None) or (maxCertaintySoFar <= minThreshold):
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
        similarityScore = compare.similarityOfProperty(argument, str(property))
        similarityScore = adjustSimilarityWithRanking(similarityScore, argument, property)
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
    
""" 
    Takes the requested argument and proposed property, adjusts if quality entires are
    in the mongo database.  Outliers are detected and ignored.
"""
def adjustSimilarityWithRanking(similarity, argument, property):
    pairEntry = wordReferencePairs.find_one({
                    'givenProperty' : argument,
                    'returnedProperty' : property
                })
    if (pairEntry == None):
        return similarity
    else:
        ratings = pairEntry['ratings']
        ratings = removeOutliers(ratings)
        ratings = compactRatings(ratings)
        similarity = similarity * \
            math.pow(0.95, ratings['oneStarRatings']) * \
            math.pow(0.98, ratings['twoStarRatings']) * \
            math.pow(1.00, ratings['threeStarRatings']) * \
            math.pow(1.02, ratings['fourStarRatings']) * \
            math.pow(1.05, ratings['fiveStarRatings'])
        return similarity
    
"""
    Takes an input list of integers and removes outliers by calculating the standard
    deviation and mean, and then removing entries further from the mean than one
    standard deviation.
"""
def removeOutliers(input):
    mean = numpy.mean(input)
    standardDeviation = numpy.std(input)
    minAcceptable = round(mean-standardDeviation)
    maxAcceptable = round(mean+standardDeviation)
    # remove entries in the list that are too small or too big - outliers
    output = filter(lambda b: b >= minAcceptable, input)
    output = filter(lambda b: b <= maxAcceptable, output)
    return output

"""
    Takes a list of integers, counts integers 1..5, then returns dictionary of the counts
"""
def compactRatings(input):
    return {
        'oneStarRatings':input.count(1),
        'twoStarRatings':input.count(2),
        'threeStarRatings':input.count(3),
        'fourStarRatings':input.count(4),
        'fiveStarRatings':input.count(5)
    }















































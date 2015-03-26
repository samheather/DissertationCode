import json
import urllib2
import requests

stopWords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours	ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]

def extractEntities(inputText):
	headers = {'content-type': 'application/json'}
	url = 'https://api.dandelion.eu/datatxt/nex/v1'
          
	params = {"$app_key": "3dccf99ae339254afbb8b642cf719131",
        	"$app_id": "d37adf4c",
        	"text": inputText,
        	"include": "types",
        	"lang": "en"}

	returnedData = json.loads(requests.post(url, params=params, headers=headers).text)

	results = returnedData['annotations']
	
	outputPlace = {'success': False}
	
	for item in results:
	    types = item['types']
	    if 'http://dbpedia.org/ontology/Place' in types:
	        outputPlace = {'wikiName': item['uri'].split('/')[-1],
	                        'realName': item['title'],
	                        'success': True}
	        break
 	return outputPlace

def nlp(workingQuestionString):
    # Prepare the string by making all lower case
    workingQuestionString = workingQuestionString.lower()

    # Identify the entity been queried about.
    place = extractEntities(workingQuestionString)
    
    # Find the words in the question relating to the place and strip them.
    wordsToStrip = place['realName'].split(' ')
    workingQuestionString = workingQuestionString.split(' ')
    for word in wordsToStrip:
        word = word.lower()
        if word in workingQuestionString:
            workingQuestionString.remove(word)
    
    # Now removing stopWords
    for stopWord in stopWords:
        stopWord = stopWord.lower()
        if stopWord in workingQuestionString:
            workingQuestionString.remove(stopWord)
    
    # Re-join workingQuestionString
    workingQuestionString = "".join(workingQuestionString)
    
    print 'Place: ', place['realName']
    print 'Property: ', workingQuestionString
    print '\n'
    

print nlp('how tall is mount everest')
print nlp('how long is the nile')
print nlp('how deep is the deepest ocean')
print nlp('what is the population of mexico city')

# how tall is mount everest
# how long is the nile
# how deep is the deepest ocean
# what is the population of mexico city
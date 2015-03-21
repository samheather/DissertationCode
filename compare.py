import json
import urllib2
import requests
import re

""" returns a value between 0 and 1 indicating the similarity of the 2 input words"""
def similarityCortical(word1, word2):
#  	print word1, " ----- ", word2
	data = [
		 { 
			"term": word1
		 },
		 {
			"text": word2
		 }
	]

	# Setup the HTTP request
	req = urllib2.Request('http://api.cortical.io:80/rest/compare?retina_name=en_associative')
	req.add_header('Content-Type', 'application/json')
	req.add_header('api-key', '8c6fa2e0-9e56-11e4-9495-ad65fdcddb54')

	# Send the request, and parse the response into JSON
	response = urllib2.urlopen(req, json.dumps(data))
	json_data = json.loads(response.read())
	
	# Extract and return the similarity value
# 	print json_data
# 	print json_data['cosineSimilarity']
	return json_data['cosineSimilarity']
	
def similarityDandelion(word1, word2, bow):
	if (not bow):
		bow_string = "never"
	else:
		bow_string = "always"
		
	headers = {'content-type': 'application/json'}
	url = 'https://api.dandelion.eu/datatxt/sim/v1'
          
	params = {"$app_key": "3dccf99ae339254afbb8b642cf719131",
        	"$app_id": "d37adf4c",
        	"text1": word1,
        	"text2": word2,
        	"lang": "en",
        	"bow": bow_string}

	result = json.loads(requests.post(url, params=params, headers=headers).text)

# 	print result
	return result['similarity']

def similarityOfProperty(word1,word2):
	word1 = camelCaseToSpace(word1)
	word2 = camelCaseToSpace(word2)
	if (len(word1.split(' ')) == 1) and (len(word2.split(' ')) == 1):
		sim = similarityCortical(word1, word2)
		print 'cort', sim, ' - ', word1, ' - ', word2
	else:
		sim = similarityDandelion(word1, word2, True)
		print 'dand', sim, ' - ', word1, ' - ', word2
	return sim

def similarityOfQuestion(question1,question2):
	return similarityDandelion(question1, question2, True)

# From: http://stackoverflow.com/questions/1175208/
# Required for semantic comparison of CamelCase keys in the infoboxes.
def camelCaseToSnakeCase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
def camelCaseToSpace(name):
	name = camelCaseToSnakeCase(name)
	return name.replace('_', ' ')
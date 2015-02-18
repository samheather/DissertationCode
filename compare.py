import json
import urllib2
import requests

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
	print json_data
	return json_data['cosineSimilarity']
	
def similarityDandelion(word1, word2):
	headers = {'content-type': 'application/json'}
	url = 'https://api.dandelion.eu/datatxt/sim/v1'
          
	params = {"$app_key": "3dccf99ae339254afbb8b642cf719131",
        	"$app_id": "d37adf4c",
        	"text1": word1,
        	"text2": word2,
        	"lang": "en"}

	result = json.loads(requests.post(url, params=params, headers=headers).text)

	return result['similarity']

def similarity(word1,word2):
	return similarityDandelion(word1, word2)

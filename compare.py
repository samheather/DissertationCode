import json
import urllib2

''' returns a value between 0 and 1 indicating the similarity of the 2 input words'''
def similarity(word1, word2):
#  	print word1, " ----- ", word2
	data = [
		 { 
			"text": word1
		 },
		 {
			"text": word2
		 }
	]

	# Setup the request
	req = urllib2.Request('http://api.cortical.io:80/rest/compare?retina_name=en_associative')
	req.add_header('Content-Type', 'application/json')
	req.add_header('api-key', '8c6fa2e0-9e56-11e4-9495-ad65fdcddb54')

	# Send the request, and parse the response into JSON
	response = urllib2.urlopen(req, json.dumps(data))
	json_data = json.loads(response.read())
	
	# Extract and return the similarity value
	return json_data['cosineSimilarity']
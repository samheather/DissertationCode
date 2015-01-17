from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import ujson
from flask import Flask, request, jsonify

import parse

# 7e2d62f74e4edd4b5fbf4d4c88ca86371b7d56f6

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dis
users = db.users
wordReferencePairs = db.wordReferencePairs

@app.route('/entry', methods=['POST'])
def entry():
	body = ujson.loads(request.data)
	userNumber = body['userNumber']
	questionParam1 = body['questionParam1']
	questionParam2 = body['questionParam2']
	currentUser = users.find_one({'userNumber' : userNumber})
	if (currentUser == None):
		currentUser = newUser(userNumber)
		
	answer = parse.findArgumentOnPage(questionParam2,questionParam1)

	
	return jsonify({'successful' : True, 'answer' : answer})
	
def newUser(cellNumber):
	user = {'cellNumber' : cellNumber}
	newUserObject = {'history' : {}}
	users.insert(newUserObject)
	return

'''
	Returns a wiki page with title matching the search term.
'''
def wikiSearch(searchTerm):
	pass

'''
	Returns a dict containing a short description, and variables related to the input page
	For example:
		{'description' : 'London is an incredible city',
		{'variables' :
			{
			'population' : 100,
			'old name' : 'Londinium'
			}
		}
'''
def wikiParse():
	pass

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug = True)
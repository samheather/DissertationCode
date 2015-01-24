from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import ujson
from flask import Flask, request, jsonify

import wikiPageParser

# 7e2d62f74e4edd4b5fbf4d4c88ca86371b7d56f6

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dis
users = db.users
wordReferencePairs = db.wordReferencePairs

@app.route('/entry', methods=['POST'])
def entry():
	body = ujson.loads(request.data)
	
	# Get the user, or create if necessary.
	cellNumber = body['cellNumber']
	currentUser = users.find_one({'cellNumber' : cellNumber})
	if (currentUser == None):
		currentUser = newUser(cellNumber)
		
	questionParam1 = body['questionParam1']
	
	if (questionParam1.lower() == 'help'):
		answer =	"For a specific fact, ask a question like 'what is the population of"\
					" London'\n" \
					"For general information, ask for a description with 'describe "\
					"London'\n" \
					"If the contents is trimmed and you want more, send 'more'\n" \
					"If an answer is of low quality, help improve the database by "\
					"sending 'poor'"
	elif (questionParam1.lower() == 'more'):
		answer = "Not yet implemented"
	elif (questionParam1.lower() == 'poor'):
		lastQuestion = currentUser['lastQuestion']
		if (lastQuestion['givenProperty'] != None)\
		and (lastQuestion['returnedProperty'] != None)\
		and (lastQuestion['receivedFeedback'] == False):
			reduceRanking(lastQuestion['givenProperty'], lastQuestion['returnedProperty'])
			currentUser['lastQuestion']['receivedFeedback'] = True
			updateUser(currentUser)
		answer = "Thank you for your feedback - it has been recorded."
	else:
		# Second parameter needed
		questionParam2 = body['questionParam2']
		if (questionParam1.lower() == 'describe'):
			answer = "Not yet implemented"
			updateUserWithLastQuestion(currentUser, questionParam1, None, None)
		else:
			# Find the answer, and retrieve the name of the property used.
			answer, keyUsed = wikiPageParser.findArgumentOnPage(questionParam2,questionParam1)
			updateUserWithLastQuestion(currentUser, questionParam1, questionParam2, keyUsed)

	return jsonify({'successful' : True, 'answer' : answer})
	
def updateUserWithLastQuestion(user, question, givenProperty, returnedProperty):
		user['lastQuestion']['text'] = question
		user['lastQuestion']['givenProperty'] = givenProperty
		user['lastQuestion']['returnedProperty'] = returnedProperty
		user['lastQuestion']['receivedFeedback'] = False
		updateUser(user)

def newUser(cellNumber):
	newUserObject = {
			'cellNumber' : cellNumber,
			'history' : [],
			'lastQuestion' : {
				'text' : None,
				'givenProperty' : None,
				'returnedProperty' : None
				}
			}
	users.insert(newUserObject)
	return newUserObject
	
def reduceRanking(givenProperty, returnedProperty):
	queryDict = {
					'givenProperty' : givenProperty,
					'returnedProperty' : returnedProperty
				}
	currentRankingDict = wordReferencePairs.find_one(queryDict)
	if currentRankingDict != None:
		# Potential race condition where chance may not be logged if executed on multiple
		# threads by two users asking the same question and providing feedback at the same
		# time.
		currentRankingDict['ranking'] = currentRankingDict['ranking']-1
		wordReferencePairs.update(queryDict,currentRankingDict)
	else:
		queryDict['ranking'] = -1
		wordReferencePairs.insert(queryDict)
	

''' Replaces the given user in the database'''	
def updateUser(user):
	users.update({"_id" : user['_id']},user)

'''
	Returns a wiki page with title matching the search term.
'''
def wikiSearch(searchTerm):
	pass

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug = True)
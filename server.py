from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import ujson
from flask import Flask, request, jsonify

import sourceProcessor

# Setup the application server
app = Flask(__name__)

# Setup Mongo
client = MongoClient('localhost', 27017)
db = client.dis
users = db.users
wordReferencePairs = db.wordReferencePairs

""" Main function for the server - takes input question or command, returns an answer. """
# Define the HTTP address to wait on
@app.route('/entry', methods=['POST'])
def entry():
	# Create dictionary from the input JSON.
	body = ujson.loads(request.data)
	
	# Get the user, or create one if one does not exist.
	cellNumber = body['cellNumber']
	currentUser = users.find_one({'cellNumber' : cellNumber})
	if (currentUser == None):
		currentUser = newUser(cellNumber)
		
	# TODO - comment this block when it's finalised with a single question field.
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
			answer, keyUsed = sourceProcessor.findArgumentOnPage(questionParam2,questionParam1)
			updateUserWithLastQuestion(currentUser, questionParam1, questionParam2, keyUsed)

	return jsonify({'successful' : True, 'answer' : answer})

""" 
	Updates the user object for this user with the parameters from their last question
	in the database, allowing for their next question to be based on the state of their 
	previous question.
"""
def updateUserWithLastQuestion(user, question, givenProperty, returnedProperty):
	# Set the properties, and update the object in the DB.
	user['lastQuestion']['text'] = question
	user['lastQuestion']['givenProperty'] = givenProperty
	user['lastQuestion']['returnedProperty'] = returnedProperty
	user['lastQuestion']['receivedFeedback'] = False
	updateUser(user)

""" Creates a new, empty user with the input cellNumber and returns it."""
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
	
""" #TODO - Fill this in once 5 stars implemented.
"""
def reduceRanking(givenProperty, returnedProperty):
	# Create the dictionary that we will query the DB to identify a pre-existing ranking,
	# then query the database.
	queryDict = {
					'givenProperty' : givenProperty,
					'returnedProperty' : returnedProperty
				}
	currentRankingDict = wordReferencePairs.find_one(queryDict)
	
	if currentRankingDict != None:
		# TODO: Potential race condition where chance may not be logged if executed on
		# multiplethreads by two users asking the same question and providing feedback at
		# the same time.
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

# Start the server
if __name__ == "__main__":
	app.run(host='0.0.0.0', debug = True)
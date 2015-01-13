from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import ujson

client = MongoClient('localhost', 27017)
db = client.dis
users = db.users
wordReferencePairs = db.wordReferencePairs

@app.route('/entry', methods=['POST'])
def entry():
	body = ujson.loads(request.data)
	userNumber = body['userNumber']
	question = body['question']
	currentUser = users.find_one({'userNumber' : userNumber})
	if (currentUser == None):
		currentUser = newUser(userNumber)
	
	# Find the correct page.

	# Parse the page

	# Parse the parsed object to the answer finder.
	
	return jsonify({'successful' : True, 'answer' : 'answer will go here'})
	
def newUser(cellNumber):
	user['cellNumber'] = cellNumber
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
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
from uuid import uuid4
import ujson

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.pwdev
users = db.users
objects = db.objects

@app.route('/entry', methods=['POST'])
def entry():
	body = ujson.loads(request.data)
	userNumber = body['userNumber']
	currentUser = users.find_one({'userNumber' : userNumber})
	if (currentUser == None):
		currentUser = newUser(userNumber)
		
	# TODO Get answer once discussed Wikipedia issue with Lilian
	
	return jsonify({'successful' : True, 'answer' : 'answer will go here'})
	
def newUser(cellNumber):
	user['cellNumber'] = cellNumber
	# TODO Global object ID below?
	newUserObject = {'_id' : 0, 'history' : {}}
	users.insert(newUserObject)
	return

def wikiSearch():
	pass

def wikiParse():
	pass

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug = True)
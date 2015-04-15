from gevent.pywsgi import WSGIServer
from pymongo import MongoClient
import ujson
from flask import Flask, request, jsonify
import twilio.twiml
import hashlib
import time

import sourceProcessor
import nlp

# Setup the application server
app = Flask(__name__)

# Setup Mongo
client = MongoClient('localhost', 27017)
db = client.dis
users = db.users
wordReferencePairs = db.wordReferencePairs
pastWholeQuestionRating = db.pastWholeQuestionRating

# 512 bit salt
constantSalt = 'ac0568f7c739f764723a68e523aa4cdb9fdec063de75a7a12f7c8b54e6675ceac62a472dc96f75d26fed168e0bcda710122c39130ad34c2b7d2f0971bf35734354c0386db9ac2642497f6d4f4b1eebb9c77bc3980519b08d7a7f2944cc43b05600f39b0639b3e8f3fb38d0ff1c09e31f7eadf35a84feaf0dc275536cc8310c41'

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    # Establish the from number and the message body
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None)
    
    f = open('logfile','w')
    
    # Hash the number
    hashedNumber = hashNumber(from_number)

    f.write(body)
    f.write('\n')
    
    body = {'cellNumber':hashedNumber,
            'question':body}
            
    answer = start(body)
    
    f.write(answer)
    f.write('\n')
    
    f.close()
    
    # Response
    reply = answer
 
    maxSmsLength = 1500
    resp = twilio.twiml.Response()
    if (len(reply) <= maxSmsLength):
        resp.message(reply)
    else:
        splitAnswer = [reply[i:i+maxSmsLength] for i in range(0, len(reply), maxSmsLength)]
        for s in splitAnswer:
            print 'sending message'
            resp.message(s)
            time.sleep(2)
 
    return str(resp)

""" Main function for the server - takes input question or command, returns an answer. """
# Define the HTTP address to wait on
@app.route('/entry', methods=['POST'])
def entry():
    # Load the dictionary
    body = ujson.loads(request.data)
    
    f = open('logfile','w')
    f.write(body['question'])
    f.write('\n')
    
    # Hash the cell number
    body['cellNumber'] = hashNumber(body['cellNumber'])
    
    # Get the answer and return it.
    answer = start(body)
    
    f.write(answer)
    f.write('\n')
    f.close()
    
    return jsonify({'answer':answer})

def hashNumber(number):
    number = constantSalt + number
    hashed = hashlib.sha512(number).hexdigest()
    
    return hashed


def start(body):  
    # Get the user, or create one if one does not exist.
    cellNumber = body['cellNumber']
    currentUser = users.find_one({'cellNumber' : cellNumber})
    if (currentUser == None):
        currentUser = newUser(cellNumber)

    # Load the question text
    question = body['question'].lower()
    
    # Check for 'help'
    if (question.lower() == 'help'):
        answer =    "For a specific fact, ask a question like 'what is the population of"\
                    " London'\n" \
                    "For general information, ask for a description with 'describe "\
                    "London'\n" \
                    "If the contents is trimmed and you want more, send 'more'\n" \
                    "If an answer is of low quality, help improve the database by "\
                    "sending 'poor'"
    elif ('rate' in question):
        lastQuestion = currentUser['lastQuestion']
        
        # Establish whether the rating is of the correct form
        splitQuestion = question.split(' ')
        if not (len(splitQuestion) == 2\
        and splitQuestion[0] == 'rate'\
        and splitQuestion[1].isdigit()\
        and int(splitQuestion[1]) in range(1,6)):
            answer = "Feedback unrecognised. Send 'Rate' followed by a quality "\
                "out of 5. E.g, for a bad quality answer, send 'Rate 1' "\
                "or for a good quality answer, send 'Rate 5'"
        
        # Check that the criteria for rating the previous question is good, then process
        elif (lastQuestion['givenProperty'] != None)\
        and (lastQuestion['returnedProperty'] != None)\
        and (lastQuestion['receivedFeedback'] == False)\
        and (lastQuestion['question'] != None)\
        and (lastQuestion['answer'] != None):# TODO - this line and the line above - correct? False?!
            successful = reduceRanking(
                            lastQuestion['question'],
                            lastQuestion['answer'],
                            lastQuestion['givenProperty'],
                            lastQuestion['returnedProperty'],
                            int(splitQuestion[1]))
            if (successful):
                currentUser['lastQuestion']['receivedFeedback'] = True
                updateUser(currentUser)
                answer = "Thank you for your feedback - it has been recorded."
            else:
                answer = "Feedback unrecognised. Send 'Rate' followed by a quality "\
                    "out of 5. E.g, for a bad quality answer, send 'Rate 1' "\
                    "or for a good quality answer, send 'Rate 5'"
        else:
            answer = "Feedback already received or not expected for this question."
    else:
        # Process the natural language in the question
        parsedQuestion = nlp.nlp(question)
        if parsedQuestion['success'] == False:
            answer = 'No answer was found'
            print 'NLP Failed'
        else:
            property = parsedQuestion['property']
            placeDict = parsedQuestion['place']
            wikiPlaceName = placeDict['wikiName']
            realName = placeDict['realName']
            print 'Finding argument ', property, ' on page ', wikiPlaceName
            answer, keyUsed = sourceProcessor.findArgumentOnPage(property,wikiPlaceName)
            updateUserWithLastQuestion(currentUser, wikiPlaceName, property, keyUsed, answer)

    return answer

""" 
    Updates the user object for this user with the parameters from their last question
    in the database, allowing for their next question to be based on the state of their 
    previous question.
"""
def updateUserWithLastQuestion(user, question, givenProperty, returnedProperty, answer):
    # Set the properties, and update the object in the DB.
    user['lastQuestion']['question'] = question
    user['lastQuestion']['givenProperty'] = givenProperty
    user['lastQuestion']['returnedProperty'] = returnedProperty
    user['lastQuestion']['receivedFeedback'] = False
    user['lastQuestion']['answer'] = answer
    updateUser(user)

""" Creates a new, empty user with the input cellNumber and returns it."""
def newUser(cellNumber):
    newUserObject = {
            'cellNumber' : cellNumber,
            'lastQuestion' : {
                'text' : None,
                'givenProperty' : None,
                'returnedProperty' : None
                }
            }
    users.insert(newUserObject)
    return newUserObject
    
""" #TODO - Fill this in once 5 stars implemented.
    Returns True/False for whether successfully parsed the rating.
"""
def reduceRanking(question, answer, givenProperty, returnedProperty, fiveStarRating):
    # Check the rating is in the valid range
    fiveStarRatingInt = int(fiveStarRating)
    if (fiveStarRatingInt < 1) or (fiveStarRatingInt > 5):
        return False
    
    # Add to pastWholeQuestionRating
    pastWholeQuestionRating.insert({'question':question,
                                    'answer':answer,
                                    'rating':int(fiveStarRating)})

    # Create the dictionary that we will query the DB to identify a pre-existing ranking,
    # then query the database.
    queryDict = {
                    'givenProperty' : givenProperty,
                    'returnedProperty' : returnedProperty
                }
    currentRankingDict = wordReferencePairs.find_one(queryDict)
    
    # TODO: Potential race condition where chance may not be logged if executed on
    # multiplethreads by two users asking the same question and providing feedback at
    # the same time.
    if currentRankingDict != None:
        print 'current ranking dict:'
        print currentRankingDict['ratings']
        currentRankingDict['ratings'].append(fiveStarRatingInt)
        print 'current ranking dict, after append:'
        print currentRankingDict['ratings']
        wordReferencePairs.update(queryDict,currentRankingDict)
    else:
        # Create the empty field, then populate
        queryDict['ratings'] = [fiveStarRatingInt]
        wordReferencePairs.insert(queryDict)
    return True

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

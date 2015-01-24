import wikipedia_utils

""" 
	Returns a key-value dictionary of the extractable values from the wikipedia 
	infobox.
"""
def getInfobox(page):
	# Download the raw page content and then parse it into nested dictionaries.
	page = wikipedia_utils.GetWikipediaPage(page)
	parsedPage = wikipedia_utils.ParseTemplates(page["text"])

	# Identify the wikipedia template been used so we can key by this template below to
	# find the dictionary representing the infobox.
	templates = dict(parsedPage["templates"])
	
	infobox = None
	for key in templates.keys():
		# Look for the word 'box' in the keys. Wikipedia is not 100% on the use of the
		# term 'infobox' (for example, the "GNF Protein box" template, as of January 2015)
		# hence the more general term 'box' has to be searched for.
		if 'box' in key.lower():
			infobox = templates.get(key)
			break
	
	# If there is no infobox, log a message for debugging later.
	if (infobox == None):
		print 'there was no infobox on this page!'
	
	return infobox
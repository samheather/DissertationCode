import lxml.etree
import wikipedia_utils
	
def getInfobox(page):
	page = wikipedia_utils.GetWikipediaPage(page)
	# If unexpected block, can print the below parsedPage to view all blocks.
	parsedPage = wikipedia_utils.ParseTemplates(page["text"])

	templates = dict(parsedPage["templates"])
	
	infobox = None
	for key in templates.keys():
		if 'box' in key.lower():
			infobox = templates.get(key)
			break
	
	if (infobox == None):
		print 'there was no infobox on this page!'
	
	return infobox
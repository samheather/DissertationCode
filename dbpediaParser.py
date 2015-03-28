from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

""" 
	Parses the ontology keys from DBPedia into a key I can do a semantic comparison on.
	For example:	http://dbpedia.org/ontology/areaUrban
	 Becomes:		areaUrban
"""
def urlToKey(input):
	return input.split('/')[-1]

""" 
	Convert a page title with spaces to the format used on wikipedia (underscores
	represent spaces.  
	For example:	"Aquamole Pot"
	 Becomes:		"Aquamole_Pot"
"""
def spaceToUnderscore(input):
	return input.replace(" ", "_")

""" 
	Returns a key-value dictionary of the extractable values from the wikipedia 
	infobox.
"""
def getInfobox(page):
    # Extract properties from DBpedia using the proerty prefix dbpedia-owl and dbpprop
    firstProperties = generalGetInfoboxWithPrefix(page, 'dbpedia-owl')
    secondProperties = generalGetInfoboxWithPrefix(page, 'dbpprop')
    
    # DBPedia-owl is more reliable (processed) than dbpprop, so when combining overwrite
    # dbpprop entries with values from dbpedia-owl
    properties = {}
    properties.update(secondProperties)
    properties.update(firstProperties)
    
    return properties
	
def generalGetInfoboxWithPrefix(page, prefix):
	# Setup the query.
	sparql.setQuery("""
		select ?p ?o where {
	  dbpedia:""" + spaceToUnderscore(page) + """ ?p ?o
	  filter (strstarts(str(?p),str(""" + prefix + """:)) && 
				(LANG(?o) = "" || LANGMATCHES(LANG(?o), "en")))
	}
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	
	# Setup the empty dictionary that we will be putting our processed, simplified,
	# key-values in.
	properties = {}

	# Fill that dictionary, trimming the keys to not be in URL form.
	for result in results["results"]["bindings"]:
		key = urlToKey(result['p']['value'])
		value = result['o']['value']
		properties[key] = value
	
	return properties
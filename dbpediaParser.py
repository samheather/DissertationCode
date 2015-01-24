from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def urlToKey(input):
	return input.split('/')[-1]
	
def spaceToUnderscore(input):
	return input.replace(" ", "_")

def getInfobox(page):
	sparql.setQuery("""
		select ?p ?o where {
	  dbpedia:""" + spaceToUnderscore(page) + """ ?p ?o
	  filter (strstarts(str(?p),str(dbpedia-owl:)) && 
				(LANG(?o) = "" || LANGMATCHES(LANG(?o), "en")))
	}
	""")
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	
	# Print everything returned from DBPedia
	#print results["results"]["bindings"]

	properties = {}

	for result in results["results"]["bindings"]:
		key = urlToKey(result['p']['value'])
		value = result['o']['value']
		properties[key] = value

	# Print the dictionary of keys and values
	#for key in properties.keys():
	#	print key, ' - ', properties[key]
	
	return properties
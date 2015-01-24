from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def urlToKey(input):
	return input.split('/')[-1]

sparql.setQuery("""
    select ?p ?o where {
  dbpedia:London ?p ?o
  filter (strstarts(str(?p),str(dbpedia-owl:)) && 
  			(LANG(?o) = "" || LANGMATCHES(LANG(?o), "en")))
}
""")
print '\n\n*** JSON Example'
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
# print results["results"]["bindings"]

properties = {}

for result in results["results"]["bindings"]:
	key = urlToKey(result['p']['value'])
	value = result['o']['value']
	properties[key] = value
# 	print '\n\n\n\n'
# 	print result
# 	#["label"]["value"]

for key in properties.keys():
	print key, ' - ', properties[key]
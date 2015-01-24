from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
# sparql.setQuery("""
#     SELECT ?label
# 	WHERE { <http://dbpedia.org/resource/London>
#             dbpedia-owl:wikiPageExternalLink ?label }
# """)
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
print results["results"]["bindings"]
# for result in results["results"]["bindings"]:
#     print result["label"]["value"]


# from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
# sparql = SPARQLWrapper("http://dbpedia.org/sparql")
# sparql.setQuery("""
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     SELECT ?label
#     WHERE { <http://en.dbpedia.org/resource/Asturias> rdfs:label ?label }
# """)
# print '\n\n*** JSON Example'
# sparql.setReturnFormat(JSON)
# results = sparql.query().convert()
# for result in results["results"]["bindings"]:
#     print result["label"]["value"]
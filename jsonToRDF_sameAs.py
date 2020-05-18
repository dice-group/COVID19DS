from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, FOAF, DCTERMS, OWL
import json
import re
import sys
import os

g = Graph()
resourse = "https://covid-19ds.data.dice-research.org/resource/"
ndice = Namespace(resourse)
schema = Namespace("http://schema.org/")
vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
bibtex = Namespace("http://purl.org/net/nknouf/ns/bibtex#") 
swc = Namespace("http://data.semanticweb.org/ns/swc/ontology#")
prov = Namespace("http://www.w3.org/ns/prov#")
nif = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
its = Namespace("http://www.w3.org/2005/11/its/rdf#")
sdo = Namespace("http://salt.semanticauthoring.org/ontologies/sdo#")
bibo = Namespace("http://purl.org/ontology/bibo/")
fabio = Namespace("http://purl.org/spar/fabio/")

def handleFile(filename):
	if filename:
		with open(filename, 'r') as f:
			datastore = json.load(f)

	sections = ['Abstract', 'Introduction', 'Background',
	 'Relatedwork', 'Prelimenaries', 'Conclusion', 'Experiment', 'Discussion']
	title = datastore["metadata"]["title"]
	authors = datastore["metadata"]["authors"]
	body_text = datastore["body_text"]
	bib_entries = datastore["bib_entries"]

	dice = URIRef(resourse+datastore["paper_id"])
	linda = BNode()

	schema.author

	g.namespace_manager.bind("covid", ndice)
	g.namespace_manager.bind("schema", schema)
	g.namespace_manager.bind("dcterms", DCTERMS)
	g.namespace_manager.bind("foaf", FOAF)
	g.namespace_manager.bind("vcard", vcard)
	g.namespace_manager.bind("bibtex", bibtex)
	g.namespace_manager.bind("swc", swc)
	g.namespace_manager.bind("prov", prov)
	g.namespace_manager.bind("nif", nif)
	g.namespace_manager.bind("its", its)
	g.namespace_manager.bind("sdo", sdo)
	g.namespace_manager.bind("bibo", bibo)
	g.namespace_manager.bind("fabio", fabio)
	g.namespace_manager.bind("owl", OWL)

	if title:
		g.add( (dice, DCTERMS.title, Literal(title)) )

	# g.add( (dice, OWL.sameAs, URIRef("http://ns.inria.fr/covid19/"+datastore["paper_id"])) )
	# if 'PMC' in datastore['paper_id']:    
	#     g.add( (dice, OWL.sameAs, URIRef("https://www.ncbi.nlm.nih.gov/pmc/articles/"+datastore["paper_id"])) )
	if 'PMC' in datastore['paper_id']:
		pmc_id = datastore['paper_id'][3:]
		# g.add( (dice, OWL.sameAs, URIRef("http://pubannotation.org/docs/sourcedb/PMC/sourceid/"+pmc_id)) )
	else:
		g.add( (dice, OWL.sameAs, URIRef("https://data.linkeddatafragments.org/covid19?object=http%3A%2F%2Fidlab.github.io%2Fcovid19%23"+datastore["paper_id"])) )
		if sys.argv[2] == 'c':
			g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/Commercial/Composition/"+datastore["paper_id"]+".ttl")) )
			g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/Commercial/Composition/"+datastore["paper_id"]+".json")) )
		if sys.argv[2] == 'n':
			g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/Non-commercial/Composition/"+datastore["paper_id"]+".ttl")) )
			g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/Non-commercial/Composition/"+datastore["paper_id"]+".json")) )
		if sys.argv[2] == 'custom':
			g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/PMC/Composition/"+datastore["paper_id"]+".ttl")) )
			g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/PMC/Composition/"+datastore["paper_id"]+".json")) )
		# g.add( (dice, OWL.sameAs, URIRef("http://pubannotation.org/docs/sourcedb/CORD-19/sourceid/"+datastore["paper_id"])) )
	
dirname = sys.argv[1]
# handleFile(dirname)

dirname1 = dirname+"pdf_json"
print(dirname1)
for filename in os.listdir(dirname1):  
	handleFile(dirname1+"/"+filename)

dirname2 = dirname+"pmc_json"
print(dirname2)
for filename in os.listdir(dirname2):  
	handleFile(dirname2+"/"+filename)    

serilizedRDF = g.serialize(format='turtle')
f = open("corona_.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
f.close()
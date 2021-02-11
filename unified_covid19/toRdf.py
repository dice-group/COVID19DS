from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
import json
import re
import sys
import os
import csv
import pandas as pd
from collections import OrderedDict, defaultdict
import pyreadr


g = Graph()
ontology = "https://covid-19ds.data.dice-research.org/ontology/"
resourse = "https://covid-19ds.data.dice-research.org/resource/"
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
cvdo = Namespace("https://covid-19ds.data/ontology/")
ndice = Namespace("https://covid-19ds.data/resource/") #cvdr
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
geo = Namespace('http://www.opengis.net/ont/geosparql#')
dowl = Namespace('http://dbpedia.org/ontology/')


def handleFile():


	g.namespace_manager.bind("cvdr", ndice)
	g.namespace_manager.bind("cvdo", cvdo)
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
	g.namespace_manager.bind("virtrdf", virtrdf)
	g.namespace_manager.bind("geo", geo)
	g.namespace_manager.bind("dbpediaOwl", dowl)

	# metadata

	dice = None

	for row in reader:
		longitude = None
		latitude = None
		for heading in row:
			heading = str(heading)

			dice = URIRef(resourse+str(row['ID']))

			metapredicate = cvdo[heading.lower()]
			metaobject = Literal(row[heading],datatype=XSD.string)
			if heading == 'Longitude' or heading == 'Latitude':
			#     metapredicate = DCTERMS.issued
				metaobject = Literal(row[heading],datatype=XSD.double)

			# dbr:Berlin geo:geometry "POINT(13.383333206177 52.516666412354)"^^virtrdf:Geometry ;
			if heading == 'Longitude':
				longitude = row[heading]
			if heading == 'Latitude':
				latitude = row[heading]
			if longitude is not None and latitude is not None and longitude != '' and latitude != '':
				g.add( (dice, geo.geometry, Literal('POINT('+latitude+' '+longitude+')', datatype=virtrdf.Geometry)) )

			if heading == "ISO1_3C":
			   iso = row[heading]
			   g.add( (dice, metapredicate, cvdo[iso]) )
			   g.add( (cvdo[iso], RDF.type, cvdo.Iso) )
			   g.add( (cvdo[iso], dowl.isoCodeRegion, metaobject) )

			if heading == "Admin0":
			   adm = capitalizeWords(row[heading])
			   g.add( (dice, metapredicate, cvdo[adm]) )
			   g.add( (cvdo[adm], RDF.type, dowl.Country) )
			   g.add( (cvdo[adm], cvdo.countryName, metaobject) )
			   

			if heading == 'Population' or heading == 'Admin':
				metaobject = Literal(row[heading],datatype=XSD.nonNegativeInteger)
			
			if row[heading] != "" and heading != "Admin0" and heading != "ISO1_3C":
				g.add( (dice, RDF.type, cvdo.GeospatialData) )
				g.add( (dice, metapredicate, metaobject) )
			# the provenance
			g.add( (dice, prov.hadPrimarySource, cvdo.UnifiedCovidDataset) )
			g.add( (cvdo.UnifiedCovidDataset, RDF.type, prov.Entity) )
			# g.add( (cvdo.covid19Dataset, prov.generatedAtTime, Literal("2020-05-21T02:52:02Z",datatype=XSD.dateTime)) )
			g.add( (cvdo.UnifiedCovidDataset, prov.wasDerivedFrom, Literal("https://github.com/CSSEGISandData/COVID-19_Unified-Dataset",datatype=XSD.string)) )


	print('Csv has finished') 

	# policy

	result = pyreadr.read_r('Policy.RData')
	print(result.keys())
	policy = result["Policy"]
	# print(len(policy['ID']))
	# print(policy['ID'][0])
	for i in range(0, len(policy['ID'])):
	    dice = URIRef(resourse+str(policy['ID'][i]))
	    pol = 'Policy_'+str(policy['ID'][i])+'_'+ policy['PolicyType'][i]+'_'+str(policy['Date'][i])
	    g.add( (dice, cvdo.hasPolicy, cvdo[pol]) )
	    g.add( (cvdo[pol], RDF.type, cvdo.Policy) )
	    g.add( (cvdo[pol], cvdo.date, Literal(policy['Date'][i],datatype=XSD.date)) )
	    g.add( (cvdo[pol], cvdo.policyType, Literal(policy['PolicyType'][i],datatype=XSD.string)) )
	    if not isnan(policy['PolicyValue'][i]):
	        g.add( (cvdo[pol], cvdo.policyValue, Literal(policy['PolicyValue'][i],datatype=XSD.double)) )
	    if not isnan(policy['PolicyFlag'][i]):
	        g.add( (cvdo[pol], cvdo.policyFlag, Literal(policy['PolicyFlag'][i],datatype=XSD.boolean)) )
	    if not isnan(policy['PolicySource'][i]):
	        g.add( (cvdo[pol], cvdo.policySource, Literal(policy['PolicySource'][i],datatype=XSD.string)) )
	    if not isnan(policy['PolicyNotes'][i]):
	        g.add( (cvdo[pol], cvdo.policyNotes, Literal(policy['PolicyNotes'][i],datatype=XSD.string)) )

	# covid19
	result1 = pyreadr.read_r('COVID-19.RData')
	print(result1.keys())
	covid19data = result1["COVID19"]
	for i in range(0, len(covid19data['ID'])):
	    dice = URIRef(resourse+str(covid19data['ID'][i]))
	    pol = 'Covid19Data_'+str(covid19data['ID'][i])+'_'+ covid19data['Type'][i]+'_'+str(covid19data['Date'][i])
	    g.add( (dice, cvdo.hasCovidData, cvdo[pol]) )
	    g.add( (cvdo[pol], RDF.type, cvdo.CasesPerAgeRecord) )
	    g.add( (cvdo[pol], cvdo.date, Literal(covid19data['Date'][i],datatype=XSD.date)) )
	    g.add( (cvdo[pol], cvdo.type, Literal(covid19data['Type'][i],datatype=XSD.string)) )
	    if not isnan(covid19data['Cases'][i]):
	        g.add( (cvdo[pol], cvdo.cases, Literal(covid19data['Cases'][i],datatype=XSD.nonNegativeInteger)) )
	    if not isnan(covid19data['Cases_New'][i]):
	        g.add( (cvdo[pol], cvdo.casesNew, Literal(covid19data['Cases_New'][i],datatype=XSD.nonNegativeInteger)) )
	    if not isnan(covid19data['Age'][i]):
	        g.add( (cvdo[pol], cvdo.age, Literal(covid19data['Age'][i],datatype=XSD.string)) )
	    if not isnan(covid19data['Sex'][i]):
	        g.add( (cvdo[pol], cvdo.sex, Literal(covid19data['Sex'][i],datatype=XSD.string)) )
	    if not isnan(covid19data['Source'][i]):
	        g.add( (cvdo[pol], cvdo.source, Literal(covid19data['Source'][i],datatype=XSD.string)) )


reader = pd.read_csv('COVID-19_LUT.csv', keep_default_na=False).to_dict('records', into=OrderedDict)


def capitalizeWords(s):
  return re.sub(r'\w+', lambda m:m.group(0).capitalize(), s).replace(" ", "")

def isnan(value):
	try:
		import math
		return math.isnan(float(value))
	except:
		return False


handleFile()

serilizedRDF = g.serialize(format='turtle')
f = open("unified_covid.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
g = Graph()


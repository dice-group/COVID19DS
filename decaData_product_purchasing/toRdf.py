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
import zipcodes


g = Graph()
ontology = "https://covid-19ds.data.dice-research.org/ontology/"
resource = "https://covid-19ds.data.dice-research.org/resource/"
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
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")
ndice = Namespace("https://covid-19ds.data.dice-research.org/resource/") #cvdr
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
geo = Namespace('http://www.opengis.net/ont/geosparql#')
ctr = Namespace("https://covid-19ds.data.dice-research.org/covidProductPurchasing#")
dowl = Namespace("http://dbpedia.org/ontology/")

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
	g.namespace_manager.bind("ctrp", ctr)
	g.namespace_manager.bind("dbpediaOwl", dowl)


	dice = None

	# COVID19_INDEX_SAMPLE_2020_09_07_20200907_200000_COVID19_INDEX_RDX_2020_09_07_20200907_200000.csv
	rowNum = 0
	for row in reader:
		rowNum = rowNum +1
		for heading in row:
			heading = str(heading)

			strName = str(rowNum)
			strCamelCase = re.sub(r"_(\w)", repl, strName)+"_ProductPurchasingBehavior" 

			dice = URIRef(resource+strCamelCase)

			headingLower = heading.lower()
			strCamelCase = re.sub(r"_(\w)", repl, headingLower)
			metapredicate = cvdo[strCamelCase]
			metaobject = Literal(row[heading],datatype=XSD.string)

			if heading == 'QTY' or heading == 'UPC':
				metaobject = Literal(row[heading],datatype=XSD.integer)

			if heading == 'QTY':
				metapredicate = cvdo.quantity

			if heading == 'STORE_ZIP_CODE':
				metapredicate = dowl.postalCode
				metaobject = Literal(row[heading],datatype=XSD.integer)

				if row[heading] != "":
					zipcodeInfo = zipcodes.matching(str(row[heading]))
					# print(zipcodeInfo[0]['country'])
					# Country
					adm = zipcodeInfo[0]['country']
					g.add( (dice, cvdo.hasCountry, ndice[adm]) )
					g.add( (dice, cvdo.hasCity, Literal(zipcodeInfo[0]['city'],datatype=XSD.string)) ) # city
					g.add( (dice, cvdo.hasCounty, Literal(zipcodeInfo[0]['county'],datatype=XSD.string)) ) # county
					g.add( (dice, geo.geometry, Literal('POINT('+zipcodeInfo[0]['lat']+' '+zipcodeInfo[0]['long']+')', datatype=virtrdf.Geometry)) ) # lat lon
					g.add( (ndice[adm], RDF.type, dowl.Country) )
					g.add( (ndice[adm], RDFS.label, Literal(adm,datatype=XSD.string)) )

			if heading == 'NET_SALES' or heading == 'GROSS_SALES':
				metaobject = Literal(row[heading],datatype=XSD.float)

			if heading == "DATE":
				metaobject = Literal(row[heading],datatype=XSD.date)
			
			if row[heading] != "":
				g.add( (dice, RDF.type, cvdo.ProductPurchasing) )
				g.add( (dice, metapredicate, metaobject) )

			# the provenance
			g.add( (dice, prov.hadPrimarySource, ndice.ProductPurchasingCovidDataset) )
			g.add( (ndice.ProductPurchasingCovidDataset, RDF.type, prov.Entity) )
			g.add( (ndice.ProductPurchasingCovidDataset, prov.generatedAtTime, Literal("2021-02-22T02:52:02Z",datatype=XSD.dateTime)) )
			g.add( (ndice.ProductPurchasingCovidDataset, prov.wasDerivedFrom, Literal("http://decadata.io/",datatype=XSD.string)) )


	print('csv has finished')

reader = pd.read_csv('COVID19_INDEX_SAMPLE_2020_09_07_20200907_200000_COVID19_INDEX_RDX_2020_09_07_20200907_200000.csv', delimiter="|", keep_default_na=False).to_dict('records', into=OrderedDict)

def isnan(value):
	try:
		import math
		return math.isnan(float(value))
	except:
		return False

def repl(m):
	return m.group(1).upper()


handleFile()

serilizedRDF = g.serialize(format='turtle')
f = open("covid_product_purchasing.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
g = Graph()


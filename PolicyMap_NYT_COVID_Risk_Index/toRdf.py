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
cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")
ndice = Namespace("https://covid-19ds.data.dice-research.org/resource/") #cvdr
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
virtrdf = Namespace('http://www.openlinksw.com/schemas/virtrdf#')
geo = Namespace('http://www.opengis.net/ont/geosparql#')
cri = Namespace("https://covid-19ds.data.dice-research.org/covidRiskIndex#")


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
    g.namespace_manager.bind("crip", cri)


    # metadata

    dice = None

    # COVID_Risk_Index_Metadata.csv
    for row in reader:
        longitude = None
        latitude = None
        for heading in row:
            heading = str(heading)

            strName = str(row['column_name'])
            # snakecase to lowerCamelCase
            strCamelCase = re.sub(r"_(\w)", repl, strName) 

            dice = URIRef(cri+strCamelCase)

            headingLower = heading.lower()
            strCamelCase = re.sub(r"_(\w)", repl, headingLower)
            metapredicate = cri[strCamelCase]
            metaobject = Literal(row[heading],datatype=XSD.string)
            
            if row[heading] != "":
                g.add( (dice, RDF.type, cvdo.RiskIndexMetadata) )
                g.add( (dice, metapredicate, metaobject) )

    print('Metadata csv has finished')

    # COVID_Risk_Index_Data.csv
    for row in reader1:
        longitude = None
        latitude = None
        for heading in row:
            heading = str(heading)

            strName = str(row['geo_boundary_identifier'])
            # snakecase to lowerCamelCase
            strCamelCase = re.sub(r"_(\w)", repl, strName) 

            dice = URIRef(resourse+strCamelCase)

            headingLower = heading.lower()
            strCamelCase = re.sub(r"_(\w)", repl, headingLower)
            metapredicate = cri[strCamelCase]
            metaobject = Literal(row[heading],datatype=XSD.string)

            if heading == 'time_frame' or heading == 'index_raw':
                metaobject = Literal(row[heading],datatype=XSD.nonNegativeInteger)

            if heading == 'index_normalized' or heading == 'index_zscore' or heading == 'index_percentile':
                metaobject = Literal(row[heading],datatype=XSD.float)
            
            if row[heading] != "":
                g.add( (dice, RDF.type, cvdo.RiskIndexData) )
                g.add( (dice, metapredicate, metaobject) )

    print('Csv has finished') 


reader = pd.read_csv('COVID_Risk_Index_Metadata.csv', keep_default_na=False).to_dict('records', into=OrderedDict)
reader1 = pd.read_csv('COVID_Risk_Index_Data.csv', keep_default_na=False).to_dict('records', into=OrderedDict)

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
f = open("covid_risk_index.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
g = Graph()


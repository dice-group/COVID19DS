from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, FOAF, DCTERMS, OWL
import json
import re
import sys
import os
import csv
import pandas as pd
from collections import OrderedDict, defaultdict

g = Graph()
ontology = "https://covid-19ds.data.dice-research.org/ontology/"
resourse = "https://covid-19ds.data.dice-research.org/resource/"
# ndice = Namespace(resourse)
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

def handleFile(filename):
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)

    dice = URIRef(resourse+datastore["paper_id"]) # old
    linda = BNode()

    schema.author

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

    # metadata
    pmcid = None
    sha = None
    cord_uid = None

    for row in reader:
        cord_uid = str(row["cord_uid"])
        sha = str(row["sha"])
        if ';' in sha:
            shas = sha.split(';')
            for s in shas:
                if datastore["paper_id"] == s.strip():
                    sha = s.strip()

        if sha == datastore["paper_id"] or row['pmcid'] == datastore['paper_id']:
            if len(str(row["pmcid"])) > 3:
                pmcid = str(row["pmcid"]).lower()
                dice = URIRef(resourse+pmcid)

    for row in makg_csv_reader:
        if cord_uid == row['cord_uid']:
            if row['mag_id']:
                g.add( (dice, OWL.sameAs, URIRef("http://ma-graph.org/entity/"+row['mag_id'])) )        


reader = pd.read_csv('metadata.csv',
    names=['cord_uid','sha','source_x','title'
    ,'doi','pmcid','pubmed_id','license',
    'abstract','publish_time','authors','journal',
    'mag_id','who_covidence_id','arxiv_id',
    'pdf_json_files','pmc_json_files','url','s2_id'],
    dtype={'cord_uid':str,'sha':str,'source_x':str,'title':str
    ,'doi':str,'pmcid':str,'pubmed_id':str,'license':str,
    'abstract':str,'publish_time':str,'authors':str,'journal':str,
    'mag_id':str,'who_covidence_id':str,'arxiv_id':str,
    'pdf_json_files':str,'pmc_json_files':str,'url':str,'s2_id':str}).to_dict('records', into=OrderedDict)

makg_csv_reader = pd.read_csv('2020-06-17-CORD-UID-MappedTo-2020-06-12-MAG-ID.csv',
    names=['cord_uid','mag_id'],
    dtype={'cord_uid':str,'mag_id':str}).to_dict('records', into=OrderedDict)

def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False

dirname = sys.argv[1]
# handleFile(dirname)

dirname1 = dirname+"pdf_json"
print(dirname1)
num = 0
for filename in os.listdir(dirname1):
    print(str(num)+"/"+str(len(os.listdir(dirname1))))  
    handleFile(dirname1+"/"+filename)
    num += 1

dirname2 = dirname+"pmc_json"
print(dirname2)
num = 0
for filename in os.listdir(dirname2): 
    print(str(num)+"/"+str(len(os.listdir(dirname2))))    
    handleFile(dirname2+"/"+filename)
    num += 1   

serilizedRDF = g.serialize(format='turtle')
f = open("corona_makg.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
f.close()
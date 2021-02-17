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
import pycountry


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
ctr = Namespace("https://covid-19ds.data.dice-research.org/covidTravelRestrictions#")
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
    g.namespace_manager.bind("ctrp", ctr)
    g.namespace_manager.bind("dbpediaOwl", dowl)


    # metadata

    dice = None

    # Data WFP Coronavirus COVID-19 Travel Restrictions - COVID-19 airline restrictions information.csv
    for row in reader:
        longitude = None
        latitude = None
        for heading in row:
            heading = str(heading)

            # strName = str(row['iso3'].split(',')[0].strip())
            strName = str(row['ObjectId'])
            # snakecase to lowerCamelCase
            strCamelCase = re.sub(r"_(\w)", repl, strName)+"_AirlineRestrictions" 

            dice = URIRef(ctr+strCamelCase)

            headingLower = heading.lower()
            strCamelCase = re.sub(r"_(\w)", repl, headingLower)
            metapredicate = ctr[strCamelCase]
            metaobject = Literal(row[heading],datatype=XSD.string)

            if heading == 'X':
                longitude = row[heading]
            if heading == 'Y':
                latitude = row[heading]
            if longitude is not None and latitude is not None and longitude != '' and latitude != '':
                g.add( (dice, geo.geometry, Literal('POINT('+str(latitude)+' '+str(longitude)+')', datatype=virtrdf.Geometry)) )

            if heading == 'ObjectId':
                metaobject = Literal(row[heading],datatype=XSD.nonNegativeInteger)

            if heading == "iso3":
                iso = row[heading].split(',')
                for isoitem in iso:
                    isoitem = isoitem.strip()
                    g.add( (dice, metapredicate, cvdo[isoitem]) )
                    g.add( (cvdo[isoitem], RDF.type, cvdo.Iso) )
                    g.add( (cvdo[isoitem], cvdo.iso3, metaobject) )
                    iso2 = pycountry.countries.get(alpha_3=row[heading])
                    if iso2:
                        g.add( (cvdo[isoitem], dowl.isoCodeRegion, Literal(iso2.alpha_2,datatype=XSD.string)) )

            if heading == "adm0_name":
               adm = capitalizeWords(row[heading])
               g.add( (dice, metapredicate, cvdo[adm]) )
               g.add( (cvdo[adm], RDF.type, dowl.Country) )
               g.add( (cvdo[adm], cvdo.countryName, metaobject) )

            if heading == 'source' and "http" in row[heading]:
                metaobject = URIRef(row[heading])

            if heading == "published":
                metaobject = Literal(row[heading],datatype=XSD.date)
            
            if row[heading] != "" and heading != "X" and heading != "Y" and heading != "iso3" and heading != "adm0_name":
                g.add( (dice, RDF.type, cvdo.AirlineRestrictions) )
                g.add( (dice, metapredicate, metaobject) )

            # the provenance
            g.add( (dice, prov.hadPrimarySource, cvdo.AirlineRestrictionsCovidDataset) )
            g.add( (cvdo.AirlineRestrictionsCovidDataset, RDF.type, prov.Entity) )
            g.add( (cvdo.AirlineRestrictionsCovidDataset, prov.wasDerivedFrom, Literal("https://data.humdata.org/dataset/covid-19-global-travel-restrictions-and-airline-information",datatype=XSD.string)) )

    print('COVID-19 airline restrictions information has finished')

    #Data WFP Coronavirus COVID-19 Travel Restrictions - COVID-19 travel restrictions by country.csv
    for row in reader1:
        longitude = None
        latitude = None
        for heading in row:
            heading = str(heading)

            # strName = str(row['iso3'].split(',')[0].strip())
            strName = str(row['ObjectId'])
            # snakecase to lowerCamelCase
            strCamelCase = re.sub(r"_(\w)", repl, strName)+"_TravelRestrictions"

            dice = URIRef(ctr+strCamelCase)

            headingLower = heading.lower()
            strCamelCase = re.sub(r"_(\w)", repl, headingLower)
            metapredicate = ctr[strCamelCase]
            metaobject = Literal(row[heading],datatype=XSD.string)

            if heading == 'X':
                longitude = row[heading]
            if heading == 'Y':
                latitude = row[heading]
            if longitude is not None and latitude is not None and longitude != '' and latitude != '':
                g.add( (dice, geo.geometry, Literal('POINT('+str(latitude)+' '+str(longitude)+')', datatype=virtrdf.Geometry)) )

            if heading == 'ObjectId':
                metaobject = Literal(row[heading],datatype=XSD.nonNegativeInteger)

            if heading == "iso3":
               iso = row[heading].split(',')
               for isoitem in iso:
                   isoitem = isoitem.strip()
                   g.add( (dice, metapredicate, cvdo[isoitem]) )
                   g.add( (cvdo[isoitem], RDF.type, cvdo.Iso) )
                   g.add( (cvdo[isoitem], cvdo.iso3, metaobject) )
                   iso2 = pycountry.countries.get(alpha_3=row[heading])
                   if iso2:
                        g.add( (cvdo[isoitem], dowl.isoCodeRegion, Literal(iso2.alpha_2,datatype=XSD.string)) )


            if heading == "adm0_name":
               adm = capitalizeWords(row[heading])
               g.add( (dice, metapredicate, cvdo[adm]) )
               g.add( (cvdo[adm], RDF.type, dowl.Country) )
               g.add( (cvdo[adm], cvdo.countryName, metaobject) )

            if heading == 'source' and "http" in row[heading]:
                metaobject = URIRef(row[heading])

            if heading == "published":
                metaobject = Literal(row[heading],datatype=XSD.date)
            
            if row[heading] != "" and heading != "X" and heading != "Y" and heading != "iso3" and heading != "adm0_name":
                g.add( (dice, RDF.type, cvdo.TravelRestrictions) )
                g.add( (dice, metapredicate, metaobject) )

            # the provenance
            g.add( (dice, prov.hadPrimarySource, cvdo.AirlineRestrictionsCovidDataset) )
            g.add( (cvdo.AirlineRestrictionsCovidDataset, RDF.type, prov.Entity) )
            g.add( (cvdo.AirlineRestrictionsCovidDataset, prov.wasDerivedFrom, Literal("https://data.humdata.org/dataset/covid-19-global-travel-restrictions-and-airline-information",datatype=XSD.string)) )


    print('COVID-19 travel restrictions by country has finished')

reader = pd.read_csv('Data WFP Coronavirus COVID-19 Travel Restrictions - COVID-19 airline restrictions information.csv', keep_default_na=False).to_dict('records', into=OrderedDict)
reader1 = pd.read_csv('Data WFP Coronavirus COVID-19 Travel Restrictions - COVID-19 travel restrictions by country.csv', keep_default_na=False).to_dict('records', into=OrderedDict)

def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False

def repl(m):
    return m.group(1).upper()

def capitalizeWords(s):
  return re.sub(r'\w+', lambda m:m.group(0).capitalize(), s).replace(" ", "")


handleFile()

serilizedRDF = g.serialize(format='turtle')
f = open("covid_travel_restrictions.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
g = Graph()


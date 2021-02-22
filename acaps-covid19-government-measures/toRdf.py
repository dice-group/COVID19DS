#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 01:58:37 2021

@author: humera
"""
import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, FOAF, RDFS, OWL, DCTERMS, SKOS, XSD
import pandas as pd
import urllib.parse
import urllib
import re


g = Graph()



cvdo = Namespace("https://covid-19ds.data.dice-research.org/ontology/")  #(for Object)
cvdr = Namespace("https://covid-19ds.data.dice-research.org/resource/")  #(for Subject/Resource)
lgdo = Namespace("http://linkedgeodata.org/page/ontology/")
vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
dbpprop = Namespace("http://dbpedia.org/property/")
dbpediaOwl = Namespace("http://dbpedia.org/ontology/")
dcmi = Namespace("http://purl.org/dc/terms/")
earth = Namespace("http://linked.earth/ontology/")
prov = Namespace("http://www.w3.org/ns/prov#")
dowl = Namespace("http://dbpedia.org/ontology/")



g.namespace_manager.bind("cvdo", cvdo)
g.namespace_manager.bind("cvdr", cvdr)
g.namespace_manager.bind("lgdo", lgdo)
g.namespace_manager.bind("vcard", vcard)
g.namespace_manager.bind("dbpediaOwl",dbpediaOwl)
g.namespace_manager.bind("dcmi",dcmi)
g.namespace_manager.bind("earth",earth)
g.namespace_manager.bind("prov", prov)
g.namespace_manager.bind("dbpediaOwl", dowl)


# Load the CSV data as a pandas Dataframe.
xls = pd.ExcelFile('acaps_covid19_government_measures_dataset.xlsx')
csv_data = pd.read_excel(xls, 'Dataset')

print(csv_data.head())
print(csv_data.count())
print(csv_data["MEASURE"])

# Here I deal with spaces (" ") in the data. I replace them with "_" so that URI's become valid.
#csv_data = csv_data.replace(to_replace=" ", value="_", regex=True)
csv_data["COUNTRY"]=csv_data["COUNTRY"].str.replace(" ","_",regex=True)
csv_data["REGION"]=csv_data["REGION"].str.replace(" ","_",regex=True)
csv_data["ADMIN_LEVEL_NAME"]=csv_data["ADMIN_LEVEL_NAME"].str.replace(" ","_",regex=True)
#csv_data["SOURCE"]=csv_data["SOURCE"].str.replace(" ","_",regex=True)
#csv_data["SOURCE"]=csv_data["SOURCE"].str.replace("\""," ",regex=True)
# Here I mark all missing/empty data as "unknown". This makes it easy to delete triples containing this later.
csv_data = csv_data.fillna("unknown")

# Loop through the CSV data, and then make RDF triples.
for index, row in csv_data.iterrows():
     dice = str(row['ID'])+'_GovMeasure'
     print(dice)
     iso = row["ISO"]
     g.add( (cvdr[dice], cvdo.hasISO, cvdo[iso]) )
     g.add( (cvdo[iso], RDF.type, cvdo.Iso) )
     g.add( (cvdo[iso], dowl.isoCodeRegion, Literal(row["ISO"], datatype=XSD.string)) )
     # g.add((URIRef(cvdr[str(row["ID"])]), cvdo.hasISO, Literal(row["ISO"], datatype=XSD.string)))
     
     g.add((URIRef(cvdr[dice]), RDF.type, cvdo.Covid19Measure))
     #g.add((cvdr.ISO, RDF.type, lgdo.Feature))
     
     g.add((URIRef(cvdr[dice]), cvdo.hasCountry, URIRef(cvdr[row["COUNTRY"]])))
    
     g.add((URIRef(cvdr[str(row["COUNTRY"])]), RDFS.label, Literal(row["COUNTRY"], lang='en')))
     g.add((URIRef(cvdr[str(row["COUNTRY"])]), RDF.type, dbpediaOwl.Country))

     g.add((URIRef(cvdr[dice]), cvdo.hasRegion, Literal(row["REGION"], datatype=XSD.string)))     

     g.add((URIRef(cvdr[dice]), cvdo.hasAdminLevelName, Literal(row['ADMIN_LEVEL_NAME'], datatype=XSD.string)))
     
     g.add((URIRef(cvdr[dice]),  cvdo.hasPCODE, Literal(row['PCODE'], datatype=XSD.integer)))
     
     g.add((URIRef(cvdr[dice]), cvdo.hasLogType, Literal(row['LOG_TYPE'], datatype=XSD.string)))
     
     g.add((URIRef(cvdr[dice]), dbpediaOwl.category, Literal(row['CATEGORY'], datatype=XSD.string)))
     
     g.add((URIRef(cvdr[dice]), cvdo.hasMeasure, Literal(row['MEASURE'], datatype=XSD.string)))
     
     g.add((URIRef(cvdr[dice]), cvdo.targetedPopGroup, Literal(row['TARGETED_POP_GROUP'], datatype=XSD.string)))
     g.add((URIRef(cvdr[dice]), RDFS.comment, Literal(row['COMMENTS'], datatype=XSD.string)))
     g.add((URIRef(cvdr[dice]), cvdo.nonCompliance, Literal(row['NON_COMPLIANCE'], datatype=XSD.string)))
     g.add((URIRef(cvdr[dice]), dcmi.date, Literal(row['DATE_IMPLEMENTED'], datatype=XSD.date)))
     
     g.add((URIRef(cvdr[dice]), cvdo.hasSource, Literal(row['SOURCE'],lang='en')))
     g.add((URIRef(cvdr[dice]), cvdo.publisher , Literal(row['SOURCE_TYPE'], datatype=XSD.string)))
     
     row['LINK'] = row['LINK'].strip()
     if " " in row['LINK']:
          row['LINK']=urllib.parse.quote_plus(row['LINK'])

     g.add((URIRef(cvdr[dice]), cvdo.hasSourceLink, URIRef(row['LINK'])))
     g.add((URIRef(cvdr[dice]), cvdo.entryDate, Literal(row['ENTRY_DATE'], datatype=XSD.date)))
     
     # row['Alternative source']=urllib.parse.quote_plus(row['Alternative source'])
     altSources = None

     altSources = re.split(';| \+| AND| and', row['Alternative source'])


     if altSources:
          for a in altSources:
               # if a != 'and' and a != 'AND' and a != '':
               g.add((URIRef(cvdr[dice]), cvdo.alternativeSource, URIRef(a.strip().replace(" ", ""))))
     else:
          if "http" in row['Alternative source']:
               g.add((URIRef(cvdr[dice]), cvdo.alternativeSource, URIRef(row['Alternative source'].strip())))
          else:
               g.add((URIRef(cvdr[dice]), cvdo.alternativeSource, Literal(row['Alternative source'], datatype=XSD.string))) 

     # the provenance
     g.add( (cvdr[dice], prov.hadPrimarySource, cvdo.GovMeasuresCovidDataset) )
     g.add( (cvdo.GovMeasuresCovidDataset, RDF.type, prov.Entity) )
     g.add( (cvdo.GovMeasuresCovidDataset, prov.wasDerivedFrom, Literal("https://data.humdata.org/dataset/acaps-covid19-government-measures-dataset",datatype=XSD.string)) )

     
     # Remove the triples that I marked as "unknown"
     g.remove((None, None, URIRef("unknown")))
     g.remove((None, None, Literal("unknown",datatype=XSD.string)))
     g.remove((None, None, Literal("unknown",datatype=XSD.integer)))
     g.remove((None, None, Literal("unknown",datatype=XSD.date)))
     
g.serialize(destination='acaps.ttl', format='ttl')

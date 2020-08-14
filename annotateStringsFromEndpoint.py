# -*- coding: utf-8 -*-
"""
Created on Mon May 11 19:15:42 2020

@author: Jan
"""

import requests
from nif import NIFDocument as NIFDocument
from nif import NIFContent as NIFContent
import spacy
import os
import sys
nlp = spacy.load("en_ner_bionlp13cg_md")
nlp.max_length=3000000
out_file=open("corona.ttl",'w', encoding='utf-8')
out_file.write('@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n @prefix nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> .\n@prefix nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> .\n@prefix itsrdf: <http://www.w3.org/2005/11/its/rdf#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .')
def add_nif_entities(reference_context,base_uri,entities,doc):
    for ent in entities:
        if "http" not in ent.text: 
            nif_content=NIFContent.NIFContent(base_uri+'#'+str(ent.start_char)+','+str(ent.end_char))
            nif_content.set_begin_index(ent.start_char)
            nif_content.set_end_index(ent.end_char)
            nif_content.set_reference_context(reference_context)
            nif_content.set_anchor_of(ent.text)
            doc.addContent(nif_content)
    return doc

                               
#webservice for entity recognition
def annotate_nif_string(string,base_uri):
    nlpdoc = nlp(string.replace('"',"'"))
    if len(nlpdoc.ents)>0:
        docnew=NIFDocument.NIFDocument()
        uri=base_uri
        nif_content=NIFContent.NIFContent(uri)
        nif_content.is_string=string
        nif_content.begin_index=0
        nif_content.end_index=len(string)
        docnew.addContent(nif_content)
        nlpdoc = nlp(string)
        docnew=add_nif_entities(base_uri,base_uri,nlpdoc.ents,docnew)
        ag_string=docnew.get_nif_string()
        #get links from agdsitis
        ag_string=docnew.get_nif_string()
        #get links from agdsitis
        resp=requests.post("http://localhost:8090/",ag_string.encode('utf-8'))
            
        if resp.status_code == 200:
            ag_doc=NIFDocument.nifStringToNifDocument(resp.content.decode())
            cont =ag_doc.get_without_head()
            for en in cont:
                # print(en.get_NIF_String().replace('#',"/"))
                en.set_reference_context(base_uri)
                out_file.write(en.get_NIF_String().replace('#',"/"))
        else: 
            print(resp)
        resp.close()
        


# filepath = 'cornoncommercial0.txt'
# with open(filepath, encoding='utf-8') as fp:
#    line = fp.readline()
#    cnt = 1
#   # while cnt<8199:
#   #     line = fp.readline()
#   #     print(cnt)
#   #     cnt=cnt+1
#    while line:
#        dat=line.split(" ::: ")
#        annotate_nif_string(dat[1].replace("\n",""),dat[0])
#        line = fp.readline()
#        cnt=cnt+1
#        print(cnt)       
#page=391810
#stop=False
#while not stop:    
#    url = 'https://covid-19ds.data.dice-research.org/sparql'
#    query = 'select distinct ?d ?s {?d a <http://salt.semanticauthoring.org/ontologies/sdo#Section>. ?d <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#isString> ?s} LIMIT 10 OFFSET '+str(page)
#    r = requests.get(url, params = {'format': 'json', 'query': query})
#    data = r.json()
#    if len(data['results']['bindings'])<10:
#           stop=True
#    print(page)
#    for item in data['results']['bindings']:
        #annotate_nif_string(item['s']["value"],item['d']["value"])
#        out_file.write(item['d']["value"]+" ::: "+item['s']["value"].replace("\n"," ")+"\n")
    #for item in data['results']['bindings']:
    #    print(item['d']["value"]+" "+item['s']["value"])
#    page=page+10
#out_file.close()        

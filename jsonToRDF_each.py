from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import RDF, FOAF, DCTERMS
import json
import re
import sys
import os

g = Graph()
resourse = "https://data.dice-research.org/covid19/resource#"
ndice = Namespace(resourse)
schema = Namespace("http://schema.org/")
vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
bibtex = Namespace("http://purl.org/net/nknouf/ns/bibtex#") 
swc = Namespace("http://data.semanticweb.org/ns/swc/ontology#")
prov = Namespace("http://www.w3.org/ns/prov#")

def addAuthors(authors, subject):
    for a in authors:
        name = re.sub("[^A-Za-z]", "", (a['first'] + a['last']))  
        g.add( (subject, bibtex.hasAuthor, ndice[name]) )
        g.add( (ndice[name], RDF.type, FOAF.Person) )
        g.add( (ndice[name], FOAF.firstName, Literal(a['first'])) )
        g.add( (ndice[name], FOAF.lastName, Literal(a['last'])) )
        if len(a['middle']) != 0:
            g.add( (ndice[name], ndice.middleName, Literal(a['middle'][0])) )
        if len(a['suffix']) != 0:
            g.add( (ndice[name], ndice.hasSuffix, Literal(a['suffix'])) )
        if 'email' in a and len(a['email']) != 0:
            g.add( (ndice[name], FOAF.mbox, Literal(a['email'])) )
        if 'affiliation' in a and len(a['affiliation']) != 0:
            aff = a['affiliation']
            if len(aff['laboratory']) != 0:
                g.add( (ndice[name], ndice.hasLab, Literal(aff['laboratory'])) )
            if len(aff['institution']) != 0:
                g.add( (ndice[name], bibtex.hasInstitution, Literal(aff['institution'])) )
            if len(aff['location']) != 0:
                location = aff['location']
                if 'settlement' in location and len(location['settlement']) != 0:    
                    g.add( (ndice[name], ndice.hasSettlement, Literal(location['settlement'])) )
                if 'region' in location and len(location['region']) != 0:    
                    g.add( (ndice[name], ndice.hasRegion, Literal(location['region'])) )
                if 'country' in location and len(location['country']) != 0:    
                    g.add( (ndice[name], vcard['country-name'], Literal(location['country'])) )

def addBibEntries(bib_entries, sectionObject, datastore, link):
    curLink = str(link).strip()
    bibId = datastore["paper_id"] + 'B' + curLink
    g.add( (sectionObject, ndice.relatedBibEntry, ndice[bibId]) )
    if 'BIBREF'+curLink in bib_entries:
        bibTitle = bib_entries['BIBREF'+curLink]['title']
        g.add( (ndice[bibId], RDF.type , bibtex.Entry) )
        g.add( (ndice[bibId], bibtex.hasTitle , Literal(bibTitle)) )
        bibAuthors = bib_entries['BIBREF'+curLink]['authors']
        addAuthors(bibAuthors, ndice[bibId])

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

    # the provenance
    g.add( (dice, prov.hadPrimarySource, ndice.commercialUseDataset) )
    g.add( (ndice.commercialUseDataset, RDF.type, prov.Entity) )
    g.add( (ndice.commercialUseDataset, prov.wasDerivedFrom, Literal('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/comm_use_subset.tar.gz')) )
    #

    g.add( (dice, DCTERMS.title, Literal(title)) )
    g.add( (dice, RDF.type, swc.Paper) )
    addAuthors(authors, dice)

    for body in body_text:
        sectionName = None
        for s in sections:
            if s.lower() in body['section'].lower():
                sectionName = s 
        if sectionName == None:
            sectionName = 'Body'              
        section = 'has' + sectionName
        sectionObject = Namespace(resourse+datastore["paper_id"]+"_")
        g.add( (dice, ndice[section], sectionObject[sectionName]) )
        text = body['text']
        g.add( (sectionObject[sectionName], schema.text, Literal(text)) )
        # [1] [1, 2, 3]
        r1 = re.findall(r"\[([0-9 ,]+)\]", text)
        # [1-5]
        r2 = re.findall(r"\[([0-9]+)\-([0-9]+)\]",text)
        for l in r1:
            l2 = re.split(",| ", l)
            for link in l2:
                addBibEntries(bib_entries, sectionObject[sectionName], datastore, link)

        for rangeLinks in r2:
            start = rangeLinks[0]
            end = rangeLinks[1]
            for link in range(int(start), int(end)):
                addBibEntries(bib_entries, sectionObject[sectionName], datastore, link)

        serilizedRDF = g.serialize(format='turtle')       
        ff.write(serilizedRDF.decode("utf-8"))

filename = sys.argv[1]
ff = open("corona.ttl", "a") 
handleFile(filename)
ff.close() 


# dirname = sys.argv[1]
# ff = open("corona.ttl", "a")
# for filename in os.listdir(dirname):  
#     handleFile(dirname+"/"+filename)

# ff.close()    

# serilizedRDF = g.serialize(format='turtle')
# f = open("corona.ttl", "w")
# f.write(serilizedRDF.decode("utf-8"))
# f.close()
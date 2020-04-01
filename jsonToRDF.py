from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
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
nif = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
its = Namespace("http://www.w3.org/2005/11/its/rdf#")

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

def addBibEntries(bib_entries, sectionObject, datastore, link, bibId):
    curLink = str(link).strip()
    # bibId = datastore["paper_id"] + 'B' + curLink
    g.add( (sectionObject, ndice.relatedBibEntry, ndice[bibId]) )
    if 'BIBREF'+curLink in bib_entries:
        bibTitle = bib_entries['BIBREF'+curLink]['title']
        g.add( (ndice[bibId], RDF.type , bibtex.Entry) )
        g.add( (ndice[bibId], bibtex.hasTitle , Literal(bibTitle)) )
        bibAuthors = bib_entries['BIBREF'+curLink]['authors']
        addAuthors(bibAuthors, ndice[bibId])

def addRefs(typeOfSpans, ref_spans, sectionName, sectionObject, datastore, refDict):
    for ref_span in ref_spans:

        ref_span_label = re.sub("[^A-Za-z0-9]", "", ref_span['text'])
        if typeOfSpans == 'cite':
            bibId = datastore["paper_id"] + '_' + sectionName + '_' + 'B' + ref_span_label

            if bibId in refDict:
                refDict[bibId] += 1
            else:
                refDict[bibId] = 1
            numRefLabel = refDict[bibId]
            bibId += '_' + str(numRefLabel)

            addBibEntries(datastore['bib_entries'], sectionObject[sectionName], datastore, ref_span_label, bibId)
            refName = ndice[bibId]
            g.add( (refName, nif.beginIndex, Literal(ref_span['start'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.endIndex, Literal(ref_span['end'],datatype=XSD.nonNegativeInteger)) )
        else:
            section_with_ref = sectionName + '_' + ref_span_label
            if section_with_ref in refDict:
                refDict[section_with_ref] += 1
            else:
                refDict[section_with_ref] = 1
            numLabel = refDict[section_with_ref]
            ref_span_with_num_label = ref_span_label + "_" + str(numLabel)
            ref = sectionName + '_' + ref_span_with_num_label
            refName = sectionObject[ref]
            refName2 = sectionObject[ref_span_with_num_label]

            g.add( (refName, RDF.type, nif.Phrase) )
            g.add( (refName, nif.anchorOf, Literal(ref_span['text'])) )
            g.add( (refName, nif.beginIndex, Literal(ref_span['start'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.endIndex, Literal(ref_span['end'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.referenceContext, sectionObject[sectionName]) )
            
            g.add( (refName, its.taIdentRef, ndice[refName2]) )
            if "fig" in ref_span_label.lower():
                typeOfRefFrom = "Figure"  
            else:
                typeOfRefFrom = "Table"
            typeOfRef = sectionObject[typeOfRefFrom]
            g.add( (refName2, RDF.type, typeOfRef) )

            ref_id = ref_span['ref_id']
            if ref_id:
                if typeOfSpans == 'cite':
                    refId = datastore['bib_entries']
                    refTitle = refId[ref_id]['title']
                else:    
                    # ref
                    refId = datastore['ref_entries']
                    refTitle = refId[ref_id]['text']
                    g.add( (refName2, bibtex.hasType,  Literal(refId[ref_id]['type'])) )
                
                g.add( (refName2, bibtex.hasTitle,  Literal(refTitle)) )
            

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

    # the provenance
    g.add( (dice, prov.hadPrimarySource, ndice.commercialUseDataset) )

    if sys.argv[2] == 'n':
        g.add( (ndice.nonCommercialUseDataset, RDF.type, prov.Entity) )
        g.add( (ndice.nonCommercialUseDataset, prov.wasDerivedFrom, Literal('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/noncomm_use_subset.tar.gz')) )
    else:
        g.add( (ndice.commercialUseDataset, RDF.type, prov.Entity) )
        g.add( (ndice.commercialUseDataset, prov.wasDerivedFrom, Literal('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/comm_use_subset.tar.gz')) )
    
    #
    if not title:
        g.add( (dice, DCTERMS.title, Literal(title)) )
    g.add( (dice, RDF.type, swc.Paper) )
    addAuthors(authors, dice)

    refDict = {}
    bodyNum = 1
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
        ref_spans = body['ref_spans']

        if  sectionName == 'Body':
            # sectionName = sectionName+str(bodyNum)
            # g.add( (dice, ndice[section], sectionObject[sectionName]) )
            g.add( (sectionObject[sectionName], bibtex.hasTitle, Literal(body['section'])) )
            g.add( (sectionObject[sectionName], nif.isString, Literal(text)) )
            bodyNum += 1

        else:
            # g.add( (dice, ndice[section], sectionObject[sectionName]) )
            g.add( (sectionObject[sectionName], schema.text, Literal(text)) )

        addRefs("ref", ref_spans, sectionName, sectionObject, datastore, refDict);
        addRefs("cite", body['cite_spans'], sectionName, sectionObject, datastore, refDict);
        

dirname = sys.argv[1]
handleFile(dirname)
# for filename in os.listdir(dirname):  
#     handleFile(dirname+"/"+filename)

serilizedRDF = g.serialize(format='turtle')
f = open("corona.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
f.close()
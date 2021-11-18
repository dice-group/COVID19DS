from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, DCTERMS, OWL
import json
import re
import sys
import os
import csv
import pandas as pd
from collections import OrderedDict, defaultdict
import annotateStringsFromEndpoint
from multiprocessing import Pool

pool = Pool(processes=4)

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
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
dbo = Namespace("https://dbpedia.org/ontology/")

def addAuthors(authors, subject):
    for a in authors:
        name = re.sub("[^A-Za-z]", "", (a['first'].lower() + a['last']))
        if name:
            name = name[0].lower()+name[1:]  
        g.add( (subject, bibtex.hasAuthor, ndice[name]) )
        g.add( (ndice[name], RDF.type, FOAF.Person) )
        g.add( (ndice[name], RDF.type, URIRef('http://ma-graph.org/class/Author')) )
        g.add( (ndice[name], FOAF.firstName, Literal(a['first'],datatype=XSD.string)) )
        g.add( (ndice[name], FOAF.lastName, Literal(a['last'],datatype=XSD.string)) )
        if len(a['middle']) != 0:
            g.add( (ndice[name], cvdo.middleName, Literal(a['middle'][0],datatype=XSD.string)) )
        if len(a['suffix']) != 0:
            g.add( (ndice[name], cvdo.hasSuffix, Literal(a['suffix'],datatype=XSD.string)) )
        if 'email' in a and a['email'] is not None and len(a['email']) != 0:
            g.add( (ndice[name], FOAF.mbox, Literal(a['email'],datatype=XSD.string)) )
        if 'affiliation' in a and len(a['affiliation']) != 0:
            aff = a['affiliation']
            if len(aff['laboratory']) != 0:
                g.add( (ndice[name], cvdo.hasLab, Literal(aff['laboratory'],datatype=XSD.string)) )
            if len(aff['institution']) != 0:
                inst = re.sub("[^A-Za-z0-9]", "", aff['institution'])
                g.add( (ndice[name], bibtex.hasInstitution, ndice[inst]) )
                g.add( (ndice[inst], RDF.type, dbo.EducationalInstitution) )
                g.add( (ndice[inst], RDFS.label, Literal(aff['institution'],datatype=XSD.string)) )
            if len(aff['location']) != 0:
                location = aff['location']
                if 'settlement' in location and len(location['settlement']) != 0:    
                    g.add( (ndice[name], cvdo.hasSettlement, Literal(location['settlement'],datatype=XSD.string)) )
                if 'region' in location and len(location['region']) != 0:    
                    g.add( (ndice[name], cvdo.hasRegion, Literal(location['region'],datatype=XSD.string)) )
                if 'country' in location and len(location['country']) != 0:    
                    g.add( (ndice[name], vcard['country-name'], Literal(location['country'],datatype=XSD.string)) )

def addBibEntries(bib_entries, sectionObject, sectionOntology, datastore, link, bibId):
    curLink = str(link).strip()
    if 'BIBREF'+curLink in bib_entries:

        bib_entry = bib_entries['BIBREF'+curLink]
        g.add( (sectionObject[bibId], RDF.type , bibtex.Entry) )
        if bib_entry['title']:
            g.add( (sectionObject[bibId], bibtex.hasTitle , Literal(bib_entry['title'],datatype=XSD.string)) )
        if bib_entry['year']:
            g.add( (sectionObject[bibId], bibtex.hasYear , Literal(bib_entry['year'],datatype=XSD.nonNegativeInteger)) )
        if bib_entry['venue']:
            g.add( (sectionObject[bibId], schema.EventVenue , Literal(bib_entry['venue'],datatype=XSD.string)) )
        if bib_entry['volume'] and bib_entry['volume'].isnumeric():
            g.add( (sectionObject[bibId], bibtex.hasVolume , Literal(bib_entry['volume'],datatype=XSD.nonNegativeInteger)) )
        if bib_entry['issn']:
            g.add( (sectionObject[bibId], bibtex.hasISSN , Literal(bib_entry['issn'],datatype=XSD.string)) )
        if bib_entry['pages']:
            g.add( (sectionObject[bibId], bibtex.Inbook , Literal(bib_entry['pages'],datatype=XSD.string)) )
        if 'DOI' in bib_entry['other_ids'] and bib_entry['other_ids']['DOI']:
            g.add( (sectionObject[bibId], bibo.doi , Literal(bib_entry['other_ids']['DOI'][0].replace(' ', ''),datatype=XSD.string)) )
        # if bib_entry['other_ids']:
            # print(bib_entry['other_ids'])

        bibAuthors = bib_entry['authors']
        addAuthors(bibAuthors, sectionObject[bibId])

def addRefs(typeOfSpans, ref_spans, sectionName, sectionObject, sectionOntology, datastore, refDict, refSectionDict):
    for ref_span in ref_spans:
        # print(ref_span)
        if 'text' in ref_span:
            ref_span_text = ref_span['text']
        else:
            ref_span_text = ref_span['mention']    
        ref_span_label = re.sub("[^A-Za-z0-9]", "", ref_span_text)
        if typeOfSpans == 'cite':
            bibId = 'B' + ref_span_label

            if bibId in refSectionDict:
                refSectionDict[bibId] += 1
            else:
                refSectionDict[bibId] = 1
            numRefLabel = refSectionDict[bibId]
            bibId += '_' + str(numRefLabel)

            addBibEntries(datastore['bib_entries'], sectionObject, sectionOntology, datastore, ref_span_label, bibId)
            refName = sectionObject[sectionName+'_'+bibId]
            g.add( (refName, RDF.type, nif.Phrase) )
            g.add( (refName, nif.anchorOf, Literal(ref_span_label,datatype=XSD.string)) )
            g.add( (refName, nif.beginIndex, Literal(ref_span['start'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.endIndex, Literal(ref_span['end'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.referenceContext, sectionObject[sectionName]) )
            g.add( (refName, its.taIdentRef, sectionObject[bibId]) )
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
            g.add( (refName, nif.anchorOf, Literal(ref_span_label,datatype=XSD.string)) )
            g.add( (refName, nif.beginIndex, Literal(ref_span['start'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.endIndex, Literal(ref_span['end'],datatype=XSD.nonNegativeInteger)) )
            g.add( (refName, nif.referenceContext, sectionObject[sectionName]) )
            
            g.add( (refName, its.taIdentRef, refName2) )
            if "fig" in ref_span_label.lower():
                typeOfRefFrom = sdo.Figure
                # "Figure"  
            else:
                typeOfRefFrom = sdo.Table
                # "Table"
            typeOfRef = typeOfRefFrom
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
                
                g.add( (refName2, bibtex.hasTitle,  Literal(refTitle.strip().replace("\n",""),datatype=XSD.string)) )
            

def handleFile(filename):
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)

    sections = ['Abstract', 'Introduction', 'Background',
     'RelatedWork', 'Preliminaries', 'Conclusion', 'Experiment', 'Discussion']
    title = datastore["metadata"]["title"]
    authors = datastore["metadata"]["authors"]
    body_text = datastore["body_text"]
    bib_entries = datastore["bib_entries"]

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
    g.namespace_manager.bind("dbo", dbo)

    # metadata
    pmcid = None
    sha = None
    cord_uid = None

    for row in reader:
        # print(row['sha'])
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
            for heading in row:
                heading = str(heading)
                if heading != 'abstract' and heading != 'authors' and heading != 'pdf_json_files' and heading != 'pmc_json_files' and len(heading) != 0:
                    
                    if '_' in heading:
                        pos = heading.find('_')
                        capitalLetter = heading[pos+1].upper()
                        h = heading[0:pos]+capitalLetter+heading[pos+2:]

                    metapredicate = cvdo[h]
                    metaobject = Literal(row[heading],datatype=XSD.string)
                    if heading == 'doi':
                        metapredicate = bibo.doi
                    if heading == 'journal':
                        metapredicate = bibtex.hasJournal
                    if heading == 'license':
                        metapredicate = DCTERMS.license
                    if heading == 'title':
                        metapredicate = DCTERMS.title
                    if heading == 'pubmed_id':
                        metapredicate = bibo.pmid
                    if heading == 'pmcid':
                        metapredicate = fabio.hasPubMedCentralId
                    if heading == 'sha':
                        metapredicate = FOAF.sha1
                    if heading == 'publish_time':
                        metapredicate = DCTERMS.issued
                        metaobject = Literal(row[heading],datatype=XSD.date)
                    if heading == 'url':
                        urls = str(row[heading])
                        metaobject = None
                        metapredicate = schema.url         
                        if ';' in urls:
                            urls = urls.split(';')
                            for u in urls:
                                metaobject = URIRef(u.strip())
                        else:
                            metaobject = URIRef(urls)
                        if not isnan(urls):
                            g.add( (dice, metapredicate, metaobject) )
                    
                    if not isnan(row[heading]) and heading != 'url':   
                        g.add( (dice, metapredicate, metaobject) )

    # print('Csv has finished')  
    for row in makg_csv_reader:
        if cord_uid == row['cord_uid']:
            if row['mag_id']:
                g.add( (dice, OWL.sameAs, URIRef("http://ma-graph.org/entity/"+row['mag_id'])) )        
                  

    # sameAs linking
    if pmcid:
        arr = pmcid.split(";")
        for item in arr:
            item = item.strip()
            g.add( (dice, OWL.sameAs, URIRef("http://ns.inria.fr/covid19/"+item)) )
            g.add( (dice, OWL.sameAs, URIRef("https://www.ncbi.nlm.nih.gov/pmc/articles/"+item)) )
    if sha:
        arr = sha.split(";")
        for item in arr:
            item = item.strip()
            g.add( (dice, OWL.sameAs, URIRef("http://ns.inria.fr/covid19/"+item)) )    
            g.add( (dice, OWL.sameAs, URIRef("http://pubannotation.org/docs/sourcedb/CORD-19/sourceid/"+item)) )
            g.add( (dice, OWL.sameAs, URIRef("https://data.linkeddatafragments.org/covid19?object=http%3A%2F%2Fidlab.github.io%2Fcovid19%23"+item)) )
            g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/PMC/Composition/"+item+".ttl")) )
            g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/PMC/Composition/"+item+".json")) )


    # the provenance
    g.add( (dice, prov.hadPrimarySource, ndice.cord19Dataset) )
    g.add( (ndice.cord19Dataset, RDF.type, prov.Entity) )
    g.add( (ndice.cord19Dataset, prov.generatedAtTime, Literal("2020-05-21T02:52:02Z",datatype=XSD.dateTime)) )
    g.add( (ndice.cord19Dataset, prov.wasDerivedFrom, Literal("https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/document_parses.tar.gz",datatype=XSD.string)) )
  
    #
    if title:
        g.add( (dice, DCTERMS.title, Literal(title.strip().replace("\n",""),datatype=XSD.string)) )
    g.add( (dice, RDF.type, swc.Paper) )
    g.add( (dice, RDF.type, fabio.ResearchPaper) )
    g.add( (dice, RDF.type, bibo.AcademicArticle) )
    g.add( (dice, RDF.type, schema.ScholarlyArticle) )
    addAuthors(authors, dice)

    # abstract

    refDict = {}
    refSectionDict = {}
    bodyNum = 1
    
    if pmcid:
        sectionObject = Namespace(resourse+pmcid+"_")
        sectionOntology = Namespace(ontology+pmcid+"_")
    else:
        sectionObject = Namespace(resourse+datastore["paper_id"]+"_")
        sectionOntology = Namespace(ontology+datastore["paper_id"]+"_")

    if 'abstract' in datastore and datastore['abstract'] is not None and len(datastore['abstract']) != 0:
        abstract = datastore['abstract'][0]
        
        g.add( (dice, cvdo['hasAbstract'], sectionObject['Abstract']) )
        s1 = sectionObject['Section'+str(bodyNum)]
        
        pool.apply_async(annotateStringsFromEndpoint.annotate_nif_string, [str(abstract['text']).replace("\n",""),str(s1)]);
        # annotateStringsFromEndpoint.annotate_nif_string(str(abstract['text']).replace("\n",""),str(s1));
        g.add( (sectionObject['Abstract'], cvdo.hasSection, s1) )
        g.add( (sectionObject['Abstract'], RDF.type, cvdo['PaperAbstract']) )
        g.add( (s1, RDF.type, sdo.Section) )
        g.add( (s1, bibtex.hasTitle, Literal(abstract['section'].strip().replace("\n",""),datatype=XSD.string)) )
        g.add( (s1, nif.isString, Literal(abstract['text'].strip().replace("\n",""),datatype=XSD.string)) )
        addRefs("ref", abstract['ref_spans'], abstract['section'], sectionObject, sectionOntology, datastore, refDict, refSectionDict);
        addRefs("cite", abstract['cite_spans'], abstract['section'], sectionObject, sectionOntology, datastore, refDict, refSectionDict);
        bodyNum += 1

    # body_text
    
    for body in body_text:
        sectionName = None
        refSectionDict = {}
        for s in sections:
            if s.lower() in body['section'].lower():
                sectionName = s 
        if sectionName == None:
            sectionName = 'Body'              
        section = 'has' + sectionName
        g.add( (dice, cvdo[section], sectionObject[sectionName]) )
        text = body['text']
        ref_spans = body['ref_spans']

        s1 = sectionObject['Section'+str(bodyNum)]
        pool.apply_async(annotateStringsFromEndpoint.annotate_nif_string, [str(text).replace("\n",""),str(s1)]);
        # annotateStringsFromEndpoint.annotate_nif_string(str(text).replace("\n",""),str(s1));
        g.add( (sectionObject[sectionName], cvdo.hasSection, s1) )
        sectionClass = 'Paper' + sectionName
        g.add( (sectionObject[sectionName], RDF.type, cvdo[sectionClass]) )
        g.add( (s1, RDF.type, sdo.Section) )
        g.add( (s1, bibtex.hasTitle, Literal(body['section'].strip().replace("\n",""),datatype=XSD.string)) )
        g.add( (s1, nif.isString, Literal(text.strip().replace("\n",""),datatype=XSD.string)) )
        sectionName = 'Section'+str(bodyNum)
        bodyNum += 1

        addRefs("ref", ref_spans, sectionName, sectionObject, sectionOntology, datastore, refDict, refSectionDict);
        addRefs("cite", body['cite_spans'], sectionName, sectionObject, sectionOntology, datastore, refDict, refSectionDict);
        

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

chunks = None
maxAmountOfFilesForOneIteration = 10000
if len(os.listdir(dirname1)) > maxAmountOfFilesForOneIteration:
    data = os.listdir(dirname1)
    chunks = [data[x:x+maxAmountOfFilesForOneIteration] for x in range(0, len(data), maxAmountOfFilesForOneIteration)]
print("chunks: "+str(len(chunks)))

for idx,chunk in enumerate(chunks):
    for filename in chunk:
        print(str(num)+"/"+str(len(chunk))+" chunk: "+str(idx))  
        handleFile(dirname1+"/"+filename)
        num += 1

    serilizedRDF = g.serialize(format='turtle')
    f = open("corona.ttl", "a")
    f.write(serilizedRDF.decode("utf-8"))
    g = Graph()

dirname2 = dirname+"pmc_json"
print(dirname2)
num = 0
chunks = None
if len(os.listdir(dirname2)) > maxAmountOfFilesForOneIteration:
    data = os.listdir(dirname2)
    chunks = [data[x:x+maxAmountOfFilesForOneIteration] for x in range(0, len(data), maxAmountOfFilesForOneIteration)]
print("chunks: "+str(len(chunks)))

for idx,chunk in enumerate(chunks):
    for filename in chunk:
        print(str(num)+"/"+str(len(chunk))+" chunk: "+str(idx))  
        handleFile(dirname2+"/"+filename)
        num += 1

    serilizedRDF = g.serialize(format='turtle')
    f = open("corona.ttl", "a")
    f.write(serilizedRDF.decode("utf-8"))
    g = Graph()

f.close()

pool.close()
pool.join()
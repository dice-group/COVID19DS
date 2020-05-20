from rdflib import URIRef, BNode, Literal, Namespace, Graph, XSD
from rdflib.namespace import RDF, RDFS, FOAF, DCTERMS, OWL
import json
import re
import sys
import os

g = Graph()
resourse = "https://covid-19ds.data.dice-research.org/resource/"
ndice = Namespace(resourse)
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
        if 'email' in a and a['email'] is not None and len(a['email']) != 0:
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
    if 'BIBREF'+curLink in bib_entries:

        bib_entry = bib_entries['BIBREF'+curLink]
        g.add( (sectionObject[bibId], RDF.type , bibtex.Entry) )
        if bib_entry['title']:
            g.add( (sectionObject[bibId], bibtex.hasTitle , Literal(bib_entry['title'])) )
        if bib_entry['year']:
            g.add( (sectionObject[bibId], bibtex.hasYear , Literal(bib_entry['year'])) )
        if bib_entry['venue']:
            g.add( (sectionObject[bibId], schema.EventVenue , Literal(bib_entry['venue'])) )
        if bib_entry['volume']:
            g.add( (sectionObject[bibId], bibtex.hasVolume , Literal(bib_entry['volume'])) )
        if bib_entry['issn']:
            g.add( (sectionObject[bibId], bibtex.hasISSN , Literal(bib_entry['issn'])) )
        if bib_entry['pages']:
            g.add( (sectionObject[bibId], bibtex.Inbook , Literal(bib_entry['pages'])) )
        if 'DOI' in bib_entry['other_ids'] and bib_entry['other_ids']['DOI']:
            g.add( (sectionObject[bibId], bibo.doi , Literal(bib_entry['other_ids']['DOI'][0])) )
        # if bib_entry['other_ids']:
            # print(bib_entry['other_ids'])

        bibAuthors = bib_entry['authors']
        addAuthors(bibAuthors, sectionObject[bibId])

def addRefs(typeOfSpans, ref_spans, sectionName, sectionObject, datastore, refDict, refSectionDict):
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

            addBibEntries(datastore['bib_entries'], sectionObject, datastore, ref_span_label, bibId)
            refName = sectionObject[sectionName+'_'+bibId]
            g.add( (refName, RDF.type, nif.Phrase) )
            g.add( (refName, nif.anchorOf, Literal(ref_span_label)) )
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
            g.add( (refName, nif.anchorOf, Literal(ref_span_label)) )
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
                
                g.add( (refName2, bibtex.hasTitle,  Literal(refTitle)) )
            

def handleFile(filename):
    if filename:
        with open(filename, 'r') as f:
            datastore = json.load(f)

    sections = ['Abstract', 'Introduction', 'Background',
     'Relatedwork', 'Preliminaries', 'Conclusion', 'Experiment', 'Discussion']
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
    g.namespace_manager.bind("sdo", sdo)
    g.namespace_manager.bind("bibo", bibo)
    g.namespace_manager.bind("fabio", fabio)
    g.namespace_manager.bind("owl", OWL)

    # sameAs linking
    g.add( (dice, OWL.sameAs, URIRef("http://ns.inria.fr/covid19/"+datastore["paper_id"])) )
    if 'PMC' in datastore['paper_id']:    
        g.add( (dice, OWL.sameAs, URIRef("https://www.ncbi.nlm.nih.gov/pmc/articles/"+datastore["paper_id"])) )
    if 'PMC' in datastore['paper_id']:
        pmc_id = datastore['paper_id'][3:]
        # g.add( (dice, OWL.sameAs, URIRef("http://pubannotation.org/docs/sourcedb/PMC/sourceid/"+pmc_id)) )
    else:
        g.add( (dice, OWL.sameAs, URIRef("http://pubannotation.org/docs/sourcedb/CORD-19/sourceid/"+datastore["paper_id"])) )
        g.add( (dice, OWL.sameAs, URIRef("https://data.linkeddatafragments.org/covid19?object=http%3A%2F%2Fidlab.github.io%2Fcovid19%23"+datastore["paper_id"])) )
        if sys.argv[2] == 'c':
            g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/Commercial/Composition/"+datastore["paper_id"]+".ttl")) )
            g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/Commercial/Composition/"+datastore["paper_id"]+".json")) )
        if sys.argv[2] == 'n':
            g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/Non-commercial/Composition/"+datastore["paper_id"]+".ttl")) )
            g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/Non-commercial/Composition/"+datastore["paper_id"]+".json")) )
        if sys.argv[2] == 'custom':
            g.add( (dice, OWL.sameAs, URIRef("https://fhircat.org/cord-19/fhir/PMC/Composition/"+datastore["paper_id"]+".ttl")) )
            g.add( (dice, RDFS.seeAlso, URIRef("https://fhircat.org/cord-19/fhir/PMC/Composition/"+datastore["paper_id"]+".json")) )
    # the provenance
    

    if sys.argv[2] == 'n':
        g.add( (dice, prov.hadPrimarySource, ndice.nonCommercialUseDataset) )
        g.add( (ndice.nonCommercialUseDataset, RDF.type, prov.Entity) )
        g.add( (ndice.nonCommercialUseDataset, prov.wasDerivedFrom, Literal('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/noncomm_use_subset.tar.gz')) )
    if sys.argv[2] == 'c':
        g.add( (dice, prov.hadPrimarySource, ndice.commercialUseDataset) )
        g.add( (ndice.commercialUseDataset, RDF.type, prov.Entity) )
        g.add( (ndice.commercialUseDataset, prov.wasDerivedFrom, Literal('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/comm_use_subset.tar.gz')) )
    if sys.argv[2] == 'custom':
        g.add( (dice, prov.hadPrimarySource, ndice.customLicenseDataset) )
        g.add( (ndice.customLicenseDataset, RDF.type, prov.Entity) )
        g.add( (ndice.customLicenseDataset, prov.wasDerivedFrom, Literal('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/custom_license.tar.gz')) )
  
    #
    if title:
        g.add( (dice, DCTERMS.title, Literal(title)) )
    g.add( (dice, RDF.type, swc.Paper) )
    g.add( (dice, RDF.type, fabio.ResearchPaper) )
    g.add( (dice, RDF.type, bibo.AcademicArticle) )
    g.add( (dice, RDF.type, schema.ScholarlyArticle) )
    g.add( (dice, DCTERMS.license, URIRef('https://www.gnu.org/licenses/gpl-3.0.html')) )
    g.add( (URIRef('https://www.gnu.org/licenses/gpl-3.0.html'), RDFS.label, Literal('GNU Affero General Public License v3.0')) )
    addAuthors(authors, dice)

    # abstract

    refDict = {}
    refSectionDict = {}
    bodyNum = 1
    abstract = datastore['abstract'][0]
    sectionObject = Namespace(resourse+datastore["paper_id"]+"_")
    g.add( (dice, ndice['hasAbstract'], sectionObject['Abstract']) )
    s1 = sectionObject['Section'+str(bodyNum)]
    g.add( (sectionObject['Abstract'], ndice.hasSection, s1) )
    g.add( (s1, RDF.type, sdo.Section) )
    g.add( (s1, bibtex.hasTitle, Literal(abstract['section'])) )
    g.add( (s1, nif.isString, Literal(abstract['text'])) )
    addRefs("ref", abstract['ref_spans'], abstract['section'], sectionObject, datastore, refDict, refSectionDict);
    addRefs("cite", abstract['cite_spans'], abstract['section'], sectionObject, datastore, refDict, refSectionDict);
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
        sectionObject = Namespace(resourse+datastore["paper_id"]+"_")
        g.add( (dice, ndice[section], sectionObject[sectionName]) )
        text = body['text']
        ref_spans = body['ref_spans']

        s1 = sectionObject['Section'+str(bodyNum)]
        g.add( (sectionObject[sectionName], ndice.hasSection, s1) )
        g.add( (s1, RDF.type, sdo.Section) )
        g.add( (s1, bibtex.hasTitle, Literal(body['section'])) )
        g.add( (s1, nif.isString, Literal(text)) )
        sectionName = 'Section'+str(bodyNum)
        bodyNum += 1

        addRefs("ref", ref_spans, sectionName, sectionObject, datastore, refDict, refSectionDict);
        addRefs("cite", body['cite_spans'], sectionName, sectionObject, datastore, refDict, refSectionDict);
        

dirname = sys.argv[1]
# handleFile(dirname)

dirname1 = dirname+"pdf_json"
print(dirname1)
for filename in os.listdir(dirname1):  
    handleFile(dirname1+"/"+filename)

dirname2 = dirname+"pmc_json"
print(dirname2)
for filename in os.listdir(dirname2):  
    handleFile(dirname2+"/"+filename)    

serilizedRDF = g.serialize(format='turtle')
f = open("corona.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
f.close()
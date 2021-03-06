# COVID19DS
The RDF file generation is based on papers related to the COVID-19 and coronavirus-related research.

To run the generation of the dataset, the following command is used:
```
python3 jsonToRDF.py folderName/
```

folderName/ - the name of the folder that contains the subset of papers. Each paper is represented as a single JSON object.

To run the full generation of the dataset including linking:
```
./runCovid19dsGeneration
```

To download the new version from CORD19 and run generation with linking:
```
./getAndRun yyyy-mm-dd
```
yyyy-mm-dd - the date of the version that you would like to get from CORD19


To run entity recognition on generated ttl file:
```
./ERfromttlScript filename
```
filename - the path to the ttl file

Here in the repository there are several scripts from different datasets connected to the Covid19. Everything that is relared to the main dataset is in the root folder. Scripts for other datasets are stored in the folders according to their names. Now there are avalable scripts for the following datasets:
- unified_covid19 (https://github.com/CSSEGISandData/COVID-19_Unified-Dataset)     
- acaps-covid19-government-measures (https://data.humdata.org/m/dataset/acaps-covid19-government-measures-dataset)
- PolicyMap_NYT_COVID_Risk_Index (https://www.policymap.com/download-covid19-data/)
- covid-19-global-travel-restrictions-and-airline-information (https://data.humdata.org/dataset/covid-19-global-travel-restrictions-and-airline-information)

## Namespaces

Below we use the following namespaces:

```turtle
@prefix bibo: <http://purl.org/ontology/bibo/> .
@prefix bibtex: <http://purl.org/net/nknouf/ns/bibtex#> .
@prefix covid: <https://covid-19ds.data.dice-research.org/resource/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix fabio: <http://purl.org/spar/fabio/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix its: <http://www.w3.org/2005/11/its/rdf#> .
@prefix nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <http://schema.org/> .
@prefix sdo: <http://salt.semanticauthoring.org/ontologies/sdo#> .
@prefix swc: <http://data.semanticweb.org/ns/swc/ontology#> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

## Article metadata
The base URI is represented as 'https://covid-19ds.data.dice-research.org/resource/paperId' where paperId is the paper_id from the JSON file of the paper.

The following items are included as an article metadata:
- authors (`bibtex:hasAuthor`)
- primary source (`prov:hadPrimarySource`)

Moreover, the article metadata includes the linking to different parts of the paper (body, discussion, introduction). There are predefined names of sections: 'Abstract', 'Introduction', 'Background', 'Relatedwork', 'Prelimenaries', 'Conclusion', 'Experiment', 'Discussion'. If the section name is different from predefined names than the section name 'Body' is chosen.
For example:
- `covid:hasBody covid:PMC1616946_Body`
- `covid:hasDiscussion covid:PMC1616946_Discussion`
- `covid:hasIntroduction covid:PMC1616946_Introduction`.

Here is an example of article metadata:
```turtle
covid:PMC1616946 a swc:Paper,
        bibo:AcademicArticle,
        fabio:ResearchPaper,
        schema:ScholarlyArticle ;
    bibtex:hasAuthor covid:ChristineAnderson,
        covid:ClarkHenderson,
        covid:MichaelHoward ;
    prov:hadPrimarySource covid:nonCommercialUseDataset ;
    covid:hasBody covid:PMC1616946_Body ;
    covid:hasDiscussion covid:PMC1616946_Discussion ;
    covid:hasIntroduction covid:PMC1616946_Introduction .
```

## Provenance information
The provenance information performs the information about the source of the paper. There are 3 available types of source subsets that are handled by the current script:
- `covid:nonCommercialUseDataset`
- `covid:commercialUseDataset`
- `covid:customLicenseDataset`.

The example of the provenance information is shown below:
```turtle
covid:nonCommercialUseDataset a prov:Entity ;
    prov:wasDerivedFrom "https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/noncomm_use_subset.tar.gz" .
```
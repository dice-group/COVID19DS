# CovidPubKG: A FAIR Knowledge Graph of COVID-19 Publications
The rapid generation of large amounts of information about the coronavirus SARS-COV-2 and the disease COVID-19 makes it increasingly difficult to gain a comprehensive overview of current insights related to the disease. With this work, we aim to support the rapid access to a comprehensive data source on COVID-19 targeted especially at researchers. Our knowledge graph, CovidPubKG, an RDF knowledge graph of scientific publications, abides by the Linked Data and FAIR principles. The base dataset for the extraction is CORD-19, a dataset of COVID-19-related publications, which is updated regularly. Consequently, CovidPubKG is updated biweekly. Our generation pipeline applies named entity recognition, entity linking and link discovery approaches to the original data. The current version of CovidPubKG contains 268,108,670 triples and is linked to 9 other datasets by over 1 million links. In our use case studies, we demonstrate the usefulness of our knowledge graph for different applications. CovidPubKG is publicly available under the Creative Commons Attribution 4.0 International license.

## CovidPubKG Ontology

![alt text](https://github.com/dice-group/COVID19DS/blob/main/uml.png?raw=true)

## Knowledge Graph Generation

The RDF file generation is based on papers related to the COVID-19 and coronavirus-related research.

To run the generation of the knowledge graph, the following command is used:
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
- decaData_product_purchasing (http://decadata.io/) 

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

## How to cite

```bibtex
@article{nature_sd_patents,
  added-at = {2022-02-03T12:41:23.000+0100},
  author = {Pestryakova, Svetlana and Vollmers, Daniel and Sherif, Mohamed Ahmed and Heindorf, Stefan and Saleem, Muhammad and Moussallem, Diego and Ngomo, Axel-Cyrille Ngonga},
  biburl = {https://www.bibsonomy.org/bibtex/24a08be85abeb4df17f52d22c7c390af5/dice-research},
  interhash = {b6e1b27c01a29f3f93c8dd78603dabcc},
  intrahash = {4a08be85abeb4df17f52d22c7c390af5},
  journal = {Scientific Data},
  keywords = {2022 Heindorf Moussallem Saleem Svetlana Vollmers dice knowgraphs limes ngonga sherif simba},
  publisher = {Nature Publishing Group},
  timestamp = {2022-02-03T12:41:23.000+0100},
  title = {{CovidPubGraph: A FAIR Knowledge Graph of COVID-19 Publications}},
  url = {https://papers.dice-research.org/2022/NSDJ_CovidPubGraph/public.pdf},
  year = 2022
}


```

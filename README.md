# COVID19DS

To run the generation ot the dataset, the following command is used: 
```
python3 jsonToRDF.py folderName/ option
```

options:
c - commercial use subset
n - non-commercial use subset 
custom - custom license subset

## Namespaces

Below we use the following namespaces:

```turtle
@prefix bibtex: <http://purl.org/net/nknouf/ns/bibtex#> .
@prefix covid: <https://data.dice-research.org/covid19/resource#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
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
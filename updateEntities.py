#!/usr/bin/env python3
import csv
import fileinput
import re
import sys
from rdflib import URIRef, Graph



sha_to_pmcid = {}
with open('metadata.csv', newline='') as file:
    reader = csv.DictReader(file)
    for item in reader:
        if item['sha'] and item['pmcid']:
            for sha in item['sha'].split(';'):
                sha_to_pmcid[sha] = item['pmcid']

missing = set()
def subst(match):
    sha = match.group(2)
    if sha in sha_to_pmcid:
        return '<' + match.group(1) + sha_to_pmcid[sha] + match.group(3) + '>'
    else:
        missing.add(match.group(0))
        return match.group(0)

r = re.compile('<(https://covid-19ds\.data\.dice-research\.org/resource/)([a-f0-9]{40})([^>]*)>')
f = open("ent.ttl", "w")
for line in fileinput.input():
    f.write(r.sub(subst, line))
f.close()

g = Graph()
g.parse("ent.ttl", format="ttl")

for m in missing:
    uri = URIRef(m[1:-1])
    g.remove((uri, None, None))

serilizedRDF = g.serialize(format='turtle')
f = open("ent2.ttl", "w")
f.write(serilizedRDF.decode("utf-8"))
f.close()
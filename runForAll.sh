#!/bin/bash
unlink corona.ttl
FILES=$(pwd)/comm_use_subset/*
for f in $FILES
do
	python3 jsonToRDF.py $f
done
delete from DB.DBA.LOAD_LIST;
 commit work; 
 ld_add('/rdfData/corona.ttl','https://covid-19ds.data.dice-research.org/resource/corona');
 rdf_loader_run();
 checkpoint;

delete from DB.DBA.LOAD_LIST;
 commit work; 
 ld_add('/rdfData/authors_sameAs.nt','https://covid-19ds.data.dice-research.org/resource/corona');
 rdf_loader_run();
 checkpoint;

delete from DB.DBA.LOAD_LIST;
 commit work; 
 ld_add('/rdfData/bibEntries_hasPublication.nt','https://covid-19ds.data.dice-research.org/resource/corona');
 rdf_loader_run();
 checkpoint;

delete from DB.DBA.LOAD_LIST;
 commit work; 
 ld_add('/rdfData/publication_sameAs.nt','https://covid-19ds.data.dice-research.org/resource/corona');
 rdf_loader_run();
 checkpoint;
 exit;
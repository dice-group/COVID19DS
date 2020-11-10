import java.io.*;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;



import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;



import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPFile;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field.Store;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.openrdf.model.Statement;
import org.openrdf.model.URI;
import org.openrdf.rio.RDFHandlerException;
import org.openrdf.rio.RDFParseException;
import org.openrdf.rio.RDFParser;
import org.openrdf.rio.helpers.RDFHandlerBase;
import org.openrdf.rio.nquads.NQuadsParser;
import org.openrdf.rio.ntriples.NTriplesParser;
import org.openrdf.rio.turtle.TurtleParser;
import org.slf4j.LoggerFactory;

import info.aduna.io.FileUtil;

    public class TripleIndexCreator {
        private static org.slf4j.Logger log = LoggerFactory.getLogger(TripleIndexCreator.class);

        public static final String N_TRIPLES = "NTriples";
        public static final String TTL = "ttl";
        public static final String NT = "nt";
        public static final String TSV = "tsv";
        private WriteIndex writeIndex;

        public static void main(String args[]) {
            System.out.println("File is running");

            try {

                Properties prop = new Properties();
                InputStream input = new FileInputStream("src/main/resources/config/indexer.properties");
                prop.load(input);


                String folder = prop.getProperty("folderWithTTLFiles");
                List<File> listOfFiles = new ArrayList<File>();
                for (File file : new File(folder).listFiles()) {
                    if (file.getName().endsWith("ttl")||file.getName().endsWith("nq")||file.getName().endsWith("nt")) {
                        listOfFiles.add(file);
                    }
                }
                System.out.println("Size"+listOfFiles);


                String envBaseUri = System.getenv("AGDISTIS_BASE_URI");
                String baseURI = envBaseUri != null ? envBaseUri : prop.getProperty("baseURI");
                String envIndexType = System.getenv("useElasticsearch");
                TripleIndexCreator ic = new TripleIndexCreator();
                ic.createIndex(listOfFiles, baseURI);
                //ic.writeIndexFromFTP(baseURI,useElasticsearch);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        public void createIndex(List<File> files, String baseURI) {
            try {

                writeIndex = new WriteIndex();

                //writeIndex =new WriteLuceneIndex(idxDirectory);
                writeIndex.createIndex();
                for (File file : files) {
                    String type = FileUtil.getFileExtension(file.getName());
                    if (type.equals(TTL))
                        indexTTLFile(file, baseURI,TTL);
                    else
                        indexTTLFile(file, baseURI,NT);
                }
                writeIndex.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }


        private void indexTTLFile(File file, String baseURI,String type)
                throws RDFParseException, RDFHandlerException, FileNotFoundException, IOException {
            System.out.println("Start parsing: " + file);
            RDFParser parser;
            parser=new NQuadsParser();
            parser.setStopAtFirstError(false);
            TripleIndexCreator.OnlineStatementHandler osh = new TripleIndexCreator.OnlineStatementHandler();
            parser.setRDFHandler(osh);
            if (baseURI == null) {
                parser.parse(new FileReader(file), "");
            } else {
                parser.parse(new FileReader(file), baseURI);
            }
            System.out.println("Finished parsing: " + file);
        }

        private void indexTSVFile(File file) throws IOException {
            System.out.println("Start parsing: " + file);
            BufferedReader br = new BufferedReader(new FileReader(file));
            while (br.ready()) {
                String[] line = br.readLine().split("\t");
                String subject = line[0];
                for (int i = 1; i < line.length; ++i) {
                    String object = line[i];
                    Document doc = new Document();
                    doc.add(new StringField("subject", subject, Store.YES));
                    doc.add(new StringField("predicate",
                            "http://www.w3.org/2004/02/skos/core#altLabel", Store.YES));
                    doc.add(new TextField("object_literal", object, Store.YES));
                    writeIndex.indexDocument(subject,"http://www.w3.org/2004/02/skos/core#altLabel",object,false);
                }
            }
            br.close();
            System.out.println("Finished parsing: " + file);
        }


        private class OnlineStatementHandler extends RDFHandlerBase {
            @Override
            public void handleStatement(Statement st) {
                String subject = st.getSubject().stringValue();
                String predicate = st.getPredicate().stringValue();
                String object = st.getObject().stringValue();
                System.out.println("new");
                System.out.println(subject);
                System.out.println(predicate);
                System.out.println(object);
                try{
                    if(predicate.equals("http://purl.org/dc/terms/title")){
                        String[]objects=object.split(";");
                        for(int i=0;i<objects.length;i++) {
                            String input=objects[i];
                            if(objects[i].contains(" ("))
                                input=objects[i].substring(0, objects[i].indexOf(" ("));
                            if(input.length()>0)
                            writeIndex.indexDocument(subject, predicate, input, false);
                        }
                    }
                    else writeIndex.indexDocument(subject, predicate, object, st.getObject() instanceof URI);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }




import org.openrdf.model.Statement;
import org.openrdf.model.URI;
import org.openrdf.rio.RDFHandlerException;
import org.openrdf.rio.RDFParseException;
import org.openrdf.rio.RDFParser;
import org.openrdf.rio.helpers.RDFHandlerBase;
import org.openrdf.rio.nquads.NQuadsParser;
import org.openrdf.rio.turtle.TurtleParser;

import java.io.*;

public class FilterTriples {


    static FileWriter myWriter;

    public static void main(String[]args){
        String filename=args[0];
//"/home/user/Documents/work/COVID19DS/version_2020-10-31/corona.ttl";
        FilterTriples f=new FilterTriples();
        try {
            myWriter= new FileWriter("coronaAnnotations.txt");
            f.index(new File(filename));

            myWriter.close();
        } catch (RDFParseException e) {
            e.printStackTrace();
        } catch (RDFHandlerException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    private void index(File file)
            throws RDFParseException, RDFHandlerException, FileNotFoundException, IOException {
        RDFParser parser;
        parser=new TurtleParser();
        parser.setStopAtFirstError(false);
        FilterTriples.OnlineStatementHandler osh = new FilterTriples.OnlineStatementHandler();
        parser.setRDFHandler(osh);
        parser.parse(new FileReader(file), "");

    }
    private class OnlineStatementHandler extends RDFHandlerBase {
        @Override
        public void handleStatement(Statement st) {
            String subject = st.getSubject().stringValue();
            String predicate = st.getPredicate().stringValue();
            String object = st.getObject().stringValue();
            System.out.println(subject+" "+predicate);
            try{
                if(predicate.equals("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#isString")) {
                    System.out.println(subject + ":::" + object.replace("\n", " "));
                    myWriter.write(subject + " ::: " + object.replace("\n", " ")+"\n");
                }

            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}

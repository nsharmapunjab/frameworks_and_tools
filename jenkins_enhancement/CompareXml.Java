import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.File;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.PrintWriter;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;
import org.xml.sax.InputSource;

public class CompareXml
{
    public static String readFile(String path, Charset encoding) throws IOException
    {
        byte[] encoded = Files.readAllBytes(Paths.get(path));
        return new String(encoded, encoding);
    }

    public static String stripNonValidXMLCharacters(String in)
    {
        StringBuffer out = new StringBuffer(); // Used to hold the output.
        char current; // Used to reference the current character.

        if (in == null || ("".equals(in)))
            return ""; // vacancy test.
        for (int i = 0; i < in.length(); i++) {
            current = in.charAt(i); // NOTE: No IndexOutOfBoundsException caught here; it should not happen.
            if ((current == 0x9) || (current == 0xA) || (current == 0xD) || ((current >= 0x20) && (current <= 0xD7FF))
                || ((current >= 0xE000) && (current <= 0xFFFD)) || ((current >= 0x10000) && (current <= 0x10FFFF)))
                out.append(current);
        }
        return out.toString();
    }


    public static HashMap parse_xml(String xml_file) throws ParserConfigurationException, SAXException, IOException {
        HashMap xml_data = new HashMap();
        System.out.println(xml_file);

        String content = readFile(xml_file, Charset.defaultCharset());
        content = stripNonValidXMLCharacters(content);
        PrintWriter out = new PrintWriter(xml_file);
        out.println(content);
        out.close();
        InputStream inputStream= new FileInputStream(xml_file);
        Reader reader = new InputStreamReader(inputStream,"UTF-8");
        InputSource is = new InputSource(reader);
        is.setEncoding("UTF-8");

        DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
        DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
        Document doc = dBuilder.parse(is);

        //File fXmlFile = new File(xml_file);
        //DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
        //DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
        //Document doc = dBuilder.parse(new InpputSource(new InputStreamReader(fXmlFile, "UTF-8")));
        doc.getDocumentElement().normalize();
        System.out.println("Root element :" + doc.getDocumentElement().getNodeName());
        NodeList nList = doc.getElementsByTagName("method");
        System.out.println("----------------------------");
        for (int temp = 0; temp < nList.getLength(); temp++) {
            Node nNode = nList.item(temp);
            if (nNode.getNodeType() == Node.ELEMENT_NODE) {
                Element eElement = (Element) nNode;
                String[] parts = eElement.getAttribute("signature").split("@");
                xml_data.put(temp, parts[0]);
            }
        }
        return xml_data;
    }

    public static void compare_xmls() throws Exception
    {

            String currentBuild = System.getProperty("CURRENT_BUILD");
            String previousBuild = "";
            int prev_build_test = Integer.parseInt(currentBuild);
            prev_build_test = prev_build_test - 1;
            previousBuild = String.valueOf(prev_build_test);
            System.out.println("Current Build : "+currentBuild);
            System.out.println("Previous Build : "+previousBuild);

            String path = "/var/lib/jenkins/jobs//builds//testng/testng-results.xml";

            String currentPath = path.replace("", currentBuild);
            String prevPath = path.replace("", previousBuild);


            HashMap xml_data = new HashMap();
            HashMap xml_data2 = new HashMap();
            HashMap final_xml_data = new HashMap();
            HashMap diff_xml_data = new HashMap();
            String usrdir = System.getProperty("user.dir");

            xml_data = parse_xml(currentPath);
            xml_data2 = parse_xml(prevPath);

            System.out.println("First Hashmap Size : "+ xml_data.size());
            System.out.println("Second Hashmap Size : "+ xml_data2.size());

            int temp1=0;
            for (int itr = 0; itr < xml_data.size(); itr++) {
                if (!xml_data2.containsValue(xml_data.get(itr))) {
                    final_xml_data.put(temp1, xml_data.get(itr));
                    temp1 = temp1 +1;
                }
            }
            System.out.println("Newly Added TCs Hashmap Size : "+ final_xml_data.size());

            int temp2 = 0;
            for( String s : xml_data2.values())
            {
                if (!xml_data.containsValue(s)) {
                    diff_xml_data.put(temp2, s);
                    temp2 = temp2 + 1;
                }
            }

            System.out.println("Deleted TCs Hashmap Size : " + diff_xml_data.size());

            HashSet final_xml_data_values = new HashSet();
            final_xml_data_values.addAll(final_xml_data.values());

            HashSet diff_xml_data_values = new HashSet();
            diff_xml_data_values.addAll(diff_xml_data.values());

            System.out.println("Newly Added Test-Cases Below : ");
            for (String str : final_xml_data_values){
                System.out.println("NEW-TC : " + str);
            }

            System.out.println("\n\n********************************");
            for (String str : diff_xml_data_values){
                System.out.println("DEL-TC : " + str);
            }

            System.out.println("Deleted Test-Cases Below : ");

    }
        public static void main(String args[]) throws Exception {
                compare_xmls();
    }

}

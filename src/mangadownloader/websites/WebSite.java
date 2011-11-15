package mangadownloader.websites;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URL;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

/**
 * Abstract class to model common elements of a website
 * @author wasser
 */
public abstract class WebSite implements ControlInterface {

    protected String siteURL = new String();
    protected Elements links = new Elements();

    /**
     * Returns all links without any kind of treatment from the website
     * @return raw list of links 
     */
    public Elements getLinksFromWebSite() throws IOException {
        Document doc = Jsoup.connect(siteURL).get();
        return doc.select("a[href]");
    }

    /**
     * General purposes downloading method
     */
    @Override
    public void startDownloading() {
        BufferedInputStream is;
        FileOutputStream os;
        int counter = 1;

        for (Element link : links) {
            System.out.println("Getting Link " + counter);
            try {
                is = new BufferedInputStream(new URL(link.attr("abs:href")).openStream());
                os = new FileOutputStream("File_" + counter++);
                BufferedOutputStream bout = new BufferedOutputStream(os, 1024);
                byte data[] = new byte[1024];
                while (is.read(data, 0, 1024) >= 0) {
                    bout.write(data);
                }
                bout.close();
                is.close();
            } catch (Exception ex) {
                System.out.println(ex.getMessage());
                System.exit(1);
            }
        }
    }

    public String getSiteURL() {
        return siteURL;
    }

    public WebSite(String siteURL) {
        this.siteURL = siteURL;
    }

    /**
     * Prints the list of links currently on the queue for the website
     */
    public void printLinks() {
        System.out.println("Printing Links for website: " + siteURL);
        for (Element link : links) {
            System.out.println("Link: " + link.attr("abs:href"));
        }
    }
}

package mangadownloader.websites;

import java.io.IOException;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

/**
 *
 * @author wasser
 */
public class CrazyManga extends WebSite {

    public CrazyManga(String siteURL) {
        super(siteURL);
    }

    @Override
    public void addToDownloadQueue(Element downloadLink) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public void removeFromDownloadQueue(Element downloadLink) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public Elements getDownloadQueue() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public void parseWebSite() {
        try {
            Elements rawLinks = getLinksFromWebSite();
            links = new Elements();

            for (Element link : rawLinks) {
                if (link.attr("abs:href").startsWith("http://dl.crazytje.be/dl.php?id")) {
                    links.add(link);
                }
            }
        } catch (IOException ex) {
            System.out.println("Error Getting links from " + siteURL + ex.getMessage());
            //TODO Treat this in a correct manner with retries (maybe with the interface?)
            System.exit(1);
        }
    }
}

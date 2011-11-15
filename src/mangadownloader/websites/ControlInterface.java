package mangadownloader.websites;

import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

/**
 * Commands implemented by the webpages to be controled
 * @author wasser
 */
public interface ControlInterface {

    /**
     * Starts downloading the download links from the queue
     */
    void startDownloading();

    /**
     * Adds an element to the download queue.
     * @param downloadLink Link to be added to the queue
     */
    void addToDownloadQueue(Element downloadLink);

    /**
     * Removes an element from the download queue.
     * @param downloadLink Link to be removed from the queue
     */
    void removeFromDownloadQueue(Element downloadLink);

    /**
     * @return List of elements queued for download for a website
     */
    Elements getDownloadQueue();

    /**
     * Takes all needed actions to obtain the correct links for a website.
     */
    void parseWebSite();
}

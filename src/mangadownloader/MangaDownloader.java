package mangadownloader;

import mangadownloader.websites.CrazyManga;

/**
 *
 * @author wasser
 */
public class MangaDownloader {

    /**
     * @param args the command line arguments
     * Used for testing purposes until an interface is created
     */
    public static void main(String[] args) {
        CrazyManga website = new CrazyManga("http://crazytje.be/Manga/4ae7008c-ebf8-41a7-a825-5270d0359e0c");
        website.parseWebSite();
        website.startDownloading();
    }
}

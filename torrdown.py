# VERSION: 1.0
# AUTHORS: LightDestory (https://github.com/LightDestory)

import re
import urllib.parse
from helpers import retrieve_url
from novaprinter import prettyPrinter


class torrentdownload(object):
    url = 'https://www.torrentdownload.info/'
    name = 'TorrentDownload'
    max_pages = 10

    class HTMLParser:

        def __init__(self, url):
            self.url = url
            self.pageResSize = 0

        def feed(self, html):
            self.pageResSize = 0
            torrents = self.__findTorrents(html)
            resultSize = len(torrents)
            if resultSize == 0:
                return
            else:
                self.pageResSize = resultSize
                count = 0
            for torrent in range(resultSize):
                count = count + 1
                data = {
                    'link': torrents[torrent][0],
                    'name': torrents[torrent][1],
                    'size': torrents[torrent][2],
                    'seeds': torrents[torrent][3],
                    'leech': torrents[torrent][4],
                    'engine_url': self.url,
                    'desc_link': urllib.parse.unquote(torrents[torrent][0])
                }
                prettyPrinter(data)

        def __findTorrents(self, html):
            torrents = []
            trs = re.findall(
                r'<tr><td.+?tt-name.+?</tr>', html)
            for tr in trs:
                # Extract from the A node all the needed information
                url_titles = re.search(
                    r'.+?href=\"/(.+?)\">(.+?)</a>.+?tdnormal\">([0-9\,\.]+ (TB|GB|MB|KB)).+?tdseed\">([0-9,]+).+?tdleech\">([0-9,]+)',
                    tr)
                if url_titles:
                    torrent_data = [
                        urllib.parse.quote('{0}{1}'.format(self.url, url_titles.group(1))),
                        url_titles.group(2).replace("<span class=\"na\">", "").replace("</span>", ""),
                        url_titles.group(3).replace(",", ""),
                        url_titles.group(5).replace(",", ""),
                        url_titles.group(6).replace(",", ""),
                    ]
                    torrents.append(torrent_data)
            return torrents

    def download_torrent(self, info):
        torrent_page = retrieve_url(urllib.parse.unquote(info))
        magnet_match = re.search(r'\"(magnet:.*?)\"', torrent_page)
        if magnet_match and magnet_match.groups():
            print('{0} {1}'.format(magnet_match.groups()[0], info))
        else:
            raise Exception('Error, please fill a bug report!')

    def search(self, what, cat='all'):
        what = what.replace("%20", "+")
        parser = self.HTMLParser(self.url)
        for currPage in range(1, self.max_pages):
            url = '{0}search?q={1}&p={2}'.format(self.url, what, currPage)
            # Some replacements to format the html source
            html = retrieve_url(url).replace("	", "").replace("\n", "").replace("\r", "")
            parser.feed(html)
            if parser.pageResSize <= 0:
                break

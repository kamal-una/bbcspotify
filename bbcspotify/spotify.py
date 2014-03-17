"""
Threading sandbox
"""
from google.appengine.api import urlfetch

import urllib2
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import logging


class BBC(object):
    """
    BBC Radio to Spotify playlist class
    """
    def __init__(self):
        """
        Initialise variables
        """
        self.playlist = ''
        self.title = ''
        self.searches = []


    def get_playlist(self, bbc_url):
        """
        Start the job and compile the playlist
        """
        self.playlist = ''
        self.find_tracks(bbc_url)

        logging.info('going through results...')
        for rpc in self.searches:
            try:
                result = rpc.get_result()
                if result.status_code == 200:

                    # search respose...
                    xml_response = ET.fromstring(result.content)
                    for track in xml_response:
                        try:
                            spotify_track = track.attrib['href']
                            logging.info('got spotify track: ' + spotify_track)
                            self.playlist += spotify_track + '\n'
                            break
                        except:
                            pass

            except urlfetch.DownloadError, error:
                logging.info('request failed: ' + str(error))
                # request failed
                pass

        return self.title, self.playlist


    def find_tracks(self, bbc_url):
        """
        Scan through the page and and find the tracks
        """
        logging.info('find_tracks...')

        # add 'http://'' if it is missing
        if not bbc_url.startswith('http://'):
            bbc_url = 'http://' + bbc_url

        try:
            req = urllib2.Request(bbc_url) 
            html = urllib2.urlopen(req)
            soup = BeautifulSoup(html)

            self.title = soup.find('title').string

            logging.info('title: ' + self.title)

            segments = soup.find_all('li', {'class': 'segment'})

            for segment in segments:
                try:
                    artist = segment.find('span', {'class':'artist'}).string
                    track = segment.find('span', {'class':'title'}).string
                except:
                    artist = None
                    track = None

                if track is not None and artist is not None:
                    self.get_track(artist, track)

                else:
                    logging.info('not adding to queue. ')
                    spotify_url = ''
        
        except:
            logging.info('invalid url')

        logging.info('find_tracks done.')


    def get_track(self, artist, track):
        """
        Use the Spotify search api to find the track
        """
        output = '%s %s' % (artist.encode('utf8'), track.encode('utf8'))
        output = urllib2.quote(output)

        spotify = 'http://ws.spotify.com/search/1/track?q='
        spotify_url = spotify + output

        # now hand the rest of the job to a thread queue work...
        logging.info('adding to urlfetch: ' + spotify_url)
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, spotify_url)
        self.searches.append(rpc)

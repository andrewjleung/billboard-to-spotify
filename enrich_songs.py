import re
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import bbfetch
from cache import Cache

MULTI_ARTIST_DELIM_REGEX = re.compile(
    r"[+&\/]|, |Featuring|With|[Vv]s.| [Xx] ")
MAX_ARTIST_LENGTH = 40
MAX_TRACKS = 50
MAX_AUDIO_FEATURES = 100

"""
These are song/Artist edge cases that don't turn up in searches via the Spotify API as-is from
Billboard, but are clearly on Spotify.

As of 04/12/2022, there are a few cases which are charting on Billboard but don't have a clear
counterpart on Spotify.

These include:
- 'Change The World' by Chris Standring
- 'G Wiggle' by Gerald Albright
- 'Crunk/Slow Down' by Showtek
- 'Dance! 2013' by Lumidee Vs. Fatman Scoop
- 'Alright/Together' by Mark Knight
- 'Love Hangover 2020' by Diana Ross
"""
EDGE_CASES = {
    # The artist on Billboard and Spotify aren't the same.
    "Me Vale Perderte": "Banda Rancho",
    # The listed artist on Billboard does not turn up in searches for this track.
    # Searching for Dreamville, the other artist on this track, does work.
    "Freedom of Speech": "Dreamville",
    "Stick": "Dreamville",
    # Billboard lists the artist here as "Silk Sonic (Bruno Mars & Anderson .Paak)".
    "Leave The Door Open": "Silk Sonic"
}


class BillboardToSpotify():
    """
    Class for enriching songs fetched from Billboard charts with metadata from Spotify.
    """

    def __init__(self, spotify_client):
        self.spotify_client = spotify_client

    def parse_artists(self, artists_str):
        """ Function:   parse_artists
            Parameters: artists_str, raw artists string from Billboard
            Return:     list, list of parsed artists
        """
        artists_lst = [a.strip() for a in MULTI_ARTIST_DELIM_REGEX.split(
            artists_str) if a.strip()]
        return artists_lst

    def get_search_params(self, title, artist):
        """ Function:   clean_search_params
            Parameters: title, the song's title
                        artist, the song's artist
            Return:     tuple, (the cleaned title, the cleaned artist)
        """
        cleaned_title = title
        cleaned_artist = EDGE_CASES.get(title, artist)

        # The Spotify API has a bug where searching for strings with apostrophes doesn't work.
        # The issue can be found here: https://github.com/spotify/web-api/issues/1212.
        # A workaround is to replace all apostrophes with spaces.
        cleaned_title = cleaned_title.replace("'", " ")
        cleaned_artist = cleaned_artist.replace("'", " ")

        return (cleaned_title, cleaned_artist)

    def find_song_id(self, song):
        """ Function:   find_song_id
            Parameters: song, tuple (song title, song artist string)
            Return:     string, the song's Spotify ID or None if not found
        """
        title = song["title"]
        artist_str = song["artist"]
        artists = self.parse_artists(artist_str)
        print(artists)

        for artist in artists:
            cleaned_title, cleaned_artist = self.get_search_params(
                title, artist)
            query = f"track:{cleaned_title} artist:{cleaned_artist}"
            results = self.spotify_client.search(
                q=query, type="track", limit=1)
            result_items = results["tracks"]["items"]

            if len(result_items) >= 1:
                return result_items[0]["id"]

            print(f"Could not find {cleaned_title} by {artist}")

        return None

    def find_songs_ids(self, songs):
        """ Function:   find_songs_ids
            Parameters: songs, list of tuples (song title, song artist string)
            Return:     list, list of strings containing Spotify IDs for songs that were found
        """
        result = [self.find_song_id(song) for song in songs]
        return result

    def get_tracks_metadata(self, tracks_dict):
        """ Function:   get_tracks_metadata
            Parameters: tracks_dict, dictionary mapping track IDs to dictionaries of metadata
            Return:     dict, updated metadata dictionary
        """
        for i in range(0, len(tracks_dict.keys()), MAX_TRACKS):
            chunk = dict.keys()[i:i + MAX_TRACKS]
            pass

        pass

    def get_tracks_audio_features(self, tracks_dict):
        """ Function:   get_tracks_metadata
            Parameters: tracks_dict, dictionary mapping track IDs to dictionaries of metadata
            Return:     dict, updated metadata dictionary
        """
        pass


load_dotenv()

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())
bbts = BillboardToSpotify(spotify)

with Cache("songs.json", bbfetch.get_chart_songs) as bb_songs:
    with Cache("song_ids.json", lambda: bbts.find_songs_ids(bb_songs)) as song_ids:
        print(song_ids)

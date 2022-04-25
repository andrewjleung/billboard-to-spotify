import csv
import re

MULTI_ARTIST_DELIM_REGEX = re.compile(
    r"[+&\/]|, |Featuring|With|[Vv]s.| [Xx] ")

MAX_ARTIST_LENGTH = 40
MAX_TRACKS = 50
MAX_AUDIO_FEATURES = 100
AUDIO_FEATURES = [
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "duration_ms",
    "time_signature"
]

"""
These are track title/artist edge cases that don't turn up in searches via the Spotify API as-is
from Billboard, but are clearly on Spotify.

As of 04/12/2022, there are a few cases which are charting on Billboard but don't have a clear
counterpart on Spotify.

These include: 
- 'Change The World' by Chris Standring 
- 'G Wiggle' by Gerald Albright - 'Crunk/Slow Down' by Showtek 
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
    Class for enriching tracks fetched from Billboard charts with metadata from Spotify.
    """

    def __init__(self, spotify_client):
        self.spotify_client = spotify_client

    @staticmethod
    def parse_billboard_artists(artists_str):
        """ Function:   parse_billboard_artists
            Parameters: artists_str, raw artists string from Billboard
            Return:     list, list of parsed artists
        """
        artists_lst = [a.strip() for a in MULTI_ARTIST_DELIM_REGEX.split(
            artists_str) if a.strip()]
        return artists_lst

    @staticmethod
    def get_search_params(title, artist):
        """ Function:   clean_search_params
            Parameters: title, the track's title
                        artist, the track's artist
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

    def find_track_id(self, track):
        """ Function:   find_track_id
            Parameters: track, tuple (track title, track artist string)
            Return:     string, the track's Spotify ID or None if not found
        """
        title = track["title"]
        artist_str = track["artist"]
        artists = BillboardToSpotify.parse_billboard_artists(artist_str)

        for artist in artists:
            cleaned_title, cleaned_artist = BillboardToSpotify.get_search_params(
                title, artist)
            query = f"track:{cleaned_title} artist:{cleaned_artist}"
            results = self.spotify_client.search(
                q=query, type="track", limit=1)
            result_items = results["tracks"]["items"]

            if len(result_items) >= 1:
                return result_items[0]["id"]

            # print(f"Could not find {cleaned_title} by {artist}")

        return None

    def find_tracks_ids(self, tracks):
        """ Function:   find_tracks_ids
            Parameters: tracks, list of tuples (track title, track artist string)
            Return:     list, list of strings containing Spotify IDs for tracks that were found
        """
        result = [self.find_track_id(track) for track in tracks]
        result = [track_id for track_id in result if track_id]
        return result

    @staticmethod
    def get_spotify_artists(track_response):
        """ Function:   get_spotify_artists
            Parameters: track_response, dict containing track response data
            Return:     list, list of strings of the track's artist names
        """
        return [artist["name"] for artist in track_response["artists"]]

    def get_tracks_metadata(self, tracks_metadata):
        """ Function:   get_tracks_metadata
            Parameters: tracks_metadata, dict mapping track IDs to dictionaries of metadata
            Return:     dict, updated metadata dictionary
        """
        for i in range(0, len(tracks_metadata.keys()), MAX_TRACKS):
            chunk = list(tracks_metadata.keys())[i:i + MAX_TRACKS]
            response = self.spotify_client.tracks(chunk)
            for track in response["tracks"]:
                track_metadata = tracks_metadata[track["id"]]
                track_metadata["track"] = track["name"]
                track_metadata["artist"] = ",".join(
                    self.get_spotify_artists(track))
                track_metadata["popularity"] = track["popularity"]

        return tracks_metadata

    @staticmethod
    def filter_audio_features(audio_features_response):
        """ Function:   filter_audio_features
            Parameters: audio_features_response, dictionary containing the audio features response
                            for a single track
            Return:     dict, a filtered dictionary containing just audio features
        """
        return {key: value for key, value in audio_features_response.items()
                if key in AUDIO_FEATURES}

    def get_tracks_audio_features(self, tracks_metadata):
        """ Function:   get_tracks_metadata
            Parameters: tracks_metadata, dictionary mapping track IDs to dictionaries of metadata
            Return:     dict, updated metadata dictionary
        """
        for i in range(0, len(tracks_metadata.keys()), MAX_AUDIO_FEATURES):
            chunk = list(tracks_metadata.keys())[i: i + MAX_AUDIO_FEATURES]
            response = self.spotify_client.audio_features(chunk)
            for track_features in response:
                filtered_track_features = BillboardToSpotify.filter_audio_features(
                    track_features)
                tracks_metadata[track_features["id"]
                                ] |= filtered_track_features

        return tracks_metadata

    @staticmethod
    def write_tracks_dataset(csv_filename, tracks_metadata):
        """ Function:   write_tracks_dataset
            Parameters: csv_filename, the file to write the CSV data to
                        tracks_metadata, dictionary mapping track IDs to dictionaries of metadata
            Return:     None
        """
        values = list(tracks_metadata.values())
        keys = values[0].keys()

        with open(csv_filename, "w+", encoding="utf-8") as out_file:
            dict_writer = csv.DictWriter(out_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(values)

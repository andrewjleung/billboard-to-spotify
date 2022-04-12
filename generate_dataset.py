from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from billboard_to_spotify import BillboardToSpotify
import bbfetch
from cache import Cache


BILLBOARD_TRACKS_FILENAME = "./bin/bb_tracks.json"
SPOTIFY_TRACK_IDS_FILENAME = "./bin/track_ids.json"
TRACKS_DATASET_FILENAME = "./bin/tracks.csv"


load_dotenv()

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials())
bbts = BillboardToSpotify(spotify)

print("Fetching songs from Billboard charts.")

with Cache(BILLBOARD_TRACKS_FILENAME, bbfetch.get_chart_songs) as bb_tracks:
    print("Fetching track IDs.")

    with Cache(SPOTIFY_TRACK_IDS_FILENAME, lambda: bbts.find_tracks_ids(bb_tracks)) as track_ids:
        tracks_metadata = {track_id: {} for track_id in track_ids}

        print("Populating tracks with basic metadata.")
        bbts.get_tracks_metadata(tracks_metadata)

        print("Populating tracks with audio features metadata.")
        bbts.get_tracks_audio_features(tracks_metadata)

        print(f"Writing tracks data to {TRACKS_DATASET_FILENAME}")
        BillboardToSpotify.write_tracks_dataset(
            TRACKS_DATASET_FILENAME, tracks_metadata)

from enum import Enum
import billboard


class Chart(Enum):
    """
    Enumeration of Billboard song charts.
    """
    HOT_100 = "hot-100"
    RAP_SONGS = "rap-songs"
    POP_SONGS = "pop-songs"
    COUNTRY_SONGS = "country-songs"
    ROCK_SONG = "rock-song"
    ALTERNATIVE_SONGS = "alternative-songs"
    DANCE_ELECTRONIC_SONGS = "dance-electronic-songs"
    LATIN_SONGS = "latin-songs"
    CHRISTIAN_SONGS = "christian-songs"
    JAZZ_SONGS = "jazz-songs"
    HOLIDAY_SONGS = "holiday-songs"
    GOSPEL_SONGS = "gospel-songs"
    GLOBAL = "global"
    DANCE = "dance"
    SUMMER_SONGS = "summer-songs"
    BUBBLING = "bubbling"
    HOT = "hot"
    GOSPEL = "gospel"
    RHYTHMIC = "rhythmic"


def get_billboard_songs():
    """ Function:   get_chart_songs
        Parameters: none
        Return:     list, list of dicts containing each song's title and artist
    """
    songs = {}

    for _name, member in Chart.__members__.items():
        chart = billboard.ChartData(member.value)

        for entry in chart:
            songs[entry.__str__()] = {
                "title": entry.title, "artist": entry.artist}

    return [entry for printed, entry in songs.items()]

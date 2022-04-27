# billboard-to-spotify

This is part of a project for DS2500 at NEU, encompassing the creation of a dataset containing songs
across various Billboard charts, linked with Spotify metadata.

Note that the scripts here for generating data are inefficient since an API request must be made for
every song within the dataset to link it with Spotify metadata. Getting through the entire dataset
may take some time.

## Dependencies

This project uses `venv` to establish a virtual environment for dependencies which are specified
within `requirements.txt`. To download dependencies and then enter the virtual environment, run the
following:

```bash
make
source .venv/bin/activate
```

## Dataset Generation

In order for this script to fetch any data from the Spotify API, you fill first need to generate a
Spotify API OAuth client ID and secret via the [Spotify developer
dashboard](https://developer.spotify.com/dashboard/) and populate a `.env` file in the root
directory to specify these as environment variables.

A template is provided in `.env.template`, and can be used like so:

```bash
cp .env.template .env
```

To then generate the dataset, run the `generate_dataset.py` script:

```bash
python3 generate_dataset.py
```

## Cached Data

The `generate_dataset.py` script will automatically utilize custom caches for expensive and lengthy
requests to Billboard and Spotify if they are present. More specifically, tracks fetched from
Billboard and track IDs are cached within separate files in the `bin` folder.

To generate a completely fresh and updated dataset, delete the files within the `bin` folder and
regenerate the dataset. This may take a couple minutes.

Sample files of each intermediate cached piece of data along with the final dataset are included:

- `billboard_tracks.json` : track titles and artists fetched from Billboard
- `track_ids.json` : track Spotify IDs fetched from the Spotify API search endpoint
- `tracks.csv` : the final dataset with popularity and audio features metadata for each song

## Data Analysis

A notebook containing all group data analysis is included within `tracks-analysis.ipynb`.

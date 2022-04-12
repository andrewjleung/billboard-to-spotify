# billboard-to-spotify

This is part of a project for DS2500 at NEU, encompassing the creation of a dataset containing songs
across various Billboard charts, linked with Spotify metadata.

Note that the scripts here for generating data are inefficient since an API request must be made for
every song within the dataset to link it with Spotify metadata. Getting through the entire dataset
may take some time.

## Dataset Generation

To generate an updated dataset, you fill first need to generate a Spotify API OAuth client ID and
secret via the [Spotify developer dashboard](https://developer.spotify.com/dashboard/) and populate
a `.env` file in the root directory to specify these as environment variables. This is required in
order to request track metadata from the Spotify API.

A template is provided in `.env.template`, and can be used like so:

```
cp .env.template .env
```

TODO...

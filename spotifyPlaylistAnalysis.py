"""
spotifyPlaylistAnalysis

This script allows the user to analyze their Spotify playlists by plotting each song's metadata.

This script requires some sensitive client info in order to access their Spotify account.
I've protected my Client ID and Client Secret Key by storing them in a separate class.

The Client ID and Client Secret Key can be obtained from Spotify by creating a Spotify Developer account.
Both Client IDs and Secret Keys are a string of alphanumerics that resemble "as645dfasdfasd45646asdf4asf654"

Dependancies:
-Python 3
-Spotify Account
-Spotify Developer app secret key
-Custom class called clientCredentials where user credentials are stored

"""

import pandas as pd
import spotipy
import spotipy.util as util
import matplotlib.pyplot as plt
import clientCredentials as cC  # Custom class where I've stored my sensitive info

plt.style.use('classic')  # use classic matplotlib styling
creds = cC.ClientCredentials()  # Instantiates custom class
client_id = creds.client_id
client_secret = creds.client_secret
scope = "user-library-read"  # Spotify REST calls require a defined scope
username = "1264646265"  # my Spotify username
redirect_url = "http://www.google.com/"  # Could be any URL
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_url)  # create Spotipy token
sp = spotipy.Spotify(auth=token)  # Creates a Spotipy object


def get_user_playlists():
    # Reads the titles of user's playlists, creates a dictionary to look up URI based on integer key value.
    if token:
        sp.trace = False  # Turns off tracing
        users_playlists = sp.current_user_playlists(limit=50)
    return users_playlists


def get_playlist_uris(p):
    playlist_tokenizer = {}
    for i, item in enumerate(p['items']):
        # Adds int and playlist uri to dict
        playlist_tokenizer[i] = item['uri']
        print(i, item['name'])  # Prints out playlist options
    print()
    # Prompts user to select one their playlists, catches for bad user input
    while True:
        try:
            playlist_choice = int(input('Type a number to analyze a playlist:'))
            if len(playlist_tokenizer) - 1 > playlist_choice > -1:  # Selection must be within range
                playlist_to_analyze = playlist_tokenizer[playlist_choice]
                break  # a proper selection has been made
            else:
                print('\nThere is no playlist with that number\n')
        except ValueError as e:
            print('\nNot a valid number\n')  # Selection must be an integer value
    return playlist_to_analyze


def get_playlist_data(playlist_id):
    # Reads tracks from playlist, returns track info dict
    results = sp.user_playlist(username, playlist_id)
    return results


def get_track_names(results):
    # Reads from track info dict, appends
    track_list = []
    for i in results['tracks']["items"]:
        track_list.append('{} - {}'.format(i['track']['artists'][0]['name'], i['track']['name']))
    return track_list


def get_track_uris(results):
    uri_list = []
    for i in results['tracks']["items"]:
        uri_list.append(i['track']['uri'])
    return uri_list


def get_analysis(uri_list):
    analysis_list = []
    for uri in uri_list:
        analysis = sp.audio_features(uri)
        analysis_list.append(analysis[0])
    # Creates a list of all fields available for analysis
    analysis_fields = list(analysis[0].keys())
    return analysis_list, analysis_fields


def combine_lists(analysis_list, track_list):
    # Combines the list of tracks on the playlist with their analysis
    i = 0
    for analysis in analysis_list:
        analysis.update(Track=track_list[i])
        i += 1
    return analysis_list


def build_dataframe(analysis_list):
    # Constructs Pandas DataFrame Object from combined lists
    df = pd.DataFrame(analysis_list)
    return df


def plot_dataframe(df, analysis_fields):
    # Plots the analysis from the DataFrame
    try:
        for field in analysis_fields:
            df.plot(kind='bar', x='Track', y=field)
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)
            plt.show()
    except TypeError:
        pass


def main():
    playlists = get_user_playlists()
    uris = get_playlist_uris(playlists)
    results = get_playlist_data(uris)
    track_list = get_track_names(results)
    track_uris = get_track_uris(results)
    analysis_list, analysis_fields = get_analysis(track_uris)
    combined_lists = combine_lists(analysis_list, track_list)
    df = build_dataframe(combined_lists)
    plot_dataframe(df, analysis_fields)


if __name__ == "__main__":
    main()

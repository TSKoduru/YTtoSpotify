import re
from bs4 import BeautifulSoup
import requests
import spotipy
import spotipy.util as util


REDIRECT_URI = 'http://localhost:8888/callback'
USERNAME = 'ENTER USERNAME HERE'
CLIENT_ID = 'ENTER CLIENT ID HERE'
CLIENT_SECRET = 'ENTER CLIENT SECRET HERE'

def get_songs_from_chapters(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    regex = r"{\"chapterRenderer\":{\"title\":{\"simpleText\":\".*\"},\"timeRangeStartMillis\""

    # Save soup as string
    soup_string = str(soup)
    result = re.findall(regex, soup_string)

    # Remove all new lines
    result = [x.replace('\n', '') for x in result]

    # Run another regex to remove all the extra stuff. We want only the parts between "simpleText":" and "}
    regex = r"\"simpleText\":\".*?\""
    result = re.findall(regex, result[0])

    # Finally, strip out everything up to the first quote and after the last quote
    for i, hit in enumerate(result): result[i] = hit[14:-1]

    return result

def convert_to_spotify(songs, username, client_id, client_secret, playlist_name):
    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)

    playlist = sp.user_playlist_create(username, name=playlist_name)

    song_uris = []
    for song in songs:
        artistName, songName = song.split(" - ")

        # Get rid of everything before first space in songName and artistName
        songName = songName[songName.find(" ")+1:]
        artistName = artistName[artistName.find(" ")+1:]

        print("-----------------------")
        print(f"Searching for {songName} by {artistName}")
        

        result = sp.search(q="artist:" + artistName + " track:" + songName, type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError: print(f"{song} doesn't exist in Spotify. Skipped.")

        print("-----------------------")
        print('\n')

    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

def main():
    url = input("Enter the URL of the video: ")
    playlist_name = input("Enter the name of the playlist: ")

    songs = get_songs_from_chapters(url)

    convert_to_spotify(songs, USERNAME, CLIENT_ID, CLIENT_SECRET, playlist_name)

if __name__ == "__main__":
    main()

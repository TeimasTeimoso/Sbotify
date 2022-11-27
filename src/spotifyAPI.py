import spotipy
from spotipy.oauth2 import SpotifyOAuth
import toml
from spotipy.exceptions import SpotifyException

configs = toml.load("config.toml")


class SpotifyAPI:

    api = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=configs["CLIENT_ID"], 
                client_secret=configs["CLIENT_SECRET"],
                redirect_uri=configs["REDIRECT_URI"],
                scope=configs["SCOPE"]))

    @classmethod
    def get_deviceID(cls):
        device_list = cls.api.devices()
        return device_list['devices'][0]['id']

    @classmethod
    def next_track(cls, deviceID):
        cls.api.next_track(deviceID)

    @classmethod
    def previous_track(cls, deviceID):
        cls.api.previous_track(deviceID)

    @classmethod
    def play_pause(cls, deviceID, status):
        try:
            if status == 0:
                cls.api.pause_playback(deviceID)
            else:
                cls.api.start_playback(deviceID)
        except SpotifyException:
            pass

    @classmethod
    def play_new_song(cls, txt_input):
        # Hoping the artist does not have an "By" in It's name
        query_tuple = txt_input.rpartition("by")        

        # we're assuming it's only the song name
        if query_tuple[1] == '':
            # in order to spotify query
            song_name = query_tuple[2].replace(" ", "+")
            song_info = cls.api.search(q=song_name,limit=1, type='track')
        elif query_tuple[1] == 'by':
            song_name = query_tuple[0].replace(" ", "+")
            artist = query_tuple[2].replace(" ", "+")
            song_info = cls.api.search(q=song_name+"&"+artist,limit=1, type='track')
        
        if song_info['tracks']['items'] == []:
            return False #could not play any song

        song_uri = song_info['tracks']['items'][0]['uri']
        cls.api.start_playback(device_id=cls.get_deviceID(), uris=[song_uri])
        return True #exit sucess

    @classmethod
    def play_artist_songs(cls, txt_input):
        artist_name = txt_input.replace(" ","+")
        artist_info = cls.api.search(q=artist_name, limit=1, type='artist')

        try:
            artist_id = artist_info['artists']['items'][0]['id']

            top_tracks = cls.api.artist_top_tracks(artist_id)
            list_of_tracks = []

            for track in top_tracks['tracks']:
                list_of_tracks.append(track['uri'])

            cls.api.start_playback(device_id=cls.get_deviceID(), uris=list_of_tracks)
            return True
        except IndexError:
            return False

    @classmethod
    def get_song_name(cls):
        res = cls.api.currently_playing()
        
        song_name = res['item']['name']
        artist = res['item']['artists'][0]['name']

        return str(song_name)+" by "+str(artist)

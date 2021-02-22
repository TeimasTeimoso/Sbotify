import os, time, sys
from datetime import datetime
import toml
from spotifyAPI import *
from pocketsphinx import LiveSpeech, get_model_path
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

configs = toml.load("config.toml")
FILE_NAME = configs["SPEECH_FILE_NAME"]
model_path = get_model_path()

def flatten(input_list):
    flattened_list = []

    for l in input_list:
        list(map(lambda e: flattened_list.append(e), l))

    return flattened_list

# initializes ibm tts module with apikey and url
def start_speaker(apikey, url):
    authenticator = IAMAuthenticator(apikey)
    tts = TextToSpeechV1(authenticator=authenticator)
    tts.set_service_url(url)
    return tts

class Bot:

    COMMANDS_DICTIONARY = {
        "next_track": ["next","next track", "play next track", "skip track"],
        "previous_track": ["previous track", "previous"],
        "resume_song": ["resume", "resume song", "continue"],
        "pause_song": ["pause", "pause song", "stop", "stop song"],
        "play_song": ["play", "search"],
        "song_name": ["what is playing", "currently playing"], 
        "artist_songs": ["artist"],
        "inactive": ["sleep"],
        "active": ["wake up"]
    }

    ALL_COMMANDS = flatten(list(COMMANDS_DICTIONARY.values()))

    def __init__(self):
        # Bot is listening
        self.SLEEPING = False
        # initializes the ibm tts service
        self.tts = start_speaker(configs['TTS_API_KEY'], configs['TTS_URL'])

        # starts the speech recognizer
        self.speech = LiveSpeech(
            verbose=False,
            sampling_rate=44100,
            buffer_size=2048,
            no_search=False,
            full_utt=False,
            hmm=os.path.join(model_path, 'en-us'),
            lm="TAR8856/8856.lm",
            dic="TAR8856/8856.dic"
        )

        self.speak("Hello! My name is Sbotify!")

        try:
            self.deviceId = SpotifyAPI().get_deviceID()
        except:
            self.speak("You need to have Spotify opened for me to help you! Bye")
            sys.exit()

        # listening for input
        for sentence in self.speech:
            print(sentence)

            if self.speech.buffer_size != 0:
                self.handle(str(sentence))

    # uses tts module
    def speak(self, tts_input):

        self.speech.buffer_size = 0

        with open('./speech.mp3', 'wb') as audio_file:
            res = self.tts.synthesize(tts_input, accept='audio/mp3', voice='en-US_AllisonV3Voice').get_result()
            audio_file.write(res.content)
            os.system(f"mpg123 {FILE_NAME}")
            time.sleep(4)
            self.speech.buffer_size = 2048
        

    # handle the voice input
    def handle(self, txt_input):
        txt_input = txt_input.lower()
        first_word = txt_input.split(" ")[0]

        if (self.SLEEPING and txt_input not in self.COMMANDS_DICTIONARY['active']) or (txt_input == ""):
            pass
        else:
            if (txt_input in self.ALL_COMMANDS) or (first_word in self.ALL_COMMANDS) or (txt_input == "") :
                if txt_input in self.COMMANDS_DICTIONARY['next_track']:
                    SpotifyAPI.next_track(self.deviceId)
                elif txt_input in self.COMMANDS_DICTIONARY['previous_track']:
                    SpotifyAPI.previous_track(self.deviceId)
                elif (txt_input in self.COMMANDS_DICTIONARY['pause_song']) or (txt_input in self.COMMANDS_DICTIONARY['resume_song']):
                    SpotifyAPI.play_pause(self.deviceId, 1 if txt_input in self.COMMANDS_DICTIONARY['resume_song'] else 0)
                elif first_word in self.COMMANDS_DICTIONARY['play_song']:
                    res = SpotifyAPI.play_new_song(txt_input.strip(first_word))
                    if not res:
                        self.speak("The song you asked does not exist! I'm sorry...")
                elif txt_input in self.COMMANDS_DICTIONARY['song_name']:
                    self.speak(SpotifyAPI.get_song_name())
                elif first_word in self.COMMANDS_DICTIONARY['artist_songs']:
                    res = SpotifyAPI.play_artist_songs(txt_input.strip(first_word))
                    if not res:
                        self.speak("I could not found the artist you asked for! Sorry.")
                elif txt_input in self.COMMANDS_DICTIONARY['inactive']:
                    self.SLEEPING = True
                elif txt_input in self.COMMANDS_DICTIONARY['active']:
                    self.SLEEPING = False
            else:
                self.speak("I'm really embarrassed, but I don't know what to do...")

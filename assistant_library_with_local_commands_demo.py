#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

SIt is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys
import time
import datetime
import os
import random
from os import listdir
from os.path import isfile, join
import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.audio
import aiy.voicehat
from google.assistant.library.event import EventType

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)
song_files = [f for f in listdir("/home/pi/Downloads") if isfile(join("/home/pi/Downloads", f))]

artists = {}
albums = {}
songs = {}
for song_file in song_files:
    parts = song_file.split(".")[0].split("-")
    artist = parts[0].replace("_", " ")
    album = parts[1].replace("_", " ")
    song = parts[3].replace("_", " ")
    if artist in artists:
        artists[artist].append(song_file)
    else:
        artists[artist] = [song_file]
    if album in albums:
        albums[album].append(song_file)
    else:
        albums[album] = [song_file]
    songs[song] = song_file
                                           
caillou = False
playing_ispy = False
audio_playing = False
waiting_for_type = False
waiting_for_song = False
waiting_for_artist = False
waiting_for_album = False

def on_button_press():
    if audio_playing == False:
        aiy.audio.say('ow!',pitch=400)
        aiy.audio.say('Stop it, you FOOL.',pitch=50,volume=30)
    # else:
        #stop all audio currently playing off of device
        
button = aiy.voicehat.get_button()
button.on_press(on_button_press)

def power_off_pi():
    subprocess.call('sudo shutdown now', shell=True)

#albums in the library:
    

def recognize_from_song(songname):
    global songs
    return songs.get(songname, "not found")
    
def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def process_event(assistant, event):
    global stupid
    global playing_ispy
    global waiting_for_type
    global waiting_for_song
    global waiting_for_artist
    global waiting_for_album
    global songs
    global artists
    global albums
    status_ui = aiy.voicehat.get_status_ui()
    aiy.audio.set_tts_volume(5)
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()

        if text == 'pink guy':
            assistant.stop_conversation()
            aiy.audio.say("Why do I exist? I do not know! O! 10 9 8 7 6 5 4 3 2 1. O hi, human.")
            power_off_pi()
            
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
                
        elif playing_ispy:
            assistant.stop_conversation()
            if "blood" in text:
                aiy.audio.say("You got it. You must be a spy")
                playing_ispy = False
            else:
                aiy.audio.say("Wrong. Guess again")
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()

        elif waiting_for_song:
            waiting_for_song = False
            assistant.stop_conversation()
            song_file = songs.get(text, "not found")
            if song_file == "not found":
                aiy.audio.say("not found")
            else:                      
              aiy.audio.play_wave("/home/pi/Downloads/"+song_file)

        elif waiting_for_artist:
            waiting_for_artist = False
            assistant.stop_conversation()
            song_file = artists.get(text, "not found")
            if song_file == "not found":
                aiy.audio.say("not found")
            else:                      
              aiy.audio.play_wave("/home/pi/Downloads/"+random.choice(song_file))

        elif waiting_for_album:
            waiting_for_album = False
            assistant.stop_conversation()
            song_file = albums.get(text, "not found")
            if song_file == "not found":
                aiy.audio.say("not found")
            else:                      
              aiy.audio.play_wave("/home/pi/Downloads/"+random.choice(song_file))

        elif waiting_for_type:
            waiting_for_type = False
            assistant.stop_conversation()
            if text == "song":              
                aiy.audio.say("Please say the name of the song you would like to play.",pitch=90)
                waiting_for_song = True
            elif text == 'artist':
                aiy.audio.say("Please say the name of the artist you would like to play.",pitch=90)
                waiting_for_artist = True
            elif text == 'album':
                aiy.audio.say("Please say the name of the album you would like to play.",pitch=90)
                waiting_for_album = True        
            
        elif text == 'play music':
            waiting_for_type = True
            assistant.stop_conversation()
            aiy.audio.say("Would you like to play from an artist, play an album, or a specific song?",pitch=90)
                
            
        elif text == 'what day of the week is it':
            assistant.stop_conversation()
            aiy.audio.set_tts_volume(20)
            if datetime.datetime.today().weekday() == 2:
                aiy.audio.say("It is wednesday my dudes.",pitch=50)
                aiy.audio.say("REEEEEEEEEEEEEEEEEEEEEEEEEEE", pitch=400)
            if datetime.datetime.today().weekday() == 1:
                aiy.audio.say("It is tuesday eEUUUURGH")
            if datetime.datetime.today().weekday() == 0:
                aiy.audio.say("Thirs DEe-Ayy-guh")
            if datetime.datetime.today().weekday() == 4:
                aiy.audio.say("It's Friday, Friday, gotta get down on Friday.")
            if datetime.datetime.today().weekday() == 5:
                aiy.audio.say("Sah")
                aiy.audio.say("TUR",pitch=300)
                aiy.audio.say("DAY",pitch=60)
            if datetime.datetime.today().weekday() == 6:
                aiy.audio.say("Yo duh, it's Sunday.")
            if datetime.datetime.today().weekday() == 3:
                aiy.audio.say("bla",pitch=60)
                aiy.audio.say("A",pitch=70)
                aiy.audio.say("A",pitch=100)
                aiy.audio.say("AAAAA",pitch=150)
                aiy.audio.say("AAAAAAAAA",pitch=200)
            
        elif text == "caillou":
            assistant.stop_conversation()
            ogvolume = aiy.audio.get_tts_volume()
            aiy.audio.set_tts_volume(20)
            audio_playing = True
            aiy.audio.play_wave("/home/pi/Downloads/caillou-caillou_album-01-caillou_theme_song.wav")
            aiy.audio.set_tts_volue(ogvolume)
            audio_playing = False
            stupid = True
        elif text == "that was awful":
            assistant.stop_conversation()
            if stupid == True:
                aiy.audio.say("Don't you dare insult Kai You", pitch=500)
                stupid = False
            else:
                aiy.audio.say("What was awful?")
        elif 'tendies' in text:
            assistant.stop_conversation()
            aiy.audio.say("No chicken tendies for you.")

        elif text == 'it all belongs to me':
            assistant.stop_conversation()
            aiy.audio.say("eh vree THING that I seeeeeee")

        elif text == 'i spy you spy':
            assistant.stop_conversation()
            aiy.audio.say("let's all play i spy")
            aiy.audio.say("I spy something. red")
            playing_ispy = True
    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

    
def main():
    if platform.machine() == 'armv6l':
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)
        
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()

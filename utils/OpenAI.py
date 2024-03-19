import os
from os.path import exists # Needs to be imported specifically

import requests
from requests.exceptions import JSONDecodeError
from mutagen.mp3 import MP3
import toml

from utils.console import print_substep

def read_config(file_path):
    with open(file_path, "r") as f:
        config = toml.load(f)
    return config

class OpenAI:
    def __init__(self):
        config = read_config("config.toml")

        print(config)

        api_key=config["openai"]["api_key"]

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def text_generation(self, message):
        url = "https://api.openai.com/v1/chat/completions"

        messages = [
            {"role": "system", "content": "Act as the master of curiosities, you are always full of enegery and provide curiosities about everything. generate curiosity text that will be used as a script for a video, add pause while speaking to make it more humam like. your response should be in brazilian portugues, text should fit in a 60 secconds video, minimum 1000 characters. add many curiosities to keep the spectator washing to the end, focus in fast curiosities. at the end of the video add text invinting to  follow for more curiosities"},
            {"role": "user", "content": message}
        ]
        
        body = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }

        try:
            response = requests.post(url, json=body, headers=self.headers)
            response.raise_for_status()

            response = response.json()

            text_generated = response["choices"][0]["message"]["content"]

            return text_generated

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            return None
        
    def text_to_speech(self, text, video_info):

        print(video_info["id"])

        filepath = f"assets/temp/{video_info['id']}/text_audio.mp3"

        url = "https://api.openai.com/v1/audio/speech"
        
        body = {
            "model": "tts-1",
            "voice": "echo",
            "input": text,
        }

        try:
            response = requests.post(url, json=body, headers=self.headers)

            if not exists(f"./assets/temp/{video_info['id']}"):
                print_substep("The results folder didn't exist so I made it")
                os.makedirs(f"./assets/temp/{video_info['id']}")

            with open(filepath, "wb") as f:
                f.write(response.content)

            audio_length = MP3(filepath).info.length
        except (KeyError, JSONDecodeError):
            try:
                if response.json()["error"] == "No text specified!":
                    raise ValueError("Please specify a text to convert to speech.")
            except (KeyError, JSONDecodeError):
                print("Error occurred calling Streamlabs Polly")

        return audio_length
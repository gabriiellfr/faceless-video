import uuid

from utils.OpenAI import OpenAI
from video_creation.background import (
    download_background,
    get_background_config,
    chop_background_video,
    crop_background
)
from video_creation.final_video import make_final_video

from utils.console import print_step

__VERSION__ = "0.1"

def main() -> None:
    print("FACELESS VIDEO MAKER STARTING", __VERSION__)

    # Initialize OpenAI instance
    openai_instance = OpenAI()

    # Generate text using OpenAI or retrieve it from another source
    print_step("Generating text...")
    text_generated = openai_instance.text_generation("qual a curiosidade do dia?")
    print(text_generated)

    video_info = {
        "id": uuid.uuid4(),
        "date": "2024-03-20",  # Example date
        "title": "video_title_here",
        "text": text_generated,
    }

    # Convert text to speech
    print_step("Converting text to speech...")
    video_info["length"] = openai_instance.text_to_speech(text_generated, video_info)

    print(video_info)

    # Generate transcription
    print_step("Generating transcription...")

    # Download, cut, and crop background video
    print("Downloading, cutting, and cropping background video...")
    bg_config = get_background_config()

    print(bg_config)

    download_background(bg_config)
    chop_background_video(bg_config, video_info)
    crop_background(video_info)

    # Make the final video
    print_step("Creating the final video...")
    make_final_video(video_info)


if __name__ == "__main__":
    main()

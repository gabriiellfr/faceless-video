import json
import random
import re
from pathlib import Path
from random import randrange
from typing import Any, Tuple
import subprocess
import ffmpeg
import multiprocessing

from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from utils.console import print_step, print_substep
from utils.progress_video import ProgressFfmpeg

# Load background videos
with open("./utils/backgrounds.json") as json_file:
    background_options = json.load(json_file)

# Remove "__comment" from backgrounds
background_options.pop("__comment", None)

# Add position lambda function
for name in list(background_options.keys()):
    pos = background_options[name][3]

    if pos != "center":
        background_options[name][3] = lambda t: ("center", pos + t)


def get_start_and_end_times(video_length: int, length_of_clip: int) -> Tuple[int, int]:
    """Generates a random interval of time to be used as the background of the video.

    Args:
        video_length (int): Length of the video
        length_of_clip (int): Length of the video to be used as the background

    Returns:
        tuple[int,int]: Start and end time of the randomized interval
    """
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def get_background_config():
    """Fetch the background/s configuration"""
    try:
        choice = "ASMR-1"
    except AttributeError:
        print_substep("No background selected. Picking random background'")
        choice = None

    # Handle default / not supported background using default option.
    # Default : pick random from supported background.
    if not choice or choice not in background_options:
        choice = random.choice(list(background_options.keys()))

    return background_options[choice]


def download_background(background_config: Tuple[str, str, str, Any]):
    """Downloads the background/s video from YouTube."""
    Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)
    uri, filename, credit, _ = background_config
    output_path = f"assets/backgrounds/{filename}"
    
    if Path(output_path).is_file():
        return
    
    print_step("We need to download the backgrounds videos. They are fairly large but it's only done once. 😎")
    print_substep("Downloading the backgrounds videos... please be patient 🙏 ")
    print_substep(f"Downloading {filename} from {uri}")
    
    # Use youtube-dl to download the video
    subprocess.run(["yt-dlp", "-f", "bestvideo", "-o", output_path, uri])

    
    print_substep("Background video downloaded successfully! 🎉", style="bold green")



def chop_background_video(
    background_config: Tuple[str, str, str, Any], 
    video_info
):
    """Generates the background footage to be used in the video and writes it to assets/temp/background.mp4

    Args:
        background_config (Tuple[str, str, str, Any]) : Current background configuration
        video_length (int): Length of the clip where the background footage is to be taken out of
    """

    print_step("Finding a spot in the backgrounds video to chop...✂️")

    choice = "asmr-1.mp4"
    id = video_info["id"]

    background = VideoFileClip(f"assets/backgrounds/{choice}")

    start_time, end_time = get_start_and_end_times(video_info["length"], background.duration)

    try:
        ffmpeg_extract_subclip(
            f"assets/backgrounds/{choice}",
            start_time,
            end_time,
            targetname=f"assets/temp/{id}/background.mp4",
        )
    except (OSError, IOError):  # ffmpeg issue see #348
        print_substep("FFMPEG issue. Trying again...")
        with VideoFileClip(f"assets/backgrounds/{choice}") as video:
            new = video.subclip(start_time, end_time)
            new.write_videofile(f"assets/temp/{id}/background.mp4")
            
    print_substep("Background video chopped successfully!", style="bold green")
    return background_config[2]

def crop_background(video_info, W = 1080, H = 1920) -> str:

    id = video_info['id']

    from tqdm import tqdm

    pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %")

    def on_update_example(progress):
        status = round(progress * 100, 2)
        old_percentage = pbar.n
        pbar.update(status - old_percentage)

    output_path = f"assets/temp/{id}/background_noaudio.mp4"

    try:
        with ProgressFfmpeg(video_info["length"], on_update_example) as progress:
            ffmpeg.input(f"assets/temp/{id}/background.mp4").filter("crop", f"ih*({W}/{H})", "ih").output(
                output_path,
                an=None,
                **{
                    "c:v": "h264",
                    "b:v": "20M",
                    "b:a": "192k",
                    "threads": multiprocessing.cpu_count(),
                },
            ).overwrite_output().global_args("-progress", progress.output_file.name).run(
                quiet=True,
            )
        
        old_percentage = pbar.n
        pbar.update(100 - old_percentage)
        pbar.close()
    except Exception as e:
        print(e)
        exit()

    print_substep("Background video cropped successfully!", style="bold green")
    return output_path
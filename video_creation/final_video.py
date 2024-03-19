import multiprocessing
import os
from os.path import exists # Needs to be imported specifically

import ffmpeg

from rich.console import Console

from utils.console import print_step, print_substep
from utils.progress_video import ProgressFfmpeg
from utils.trasncription import generate_text_overlay

console = Console()

def make_final_video(video_info):

    video_id = video_info["id"]
    video_text = video_info["text"]
    length = video_info["length"]

    print_step("Creating the final video 🎥")

    background_clip = ffmpeg.input(f"assets/temp/{video_id}/background_noaudio.mp4")

    console.log(f"[bold green] Video Will Be: {length} Seconds Long")

    audio = ffmpeg.input(f"assets/temp/{video_id}/text_audio.mp3")

    if not exists(f"./results/{video_id}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{video_id}")

    print_step("Rendering the video 🎥")

    background_clip_with_text = generate_text_overlay(background_clip, video_text, length)

    from tqdm import tqdm

    pbar = tqdm(total=100, desc="Progress: ", bar_format="{l_bar}{bar}", unit=" %")

    def on_update_example(progress):
        status = round(progress * 100, 2)
        old_percentage = pbar.n
        pbar.update(status - old_percentage)

    path = f"results/{video_id}/final_video"
    path = path[:251]
    path = path + ".mp4"

    with ProgressFfmpeg(length, on_update_example) as progress:
        ffmpeg.output(
            background_clip_with_text,
            audio,
            path,
            f="mp4",
            **{
                "c:v": "h264",
                "b:v": "20M",
                "b:a": "192k",
                "threads": multiprocessing.cpu_count(),
            },
        ).overwrite_output().global_args("-progress", progress.output_file.name).run(
            quiet=True,
            overwrite_output=True,
            capture_stdout=False,
            capture_stderr=False,
        )
        
    print_step("Done! 🎉 The video is in the results folder 📁")
    
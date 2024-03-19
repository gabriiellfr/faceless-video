import os
import ffmpeg

def split_text(text, max_words=12):
    """Split text into smaller parts by words with a maximum of 10 words per part."""
    words = text.split()
    parts = []
    current_part = ''
    word_count = 0
    for word in words:
        if word_count < max_words:
            current_part += ' ' + word
            word_count += 1
        else:
            parts.append(current_part.strip())
            current_part = word
            word_count = 1  # Reset word count for new part
        if word_count == 6:  # Add newline after every 5 words
            current_part += '\n'
    if current_part:
        parts.append(current_part.strip())
    return parts


def generate_text_overlay(background_video, video_text, audio_duration):
    """Generate ffmpeg commands to overlay text onto video."""

    text_parts = split_text(video_text)
    
    timestamp = 0
    for part in text_parts:
        duration = min(len(part) / 15, audio_duration - timestamp)  # Adjust speed as needed
        
        background_video = ffmpeg.drawtext(
            background_video,
            text=part,
            fontsize=30,
            fontcolor="white",
            fontfile=os.path.join("fonts", "Roboto-Regular.ttf"),
            x="(w-text_w)/2",
            y="(h-text_h)/2",
            start_number=0,
            enable=f"between(t,{timestamp},{timestamp + duration})",
            box=1,  # Add box background
            boxcolor="black",  # Black background with 50% opacity
            boxborderw=5,  # Box border width
        )

        timestamp += duration

        print(timestamp, "timestamp")
        
    return background_video
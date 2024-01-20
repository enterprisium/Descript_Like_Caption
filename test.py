from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip, ColorClip, concatenate_videoclips, AudioFileClip
import os
import whisper
import json
import ffmpeg


audiofilename = "tips.mp3"
model = whisper.load_model("medium")
result = model.transcribe(audiofilename, word_timestamps=True)



wordlevel_info = []

for segment in result['segments']:
    words = segment['words']
    for word in words:
        # Append the word and its start and end times to the wordlevel_info list
        wordlevel_info.append({
            'word': word['word'].strip(),
            'start': word['start'],
            'end': word['end']
        })



def split_text_into_lines(data):
    MaxChars = 80  # Maximum number of characters per line
    MaxDuration = 5.0  # Maximum duration of speech per line (in seconds)
    MaxGap = 1.5  # Split if the gap between words exceeds this duration (in seconds)

    lines = []
    current_line = []
    current_duration = 0
    current_chars = 0

    for idx, word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        current_line.append(word_data)
        current_duration += end - start
        temp_line = " ".join(item["word"] for item in current_line)
        new_line_chars = len(temp_line)

        # Check if adding a new word exceeds the maximum character count or duration
        duration_exceeded = current_duration > MaxDuration
        chars_exceeded = new_line_chars > MaxChars

        # Check for a significant gap between words
        if idx > 0:
            gap = word_data['start'] - data[idx - 1]['end']
            maxgap_exceeded = gap > MaxGap
        else:
            maxgap_exceeded = False

        # If any condition is met, start a new line
        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if current_line:
                # Create a line with combined text and the timing of the first and last word
                line = {
                    "word": temp_line,
                    "start": current_line[0]["start"],
                    "end": current_line[-1]["end"]
                }
                lines.append(line)
                current_line = []
                current_duration = 0
                current_chars = 0

    # Add the last line if it exists
    if current_line:
        line = {
            "word": " ".join(item["word"] for item in current_line),
            "start": current_line[0]["start"],
            "end": current_line[-1]["end"]
        }
        lines.append(line)

    return lines

subtitles = split_text_into_lines(wordlevel_info)

def create_video_with_subtitles(subtitles, audiofilename):
    # Settings for the subtitles
    font_size = 24
    font = 'Arial'
    color = 'white'

    # Initialize an array to hold clips
    clips = []

    # Define the size of the video frame
    frame_size = (1920, 1080)

    # Create a clip of the desired color and size to serve as the background
    background_clip = ColorClip(size=frame_size, color=(0, 0, 0))

    # Iterate over your subtitles
    for subtitle in subtitles:
        # Create a TextClip for each subtitle
        text_clip = TextClip(subtitle["word"], fontsize=font_size, font=font, color=color, size=frame_size)

        # Set the duration and start time for each text clip
        start_time = subtitle["start"]
        end_time = subtitle["end"]
        text_clip = text_clip.set_start(start_time).set_end(end_time).set_position('center').set_duration(
            end_time - start_time)

        # Append the clip to the clips array
        clips.append(text_clip)

    # Composite video clip with background and text clips
    video = CompositeVideoClip([background_clip] + clips, size=frame_size)

    # Load the audio file
    audio = AudioFileClip(audiofilename)

    # Set the audio of the combined clip
    video = video.set_audio(audio)

    # Set the duration of the video to the duration of the audio
    video = video.set_duration(audio.duration)

    # Write the final video file
    video.write_videofile("output_with_subtitles.mp4", fps=24, codec='libx264', audio_codec='aac')

# Example usage:
create_video_with_subtitles(subtitles, 'tips.mp3')

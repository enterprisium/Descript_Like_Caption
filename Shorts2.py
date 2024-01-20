import os
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.VideoClip import ImageClip
import numpy as np
import whisper
import json
import urllib.request
import ffmpeg
from IPython.display import Audio


Audiofilename = "demo audio.mp3"

model = whisper.load_model("medium")
result = model.transcribe(Audiofilename,word_timestamps=True)

for each in result['segments']:
    print(each)
wordlevel_info = []
for each in result['segments']:
  words = each['words']
  for word in words:
    wordlevel_info.append({'word':word['word'].strip(),'start':word['start'],'end':word['end']})
wordlevel_info
with open('data.json', 'w') as f:
    json.dump(wordlevel_info, f,indent=4)
with open('data.json', 'r') as f:
    wordlevel_info_modified = json.load(f)
wordlevel_info_modified
def split_text_into_lines(data):
    MaxChars = 20
    MaxDuration = 3.0
    MaxGap = 1.5
    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0
    for idx, word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]
        line.append(word_data)
        line_duration += end - start
        temp = " ".join(item["word"] for item in line)
        new_line_chars = len(temp)
        duration_exceeded = line_duration > MaxDuration
        chars_exceeded = new_line_chars > MaxChars
        if idx > 0:
            gap = word_data['start'] - data[idx - 1]['end']
            maxgap_exceeded = gap > MaxGap
        else:
            maxgap_exceeded = False
        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0
    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)
    return subtitles

linelevel_subtitles = split_text_into_lines(wordlevel_info_modified)

for line in linelevel_subtitles:
  json_str = json.dumps(line, indent=4)


def create_caption(textJSON, framesize, font="Montserrat-Bold", fontsize=30, color='Black', bgcolor='white'):
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end'] - textJSON['start']
    word_clips = []
    xy_textclips_positions = []
    x_pos = 0
    y_pos = 0
    frame_width = framesize[0]
    frame_height = framesize[1]
    x_buffer = frame_width * 1 / 10
    y_buffer = frame_height * 1 / 5
    space_width = ""
    space_height = ""
    line_width = 0  # Track the total width of the current line
    max_line_width = frame_width - 2 * x_buffer  # Maximum width for a line
    lines = []  # Store lines of text

    for index, wordJSON in enumerate(textJSON['textcontents']):
        duration = wordJSON['end'] - wordJSON['start']
        word_clip = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color).set_start(
            textJSON['start']).set_duration(full_duration)
        word_clip_space = TextClip(" ", font=font, fontsize=fontsize, color=color).set_start(
            textJSON['start']).set_duration(full_duration)
        word_width, word_height = word_clip.size
        space_width, space_height = word_clip_space.size

        # Check if adding the current word would exceed the line width
        if line_width + word_width + space_width <= max_line_width:
            # Add the word to the current line
            lines.append(wordJSON['word'])
            line_width += word_width + space_width
        else:
            # Create a new line with the collected words
            line_text = " ".join(lines)
            line_clip = TextClip(line_text, font=font, fontsize=fontsize, color=color, bg_color=bgcolor).set_start(
                textJSON['start']).set_duration(full_duration)
            line_clip = line_clip.set_position((x_buffer, y_pos + y_buffer))
            word_clips.append(line_clip)

            # Reset line variables for the new line
            lines = [wordJSON['word']]
            line_width = word_width + space_width
            y_pos += word_height + 10  # Adjust line spacing here

        word_clips.append(word_clip)
        word_clips.append(word_clip_space)

    # Create the last line of text
    if lines:
        line_text = " ".join(lines)
        line_clip = TextClip(line_text, font=font, fontsize=fontsize, color=color, bg_color=bgcolor).set_start(
            textJSON['start']).set_duration(full_duration)
        line_clip = line_clip.set_position((x_buffer, y_pos + y_buffer))
        word_clips.append(line_clip)

    return word_clips



from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips,VideoFileClip, ColorClip
frame_size = (1080,1920)
all_linelevel_splits=[]
for line in linelevel_subtitles:
  out = create_caption(line,frame_size)
  all_linelevel_splits.extend(out)

input_audio = AudioFileClip(Audiofilename)
input_audio_duration = input_audio.duration
image_path = "bg_shorts.png"
background_image = ImageClip(image_path, duration=input_audio_duration)
final_video = CompositeVideoClip([background_image] + all_linelevel_splits)
final_video = final_video.set_audio(input_audio)

final_video.write_videofile("Kids Story.mp4", fps=24, codec="libx264", audio_codec="aac")
import os
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.VideoClip import ImageClip
import numpy as np
import whisper
import json
import urllib.request
import ffmpeg
from IPython.display import Audio


Audiofilename = "5 tips.mp3"

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
    MaxChars = 220
    MaxDuration = 15.0
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

from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip, ColorClip, concatenate_videoclips, AudioFileClip

def create_caption(textJSON, framesize, font="Montserrat-Bold", fontsize=25, color='Black', bgcolor='white', line_height=20, top_margin=00, bottom_margin=10):
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end'] - textJSON['start']
    word_clips = []
    xy_textclips_positions = []
    x_pos = 0
    y_pos = top_margin  # Initialize y_pos with the top margin
    frame_width = framesize[0]
    frame_height = framesize[1]
    x_buffer = frame_width * 1 / 10
    y_buffer = frame_height * 1 / 5
    space_width = ""
    space_height = ""
    for index, wordJSON in enumerate(textJSON['textcontents']):
        duration = wordJSON['end'] - wordJSON['start']
        word_clip = TextClip(wordJSON['word'], font=font, fontsize=fontsize, color=color).set_start(
            textJSON['start']).set_duration(full_duration)
        word_clip_space = TextClip(" ", font=font, fontsize=fontsize, color=color).set_start(
            textJSON['start']).set_duration(full_duration)
        word_width, word_height = word_clip.size
        space_width, space_height = word_clip_space.size
        if x_pos + word_width + space_width > frame_width - 2 * x_buffer:
            new_y_pos = y_pos + word_height + line_height  # Calculate the new y position
            if new_y_pos + word_height <= frame_height - bottom_margin:  # Check if within bottom margin
                x_pos = 0
                y_pos = new_y_pos
                xy_textclips_positions.append({
                    "x_pos": x_pos + x_buffer,
                    "y_pos": y_pos + y_buffer,
                    "width": word_width,
                    "height": word_height,
                    "word": wordJSON['word'],
                    "start": wordJSON['start'],
                    "end": wordJSON['end'],
                    "duration": duration
                })
                word_clip = word_clip.set_position((x_pos + x_buffer, y_pos + y_buffer))
                word_clip_space = word_clip_space.set_position((x_pos + word_width + x_buffer, y_pos + y_buffer))
                x_pos = word_width + space_width
            else:
                # Handle the case where adding another line would exceed the bottom margin
                # You might want to stop adding more lines, or handle it in another way
                break  # As an example, just stop adding more lines
        else:
            xy_textclips_positions.append({
                "x_pos": x_pos + x_buffer,
                "y_pos": y_pos + y_buffer,
                "width": word_width,
                "height": word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })
            word_clip = word_clip.set_position((x_pos + x_buffer, y_pos + y_buffer))
            word_clip_space = word_clip_space.set_position((x_pos + word_width + x_buffer, y_pos + y_buffer))
            x_pos = x_pos + word_width + space_width
        word_clips.append(word_clip)
        word_clips.append(word_clip_space)
    for highlight_word in xy_textclips_positions:
        word_clip_highlight = TextClip(highlight_word['word'], font=font, fontsize=fontsize, color=color,
                                       bg_color=bgcolor).set_start(highlight_word['start']).set_duration(
            highlight_word['duration'])
        word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
        word_clips.append(word_clip_highlight)
    return word_clips



from moviepy.editor import TextClip, CompositeVideoClip, concatenate_videoclips,VideoFileClip, ColorClip
frame_size = (540,540)
all_linelevel_splits=[]
for line in linelevel_subtitles:
  out = create_caption(line,frame_size)
  all_linelevel_splits.extend(out)

input_audio = AudioFileClip(Audiofilename)
input_audio_duration = input_audio.duration
image_path = "demo short.png"
background_image = ImageClip(image_path, duration=input_audio_duration)
final_video = CompositeVideoClip([background_image] + all_linelevel_splits)
final_video = final_video.set_audio(input_audio)

final_video.write_videofile("demo short11.mp4", fps=24, codec="libx264", audio_codec="aac")
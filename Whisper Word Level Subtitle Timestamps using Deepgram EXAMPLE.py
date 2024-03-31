# Deepgram API Reference: https://developers.deepgram.com/documentation/guides/deepgram-whisper-cloud/
# Deepgram Website to signup for API key: https://deepgram.com/


from getpass import getpass
deepgramapiKey = getpass('Enter your deepgram API key: ')

# shows execution time of each cell
!pip install --quiet ipython-autotime
%load_ext autotime

import requests
def getDeepgramTranscription(p_url):
    # Use this to get subtitles in English
    url = "https://api.deepgram.com/v1/listen?model=whisper-large&language=en&punctuate=true&diarize=true&smart_format=true"

    # Use this to get subtitles in the same language as the audio/video
    # url = "https://api.deepgram.com/v1/listen?model=whisper-large&detect_language=true"

    payload = {
        "url": p_url
    }

    headers = {
        "Authorization": 'Token ' + deepgramapiKey,
        "content-type": "application/json"
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    output = response.json()
    return output


## Audio in English and Subtitles in English
mp3url = "https://github.com/ramsrigouthamg/Supertranslate.ai/raw/main/Deepgram_Whisper_Transcription/ps1_English.mp3"
output = getDeepgramTranscription(mp3url)
print (output)



from pprint import pprint
pprint (output['results']['channels'][0]['alternatives'][0]['transcript'])



from pprint import pprint
pprint (output['results']['channels'][0]['alternatives'][0]['words'])

def convert_to_srt(data, output_filename):
    def format_time(seconds):
        # Convert seconds to hours, minutes, seconds, milliseconds format
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, milliseconds = divmod(remainder, 1)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds*1000):03d}"

    with open(output_filename, 'w') as f:
        for i, entry in enumerate(data, start=1):
            start_time = format_time(entry['start'])
            end_time = format_time(entry['end'])
            subtitle_text = entry['punctuated_word']
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{subtitle_text}\n\n")  

import os
subtitle_data = output['results']['channels'][0]['alternatives'][0]['words']

# Extract the filename from the URL
filename = os.path.basename(mp3url)
name, extension = os.path.splitext(filename)
output_filename = name + ".srt"

# write a subtitle (.srt) file with word-level timestamps
convert_to_srt(subtitle_data,output_filename)   




# Place files in this path or modify the paths to point to where the files are
srtfilename = output_filename
mp4video = "/content/gdrive/My Drive/Deepgram_Whisper_Transcription/ps1_English.mp4"



import shutil
target = os.path.basename(mp4video)
print (target)
shutil.copy(mp4video, target)


output_video = target.replace(".mp4","_wordlevel_subtitles.mp4")
print (target)
print (srtfilename)
print (output_video)



# This will take 2-3 mins to run
os.system(f"ffmpeg -i {target} -vf subtitles={srtfilename} {output_video}")



parent_directory = os.path.dirname(mp4video)
print (parent_directory)
copy_path = os.path.join(parent_directory,output_video)
print (copy_path)
shutil.copy(output_video, copy_path)

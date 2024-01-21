import ffmpeg

# pip install ffmpeg-python

mp4videoURL = "John's Good Habit.mp4"
videofilename = mp4videoURL.split('/')[-1]
audiofilename = videofilename.replace(".mp4",'.mp3')

input_stream = ffmpeg.input(videofilename)

audio = input_stream.audio
output_stream = ffmpeg.output(audio, audiofilename)

# Overwrite output file if it already exists
output_stream = ffmpeg.overwrite_output(output_stream)

ffmpeg.run(output_stream)


import whisper

model = whisper.load_model("base")
result =  model.transcribe("Audion.mp3")

with open ("transcription.txt", "w") as f:
    f.write(result["text"])
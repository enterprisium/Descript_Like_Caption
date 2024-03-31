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


Audio in English and Subtitles in English



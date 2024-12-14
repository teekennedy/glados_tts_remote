# GLaDOS Text-to-speech (TTS) Home Assistant Integraton

Neural network based TTS engine for the character GLaDOS.

## Server Quickstart

1. Download the model files from [`Google Drive`](https://drive.google.com/file/d/1TRJtctjETgVVD5p7frSVPmgw8z8FFtjD/view?usp=sharing) and unzip into the repo folder
1. Start the glados-tts server:

   `docker run -v $(pwd)/models:/app/models --rm -p 8124:8124 ghcr.io/teekennedy/glados_tts_remote`

1. Send a request to the `/say` endpoint and you'll get an audio file in response:

   `curl -G localhost:8124/say --data-urlencode "text=This is the GLaDOS text-to-speech service." --data-urlencode "format=mp3" --output output.mp3`
